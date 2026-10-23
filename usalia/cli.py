import argparse
import json
from pathlib import Path
import sys
from . import __version__
from .common import write_bytes, write_json, require
from . import archives,compression,text,textures,ips,release


def parser():
    p=argparse.ArgumentParser(prog='usalia',description='Usalia Tool — Disgaea 1 Complete NX | PT-BR / English documentation: docs/')
    p.add_argument('--version',action='version',version=__version__)
    s=p.add_subparsers(dest='command',required=True)
    def command(name,help):return s.add_parser(name,help=help)
    a=command('archive-list','List/validate NX or PC archive | Listar/validar arquivo');a.add_argument('file');a.add_argument('--json',dest='json_out')
    a=command('archive-extract','Extract indexed resources | Extrair recursos');a.add_argument('file');a.add_argument('output');a.add_argument('--entry')
    a=command('archive-replace','Append resource without rebuilding unrelated data');a.add_argument('file');a.add_argument('entry');a.add_argument('replacement');a.add_argument('output')
    a=command('anm-list','Inspect legacy ANM object IDs, useful for HD matching');a.add_argument('file')
    a=command('start-extract','Extract plain START slots | Extrair slots');a.add_argument('file');a.add_argument('output')
    a=command('start-replace','Replace an equal-size START slot');a.add_argument('file');a.add_argument('index',type=int);a.add_argument('replacement');a.add_argument('output')
    a=command('decompress','Decode YKCMP 4/7, IMY or IMY package');a.add_argument('file');a.add_argument('output');a.add_argument('--format',choices=['ykcmp','imy','imy-package'],required=True)
    a=command('compress','Encode YKCMP 4 (literal) / 7 (zlib)');a.add_argument('file');a.add_argument('output');a.add_argument('--type',choices=[4,7],type=int,default=7)
    a=command('text-export','Export fixed-slot CSV + source metadata');a.add_argument('file');a.add_argument('output');a.add_argument('--kind',choices=['banks','story','cstrings'],default='banks');a.add_argument('--mapping',help='ptbr or JSON path; requires matching executable patch')
    for name in ['text-check','text-build']:
        a=command(name,'Validate/build edited translation CSV | Validar/aplicar CSV');a.add_argument('file');a.add_argument('csv');a.add_argument('--mapping');a.add_argument('--extra-csv',action='append',default=[]);a.add_argument('--ascii',action='store_true',help='Write ASCII directly instead of fullwidth; only for an appropriate renderer')
        if name=='text-build':a.add_argument('output')
    a=command('texture-export','Export observed NLTX/TX2 to PNG');a.add_argument('file');a.add_argument('output');a.add_argument('--format',choices=['nltx','tx2'],required=True)
    a=command('texture-import','Import PNG, preserve dimensions and unaffected data');a.add_argument('file');a.add_argument('png');a.add_argument('output');a.add_argument('--format',choices=['nltx','tx2'],required=True)
    a=command('hd-list','Inspect the HD archive extracted from START[96]');a.add_argument('file');a.add_argument('--json',dest='json_out')
    a=command('hd-export','Export an HD sheet; object/sheet are zero-based');a.add_argument('file');a.add_argument('object',type=int);a.add_argument('sheet',type=int);a.add_argument('output')
    a=command('hd-import','Replace direct ARGB or original-palette HD sheet');a.add_argument('file');a.add_argument('object',type=int);a.add_argument('sheet',type=int);a.add_argument('png');a.add_argument('output')
    a=command('fad-export','Export observed zz_anmdat.fad texture');a.add_argument('file');a.add_argument('index',type=int);a.add_argument('output')
    a=command('font-info','Inspect original font.bin + optional atlas');a.add_argument('file');a.add_argument('--atlas')
    a=command('ips-info','Inspect patch without applying to a game');a.add_argument('file')
    a=command('ips-merge','Merge patches, reject conflicting bytes');a.add_argument('files',nargs='+');a.add_argument('--out',required=True);a.add_argument('--ips32',action='store_true')
    a=command('nso-memory','Decompress NSO to analysis image; not an installable executable');a.add_argument('file');a.add_argument('output')
    a=command('accent-patch','Generate verified ENG native 48-character patch');a.add_argument('main');a.add_argument('output')
    a=command('patch-manifest','Create IPS from hash-bound researched edits');a.add_argument('source');a.add_argument('manifest');a.add_argument('output');a.add_argument('--ips32',action='store_true')
    a=command('release','Package the five required game files + readme only')
    for k in ['subdata','script','font-root','font-data','ips','readme','output']:a.add_argument('--'+k,required=True)
    a.add_argument('--title-id',default=release.TITLE_ID);a.add_argument('--build-id',default=ips.BUILD_ID)
    command('gui','Open bilingual CSV editor / Abrir editor bilíngue')
    return p

