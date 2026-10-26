"""Generate bounded retail model lookups and local presentation controller."""
from pathlib import Path
import argparse,json

def build(model_report,out):
    report=json.loads(Path(model_report).read_text());rows=report['models'];out=Path(out)
    # Original MotS independently caps resource references at 128. Seventy
    # pairs silently truncate to 128 models and indexed access then crashes.
    # Sixty pairs leave eight resource slots free in each lookup COG.
    groups=[rows[i:i+60] for i in range(0,len(rows),60)]
    bins=[146,147,148,149,151,152]
    if len(groups)>len(bins):raise ValueError('Model map exceeds explicitly allocated bins')
    item_rows=['sbxd_view 145 1 1 0x000 cog=sbxd_view.cog']
    def emit(name,text):
        p=out/'cog'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(text.replace('\n','\r\n').encode('ascii'))
    for gi,group in enumerate(groups):
        lines=['# Generated source-model lookup, Coda with Andrei.','flags=0x240','symbols','int current local','int wanted local','int i local']
        for stem,key in [('base','source'),('dual','variant')]:
            lines += [f'model {stem}{i}={row[key]} local' for i,row in enumerate(group)]
        lines += ['message user0','end','code','user0:','current=GetParam(0);','wanted=GetParam(1);',f'for(i=0; i<{len(group)}; i=i+1)','{',' if((current == base0[i]) || (current == dual0[i]))',' {','  if(wanted) ReturnEx(dual0[i]);','  else ReturnEx(base0[i]);','  Return;',' }','}','ReturnEx(-1);','Return;','end','']
        emit(f'sbxd_map{gi}.cog','\n'.join(lines));item_rows.append(f'sbxd_map{gi} {bins[gi]} 1 1 0x000 cog=sbxd_map{gi}.cog')
    declarations='\n'.join(f'int {stem}{i}={initial} local' for stem,initial in [('want',0),('track',-1),('signature',-1)] for i in range(32))
    lookups='\n'.join(f' if(mapped == -1) mapped=SendMessageEx(GetInvCog(localplayer,{bins[gi]}),user0,current,visible,0,0);' for gi in range(len(groups)))
    text='''# Retail-native dual hilt variants and persistent upper-body idle.
# Coda with Andrei. Only local presentation changes; peers reconstruct from
# existing stance triggers. Every player needs the same overlay installed.
flags=0x240
symbols
thing localplayer local
thing actor local
int slot local
int triggerid local
int visible local
int current local
int mapped local
int newsig local
keyframe upper=rt_boupper.key local
DECLARATIONS
message startup
message pulse
message trigger
message shutdown
end
code
startup:
 localplayer=GetLocalPlayerThing();
 SetPulse(0.08);
 Return;
trigger:
 triggerid=GetSourceRef();
 if((triggerid < 1431) || (triggerid > 1438)) Return;
 actor=GetParam(0);
 slot=GetPlayerNum(actor);
 if((slot < 0) || (slot >= 32)) Return;
 newsig=GetThingSignature(actor);
 if(signature0[slot] != newsig)
 {
  signature0[slot]=newsig;
  track0[slot]=-1;
 }
 if(triggerid == 1438) want0[slot]=1;
 else want0[slot]=0;
 Return;
pulse:
 for(slot=0; slot<32; slot=slot+1)
 {
  actor=GetPlayerThing(slot);
  if(actor != -1)
  {
   newsig=GetThingSignature(actor);
   if(signature0[slot] != newsig)
   {
    signature0[slot]=newsig;
    want0[slot]=0;
    track0[slot]=-1;
   }
   call update;
  }
 }
 Return;
update:
 visible=0;
 if((want0[slot] == 1) && (GetThingHealth(actor)>0) && ((jkGetFlags(actor)&9) == 1) && ((jkGetFlags(actor)&16) != 0)) visible=1;
 current=GetThingModel(actor);
 mapped=-1;
LOOKUPS
 if((mapped == -1) && (visible == 1))
 {
  want0[slot]=0;
  if(actor == localplayer)
  {
   Print("SBX dual stance: this custom skin has no prepared hilt variant.");
   SendMessageEx(GetInvCog(localplayer,143),user3,0,0,0,0);
  }
  Return;
 }
 if((mapped != -1) && (mapped != current)) SetThingModel(actor,mapped);
 if(visible == 1)
 {
  if((track0[slot] == -1) && (upper != -1)) track0[slot]=PlayKey(actor,upper,1,0);
 }
 else
 {
  if(track0[slot] != -1) StopKey(actor,track0[slot],0.1);
  track0[slot]=-1;
 }
 Return;
shutdown:
 SetPulse(0);
 for(slot=0; slot<32; slot=slot+1)
 {
  actor=GetPlayerThing(slot);
  if(actor != -1)
  {
   want0[slot]=0;
   call update;
  }
 }
 Return;
end
'''.replace('DECLARATIONS',declarations).replace('LOOKUPS',lookups)
    emit('sbxd_view.cog',text)
    (out/'controller-items.txt').write_text('\n'.join(item_rows)+'\n')
    return {'models':len(rows),'mapper_cogs':len(groups),'bins':[145]+bins[:len(groups)]}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--models',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();print(json.dumps(build(a.models,a.out),indent=2))
