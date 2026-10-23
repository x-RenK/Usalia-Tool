"""Bounded YKCMP types 4/7 and IMY decompression. No proprietary payloads."""
import struct
import zlib
from .common import require

MAX_OUTPUT = 1024 * 1024 * 1024

def yk_decode(data, max_output=MAX_OUTPUT):
    require(len(data) >= 20 and data[:8] == b'YKCMP_V1', 'Invalid YKCMP header')
    kind, packed, size = struct.unpack_from('<III', data, 8)
    require(20 <= packed <= len(data) and size <= max_output, 'Invalid YKCMP sizes')
    payload = data[20:packed]
    if kind == 7:
        d = zlib.decompressobj()
        out = d.decompress(payload, size + 1)
        require(len(out) == size and d.eof and not d.unconsumed_tail and not d.unused_data, 'Invalid YKCMP zlib size/stream')
        return out
    require(kind == 4, f'Unsupported YKCMP type {kind}')
    out = bytearray(); p = 0
    def byte():
        nonlocal p
        require(p < len(payload), 'Truncated YKCMP command')
        v = payload[p]; p += 1; return v
    while len(out) < size:
        c = byte()
        if c < 128:
            require(c > 0 and p + c <= len(payload) and len(out) + c <= size, 'Invalid YKCMP literal')
            out.extend(payload[p:p+c]); p += c; continue
        if c < 192:
            count, back = (c >> 4) - 7, (c & 15) + 1
        elif c < 224:
            count, back = c - 190, byte() + 1
        else:
            x, y = byte(), byte()
            count, back = ((c & 31) << 4) + (x >> 4) + 3, ((x & 15) << 8) + y + 1
        require(back <= len(out) and len(out) + count <= size, 'Invalid YKCMP backreference')
        for _ in range(count):
            out.append(out[-back])
    return bytes(out)

def yk_encode(data, kind=7):
    if kind == 7:
        payload = zlib.compress(data, 9)
    elif kind == 4:
        # Canonical literals. Larger than an optimized LZ stream but valid and lossless.
        payload = b''.join(bytes([len(data[i:i+127])]) + data[i:i+127] for i in range(0,len(data),127))
    else:
        raise ValueError('Encoding supports YKCMP 4 and 7 only')
    return struct.pack('<8sIII', b'YKCMP_V1', kind, len(payload)+20, len(data)) + payload

def imy_decode(data, max_output=MAX_OUTPUT):
    require(len(data) >= 34 and data[:4] == b'IMY\0', 'Invalid IMY header')
    stride = struct.unpack_from('<H', data, 8)[0]
    size = stride * struct.unpack_from('<H', data, 12)[0]
    flags_size = struct.unpack_from('<H', data, 32)[0]
    require(stride >= 2 and 0 < size <= max_output and 34 + flags_size <= len(data), 'Invalid IMY sizes')
    p = 34 + flags_size
    flags = data[34:p]; out = bytearray()
    for c in flags:
        if len(out) == size: break
        if c < 16:
            n = (c+1)*2
            require(p+n <= len(data) and len(out)+n <= size, 'Invalid IMY literal')
            out.extend(data[p:p+n]); p += n
        elif c < 192:
            src = p - (c-16)*2 - 2
            require(src >= 34+flags_size and src+2 <= p and len(out)+2 <= size, 'Invalid IMY data backreference')
            out.extend(data[src:src+2])
        else:
            n = ((c&15)+1)*2
            back = (2, stride, stride+2, stride-2)[(c&48)>>4]
            require(0 < back <= len(out) and len(out)+n <= size, 'Invalid IMY output backreference')
            for _ in range(n):out.append(out[-back])
    require(len(out) == size, 'Incomplete IMY output')
    return bytes(out)

def imy_package_decode(data, max_output=MAX_OUTPUT):
    require(len(data) >= 12, 'Truncated IMY package')
    n, block_size = struct.unpack_from('<II', data)
    require(0 < n <= 100000 and 8+n*4 <= len(data), 'Invalid IMY package table')
    offsets = struct.unpack_from(f'<{n}I', data, 8)
    require(offsets[0] >= 8+n*4 and list(offsets) == sorted(offsets) and offsets[-1] < len(data), 'Invalid IMY package offsets')
    out = bytearray()
    for a,b in zip(offsets, offsets[1:] + (len(data),)):
        chunk = imy_decode(data[a:b], max_output-len(out))
        require(len(chunk) <= block_size, 'IMY block exceeds declared block size')
        out.extend(chunk)
    return bytes(out)
