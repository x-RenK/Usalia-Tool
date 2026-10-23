"""Deterministic, allowlisted localization release packaging."""
from pathlib import Path
import shutil
import zipfile
from .archives import psfs_entries
from .common import require, sha256, atomic_output
from .ips import parse, BUILD_ID

TITLE_ID='01004B100AF18000'

def package(subdata,script,font_root,font_data,ips,readme,output,title_id=TITLE_ID,build_id=BUILD_ID):
    require(len(title_id)==16 and all(c in '0123456789abcdefABCDEF' for c in title_id),'Title ID must be 16 hex digits')
    require(len(build_id)==32 and all(c in '0123456789abcdefABCDEF' for c in build_id),'IPS filename Build ID must be 32 hex digits')
    psfs_entries(subdata);parse(Path(ips).read_bytes())
    from .textures import font_info
    font_info(font_root);font_info(font_data)
    require(Path(script).stat().st_size>0,'Empty external script')
    require(Path(ips).stem.upper()==build_id.upper(),'IPS filename does not match the selected Build ID')
    inputs=[Path(p) for p in (subdata,script,font_root,font_data,ips,readme)]
    require(all(p.is_file() for p in inputs),'Missing required release input')
    rf=f'atmosphere/contents/{title_id.upper()}/romfs/'
    names=[rf+'data/SUBDATA.DAT',rf+'data/script.dat',rf+'font.bin',rf+'data/font.bin',f'atmosphere/exefs_patches/Usalia_Localization/{build_id.upper()}.ips','LEIA-ME.txt']
    with atomic_output(output) as tmp:
        with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for name,p in zip(names,inputs):
                info=zipfile.ZipInfo(name,(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
                with p.open('rb') as src,z.open(info,'w',force_zip64=True) as dst:shutil.copyfileobj(src,dst,8*1024*1024)
        with zipfile.ZipFile(tmp) as z:
            require(z.namelist()==names and z.testzip() is None,'Release validation failed')
    return {'files':names,'sha256':sha256(output),'note':'Archive integrity checked; gameplay still requires NX testing'}
