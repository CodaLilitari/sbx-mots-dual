"""Source-checked MotS integration. All replacements fail closed on drift."""
from pathlib import Path
import argparse,json,re
from archive_io import digest

def replace(text,old,new,count=1):
    actual=text.count(old)
    if actual!=count:raise ValueError(f'Expected {count} occurrences, got {actual}: {old[:100]!r}')
    return text.replace(old,new)

def unwrap_fan_gates(text):
    # SBX3.0 incorrectly gates timer cleanup as well as visible fan changes.
    pattern=r'if\(allowfans\)\s*// If trails are enabled\s*\{'
    while match:=re.search(pattern,text):
        start=match.start();body=match.end();depth=1;i=body
        while depth:
            if text[i]=='{':depth+=1
            elif text[i]=='}':depth-=1
            i+=1
        text=text[:start]+text[body:i-1]+text[i:]
    text=re.sub(r'(?m)^(\s*)jkSetWeaponMesh\(player, (Fan[12]\[color\])\);',r'\1if(allowfans) jkSetWeaponMesh(player, \2);',text)
    return text

def cog_budget(text):
    """Count native declaration slots separately from resource references.

    Original MotS ParseSymbolRef (0x5427db) rejects references after128 even
    though its local symbol table has256 slots. Local numeric variables do not
    consume reference records; local models/sounds/keys/cog handles still do.
    """
    section=re.search(r'(?ims)^\s*symbols\s*$(.*?)^\s*end\s*$',text)
    if section is None:raise ValueError('Missing COG symbols section')
    resources={'thing','surface','sector','sound','template','model','keyframe','cog','material','ai'}
    numeric={'int','flex','float','vector'}
    count=0;refs=0;overflow=[]
    for line in section[1].splitlines():
        words=line.split('#')[0].split('//')[0].split()
        if not words:continue
        count+=1;kind=words[0].lower()
        if kind in resources or (kind in numeric and 'local' not in [w.lower() for w in words[2:]]):
            refs+=1
            if refs>128:overflow.append(words[1].split('=')[0])
    if overflow:raise ValueError('Native128 resource-reference cap exceeded: '+', '.join(overflow))
    if count>256:raise ValueError('Native256 local-symbol declaration cap exceeded')
    return {'declared_symbols':count,'resource_references':refs,'resource_reference_limit':128,
            'method':'Declaration count only; not full compiled symbol count or VM execution.'}

