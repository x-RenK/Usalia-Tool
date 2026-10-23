"""Small bilingual CSV workbench; binary tools are exposed through the CLI."""
from pathlib import Path
import csv
import os
import queue
import threading
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from .text import load_sheet,FIELDS,encode,load_mapping,export_text,prepare_text,build_text

STRINGS={
'en':{'title':'Usalia Tool — Disgaea 1 Complete NX','open':'Open CSV','save':'Save CSV as…','source':'Choose source file','export':'Export text…','check':'Validate','build':'Build translated file…','find':'Search original / translation','apply':'Update selected row','original':'Original','translation':'Translation','kind':'Extraction kind','mapping':'Carrier mapping','hint':'Edit translation only. Keep the CSV .json sidecar. ptbr requires a verified native accent IPS. Binary/archive/image tools: python -m usalia --help','busy':'Working…','done':'Completed','select':'Select a row first'},
'pt-BR':{'title':'Usalia Tool — Disgaea 1 Complete NX','open':'Abrir CSV','save':'Salvar CSV como…','source':'Escolher arquivo base','export':'Extrair textos…','check':'Validar','build':'Gerar arquivo traduzido…','find':'Buscar original / tradução','apply':'Atualizar linha selecionada','original':'Original','translation':'Tradução','kind':'Tipo de extração','mapping':'Mapa de caracteres','hint':'Edite somente translation. Preserve o .json ao lado do CSV. ptbr exige o IPS de acentos verificado. Arquivos/imagens: python -m usalia --help','busy':'Processando…','done':'Concluído','select':'Selecione uma linha primeiro'}
}