def run(a):
    c=a.command
    if c=='archive-list':
        r=[e.json() for e in archives.psfs_entries(a.file)]
        if a.json_out:write_json(a.json_out,r)
        return r
    if c=='archive-extract':return {'extracted':archives.extract(a.file,a.output,a.entry)}
    if c=='archive-replace':return archives.replace(a.file,a.entry,a.replacement,a.output)
    if c=='anm-list':return archives.anm_index(Path(a.file).read_bytes())
    if c=='start-extract':return {'extracted':archives.extract_start(a.file,a.output)}
    if c=='start-replace':archives.replace_start(a.file,a.index,a.replacement,a.output);return {'output':a.output}
    if c=='decompress':
        fn={'ykcmp':compression.yk_decode,'imy':compression.imy_decode,'imy-package':compression.imy_package_decode}[a.format];b=fn(Path(a.file).read_bytes());write_bytes(a.output,b,a.file);return {'bytes':len(b)}
    if c=='compress':b=compression.yk_encode(Path(a.file).read_bytes(),a.type);write_bytes(a.output,b,a.file);return {'bytes':len(b)}
    if c=='text-export':return {'records':text.export_text(a.file,a.output,a.kind,a.mapping)}
    if c=='text-check':return {'valid_translations':len(text.prepare_many(a.file,[a.csv]+a.extra_csv,a.mapping,not a.ascii))}
    if c=='text-build':return {'applied':text.build_text(a.file,a.csv,a.output,a.mapping,not a.ascii,a.extra_csv)}
    if c in ('texture-export','hd-export','fad-export'):
        require(not Path(a.output).exists(),'Image output already exists')
        if c=='texture-export':
            b=Path(a.file).read_bytes();im=textures.decode_nltx(b)[0] if a.format=='nltx' else textures.decode_tx2(b)
        elif c=='hd-export':im=textures.hd_sheet(a.file,a.object,a.sheet)
        else:im=textures.fad_sheet(a.file,a.index)
        im.save(a.output);return {'output':a.output,'size':im.size}
    if c=='texture-import':
        from PIL import Image
        b=Path(a.file).read_bytes()
        with Image.open(a.png) as im:
            if a.format=='nltx':out,n=textures.encode_nltx(b,im)
            else:out=textures.encode_tx2(b,im);n=None
        write_bytes(a.output,out,a.file);return {'output':a.output,'changed_bc1_blocks':n}
    if c=='hd-list':
        r=textures.hd_index(a.file)
        if a.json_out:write_json(a.json_out,r)
        return r
    if c=='hd-import':
        from PIL import Image
        with Image.open(a.png) as im:return textures.hd_replace_rgba(a.file,a.object,a.sheet,im,a.output)
    if c=='font-info':return textures.font_info(a.file,a.atlas)
    if c=='ips-info':
        p=ips.parse(Path(a.file).read_bytes());return {'bytes':len(p),'min_offset':min(p) if p else None,'max_offset':max(p) if p else None}
    if c=='ips-merge':write_bytes(a.out,ips.serialize(ips.merge(a.files),a.ips32));return {'output':a.out}
    if c=='nso-memory':
        from .nso import memory_image
        write_bytes(a.output,memory_image(Path(a.file).read_bytes()),a.file);return {'output':a.output,'installable_executable':False}
    if c=='accent-patch':write_bytes(a.output,ips.serialize(ips.accents(a.main)));return {'output':a.output,'characters':len(text.CARRIERS)}
    if c=='patch-manifest':
        from .patches import from_manifest
        write_bytes(a.output,ips.serialize(from_manifest(a.source,a.manifest),a.ips32));return {'output':a.output}
    if c=='release':return release.package(a.subdata,a.script,a.font_root,a.font_data,a.ips,a.readme,a.output,a.title_id,a.build_id)
    if c=='gui':
        from .gui import main
        main();return None
    raise ValueError('Unknown command')

def main(argv=None):
    p=parser();a=p.parse_args(argv)
    try:
        result=run(a)
        if result is not None:print(json.dumps(result,ensure_ascii=False,indent=2))
    except (ValueError,OSError,KeyError,UnicodeError,struct_error()) as ex:
        print(f'Usalia: {ex}',file=sys.stderr);sys.exit(2)

def struct_error():
    import struct
    return struct.error
