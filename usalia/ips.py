"""IPS/IPS32 inspection, conflict-aware merging and validated native accent patches."""
import struct
from pathlib import Path
from .common import require
from .text import CARRIERS

BUILD_ID='81F7AB934AD9A6DC823F64A10E12C93C'

def parse(data):
    if data[:5]==b'PATCH':width,end,p=3,b'EOF',5
    elif data[:5]==b'IPS32':width,end,p=4,b'EEOF',5
    else:raise ValueError('Invalid IPS/IPS32 header')
    out={}
    while True:
        require(p+len(end)<=len(data),'Missing IPS end marker')
        if data[p:p+len(end)]==end:
            p+=len(end);break
        require(p+width+2<=len(data),'Truncated IPS record')
        off=int.from_bytes(data[p:p+width],'big');n=int.from_bytes(data[p+width:p+width+2],'big');p+=width+2
        if n:
            require(p+n<=len(data),'Truncated IPS payload');chunk=data[p:p+n];p+=n
        else:
            require(p+3<=len(data),'Truncated IPS RLE');n=int.from_bytes(data[p:p+2],'big');chunk=data[p+2:p+3]*n;p+=3
            require(n>0,'Zero length IPS RLE')
        for i,v in enumerate(chunk):
            k=off+i;require(k not in out or out[k]==v,'Conflicting overlapping records inside IPS');out[k]=v
    require(p==len(data),'IPS truncate/footer extension not supported; no silent discard')
    return out

def serialize(patch,ips32=False):
    width,end=(4,b'EEOF') if ips32 else (3,b'EOF')
    marker=int.from_bytes(end,'big')
    keys=sorted(patch);out=bytearray(b'IPS32' if ips32 else b'PATCH');i=0
    while i<len(keys):
        start=keys[i];require(0<=start<2**(width*8),'IPS address out of range')
        require(start!=marker,'Record address equals IPS end marker; use IPS32')
        payload=bytearray([patch[start]]);i+=1
        while i<len(keys) and keys[i]==start+len(payload) and len(payload)<65535:
            payload.append(patch[keys[i]]);i+=1
        out+=start.to_bytes(width,'big')+len(payload).to_bytes(2,'big')+payload
    return bytes(out+end)

def merge(paths):
    result={};owners={}
    for path in paths:
        for k,v in parse(Path(path).read_bytes()).items():
            require(k not in result or result[k]==v,f'IPS conflict at 0x{k:X}: {owners.get(k)} vs {Path(path).name}')
            result[k]=v;owners[k]=Path(path).name
    return result

def accents(main):
    data=Path(main).read_bytes()
    require(data[:4]==b'NSO0' and len(data)>0x20ba00,'Expected decompressed NSO with 0x100-byte header')
    require(data[0x40:0x60]==bytes.fromhex(BUILD_ID).ljust(32,b'\0'),'Unsupported Build ID: do not reuse ENG offsets on another executable')
    flags=struct.unpack_from('<I',data,12)[0]
    require(flags&7==0,'NSO segments are still compressed')
    patch={}
    for ch,row in CARRIERS.items():
        off=0x100+row['unicode_table_offset'];old=struct.unpack_from('<H',data,off)[0]
        require(old in (ord(row['carrier']),ord(ch)),f'Unexpected CP932 table at 0x{off:X}; wrong decompression layout/build')
        new=struct.pack('<H',ord(ch));patch.update({off+i:v for i,v in enumerate(new)})
    return patch