def build(root,out):
    root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    receipts=[]
    def read(tag,name):return (root/'sources'/tag/name).read_text(encoding='latin1')
    def emit(name,text,why):
        path=out/name;path.parent.mkdir(parents=True,exist_ok=True);data=text.replace('\r\n','\n').replace('\n','\r\n').encode('latin1');path.write_bytes(data)
        row={'path':name,'sha256':digest(data),'reason':why}
        if name.endswith('.cog'):row['native_symbol_budget']=cog_budget(text)
        receipts.append(row)
    source=read('dual','cog/weap_sithsaber.cog')
    block=source[source.index('      bocStance = SendMessageEx(stanceCog, user1',source.index('fire:')):source.index('      if (mode == 0)',source.index('fire:'))]
    # Retail has four tracks. Keep one persistent upper loop, one locomotion
    # track, one attack and one block. Never keep an attack slot number after
    # this event: retail has no verb for proving that a reused slot is ours.
    block=replace(block,'         if(allowdamage == 1) jkEnableSaber(player, 50, 0.123, 1.0);\n         else jkEnableSaber(player, 0, 0.123, 1.0);\n','')
    block=replace(block,'         dualFlags = 0x38;','         dualFlags = 0x1a; // NOLOOP + UNIQUE + immediate start')
    block=replace(block,'            dualFlags = 0x20;','            dualFlags = 0x0a; // NOLOOP + UNIQUE; fade in')
    block=block.replace('// instead of jumping to its first frame, and another one\n            // fades in over this one\'s end instead of restarting it','// instead of jumping to its first frame. Retail waits for its\n            // full duration so the upper idle and blocking retain a track.')
    block=re.sub(r'jkPlayPOVKey\( player, (\w+), 2, 0x38 \);',r'dualPovKey = \1;',block)
    block=replace(block,'            PlayKey(player, dualKey, 2, dualFlags);','            dualResult = PlayKey(player, dualKey, 2, dualFlags);')
    block=replace(block,'            PlayMode(player, 8);','            dualResult = PlayMode(player, 8);')
    block=replace(block,'            PlayMode(player, 18);','            dualResult = PlayMode(player, 18);')
    block=replace(block,'         fanwait = (keylen / 10);','''         // Allocation can fail during a transient locomotion/action change.
         // A failed key must not reset the native hit list or start an attack.
         if(dualResult == -1)
         {
            // The reverse grip's second fire armed its hop when asked for
            // its key (stance user2 9); no key, no hop (user2 13).
            if(mode != 0) SendMessageEx(stanceCog, user2, 13, 0, 0, 0);
            SetFireWait(player, 0.08);
            Return;
         }
         jkPlayPOVKey(player, dualPovKey, 2, 0x38);
         if(allowdamage == 1) jkEnableSaber(player, 50, 0.123, 1.0);
         else jkEnableSaber(player, 0, 0.123, 1.0);
         fanwait = (keylen / 10);''')
    block=replace(block,'         SetFireWait(player, keylen * 0.75);','''         // Full-duration cooldown is the retail four-track adaptation.
         // The browser add-on overlaps attacks at 75 percent of this length.
         SetFireWait(player, keylen);''')
    helpers=source[source.index('user3:\n'):source.rindex('#======================================================================')]
    helpers=helpers.replace("# stance (the engine draws the hilt again in the left hand), which\n# saberstance.cog keeps.","# stance. Retail draws two native polylines with visible materials. The\n# controller selects a generated player model with the left hilt; user2\n# supplies the hilt-only right mesh. Browser-style mesh fans are not used\n# in dual stance; the original staff fans remain available.")
    helpers=replace(helpers,'''   if (bocStance == 1) jkSetWeaponMesh(player, SendMessageEx(stanceCog, user2, 0, color, 0, 0));
   else jkSetWeaponMesh(player, saber[color]);''','''   if (bocStance == 1)
   {
      // Changing materials preserves native length and the current hit list.
      // Do it only on entry or a color change, not on every trail timer.
      if((dualVisible == 0) || (dualColor != color))
      {
         dualVisible = SendMessageEx(stanceCog, user2, 12, color, 0, 0);
         dualColor = color;
      }
      jkSetWeaponMesh(player, SendMessageEx(stanceCog, user2, 0, color, 0, 0));
   }
   else
   {
      call cleardualvisual;
      jkSetWeaponMesh(player, saber[color]);
   }''')
    helpers+='''
cleardualvisual:

   // SBX supplies transparent native materials because its usual blades
   // are weapon meshes. Restore those materials before any non-dual use.
   if(dualVisible == 1)
      jkSetSaberInfo(player, mat0[(2*color)+1], mat0[(2*color)], 0.007, 0.004, bladelen, tpl_wall, tpl_blood, tpl_saber);
   dualVisible = 0;
   dualColor = -1;

   Return;

'''
    # Keep MotS native bins, color order, Projection notifications, AI attention,
    # alignment priorities, extra weapons, Force ranks, and campaign lifecycle.
    for name in ['weap_saber_m.cog','weap_sithsaber_m.cog','weap_extsaber_m.cog']:
        text=unwrap_fan_gates(read('mots30','cog/'+name))
        text='# Retail MotS overlay by Coda with Andrei; source SBX by ShadowX.\n'+text
        if name!='weap_sithsaber_m.cog':
            # Both original MotS single-blade scripts have131 reference records.
            # Five unused legacy impact sounds are safe to remove; this retains
            # the final class/Projection/stance COG references below native128.
            code=text[text.index('\ncode'):]
            for symbol in ('hitSound01','hitSound02','hitSound03','hitSound12','hitSound14'):
                if re.search(r'\b'+symbol+r'\b',code,re.I):raise ValueError('Impact sound unexpectedly used: '+symbol)
                text,n=re.subn(r'(?im)^sound\s+'+symbol+r'=.*\n','',text)
                if n!=1:raise ValueError('Impact sound declaration drift: '+symbol)
        # Carry the actual JK31 startup repair into the MotS-native script.
        i=text.index('startup:');j=text.index('timer:',i)
        part=replace(text[i:j],'   nextAttack = 0;','   nextAttack = 0;\n   humChannel = -1;')
        text=text[:i]+part+text[j:]
        # JK31 makes the stance item available whenever a saber is ignited.
        # MotS uses143; refreshing the handle also avoids a stale saved value.
        i=text.index('user7:');j=text.index('user1:',i)
        part=replace(text[i:j],'   if (active == 0)\n   {','''   if (active == 0)
   {
      SetInv(player, 143, 1);
      SetInvAvailable(player, 143, 1);
      stanceCog = GetInvCog(player, 143);''')
        text=text[:i]+part+text[j:]
        # JK31 orders long<staff<single. MotS also has concussion at800, so its
        # long saber uses850 to retain all native guns below the saber group.
        if name=='weap_saber_m.cog':text=replace(text,'ReturnEx(850.0);','ReturnEx(1000.0);')
        if name=='weap_extsaber_m.cog':text=replace(text,'ReturnEx(1000.0);','ReturnEx(850.0);')
        # Updating trail preference must immediately restore the steady blade.
        ordinal={'weap_saber_m.cog':11,'weap_sithsaber_m.cog':5,'weap_extsaber_m.cog':19}[name]
        text=replace(text,'allowfans=(1-allowfans);',f'allowfans=(1-allowfans);\n   if((GetCurWeapon(player) == {ordinal}) && (active == 1)) jkSetWeaponMesh(player, saber[color]);')
        if name=='weap_sithsaber_m.cog':
            text=replace(text,'message  user2', 'message user3 # Dual stance changed\nmessage  user2')
            text=replace(text,'# -------------- End custom variables', 'int bocStance=0 local\nint dualKey=-1 local\nint dualFlags=0x1a local\nint dualResult=-1 local\nint dualPovKey=-1 local\nint dualVisible=0 local\nint dualColor=-1 local\n\n# -------------- End custom variables')
            text=replace(text,'      mode = GetSenderRef();','      mode = GetSenderRef();\n'+block)
            for original,label in [('saber','setblade'),('Fan1','setfan1'),('Fan2','setfan2')]:
                text=text.replace(f'jkSetWeaponMesh(player, {original}[color]);',f'call {label};')
            # A timer/reactivation must not reset the hit list mid dual attack.
            pair='if(allowdamage) jkEnableSaber(player, 50, 0.123, 1.0);\n\telse jkEnableSaber(player, 0, 0.123, 1.0);'
            for begin,end in [('if (id == 1)','if (id == 2)'),('activated:','deactivated:'),('deactivated:','fire:')]:
                i=text.index(begin);j=text.index(end,i);part=text[i:j]
                part=part.replace(pair,'if ((bocStance != 1) || ((jkGetFlags(player) & 2) == 0))\n   {\n   '+pair+'\n   }')
                text=text[:i]+part+text[j:]
            text=replace(text,'ReturnEx(900.0);','if(GetCurWeapon(player) == 5) ReturnEx(1001.0);\n      else ReturnEx(900.0);')
            # user4 calls setblade first. Do not immediately overwrite its
            # visible native dual materials with SBX's transparent pair.
            text=replace(text,'jkSetSaberInfo(player, mat0[(2*color)+1], mat0[(2*color)], 0.007, 0.004, bladelen, tpl_wall, tpl_blood, tpl_saber);','if(bocStance != 1) jkSetSaberInfo(player, mat0[(2*color)+1], mat0[(2*color)], 0.007, 0.004, bladelen, tpl_wall, tpl_blood, tpl_saber);')
            # All eight disable sites are startup, reset, death, deselection,
            # or explicit shutdown. None is an attack timer or damage marker.
            text=replace(text,'jkDisableSaber(player);','call cleardualvisual;\n   jkDisableSaber(player);',8)
            text=text[:text.rindex('\nend')]+ '\n'+helpers+'\nend\n'
            # Put the stationary twin mesh back when the current attack ends,
            # including when the stance was changed during a prior swing.
            text=replace(text,'   // Shrink saber\n','   jkClearFlags(player, 0x10);\n   // Shrink saber\n') if '   // Shrink saber\n' in text else text
        emit('cog/'+name,text,'MotS-native weapon retained; JK31 trail cleanup/immediacy, startup hum reset, ignition stance availability/re-fetch; native auto-select order long850/staff900/single1000 (current staff1001); unused sound removal where needed to preserve all COG handles within128 resource references'+('; dual integration uses full-key-duration cooldown instead of browser 75-percent overlap, NOLOOP end-removal, and failed-allocation guard before hit-list reset; no persistent attack track handles; dual-only visible native polylines with hilt-only right mesh replace browser duplicated blade/fan meshes; restores SBX transparent materials on stance exit and all eight disable paths; non-dual fans preserved' if name=='weap_sithsaber_m.cog' else ''))
    # Existing stance key cycles staff -> Sariss -> dual -> staff. No new action
    # slot is needed and all existing MotS controls remain available.
    stance=read('dual','cog/saberstance.cog')
    stance=re.sub(r'^#.*\n','',stance,flags=re.M)
    stance='# SBX MotS retail dual stance; derived from ShadowX and supplied Dual Sabers.\n'+stance
    stance=stance.replace('GetCurWeapon(player) == 10','GetCurWeapon(player) == 11').replace('GetCurWeapon(player) == 9','GetCurWeapon(player) == 19').replace('GetInvCog(player, 5)','GetInvCog(player, 125)')
    # SBX's native saber MATs are transparent; the browser draws its custom
    # blade mesh twice. Retail instead uses its existing dual-polyline draw.
    # Keep the additional resources here, below the128-reference cap.
    stance,n=re.subn(r'^model\s+(?:bocSaber|bocFan1|bocFan2)\d*=\S+\s+local.*\n','',stance,flags=re.M)
    if n!=30:raise ValueError('Expected30 browser dual blade/fan model declarations')
    visible='model bocHilt=dxrhilt.3do local\n'
    visible+='\n'.join(f'material dualSide{i}=dxbs{i}.mat local' for i in range(10))+'\n'
    visible+='\n'.join(f'material dualTip{i}=dxbt{i}.mat local' for i in range(10))+'\n'
    visible+='template tpl_wall=+ssparks_wall local\ntemplate tpl_blood=+ssparks_blood local\ntemplate tpl_saber=+ssparks_saber local\n'
    stance=replace(stance,'symbols\n','symbols\n\n'+visible)
    for old in ('bocSaber[color]','bocFan1[color]','bocFan2[color]'):
        stance=replace(stance,'ReturnEx('+old+');','ReturnEx(bocHilt);')
    stance=replace(stance,'   if(what == 0) ReturnEx(bocHilt);','''   // Native MotS color order: orange, purple, dark-purple, blue,
   // light-blue, red, dark-red, yellow, green, silver.
   // Side and tip materials are locally derived from owned retail data.
   if(what == 12)
   {
      jkSetSaberInfo(player, dualSide0[color], dualTip0[color], 0.007, 0.004, 0.123, tpl_wall, tpl_blood, tpl_saber);
      ReturnEx(1);
      Return;
   }
   // What13: the weapon could not start the reverse grip's hop and spin,
   // so its hop (timer 2, armed by what9) does not happen either.
   if(what == 13)
   {
      KillTimerEx(2);
      ReturnEx(1);
      Return;
   }
   if(what == 0) ReturnEx(bocHilt);''')
    stance=stance.replace("// Boc's stance's meshes, keys and key lengths. Param 0 says which: 0", "// Boc's hilt, keys and key lengths. Param 0 says which: 0")
    stance=stance.replace("// blade, 1 first trail, 2 second trail, 3 chop's length, 4 cut's length,", "// hilt, 1/2 hilt during trail timers, 3 chop's length, 4 cut's length,")
    stance=replace(stance,"   // colour. In the reverse grip,","   // colour. What12 applies the visible native dual material pair and\n   // what13 cancels the reverse grip's hop. In the reverse grip,")
    # Dual Sabers 17 tells a player once when a stance's keys could not be
    # made. Here they are prepared files: say which ones are missing.
    stance=replace(stance,'Print("No Boc\'s stance or reverse grip in this game.");','Print("SBX MotS Dual Sabers: prepared animation files are missing.");')
    stance=replace(stance,'Print("No reverse grip in this game.");','Print("SBX MotS Dual Sabers: the reverse grip\'s prepared files are missing.");')
    stance=replace(stance,"# Boc's, made at load (misc\\keyretarget.dat)","# Prepared locally from owned JK animations")
    stance=replace(stance,"# the reverse grip's, made at load; -1 (startup) on a game that can't draw it, -2 once said so","# Prepared locally; -1 (startup) if missing, -2 once said so")
    stance=stance.replace('// From the Dual Sabers key (dualsabers.cog): the Sith lightsaber\'s stance','// From the retail controller: the Sith lightsaber\'s stance')
    # The browser build ships 0.01 s stand-ins for keys it makes at load; this
    # overlay ships the prepared keys, and a missing one loads as -1.
    stance=replace(stance,'''   // A game that can't make these keys loads this GOB's stand-ins, 0.01 s
   // long: then they count as missing
   if(GetKeyLen(bocChop) < 0.05) bocChop = -1;
   if(GetKeyLen(rgStand) < 0.05) rgStand = -1;
''','')
    emit('cog/saberstance.cog',stance,'MotS stance ordinals and bin125; native four-stance cycle (staff, Sariss, dual, reverse grip); hilt-only right mesh and twenty visible native blade materials, used only by the two-saber stances; browser mesh fans adapted to native static polylines; reverse-grip hop cancelled when its key cannot start')
    client=read('mots30','cog/client_weapons.cog')
    client=replace(client,'message     trigger','keyframe bocStand=rt_bostand.key local\nkeyframe rgStand=rt_rgstand.key local\n\nmessage     trigger')
    pos=client.index('\tif(TrigID == 129)')
    # Dual Sabers 17's reverse grip (1440) and its dash (1441). The browser
    # turns its blades with an engine flag (jk flag 0x200) that retail does
    # not have; here the controller's upper loop (rt_rgupper.key) turns the
    # grip anchors instead, so no flag is set.
    client=client[:pos]+'''\tif(TrigID == 1438)
    {
        if(bocStand != -1) ParseArg(Sender, "puppet=ky_bo.pup");
    }
    else
\tif((TrigID == 1440) || (TrigID == 1441))
    {
        if(rgStand != -1)
        {
            if(TrigID == 1441) ParseArg(Sender, "puppet=ky_rgd.pup");
            else ParseArg(Sender, "puppet=ky_rg.pup");
        }
        else
        if(bocStand != -1) ParseArg(Sender, "puppet=ky_bo.pup");
    }
    else
'''+client[pos:]
    emit('cog/client_weapons.cog',client,'Retains MotS projectile handlers, saber damage and hilt palette; adds dual and reverse-grip puppet triggers (the reverse grip falls back to the dual puppet if its keys are missing)')
    # The dual add-on's general modes were JK-specific. Retain the MotS staff
    # PUP's unarmed, gun and swimming modes, including native casting keys.
    def retail_pup(supplied_name,heading):
        supplied_pup=read('dual','misc/pup/'+supplied_name)
        dual_mode=re.search(r'(?ms)^Mode=2\b.*?(?=^Mode=3\b)',supplied_pup)
        if dual_mode is None:raise ValueError('Missing supplied dual PUP mode2: '+supplied_name)
        pup=read('mots30','misc/pup/ky_ls.pup')
        pup,n=re.subn(r'(?ms)^Mode=2\b.*?(?=^Mode=3\b)',lambda m:dual_mode[0],pup)
        if n!=1:raise ValueError('Expected one MotS staff PUP mode2')
        pup=replace(pup,'# Puppet control file for player with lightstaff -- Darth Maul stance',heading)
        pup=re.sub(r'(?m)^3=12.*$','3=19 # primary: native right grip in generated variant',pup)
        pup=re.sub(r'(?m)^4=19.*$','4=18 # secondary: native left grip in generated variant',pup)
        pup=re.sub(r'(?m)^((?:block2?|hit|magic2?)\s+r[tg]_\w+.key\s+0x28\s+1\s+)3',r'\g<1>4',pup)
        pup=re.sub(r'(?m)^((?:fire2?|block2?)\s+r[tg]_\w+.key\s+)0x28',r'\g<1>0x0a',pup)
        return pup
    reasons='MotS ky_ls unarmed/gun/swim modes retained exactly; supplied {} mode2 and native grip anchors; block/hit/Force priorities above upper idle; attacks and blocks use NOLOOP end-removal; lower-only locomotion keys prepared locally'
    emit('misc/pup/ky_bo.pup',retail_pup('ky_bo.pup','# Retail MotS dual PUP: native staff modes, supplied dual mode2.\n# The rt_ keys are prepared locally from owned JK data before installation.'),reasons.format('dual'))
    emit('misc/pup/ky_rg.pup',retail_pup('ky_rg.pup','# Retail MotS reverse-grip PUP: native staff modes, supplied reverse-grip mode2.\n# The rt_ keys are prepared locally from owned JK data and the add-on\'s own idle.'),reasons.format('reverse-grip'))
    emit('misc/pup/ky_rgd.pup',retail_pup('ky_rgd.pup','# Retail MotS reverse-grip PUP, dashing: as ky_rg.pup, with the dash for its run.\n# The rt_ keys are prepared locally from owned JK data and the add-on\'s own idle.'),reasons.format('reverse-grip dash'))
    for name in ['kyle_m.cog','mara_m.cog']:
        text=read('mots30','cog/'+name)
        text=replace(text,'symbols\n','symbols\n\nkeyframe bocBlock=rt_boblock.key local\n')
        old='blockSithTrack = PlayKey(player, blockSithAnim0[nextSithBlock], 1, 0x38);'
        # UNIQUE finds this exact key. A later event never stops an old slot
        # number, which could by then hold the persistent upper idle or legs.
        oldstop='''\tif (blockSithTrack != -1)
\t{
         StopKey( player, blockSithTrack, 0.1 );
         blockSithTrack = -1;
\t}'''
        text=replace(text,oldstop,'''   // Only the original staff path retains its original track handling.
   if(SendMessageEx(GetInvCog(player, 143), user1, 0, 0, 0, 0) == 1)
      blockSithTrack = -1;
   else
   {
'''+oldstop+'''
   }''')
        new='''if(SendMessageEx(GetInvCog(player, 143), user1, 0, 0, 0, 0) == 1)
   {
      // UNIQUE reuses only this key; NOLOOP releases its track at key end.
      // No retained slot handle can later stop an unrelated animation.
      PlayKey(player, bocBlock, 2, 0x1a);
      blockSithTrack = -1;
   }
   else '''+old
        text=replace(text,old,new)
        emit('cog/'+name,text,'Preserves MotS class/campaign logic; dual block uses exact-key UNIQUE and NOLOOP end-removal without retained track handle; original staff path retained')
    (out/'script-build.json').write_text(json.dumps(receipts,indent=2))
    return receipts

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();print(json.dumps(build(a.root,a.out),indent=2))