class Workbench:
    def __init__(self,root):
        self.root=root;self.lang=tk.StringVar(value='pt-BR');self.rows=[];self.sheet=None;self.source=None;self.dirty=False;self.jobs=queue.Queue();self.locked=False
        self.root.geometry('1100x760');self.root.protocol('WM_DELETE_WINDOW',self.close)
        top=ttk.Frame(root);top.pack(fill='x',padx=10,pady=8)
        box=ttk.Combobox(top,textvariable=self.lang,values=list(STRINGS),state='readonly',width=8);box.pack(side='right');box.bind('<<ComboboxSelected>>',lambda e:self.labels())
        self.buttons={}
        for key,fn in [('open',self.open),('save',self.save),('source',self.choose_source),('export',self.export),('check',self.check),('build',self.build)]:
            b=ttk.Button(top,command=fn);b.pack(side='left',padx=2);self.buttons[key]=b
        config=ttk.Frame(root);config.pack(fill='x',padx=10)
        self.kindlabel=ttk.Label(config);self.kindlabel.pack(side='left');self.kind=tk.StringVar(value='banks');ttk.Combobox(config,textvariable=self.kind,values=['banks','story','cstrings'],state='readonly',width=10).pack(side='left',padx=6)
        self.maplabel=ttk.Label(config);self.maplabel.pack(side='left');self.mapping=tk.StringVar(value='none');ttk.Combobox(config,textvariable=self.mapping,values=['none','ptbr'],state='readonly',width=10).pack(side='left',padx=6)
        self.search=tk.StringVar();self.search.trace_add('write',lambda *_:self.refresh());self.findlabel=ttk.Label(root);self.findlabel.pack(anchor='w',padx=10);ttk.Entry(root,textvariable=self.search).pack(fill='x',padx=10)
        frame=ttk.Frame(root);frame.pack(fill='both',expand=True,padx=10,pady=8)
        self.tree=ttk.Treeview(frame,columns=['id','original','translation','bytes'],show='headings',selectmode='browse');self.tree.pack(side='left',fill='both',expand=True)
        for c,w in [('id',55),('original',450),('translation',450),('bytes',80)]:self.tree.heading(c,text=c);self.tree.column(c,width=w,stretch=c in ['original','translation'])
        scroll=ttk.Scrollbar(frame,orient='vertical',command=self.tree.yview);scroll.pack(side='right',fill='y');self.tree.configure(yscrollcommand=scroll.set);self.tree.bind('<<TreeviewSelect>>',self.select)
        self.origlabel=ttk.Label(root);self.origlabel.pack(anchor='w',padx=10);self.original=tk.Text(root,height=3,wrap='word',state='disabled');self.original.pack(fill='x',padx=10)
        self.trlabel=ttk.Label(root);self.trlabel.pack(anchor='w',padx=10);self.translation=tk.Text(root,height=4,wrap='word');self.translation.pack(fill='x',padx=10)
        self.applybutton=ttk.Button(root,command=self.apply);self.applybutton.pack(pady=4)
        self.hint=ttk.Label(root,wraplength=1080);self.hint.pack(fill='x',padx=10)
        self.status=tk.StringVar();ttk.Label(root,textvariable=self.status).pack(fill='x',padx=10,pady=5);self.labels();root.after(150,self.poll)
    def t(self,k):return STRINGS[self.lang.get()][k]
    def labels(self):
        self.root.title(self.t('title'))
        for k,b in self.buttons.items():b.config(text=self.t(k))
        for w,k in [(self.kindlabel,'kind'),(self.maplabel,'mapping'),(self.findlabel,'find'),(self.origlabel,'original'),(self.trlabel,'translation'),(self.applybutton,'apply'),(self.hint,'hint')]:w.config(text=self.t(k))
    def mp(self):return None if self.mapping.get()=='none' else self.mapping.get()
    def confirm_dirty(self):return not self.dirty or messagebox.askyesno('Usalia','Discard unsaved changes? / Descartar alterações não salvas?')
    def open(self):
        if not self.confirm_dirty():return
        p=filedialog.askopenfilename(filetypes=[('CSV','*.csv')])
        if p:
            try:self.rows=load_sheet(p);self.sheet=Path(p);self.dirty=False;self.refresh();self.status.set(p)
            except Exception as e:messagebox.showerror('Usalia',str(e))
    def refresh(self):
        self.tree.delete(*self.tree.get_children());query=self.search.get().casefold()
        for i,r in enumerate(self.rows):
            if not query or query in (r['original']+' '+r['translation']).casefold():self.tree.insert('', 'end',iid=str(i),values=[r['id'],r['original'],r['translation'],r['slot_bytes']])
    def select(self,_=None):
        s=self.tree.selection()
        if not s:return
        r=self.rows[int(s[0])];self.original.config(state='normal');self.original.delete('1.0','end');self.original.insert('1.0',r['original']);self.original.config(state='disabled');self.translation.delete('1.0','end');self.translation.insert('1.0',r['translation'])
    def apply(self):
        s=self.tree.selection()
        if not s:return
        r=self.rows[int(s[0])];tr=self.translation.get('1.0','end-1c')
        try:
            size=len(encode(tr,load_mapping(self.mp())))+(1 if r['padding']=='nul' else 0)
            if size>int(r['slot_bytes']):raise ValueError(f'{size} bytes > {r["slot_bytes"]}')
        except Exception as e:messagebox.showerror('Usalia',str(e));return
        r['translation']=tr;self.dirty=True;self.refresh();self.status.set(f'{size} / {r["slot_bytes"]} bytes')
    def save(self):
        if not self.sheet:return
        p=filedialog.asksaveasfilename(defaultextension='.csv',initialfile=self.sheet.name)
        if not p:return
        try:
            import shutil
            side=Path(str(self.sheet)+'.json');dest=Path(str(p)+'.json')
            if side.resolve()!=dest.resolve():
                if dest.exists():raise ValueError('Sidecar exists; choose a new filename / JSON já existe')
                shutil.copyfile(side,dest)
            with open(p,'w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=FIELDS,delimiter=';');w.writeheader();w.writerows(self.rows)
            self.sheet=Path(p);self.dirty=False;self.status.set(p)
        except Exception as e:messagebox.showerror('Usalia',str(e))
    def choose_source(self):
        p=filedialog.askopenfilename()
        if p:self.source=Path(p);self.status.set(p)
    def worker(self,fn):
        if self.locked:return
        self.locked=True;self.status.set(self.t('busy'))
        for b in self.buttons.values():b.config(state='disabled')
        def task():
            try:self.jobs.put((True,fn()))
            except Exception as e:self.jobs.put((False,str(e)))
        threading.Thread(target=task,daemon=True).start()
    def poll(self):
        try:
            ok,r=self.jobs.get_nowait();self.locked=False
            for b in self.buttons.values():b.config(state='normal')
            self.status.set(self.t('done')+': '+str(r))
            if not ok:messagebox.showerror('Usalia',str(r))
        except queue.Empty:pass
        self.root.after(150,self.poll)
    def export(self):
        if not self.source:self.choose_source()
        if not self.source:return
        p=filedialog.asksaveasfilename(defaultextension='.csv')
        if p:
            source,kind,mp=self.source,self.kind.get(),self.mp();self.worker(lambda:export_text(source,p,kind,mp))
    def ready(self):
        if self.dirty:messagebox.showinfo('Usalia','Save CSV first / Salve o CSV primeiro');return False
        return self.sheet is not None and self.source is not None
    def check(self):
        if self.ready():
            src,sheet,mp=self.source,self.sheet,self.mp();self.worker(lambda:len(prepare_text(src,sheet,mp)))
    def build(self):
        if not self.ready():return
        p=filedialog.asksaveasfilename()
        if p:
            src,sheet,mp=self.source,self.sheet,self.mp();self.worker(lambda:build_text(src,sheet,p,mp))
    def close(self):
        if self.locked:messagebox.showinfo('Usalia','Wait for operation / Aguarde a operação');return
        if self.confirm_dirty():self.root.destroy()

def main():
    root=tk.Tk();Workbench(root);root.mainloop()
if __name__=='__main__':main()
