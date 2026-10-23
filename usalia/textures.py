"""Observed NX NLTX/BC1, paletted TX2 and HD/FAD image access."""
import io
import struct
from pathlib import Path
import numpy as np
from PIL import Image
from .common import require, write_bytes, write_json, read_at
from .compression import yk_decode, yk_encode


def block_indices(w,h,size):
    pw=(w+511)//512*512;ph=(h+255)//256*256
    require(0<w<=16384 and 0<h<=16384 and size==pw*ph//2, 'Unsupported NLTX dimensions/BC1 tiling')
    x,y=np.meshgrid(np.arange(pw//4)*8,np.arange(ph//4))
    a=y//64*(pw*2//64)*4096+x//64*4096+(y%64//8)*512+(x%64//32)*256+(y%8//2)*64+(x%32//16)*32+y%2*16+x%16
    idx=a[:,:,None]+np.arange(8)
    require(int(idx.max())<size,'Invalid tiled address')
    return idx,pw,ph

def decode_nltx(data):
    require(len(data)>=148 and data[:8]==b'NMPLTEX1','Expected NMPLTEX1 NLTX')
    require(data[128:136]==b'YKCMP_V1','Unsupported NLTX payload location')
    w,h=struct.unpack_from('<II',data,24)
    raw=yk_decode(data[128:]);idx,pw,ph=block_indices(w,h,len(raw));linear=np.frombuffer(raw,np.uint8)[idx].copy()
    im=Image.frombytes('RGBA',(pw,ph),linear.tobytes(),'bcn',1)
    return im.crop((0,0,w,h)),raw,idx,pw,ph,linear

def encode_nltx(original,image):
    old,raw,idx,pw,ph,linear=decode_nltx(original)
    image=image.convert('RGBA')
    require(image.size==old.size,'NLTX dimensions must stay identical')
    # The verified background path uses opaque BC1. Avoid silently flattening transparency.
    require(image.getchannel('A').getextrema()==(255,255),'This NLTX writer supports opaque backgrounds only')
    delta=np.any(np.asarray(image)!=np.asarray(old),axis=2)
    if not delta.any():return original,0
    padded=Image.frombytes('RGBA',(pw,ph),linear.tobytes(),'bcn',1).convert('RGB');padded.paste(image.convert('RGB'),(0,0))
    buf=io.BytesIO();padded.save(buf,format='DDS',pixel_format='DXT1')
    dds=buf.getvalue();require(dds[:4]==b'DDS ' and dds[84:88]==b'DXT1','Pillow did not produce BC1')
    fresh=np.frombuffer(dds[128:],np.uint8).reshape(ph//4,pw//4,8)
    changed=np.zeros((ph,pw),bool);changed[:old.height,:old.width]=delta
    blocks=changed.reshape(ph//4,4,pw//4,4).any(axis=(1,3))
    linear[blocks]=fresh[blocks]
    tiled=np.frombuffer(raw,np.uint8).copy();tiled[idx]=linear
    yk=yk_encode(tiled.tobytes(),7);head=bytearray(original[:128]);struct.pack_into('<I',head,48,len(yk))
    out=bytes(head)+yk
    check=decode_nltx(out)
    require(np.array_equal(check[5][~blocks],np.frombuffer(raw,np.uint8)[idx][~blocks]),'Untouched BC1 blocks changed')
    return out,int(blocks.sum())

def decode_tx2(data):
    require(len(data)>=16,'Truncated TX2')
    w,h,fmt,_,colors,palettes,_,_=struct.unpack_from('<8H',data)
    require(0<w<=8192 and 0<h<=8192,'Invalid TX2 dimensions')
    if fmt==3 and palettes==0:
        require(len(data)>=16+w*h*4,'Truncated RGBA TX2')
        return Image.frombytes('RGBA',(w,h),data[16:16+w*h*4])
    require((fmt,colors,palettes) in ((16,16,1),(256,256,1)),'Only single-palette linear TX2 4/8 bpp and RGBA type 3 are supported')
    base=16+colors*4;need=w*h if fmt==256 else (w*h+1)//2
    require(len(data)>=base+need,'Truncated paletted TX2')
    pal=np.frombuffer(data[16:base],np.uint8).reshape(colors,4)
    packed=np.frombuffer(data[base:base+need],np.uint8)
    pix=packed if fmt==256 else np.stack((packed&15,packed>>4),axis=1).reshape(-1)[:w*h]
    return Image.fromarray(pal[pix.reshape(h,w)])

def encode_tx2(original,image):
    old=decode_tx2(original);im=image.convert('RGBA');require(im.size==old.size,'TX2 dimensions must stay identical')
    if np.array_equal(np.asarray(im),np.asarray(old)):return original
    w,h,fmt,_,colors,palettes,_,_=struct.unpack_from('<8H',original)
    result=bytearray(original)
    if fmt==3:
        result[16:16+w*h*4]=im.tobytes();return bytes(result)
    # Exact palette lookup preserves every palette byte; no implicit quantization.
    pal=np.frombuffer(original[16:16+colors*4],np.uint8).reshape(colors,4)
    lookup={tuple(c):i for i,c in reversed(list(enumerate(pal)))}
    pixels=np.asarray(im).reshape(-1,4)
    try:indices=np.array([lookup[tuple(c)] for c in pixels],np.uint8)
    except KeyError as ex:raise ValueError('Edited TX2 uses colors outside the original palette; prepare indexed artwork with the same palette') from ex
    if fmt==16:
        if len(indices)%2:indices=np.append(indices,0).astype(np.uint8)
        indices=indices[::2] | (indices[1::2]<<4)
    base=16+colors*4;result[base:base+len(indices)]=indices.tobytes()
    return bytes(result)

def hd_index(path):
    """Parse START[96] HD object archive dynamically, without absolute SUBDATA offsets."""
    total=Path(path).stat().st_size;head=read_at(path,0,32)
    metadata_size,_,sheets,palettes,objects,*_=struct.unpack('<8I',head)
    require(0<objects<=10000 and sheets<=100000 and palettes<=100000,'Unsupported HD header')
    data_start=metadata_size+16
    require(32<=data_start<=total,'Invalid HD metadata length')
    meta=read_at(path,0,data_start);p=32;sb=pb=0;rows=[]
    for i in range(objects):
        require(p+28<=len(meta),'Truncated HD object')
        size=struct.unpack_from('<I',meta,p)[0];h=struct.unpack_from('<12H',meta,p+4)
        require(size>=28 and p+size<=len(meta),'Invalid HD object length')
        rows.append({'index':i,'id':h[0],'offset':p,'size':size,'header':list(h),'sheet_base':sb,'palette_base':pb})
        sb+=h[5];pb+=h[4];p+=size
    require(sb==sheets and pb==palettes and p+16*(sheets+palettes)==data_start,'Unsupported HD table layout')
    return {'data_start':data_start,'table_offset':p,'sheet_count':sheets,'palette_count':palettes,'objects':rows}

def hd_sheet(path,obj,sheet):
    index=hd_index(path);require(0<=obj<len(index['objects']),'HD object index out of range');o=index['objects'][obj];h=o['header'];require(0<=sheet<h[5],'HD sheet index out of range')
    t=index['table_offset'];d=index['data_start']
    def descriptor(i):return struct.unpack('<HHHHII',read_at(path,t+i*16,16))
    fmt,_,w,hh,_,off=descriptor(o['sheet_base']+sheet)
    if fmt==256:
        a=np.frombuffer(read_at(path,d+off,w*hh*4),np.uint8).reshape(hh,w,4)[:,:,[1,2,3,0]]
    else:
        require(h[4]>0,'Indexed HD image without palette')
        _,_,pw,ph,_,poff=descriptor(index['sheet_count']+o['palette_base']+min(sheet,h[4]-1))
        pal=np.frombuffer(read_at(path,d+poff,pw*ph*4),np.uint8).reshape(-1,4)[:,[1,2,3,0]]
        pix=np.frombuffer(read_at(path,d+off,w*hh),np.uint8).reshape(hh,w);require(int(pix.max())<len(pal),'HD palette index out of range');a=pal[pix]
    return Image.fromarray(a)

def hd_replace_rgba(path,obj,sheet,image,output):
    index=hd_index(path);old=hd_sheet(path,obj,sheet);im=image.convert('RGBA');require(im.size==old.size,'HD dimensions must stay identical')
    o=index['objects'][obj];t=index['table_offset']+(o['sheet_base']+sheet)*16
    fmt,_,w,h,_,off=struct.unpack('<HHHHII',read_at(path,t,16))
    if np.array_equal(np.asarray(im),np.asarray(old)):
        encoded=read_at(path,index['data_start']+off,w*h*(4 if fmt==256 else 1))
    elif fmt==256:
        encoded=np.asarray(im)[:,:,[3,0,1,2]].tobytes()
    else:
        require(fmt==265 and o['header'][4]>0,'Unsupported indexed HD format')
        pi=index['sheet_count']+o['palette_base']+min(sheet,o['header'][4]-1)
        _,_,pw,ph,_,poff=struct.unpack('<HHHHII',read_at(path,index['table_offset']+pi*16,16))
        pal=np.frombuffer(read_at(path,index['data_start']+poff,pw*ph*4),np.uint8).reshape(-1,4)[:,[1,2,3,0]]
        require(len(pal)<=256,'HD palette exceeds byte indices')
        lookup={tuple(c):i for i,c in reversed(list(enumerate(pal)))}
        unique,inverse=np.unique(np.asarray(im).reshape(-1,4),axis=0,return_inverse=True)
        try:values=np.array([lookup[tuple(c)] for c in unique],np.uint8)
        except KeyError as ex:raise ValueError('Edited HD image uses colors outside its original palette') from ex
        encoded=values[inverse].tobytes()
    from .common import atomic_output
    import shutil
    with atomic_output(output,path) as tmp:
        shutil.copyfile(path,tmp)
        with tmp.open('r+b') as f:
            f.seek(index['data_start']+off);f.write(encoded)
    return {'object':obj,'sheet':sheet,'width':w,'height':h}

def fad_sheet(path,index):
    # Historical zz_anmdat.fad: texture descriptors at 0x430, 32 bytes each.
    head=read_at(path,0,0x430);count=struct.unpack_from('<I',head,12)[0]
    require(0<=index<count<=10000,'Unsupported FAD texture index/header')
    desc=struct.unpack('<8I',read_at(path,0x430+index*32,32));_,_,size,_,off,w,h,_=desc
    b=read_at(path,off,size);require(len(b)>=68,'Truncated FAD texture');raw=yk_decode(b[48:])
    if len(raw)==w*h+1024:
        pal=np.frombuffer(raw[:1024],np.uint8).reshape(256,4);pixels=np.frombuffer(raw[1024:],np.uint8).reshape(h,w);return Image.fromarray(pal[pixels])
    require(len(raw)==w*h*4,'Unsupported FAD image layout');return Image.frombytes('RGBA',(w,h),raw)

def font_info(path,atlas=None):
    size=Path(path).stat().st_size;h=read_at(path,0,64);w,hh,cw,ch=struct.unpack_from('<4H',h);count=struct.unpack_from('<I',h,24)[0]
    require(0<w<=8192 and 0<hh<=8192 and 64+count*24<=size-w*hh,'Unsupported font.bin layout')
    result={'width':w,'height':hh,'cell_width':cw,'cell_height':ch,'record_count':count,'record_offset':64,'record_size':24,'atlas_offset':size-w*hh,'size':size}
    if atlas:
        im=Image.frombytes('L',(w,hh),read_at(path,result['atlas_offset'],w*hh));require(not Path(atlas).exists(),'Atlas output exists');im.save(atlas)
    return result
