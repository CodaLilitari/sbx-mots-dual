SBX DUAL SABERS (TEST VERSION)
An add-on for SBX-JK v3.1 by ShadowX

WHAT IT DOES
The Sith lightsaber gets a third stance: Boc's, with a single saber in each hand. Any player skin can use it.
- Boc's stance and swings (stand, chop, cut, block) are converted to your own skeleton from your own copy of Jedi Knight when a level loads, so no LucasArts animation is shipped.
- Only Boc's upper body is used when you move: your legs walk, run, strafe, turn, crouch and jump with SBX's own animations while your arms keep twirling the two sabers as Boc does standing, at his own pace however fast you move, carrying on from one move to the next. His chop, cut and block move only the upper body, so you can swing while you walk. Standing still, you crouch like Boc and twirl the sabers as he does.
- Boc twists his whole upper body hard as he chops and cuts. Your torso follows a steadier version of it: his turns smoothed out and 60% as far, while your arms and sabers still swing where his do.
- Each hand holds its saber by the middle of the hilt.
- The attacks while backing up or sliding left or right, and the heavy cut, are the twin saber attacks from EAH_CL0wN's Sith Sabers, used with permission. One fix: in the heavy cut, the left arm kept turning after its last move and swung that blade behind you and through your hips. It now comes back to guard and holds.
- The attack while walking or running forward is this add-on's own twin cross-cut: both sabers come up beside your head and over your shoulders, swing over to point straight ahead, and cut down and inward, meeting at the tips and crossing halfway along in an X in front of you, then come back to guard. It sweeps through the space right in front of you, so it hits someone there. It moves only the upper body, so your legs keep walking or running, and it starts and ends in Boc's stance, so it blends in and out of it. On SBX's Kyle the blades stay clear of the head and body all the way through, over SBX's walk, run and crouch-walk (a skin with a much bigger body could still touch).
- Attacking while you stand and turn fast (drag the mouse left or right) does a twin spinning slash that way, like SBX's lightsaber spinning slash: SBX's spin and legs, with both arms swinging the Sith Sabers cut for that way.

WHAT YOU NEED
- SBX-JK v3.1 (SBX-JK v31.gob).
- The browser version of Jedi Knight at https://jkdf2mp.jkdf2mp-lobby.workers.dev/ (since 22 October 2026, when its main menu showed ba4df7d0 in the corner), which converts the animations as the level loads. A tab opened before then still has the old version: reload it. Earlier test builds can't read this version's misc\keyretarget.dat and give the staff. It doesn't work in the original JK.EXE or in other OpenJKDF2 builds. There Boc's stance is left out and the Lightsaber Stance key goes staff, Sariss, staff. The Dual Sabers key can't be bound at all: Setup says "Unable to bind control to this action", because those games have room for only 20 action keys (see GOOD TO KNOW), so removing other keys won't help. A few seconds into a level the game says "SBX Dual Sabers is off". A player on such a game sees anyone in Boc's stance in the staff stance.

INSTALL
Put SBX Dual Sabers.gob in the same folder as SBX-JK v31.gob, wherever that is (Resource, or a mod folder such as expansions\SBX), and play with both ticked. In the browser version's list of mods, SBX Dual Sabers has to be above SBX-JK v31.
Don't put it in Resource if SBX-JK v31.gob is in a mod folder: a mod folder comes before Resource, as in the original game, so SBX's files replace this add-on's and there's no Dual Sabers key. (The other way round, SBX-JK v31.gob in Resource and this GOB alone in a mod folder, works, but the list names it after the folder.)

USE
Press your Dual Sabers key. From any weapon it takes out the Sith lightsaber, lit, in Boc's stance. Press it again to go back to the staff, and again for Boc's. Bind it first in Setup > Controls > Keyboard, where it's just after Lightsaber Stance.
Or take out the Sith lightsaber (5) and press your Lightsaber Stance key. The stances go: staff, Sariss, Boc's two sabers, then back to the staff.
In Boc's stance:
- Fire, standing still: Boc's chop, then his cut, one after the other.
- Fire while moving: a twin saber attack for the way you're going (forward, back, or sliding left or right). Forward, walking or running, it's the twin cross-cut.
- Fire while standing and turning fast (drag the mouse left or right): a twin spinning slash that way. As with SBX's lightsaber, the turn has to be fast (over 200 degrees a second), which in practice takes the mouse, and it doesn't happen while crouching.
- Second fire (Z unless you changed it): the twin saber heavy cut.

GOOD TO KNOW
- In first person you still see SBX's staff. Use the third-person view to see both sabers.
- Like SBX's other stances, the blades hurt on any touch, not only during an attack.
- Like the lightsaber, it isn't switched away when you pick up a backpack or a weapon. Switching by hand works as usual.
- Each attack hits an enemy once, even if both blades touch it. A hit does the same damage as SBX's other Sith saber stances.
- The Sith Sabers attacks play 1.5 times as fast as in Sith Sabers, like Boc's converted chop and cut. The forward cross-cut takes a second, about as long as Sith Sabers' forward cut.
- The Dual Sabers key is a 21st action key. Jedi Knight has room for 20, and SBX uses all of them, so it needs the browser version above, which has room for 32.
- Its static.jkl makes room for 256 scripts instead of SBX's 1000 (SBX uses about 50). In OpenJKDF2 each one takes about 1 MB, so this saves about 750 MB, and lets a player who only has SBX join a game with this add-on: the browser version has 2 GB in all.
- It replaces SBX's saberstance.cog, client_weapons.cog, weap_sithsaber.cog, kyle.cog, static.jkl, items.dat and jkstrings.uni with changed copies, and adds cog\dualsabers.cog, misc\keyretarget.dat, misc\pup\ky_bo.pup and seven 3do\key\sbxd_*.key files. Another mod that changes those files won't work alongside it.

CREDITS
SBX-JK by ShadowX: the changed scripts are his, with the dual saber stance added. The twin spinning slashes use the spin and legs of his lightsaber spinning slashes (spinl.key and spinr.key).
Twin saber attacks (left, right, back and heavy cuts, and the arms of the twin spinning slashes): from Sith Sabers by EAH_CL0wN, used with permission. The forward cross-cut was made for this add-on. Sith Sabers' own readme comes with this add-on, unchanged.
Jedi Knight, Boc and his animations: LucasArts.

This add-on is not made, distributed, or supported by LucasArts Entertainment Company. Elements TM & (C) LucasArts Entertainment Company.
