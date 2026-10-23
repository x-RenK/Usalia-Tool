"""Exact-source binary edits, useful for executable strings and researched layout fields."""
import json
from pathlib import Path
from .common import require,sha256,read_at
from .text import encode,load_mapping

def from_manifest(source,manifest):
    spec=json.loads(Path(manifest).read_text('utf-8'))
    require(spec.get('source_sha256')==sha256(source),'Binary edit manifest source hash mismatch')
    result={}
    for row in spec['edits']:
        off=int(row['offset'],0) if isinstance(row['offset'],str) else row['offset']
        old=bytes.fromhex(row['expected_hex']);require(old and read_at(source,off,len(old))==old,'Expected bytes mismatch')
        if 'replacement_hex' in row:
            new=bytes.fromhex(row['replacement_hex'])
        else:
            mode=row.get('encoding','cp932-fullwidth');require(mode in ('ascii','cp932','cp932-fullwidth'),'Unknown encoding')
            new=row['text'].encode('ascii') if mode=='ascii' else encode(row['text'],load_mapping(row.get('mapping')),mode=='cp932-fullwidth')
            if row.get('nul_terminated',True):new+=b'\0'
            require(len(new)<=len(old),'Replacement exceeds the researched slot')
            new=new.ljust(len(old),b'\0')
        require(len(new)==len(old),'Binary edits must preserve size')
        for i,v in enumerate(new):
            require(off+i not in result,'Overlapping manifest edits');result[off+i]=v
    return result
