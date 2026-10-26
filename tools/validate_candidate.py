"""Layer-aware resource and original-MotS verb preflight; not a runtime test."""
from pathlib import Path
import argparse, collections, importlib.util, json, re
from archive_io import read_gob, digest

PREFIXES={'.cog':['cog/'],'.3do':['3do/'],'.key':['3do/key/'],'.mat':['3do/mat/','mat/'],'.pup':['misc/pup/'],'.wav':['sound/','voice/'],'.snd':['misc/snd/'],'.ai':['misc/ai/'],'.spr':['misc/spr/'],'.par':['misc/par/']}

def symbol_budget(raw):
    text=re.sub(r'(?m)(?:#|//).*$', '',raw.decode('latin1'))
    section=re.search(r'(?ims)^\s*symbols\s*$(.*?)^\s*end\s*$',text)
    count=0;skipped=[]
    resource_types={'thing','sector','surface','sound','template','model','keyframe','material','ai','aiclass','cog'}
    for kind,name,tail in re.findall(r'(?m)^\s*(\w+)\s+(\w+)([^\r\n]*)',section.group(1) if section else ''):
        kind=kind.lower()
        if kind in resource_types or kind in {'int','flex','float','vector'}:
            # The original parser checks capacity before distinguishing a
            # scalar local from a serialized reference. This is independent
            # of its 256-symbol bytecode table.
            if count>=128:skipped.append(name)
            if kind in resource_types or not re.search(r'\blocal\b',tail):count+=1
    return {'resource_references':count,'native_limit':128,'declarations_rejected_by_capacity':skipped}

def refs(name,raw):
    text=raw.decode('latin1').rstrip('\x1a')
    text=re.sub(r'(?m)(?:#|//).*$', '',text)
    if name.endswith('.cog'):
        section=re.search(r'(?ims)^\s*symbols\s*$(.*?)^\s*end\s*$',text)
        return re.findall(r'(?im)^\s*(?:keyframe|sound|model|material|aiclass)\s+\w+\s*=\s*([^\s]+)',section.group(1)) if section else []
    if name.endswith('.3do'):
        section=re.search(r'(?ims)^MATERIALS\s+\d+\s*$(.*?)(?=^SECTION:)',text)
        return re.findall(r'(?m)^\s*\d+:\s+(\S+\.mat)',section.group(1)) if section else []
    if name.endswith(('.pup','.snd')) or name=='misc/models.dat':
        return re.findall(r'(?i)\b([a-z0-9_+.-]+\.(?:key|wav|3do|snd))\b',text)
    if name=='misc/items.dat':return re.findall(r'(?i)\bcog\s*=\s*(\S+)',text)
    if name.endswith(('.jkl','.spr','.par')):
        return re.findall(r'(?i)(?<![\w/\\])([a-z0-9_+.$-]+\.(?:cog|3do|key|mat|pup|wav|snd|ai|spr|par))\b',text)
    return []

def reachable_missing(layer,roots):
    todo=list(roots);seen=set();missing=set()
    while todo:
        name=todo.pop()
        if name in seen:continue
        seen.add(name)
        for ref in refs(name,layer[name]):
            ref=ref.lower()
            if ref in ('none','-1','0'):continue
            prefixes=PREFIXES.get(Path(ref).suffix,[])
            found=next((pre+ref for pre in prefixes if pre+ref in layer),None)
            if found:todo.append(found)
            elif prefixes:missing.add((name,ref))
    return missing,len(seen)

def hierarchy_errors(overlay):
    # Validate the actual serialized native child/sibling traversal, separate
    # from modern authoring restrictions on historical mesh normals.
    from build_dual_models import parsed
    result=[]
    for name,raw in overlay.items():
        if not name.endswith('.3do'):continue
        try:
            nodes=parsed(raw)['nodes'];visited=set()
            def visit(i,parent):
                if not 0<=i<len(nodes) or i in visited:raise ValueError('Repeated or invalid node '+str(i))
                node=nodes[i];visited.add(i)
                if node['parent']!=parent:raise ValueError('Parent mismatch at '+str(i))
                child=node['child'];count=0
                while child!=-1:
                    visit(child,i);count+=1;child=nodes[child]['sibling']
                if count!=node['numChildren']:raise ValueError('Child count mismatch at '+str(i))
            visit(0,-1)
            # Source SBX skins intentionally reserve an unparented, empty
            # node18. It has no renderable mesh or child chain to lose.
            detached=[i for i in range(len(nodes)) if i not in visited]
            if any(not(nodes[i]['parent']==-1 and nodes[i]['mesh']==-1 and nodes[i]['child']==-1 and nodes[i]['numChildren']==0) for i in detached):
                raise ValueError('Unreachable renderable nodes')
        except (ValueError,KeyError,IndexError) as e:result.append({'path':name,'error':str(e)})
    return result

