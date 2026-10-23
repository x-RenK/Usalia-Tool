"""Validated PS_FS_V1 (NX) / PSPFS_V1 (PC) and uncompressed START archives."""
from dataclasses import dataclass, asdict
from pathlib import Path
import shutil
import struct
from .common import require, read_at, atomic_output, sha256, write_json

@dataclass(frozen=True)
class Entry:
    index: int
    name: str
    size: int
    offset: int
    directory_offset: int
    layout: str

    def json(self):
        return asdict(self)

def psfs_entries(path):
    path = Path(path)
    total = path.stat().st_size
    h = read_at(path, 0, 16)
    if h[:8] == b'PS_FS_V1':
        n = struct.unpack_from('<Q', h, 8)[0]
        stride, namelen, kind = 64, 48, 'nx64'
    elif h[:8] == b'PSPFS_V1':
        n = struct.unpack_from('<I', h, 8)[0]
        stride, namelen, kind = 52, 40, 'pc32'
    else:
        raise ValueError('Expected PS_FS_V1 or PSPFS_V1')
    require(0 < n <= 100000 and 16 + n * stride <= total, 'Invalid PSFS directory')
    rows = []
    table = read_at(path, 16, n * stride)
    for i in range(n):
        p = i * stride
        raw = table[p:p + namelen]
        require(b'\0' in raw, f'Unterminated entry name #{i}')
        name = raw.split(b'\0', 1)[0].decode('ascii', 'strict')
        require(name and '/' not in name and '\\' not in name and name not in ('.', '..'), 'Unsafe entry name')
        if kind == 'nx64':
            size, offset = struct.unpack_from('<QQ', table, p + 48)
        else:
            size, offset = struct.unpack_from('<II', table, p + 44)
        require(offset >= 16 + n * stride and offset + size <= total, f'Out-of-bounds entry #{i}: {name}')
        rows.append(Entry(i, name, size, offset, 16 + p, kind))
    return rows

def select(entries, selector):
    # Indices disambiguate duplicate dummy.dat entries.
    if str(selector).startswith('#'):
        i = int(str(selector)[1:])
        require(0 <= i < len(entries), 'Entry index out of range')
        return entries[i]
    hits = [e for e in entries if e.name.lower() == str(selector).lower()]
    require(len(hits) == 1, 'Entry not found or duplicate name; use #index')
    return hits[0]

def extract(path, output, selector=None):
    rows = psfs_entries(path)
    dest = Path(output)
    require(not dest.exists(), 'Choose a new extraction directory')
    dest.mkdir(parents=True)
    selected = [select(rows, selector)] if selector is not None else rows
    with Path(path).open('rb') as src:
        for e in selected:
            target = dest / f'{e.index:04d}_{e.name}'
            with target.open('xb') as dst:
                src.seek(e.offset)
                left = e.size
                while left:
                    b = src.read(min(left, 8 * 1024 * 1024))
                    require(b, 'Truncated extraction')
                    dst.write(b); left -= len(b)
    write_json(dest / 'archive.json', {'source_sha256': sha256(path), 'entries': [e.json() for e in selected]})
    return len(selected)

def replace(path, selector, replacement, output, alignment=512):
    """Append resource and update its directory record only; retain all other bytes."""
    e = select(psfs_entries(path), selector)
    require(alignment > 0 and alignment & (alignment - 1) == 0, 'Alignment must be a power of two')
    replacement = Path(replacement)
    require(replacement.is_file(), 'Replacement is not a regular file')
    size = replacement.stat().st_size
    with atomic_output(output, path) as tmp:
        shutil.copyfile(path, tmp)
        with tmp.open('r+b') as dst, replacement.open('rb') as src:
            dst.seek(0, 2)
            off = (dst.tell() + alignment - 1) // alignment * alignment
            require(e.layout == 'nx64' or off + size < 2**32, 'PC 32-bit archive limit')
            dst.write(b'\0' * (off - dst.tell()))
            shutil.copyfileobj(src, dst)
            dst.seek(e.directory_offset + (48 if e.layout == 'nx64' else 44))
            dst.write(struct.pack('<QQ' if e.layout == 'nx64' else '<II', size, off))
        check = select(psfs_entries(tmp), '#' + str(e.index))
        require(check.size == size and read_at(tmp, off, min(size, 32)) == read_at(replacement, 0, min(size, 32)), 'Replacement validation failed')
    return {'index': e.index, 'name': e.name, 'old_offset': e.offset, 'new_offset': off, 'new_size': size}

def start_entries(blob):
    require(len(blob) >= 8, 'START header is truncated')
    n = struct.unpack_from('<I', blob)[0]
    require(0 < n <= 10000 and 4 + n * 4 <= len(blob), 'START is compressed or has an unsupported layout')
    offsets = struct.unpack_from(f'<{n}I', blob, 4)
    require(offsets[0] >= 4 + n * 4 and list(offsets) == sorted(offsets) and offsets[-1] <= len(blob), 'Invalid START offsets')
    return [(i, a, b - a) for i, (a, b) in enumerate(zip(offsets, offsets[1:] + (len(blob),)))]

def start_from_archive(path):
    e = select(psfs_entries(path), 'start.dat')
    return e, read_at(path, e.offset, e.size)

def extract_start(path, output):
    data = Path(path).read_bytes()
    rows = start_entries(data)
    dest = Path(output)
    require(not dest.exists(), 'Choose a new extraction directory')
    dest.mkdir(parents=True)
    for i, off, size in rows:
        (dest / f'{i:03d}.bin').write_bytes(data[off:off+size])
    write_json(dest/'start.json', {'source_sha256': sha256(path), 'entries': [{'index': i, 'offset': o, 'size': s} for i,o,s in rows]})
    return len(rows)

def replace_start(path, index, replacement, output):
    """Fixed-size replacement only: preserve unknown relative pointers and offsets."""
    data = bytearray(Path(path).read_bytes())
    rows = start_entries(data)
    require(0 <= index < len(rows), 'START index out of range')
    _, off, size = rows[index]
    new = Path(replacement).read_bytes()
    require(len(new) == size, f'START replacement must be exactly {size} bytes')
    data[off:off+size] = new
    from .common import write_bytes
    write_bytes(output, data, path)

def anm_index(data):
    """Observed legacy ANM: object offsets + u16 resource IDs before aligned objects."""
    require(len(data)>=16,'Truncated ANM')
    n=struct.unpack_from('<I',data)[0]
    require(0<n<=10000 and 4+n*6<=len(data),'Unsupported ANM table')
    offsets=struct.unpack_from(f'<{n}I',data,4)
    ids=struct.unpack_from(f'<{n}H',data,4+n*4)
    require(offsets[0]>=4+n*6 and list(offsets)==sorted(offsets) and offsets[-1]<len(data),'Invalid ANM object offsets')
    result=[]
    for i,(a,b,ident) in enumerate(zip(offsets,offsets[1:]+(len(data),),ids)):
        require(a+12<=b,'Truncated ANM object header')
        result.append({'index':i,'resource_id':ident,'offset':a,'size':b-a,'header_u16':list(struct.unpack_from('<6H',data,a))})
    return result
