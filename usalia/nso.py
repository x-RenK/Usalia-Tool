"""NSO -> analysis memory image (0x100 header + virtual segment addresses).
The output is NOT a rebuilt executable. IPS offsets use this analysis convention.
"""
import struct
from .common import require

def memory_image(data):
    require(len(data)>=256 and data[:4]==b'NSO0','Expected NSO0')
    flags=struct.unpack_from('<I',data,12)[0];segments=[];end=256
    for i in range(3):
        off,addr,size=struct.unpack_from('<III',data,16+i*16);stored=struct.unpack_from('<I',data,96+i*4)[0] if flags&(1<<i) else size
        require(size<=256*1024*1024 and off+stored<=len(data),'Invalid NSO segment bounds')
        segments.append((i,off,addr,size,stored));end=max(end,256+addr+size)
    require(end<=512*1024*1024,'NSO memory image too large')
    out=bytearray(end);out[:256]=data[:256];struct.pack_into('<I',out,12,flags&~7)
    for i,off,addr,size,stored in segments:
        chunk=data[off:off+stored]
        if flags&(1<<i):
            try:import lz4.block
            except ImportError as ex:raise ValueError('Install optional NSO support: python -m pip install "usalia-tool[nso]"') from ex
            chunk=lz4.block.decompress(chunk,uncompressed_size=size)
        require(len(chunk)==size,'NSO decompression size mismatch');out[256+addr:256+addr+size]=chunk
    return bytes(out)