def validate(candidate,base,mots_res,mots_snd,inspector=None):
    candidate=Path(candidate);overlay=read_gob(candidate/'SBX-MotS-Dual-Overlay.goo')
    base=read_gob(base);stock=read_gob(mots_res)|read_gob(mots_snd)
    lower=stock|base;merged=lower|overlay
    def missing(layer,names):
        result=set()
        for name in names:
            for ref in refs(name,layer[name]):
                ref=ref.lower()
                if ref in ('none','-1','0'):continue
                prefixes=PREFIXES.get(Path(ref).suffix,[])
                if prefixes and not any(pre+ref in layer for pre in prefixes):result.add((name,ref))
        return result
    prior,prior_count=reachable_missing(lower,base)
    after,reachable_count=reachable_missing(merged,overlay)
    inherited=after&prior;introduced=after-prior
    items=merged['misc/items.dat'].decode('latin1')
    rows=re.findall(r'(?m)^\s*([^#\s]+)\s+(\d+)\s+(-?\d+)\s+(-?\d+)\s+(0x[0-9a-fA-F]+)([^\r\n]*)',items)
    bins=[int(row[1]) for row in rows]
    duplicate_bins=[b for b,count in collections.Counter(bins).items() if count>1]
    base_rows=re.findall(r'(?m)^\s*([^#\s]+)\s+(\d+)\s+(-?\d+)\s+(-?\d+)\s+(0x[0-9a-fA-F]+)([^\r\n]*)',base['misc/items.dat'].decode('latin1'))
    retained={row[1]:row for row in rows};lost_bins=[row for row in base_rows if retained.get(row[1])!=row]
    identical=[name for name,data in overlay.items() if base.get(name)==data]
    loose_mismatch=[name for name,data in overlay.items() if (candidate/'overlay'/name).read_bytes()!=data]
    budgets={name:symbol_budget(raw) for name,raw in overlay.items() if name.endswith('.cog')}
    capacity_failures=[name for name,budget in budgets.items() if budget['declarations_rejected_by_capacity']]
    hierarchy_failures=hierarchy_errors(overlay)
    findings=[];lexical=[]
    if inspector:
        spec=importlib.util.spec_from_file_location('retail_inspector',inspector);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        for name in overlay:
            if name.endswith('.cog'):
                report=module.inspect(candidate/'overlay'/name,'mots')
                lexical.append({'path':name,'sha256':report['sha256'],'availability_findings':report['availability_findings'],'calls_absent':report['calls_absent_from_target_registry'],'messages_absent':report['messages_absent_from_target_registry'],'warnings':report['warnings']})
                if report['availability_findings']:findings.append(name)
    result={'schema':'sbx-layered-static-validation-v1','method':'Archive roundtrip, layered resource closure, MotS inventory preservation, optional lexical registry check; not a compiler or gameplay proof.',
        'archive_sha256':digest((candidate/'SBX-MotS-Dual-Overlay.goo').read_bytes()),'members':len(overlay),'bytes':sum(map(len,overlay.values())),
        'introduced_missing_resources':sorted(introduced),'inherited_missing_resources':sorted(inherited),'duplicate_bins':duplicate_bins,'changed_or_lost_base_bins':lost_bins,
        'byte_identical_base_members':identical,'loose_archive_mismatches':loose_mismatch,'lexical_reports':lexical,'native_resource_budgets':budgets,'capacity_failures':capacity_failures,
        'reachable_resources_checked':reachable_count,'model_hierarchy_failures':hierarchy_failures,
        'passed':not(introduced or duplicate_bins or lost_bins or identical or loose_mismatch or findings or capacity_failures or hierarchy_failures)}
    (candidate/'static-validation.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--candidate',required=True);ap.add_argument('--base',required=True);ap.add_argument('--mots-res',required=True);ap.add_argument('--mots-snd',required=True);ap.add_argument('--inspector');a=ap.parse_args()
    result=validate(a.candidate,a.base,a.mots_res,a.mots_snd,a.inspector)
    print(json.dumps({k:v for k,v in result.items() if k not in {'lexical_reports','native_resource_budgets'}},indent=2));raise SystemExit(0 if result['passed'] else 1)
