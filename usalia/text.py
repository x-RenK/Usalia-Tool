"""Fixed-slot localization. Translation sheets are bound to exact source bytes."""
import csv
from importlib.resources import files
import json
from pathlib import Path
import shutil
import struct
import unicodedata
from .archives import psfs_entries, select
from .common import require, read_at, sha256, write_json, atomic_output

LAYOUTS = json.loads(files('usalia').joinpath('data/layouts.json').read_text('utf-8'))
CARRIERS = json.loads(files('usalia').joinpath('data/ptbr-carriers.json').read_text('utf-8'))
FIELDS = ['id','resource','offset','slot_bytes','padding','raw_hex','original','translation']

def load_mapping(name=None):
    if name is None: return {}
    if name == 'ptbr': return {c:r['cp932'] for c,r in CARRIERS.items()}
    data = json.loads(Path(name).read_text('utf-8'))
    mapping = {c:(r['cp932'] if isinstance(r,dict) else r) for c,r in data.items()}
    require(all(len(c)==1 and len(bytes.fromhex(v))==2 for c,v in mapping.items()), 'Mapping expects one character to two CP932 bytes')
    return mapping

def decode(data, mapping=None):
    reverse = {bytes.fromhex(v).decode('cp932'): k for k,v in (mapping or {}).items()}
    s = data.decode('cp932', 'strict')
    return unicodedata.normalize('NFKC', ''.join(reverse.get(c,c) for c in s))

def encode(text, mapping=None, fullwidth=True):
    text = unicodedata.normalize('NFC', text)
    require('\0' not in text, 'NUL is not allowed in a translation')
    out = bytearray()
    for c in text:
        if c in (mapping or {}):
            out.extend(bytes.fromhex(mapping[c])); continue
        if fullwidth:
            if c == ' ': c = '\u3000'
            elif 0x21 <= ord(c) <= 0x7e:c = chr(ord(c)+0xfee0)
            elif c == '¥':c = '\uffe5'
        try: out.extend(c.encode('cp932', 'strict'))
        except UnicodeEncodeError as ex:raise ValueError(f'Unrepresentable character {c!r}; supply a verified carrier mapping + executable patch') from ex
    return bytes(out)

def start_index(path):
    e = select(psfs_entries(path), 'start.dat')
    n = struct.unpack('<I', read_at(path,e.offset,4))[0]
    require(0 < n <= 10000 and 4+n*4 <= e.size, 'Compressed/unsupported START; ENG bank extraction requires plain START')
    offsets = struct.unpack(f'<{n}I', read_at(path,e.offset+4,n*4))
    require(offsets[0] >= 4+n*4 and list(offsets)==sorted(offsets) and offsets[-1]<=e.size, 'Invalid START table')
    return [(i,e.offset+a,b-a) for i,(a,b) in enumerate(zip(offsets,offsets[1:]+(e.size,)))]

def candidates(blob, mapping=None):
    """Heuristic ENG CP932/fullwidth cstrings, not a bytecode disassembler."""
    p = 0
    while p < len(blob):
        end = blob.find(b'\0',p)
        if end < 0:break
        raw = blob[p:end]
        if len(raw)>=4:
            for prefix in range(min(12,len(raw))):
                if len(raw)-prefix<4:continue
                try: s = decode(raw[prefix:],mapping)
                except UnicodeDecodeError:continue
                letters = sum(c.isascii() and c.isalpha() for c in s)
                allowed = sum((c.isascii() and c.isprintable()) or c in "’“”‘…—–・♥★♪×○△□¥\r\n\t" or c in (mapping or {}) for c in s)
                if letters>=2 and allowed/max(len(s),1)>=.93 and all(ord(c)>=32 or c in '\r\n\t' for c in s):
                    if s and (s[0].isascii() and (s[0].isalnum() or s[0] in " .,!?'\"<([*-_")):
                        yield p+prefix, end-p-prefix, s
                        break
        p = end+1

