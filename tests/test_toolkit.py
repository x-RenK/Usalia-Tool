import csv
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
import numpy as np
from PIL import Image
from usalia import archives,compression,ips,text,textures,release,patches
from usalia.common import FormatError,sha256


def archive(path, entries, pc=False):
    stride=52 if pc else 64;off=16+stride*len(entries);head=bytearray((b'PSPFS_V1' if pc else b'PS_FS_V1')+struct.pack('<Q',len(entries)));body=bytearray()
    for name,payload in entries:
        if pc:r=name.encode().ljust(40,b'\0')+struct.pack('<III',0,len(payload),off)
        else:r=name.encode().ljust(48,b'\0')+struct.pack('<QQ',len(payload),off)
        head+=r;body+=payload;off+=len(payload)
    path.write_bytes(head+body)

class ToolkitTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def path(self,n):return self.root/n
    def test_archives_append_preserves_prefix(self):
        for pc in (False,True):
            a=self.path('in'+str(pc));archive(a,[('foo',b'abc'),('dummy.dat',b'x'),('dummy.dat',b'y')],pc);old=a.read_bytes()
            self.assertEqual(len(archives.psfs_entries(a)),3)
            with self.assertRaises(ValueError):archives.select(archives.psfs_entries(a),'dummy.dat')
            repl=self.path('replace'+str(pc));repl.write_bytes(b'expanded payload');out=self.path('out'+str(pc));archives.replace(a,'foo',repl,out)
            row=archives.psfs_entries(out)[0];self.assertEqual(row.offset%512,0);self.assertEqual(out.read_bytes()[row.offset:row.offset+row.size],repl.read_bytes())
            patched=bytearray(out.read_bytes()[:len(old)]);start=16+(44 if pc else 48);n=8 if pc else 16;patched[start:start+n]=old[start:start+n];self.assertEqual(bytes(patched),old)
            with self.assertRaises(ValueError):archives.replace(a,'foo',repl,a)
            with self.assertRaises(ValueError):archives.replace(a,'foo',repl,out)
    def test_truncated_archive(self):
        p=self.path('a');archive(p,[('a',b'abc')]);p.write_bytes(p.read_bytes()[:-1])
        with self.assertRaises(ValueError):archives.psfs_entries(p)
    def test_start_equal_size(self):
        p=self.path('start');p.write_bytes(struct.pack('<3I',2,12,15)+b'abcdef');r=self.path('r');r.write_bytes(b'XYZ');out=self.path('out');archives.replace_start(p,1,r,out);self.assertEqual(out.read_bytes()[-6:],b'abcXYZ')
        r.write_bytes(b'long')
        with self.assertRaises(ValueError):archives.replace_start(p,1,r,self.path('bad'))
    def test_yk_roundtrip_and_backreferences(self):
        raw=bytes(range(256))*7
        for k in (4,7):self.assertEqual(compression.yk_decode(compression.yk_encode(raw,k)),raw)
        # Three literals followed by an overlapping six-byte backreference.
        payload=b'\x03abc\xc4\x02';packed=struct.pack('<8sIII',b'YKCMP_V1',4,20+len(payload),9)+payload
        self.assertEqual(compression.yk_decode(packed),b'abcabcabc')
        with self.assertRaises(ValueError):compression.yk_decode(packed[:-1])
    def test_imy_literal_and_package(self):
        h=bytearray(34);h[:4]=b'IMY\0';struct.pack_into('<H',h,8,4);struct.pack_into('<H',h,12,1);struct.pack_into('<H',h,32,1);b=bytes(h)+b'\x01abcd'
        self.assertEqual(compression.imy_decode(b),b'abcd')
        package=struct.pack('<III',1,4,12)+b;self.assertEqual(compression.imy_package_decode(package),b'abcd')
        with self.assertRaises(ValueError):compression.imy_decode(b[:-1])
    def test_ips_conflicts_and_roundtrip(self):
        for wide in (False,True):
            p={100:1,101:2,800:4};self.assertEqual(ips.parse(ips.serialize(p,wide)),p)
        a=self.path('a.ips');b=self.path('b.ips');a.write_bytes(ips.serialize({1:2}));b.write_bytes(ips.serialize({1:3}))
        with self.assertRaises(ValueError):ips.merge([a,b])
        with self.assertRaises(ValueError):ips.parse(a.read_bytes()+b'extra')
    def test_native_accent_patch(self):
        data=bytearray(0x210000);data[:4]=b'NSO0';data[0x40:0x50]=bytes.fromhex(ips.BUILD_ID)
        for ch,r in text.CARRIERS.items():struct.pack_into('<H',data,0x100+r['unicode_table_offset'],ord(r['carrier']))
        p=self.path('main');p.write_bytes(data);patch=ips.accents(p);self.assertEqual(len(patch),96)
        for k,v in patch.items():data[k]=v
        p.write_bytes(data);self.assertEqual(ips.accents(p),patch)
        data[0x40]=0;p.write_bytes(data)
        with self.assertRaises(ValueError):ips.accents(p)
    def test_unicode_encoding(self):
        mp=text.load_mapping('ptbr');s='Próximo Episódio — ação'
        # Em dash compatibility is intentionally not silently substituted.
        encoded=text.encode('Próximo Episódio, ação',mp);self.assertEqual(text.decode(encoded,mp),'Próximo Episódio, ação');self.assertIn(bytes.fromhex('8b8f'),encoded)
        with self.assertRaises(ValueError):text.encode('ã')
    def test_text_sheet_integrity_and_story_padding(self):
        p=self.path('script');p.write_bytes(b'\x01'+text.encode('Hello world')+b'\0'+b'\x05'+text.encode('Second line')+b'\0')
        sheet=self.path('texts.csv');self.assertEqual(text.export_text(p,sheet,'cstrings'),2)
        rows=text.load_sheet(sheet);rows[0]['translation']='Oi'
        def save():
            with sheet.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=text.FIELDS,delimiter=';');w.writeheader();w.writerows(rows)
        save();out=self.path('translated');text.build_text(p,sheet,out);self.assertEqual(len(out.read_bytes()),len(p.read_bytes()));self.assertEqual(out.read_bytes().count(b'\0'),p.read_bytes().count(b'\0'))
        rows[0]['translation']='x'*100;save()
        with self.assertRaises(ValueError):text.prepare_text(p,sheet)
        rows[0]['translation']='Oi';rows[0]['offset']='0';save()
        with self.assertRaises(ValueError):text.prepare_text(p,sheet)
    def test_tx2_palette_exact(self):
        pal=bytes([0,0,0,0,255,255,255,255])+bytes(14*4);data=struct.pack('<8H',2,2,16,0,16,1,0,1)+pal+b'\x10\x01'
        im=textures.decode_tx2(data);self.assertEqual(textures.encode_tx2(data,im),data)
        im.putpixel((0,0),(30,40,50,255))
        with self.assertRaises(ValueError):textures.encode_tx2(data,im)
    def test_nltx_block_preservation(self):
        w=h=32;pw=512;ph=256;im=Image.new('RGB',(pw,ph),(60,40,90));buf=io.BytesIO();im.save(buf,format='DDS',pixel_format='DXT1');lin=np.frombuffer(buf.getvalue()[128:],np.uint8).reshape(ph//4,pw//4,8);idx,_,_=textures.block_indices(w,h,pw*ph//2);raw=np.zeros(pw*ph//2,np.uint8);raw[idx]=lin
        head=bytearray(128);head[:8]=b'NMPLTEX1';struct.pack_into('<II',head,24,w,h);data=bytes(head)+compression.yk_encode(raw.tobytes());old=textures.decode_nltx(data)[0];unchanged,n=textures.encode_nltx(data,old);self.assertEqual(unchanged,data);self.assertEqual(n,0)
        new=old.copy();new.putpixel((8,8),(255,255,255,255));result,n=textures.encode_nltx(data,new);self.assertEqual(n,1);a=textures.decode_nltx(data)[5];b=textures.decode_nltx(result)[5];self.assertEqual(int(np.any(a!=b,axis=2).sum()),1)
    def test_hd_indexed_import_and_anm_ids(self):
        header=struct.pack('<8I',76,0,1,1,1,0,0,0)
        fields=[0]*12;fields[0]=5002;fields[4]=1;fields[5]=1
        obj=struct.pack('<I12H',28,*fields)
        descriptors=struct.pack('<HHHHII',265,257,2,2,1,0)+struct.pack('<HHHHII',0,0,2,1,1,4)
        data=header+obj+descriptors+bytes([0,1,1,0])+bytes([0,0,0,0,255,255,255,255])
        p=self.path('hd');p.write_bytes(data);im=textures.hd_sheet(p,0,0);out=self.path('hd_noop');textures.hd_replace_rgba(p,0,0,im,out);self.assertEqual(out.read_bytes(),data)
        im.putpixel((0,0),(255,255,255,255));changed=self.path('hd_new');textures.hd_replace_rgba(p,0,0,im,changed);self.assertEqual(changed.read_bytes()[:92],data[:92]);self.assertEqual(changed.read_bytes()[96:],data[96:]);self.assertEqual(changed.read_bytes()[92],1)
        anm=struct.pack('<IIH',1,16,5002)+bytes(6)+struct.pack('<6H',1,1,0,0,0,0)
        self.assertEqual(archives.anm_index(anm)[0]['resource_id'],5002)
    def test_nso_memory_address_convention(self):
        from usalia.nso import memory_image
        data=bytearray(280);data[:4]=b'NSO0'
        for i in range(3):struct.pack_into('<III',data,16+i*16,256+i*8,i*32,8);data[256+i*8:264+i*8]=bytes([i+1])*8
        out=memory_image(data)
        self.assertEqual(out[256:264],bytes([1])*8);self.assertEqual(out[288:296],bytes([2])*8);self.assertEqual(out[320:328],bytes([3])*8)
    def test_multiple_sheets_overlap_rejected(self):
        p=self.path('script');p.write_bytes(text.encode('Hello world')+b'\0');sheet=self.path('text.csv');text.export_text(p,sheet,'cstrings');rows=text.load_sheet(sheet);rows[0]['translation']='Hi'
        with sheet.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=text.FIELDS,delimiter=';');w.writeheader();w.writerows(rows)
        with self.assertRaises(ValueError):text.prepare_many(p,[sheet,sheet])
    def test_manifest_and_clean_release(self):
        src=self.path('source');src.write_bytes(b'old\0');m=self.path('edits.json');m.write_text(json.dumps({'source_sha256':sha256(src),'edits':[{'offset':0,'expected_hex':src.read_bytes().hex(),'text':'new','encoding':'ascii'}]}));self.assertEqual(ips.parse(ips.serialize(patches.from_manifest(src,m))),dict(enumerate(b'new\0')))
        sub=self.path('SUBDATA.DAT');archive(sub,[('x',b'abc')]);others=[]
        for name in ['script.dat','rootfont.bin','datafont.bin',ips.BUILD_ID+'.ips','README.txt']:
            p=self.path(name)
            if 'font.bin' in name:
                data=bytearray(64+24+64);struct.pack_into('<4H',data,0,8,8,8,8);struct.pack_into('<I',data,24,1);p.write_bytes(data)
            else:p.write_bytes(ips.serialize({4:2}) if name.endswith('.ips') else b'example')
            others.append(p)
        out=self.path('release.zip');r=release.package(sub,*others,out);self.assertEqual(len(r['files']),6)

if __name__=='__main__':unittest.main()
