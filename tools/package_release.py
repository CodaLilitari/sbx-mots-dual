"""Create deterministic v1.2.0 end-user editions and a source Builder ZIP."""
from pathlib import Path
import argparse,hashlib,json,zipfile

VERSION='1.2.0'
PREFIX='SBX-MotS-Dual-Special-Edition'
FIXED_TIME=(2026,10,26,0,0,0)

def sha(raw):return hashlib.sha256(raw).hexdigest()

def write_zip(path,members):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,raw in sorted(members.items()):
            info=zipfile.ZipInfo(name,FIXED_TIME);info.create_system=3;info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,raw,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(path) as archive:
        if set(archive.namelist())!=set(members) or any(archive.read(n)!=raw for n,raw in members.items()):
            raise ValueError('ZIP member verification failed')
        if archive.testzip() is not None:raise ValueError('ZIP CRC check failed')
    return {'filename':path.name,'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size,'members':len(members)}

def build(source,build_root,output):
    source,build_root,output=Path(source).resolve(),Path(build_root).resolve(),Path(output).resolve()
    if output.exists():raise FileExistsError('Choose a new release output directory')
    if any((p/'.git').exists() for p in [output,*output.parents]):raise ValueError('Put generated ZIPs outside Git checkouts')
    output.mkdir(parents=True)
    docs={'docs/CREDITS.md':(source/'CREDITS.md').read_bytes(),
          'docs/licenses/OpenJKDF2-LICENSE.md':(source/'docs/licenses/OpenJKDF2-LICENSE.md').read_bytes()}
    for p in sorted((source/'docs/original').iterdir()):
        if p.is_file():docs['docs/original/'+p.name]=p.read_bytes()
    reports=[]
    for edition,suffix in [('accelerated',''),('software','-Software')]:
        goo=(build_root/'standalone'/edition/'SBX-MotS-Dual.goo').read_bytes()
        receipt=json.loads((build_root/'standalone'/edition/'PACKAGE-MANIFEST.json').read_text(encoding='utf-8'))
        if not receipt['passed'] or receipt['archive_sha256']!=sha(goo):raise ValueError('Archive does not match successful build manifest')
        readme=('SBX MOTS DUAL SABERS - SPECIAL EDITION v'+VERSION+'\nEdition: '+edition+'\n\n'+
                (source/'INSTALL.txt').read_text(encoding='utf-8')+'\n\nVALIDATION AND LIMITS\n\n'+
                (source/'STANDALONE-VALIDATION.md').read_text(encoding='utf-8')+
                '\n\nCREDITS AND ORIGINAL DOCUMENTS\n\nSee docs/CREDITS.md for full attribution. The unmodified original documents\nare retained under docs/original to honor the source packages. These small\ncompanion documents are not game dependencies; only the GOO goes into the mod\nfolder. Keep the documents with any redistribution. No retail executable or\ncomplete retail game archive is included.\n\nGOO SHA-256: '+sha(goo)+'\n')
        members={'SBX-MotS-Dual.goo':goo,'README.txt':readme.encode('utf-8')}|docs
        reports.append(write_zip(output/(PREFIX+suffix+'.zip'),members))
    source_members={}
    for p in sorted(source.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or '.git' in p.parts:continue
        rel=p.relative_to(source).as_posix()
        if p.suffix.lower() in {'.goo','.gob','.zip','.pyc'}:raise ValueError('Unexpected generated/archive input in source bundle: '+rel)
        source_members[rel]=p.read_bytes()
    manifest={n:{'bytes':len(raw),'sha256':sha(raw)} for n,raw in source_members.items()}
    source_members['PACKAGE-MANIFEST.json']=(json.dumps({'schema':'sbx-special-edition-source-package-v1','version':VERSION,'files':manifest},indent=2,sort_keys=True)+'\n').encode('utf-8')
    reports.append(write_zip(output/(PREFIX+'-Builder.zip'),source_members))
    result={'schema':'sbx-special-edition-release-packages-v1','version':VERSION,'packages':reports,
            'end_user_contents':'One final GOO and README, with full credits, original source documents and license retained as small companions.',
            'source_files':len(manifest),'zip_member_bytes_verified':True,'timestamps_fixed':True}
    (output/'release-manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (output/'SHA256SUMS.txt').write_text(''.join(x['sha256']+'  '+x['filename']+'\n' for x in reports),encoding='ascii')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['source','build-root','output']:p.add_argument('--'+n,required=True)
    a=p.parse_args();print(json.dumps(build(a.source,a.build_root,a.output),indent=2))