def export_text(path, csv_path, kind='banks', mapping=None):
    path, csv_path = Path(path),Path(csv_path)
    mp = load_mapping(mapping)
    records=[]
    def add(resource,offset,slot,padding,original):
        raw=read_at(path,offset,slot)
        records.append(dict(id=len(records),resource=resource,offset=offset,slot_bytes=slot,padding=padding,raw_hex=raw.hex(),original=original,translation=''))
    if kind=='banks':
        entries=start_index(path)
        names=LAYOUTS['start_names_historical']
        for key,layout in LAYOUTS['english_layouts'].items():
            idx=int(key);require(idx<len(entries),'Missing supported START bank')
            _,off,size=entries[idx];blob=read_at(path,off,size)
            n=struct.unpack_from('<I',blob)[0]
            require(0<n<=100000 and 8+n*layout['row_size']<=len(blob),f'Unsupported ENG bank layout #{idx}')
            for row in range(n):
                for field,rel,slot in layout['fields']:
                    pos=8+row*layout['row_size']+rel
                    raw=blob[pos:pos+slot].split(b'\0',1)[0]
                    try:s=decode(raw,mp)
                    except UnicodeDecodeError:continue
                    if s.strip() and any(c.isalpha() for c in s):
                        add(f'START[{idx}]/{names[idx]}/{row}/{field}',off+pos,slot,'nul',s)
    elif kind in ('story','cstrings'):
        if kind=='story':
            _,off,size=start_index(path)[0];blob=read_at(path,off,size);resource='START[0]/script.dat/heuristic'
        else:
            off=0;blob=path.read_bytes();resource='external/heuristic'
        for pos,slot,s in candidates(blob,mp):add(resource,off+pos,slot,'spaces',s)
    else:raise ValueError('Unknown extraction kind')
    require(records,'No supported text found')
    require(not csv_path.exists() and not Path(str(csv_path)+'.json').exists(),'Output sheet already exists')
    with atomic_output(csv_path) as tmp:
        with tmp.open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=FIELDS,delimiter=';');w.writeheader();w.writerows(records)
    write_json(str(csv_path)+'.json',{'schema':1,'source_sha256':sha256(path),'source_size':path.stat().st_size,'kind':kind,'records':[{k:v for k,v in r.items() if k!='translation'} for r in records]})
    return len(records)

def load_sheet(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        line=f.readline();f.seek(0)
        delim=max([';',',','\t'],key=line.count)
        return list(csv.DictReader(f,delimiter=delim))

def prepare_text(path,sheet,mapping=None,fullwidth=True):
    meta=json.loads(Path(str(sheet)+'.json').read_text('utf-8'))
    require(meta['schema']==1 and meta['source_size']==Path(path).stat().st_size and meta['source_sha256']==sha256(path),'Sheet was exported from a different source file')
    trusted={str(r['id']):r for r in meta['records']};seen=set();patches=[];mp=load_mapping(mapping)
    for row in load_sheet(sheet):
        key=row['id'];require(key in trusted and key not in seen,'Unknown or duplicate record ID');seen.add(key)
        original=trusted[key]
        for k in FIELDS:
            if k!='translation':require(str(original[k])==row[k],f'Metadata edited at #{key}: edit translation only')
        tr=row['translation']
        if not tr:continue
        data=encode(tr,mp,fullwidth);slot=int(original['slot_bytes']);off=int(original['offset'])
        require(read_at(path,off,slot).hex()==original['raw_hex'],'Original bytes mismatch')
        if original['padding']=='nul':
            require(len(data)+1<=slot,f'#{key}: needs {len(data)+1} bytes, slot {slot}')
            data=(data+b'\0').ljust(slot,b'\0')
        else:
            require(len(data)<=slot,f'#{key}: needs {len(data)} bytes, slot {slot}')
            left=slot-len(data);data+=b'\x81\x40'*(left//2)+b' '*(left%2)
        patches.append((off,data))
    require(seen==set(trusted),'Records removed from sheet; keep all rows')
    spans=sorted((off,off+len(data)) for off,data in patches)
    require(all(a[1]<=b[0] for a,b in zip(spans,spans[1:])),'Overlapping text writes')
    return patches

def prepare_many(path,sheets,mapping=None,fullwidth=True):
    patches=[]
    for sheet in sheets:patches.extend(prepare_text(path,sheet,mapping,fullwidth))
    spans=sorted((off,off+len(data)) for off,data in patches)
    require(all(a[1]<=b[0] for a,b in zip(spans,spans[1:])),'Overlapping edits across sheets')
    return patches

def build_text(path,sheet,output,mapping=None,fullwidth=True,extra_sheets=None):
    patches=prepare_many(path,[sheet]+list(extra_sheets or []),mapping,fullwidth)
    with atomic_output(output,path) as tmp:
        shutil.copyfile(path,tmp)
        with tmp.open('r+b') as f:
            for off,data in patches:f.seek(off);f.write(data)
    return len(patches)
