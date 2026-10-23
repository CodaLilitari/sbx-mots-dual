# Original-retail MotS validation

The requested overlay passed the bounded original-retail single-player checks below. This is direct execution of the unchanged owned JKM.EXE in isolated Wine/Xvfb, using SBX-MotS3.0 as the base. It is not a claim of exhaustive campaign or connected multiplayer compatibility.

The executable SHA256 is `23cd064217f904d36d896f52d3cdd17635bb85441a12e0415c0637504191d974`. Every recorded case preserved its source input hashes. Both original rendering paths were observed: indexed software and the native accelerated path through Wine llvmpipe. No foreground desktop, physical GPU or audible-sound test was used.

| Case | Observed result | Evidence |
|---|---|---|
| sbx-base-02 | Control: stock SBX-MotS3.0 staff/single/long selection, stance messages, off/on and actual primary/alternate input work. | periodic-0032.png (private evidence; not included)<br>periodic-0039.png (private evidence; not included)<br>periodic-0041.png (private evidence; not included)<br>periodic-0045.png (private evidence; not included)<br>attack-primary-01.png (private evidence; not included)<br>attack-secondary-02.png (private evidence; not included) |
| sbx-candidate07-render02 | Original native accelerated path renders two glowing blades in separate hands, actual primary/alternate swings, color change and dual reentry without crash. | display-before.png (private evidence; not included)<br>[display-accel-selected.png](../evidence/native-accelerated-menu.png)<br>route-external.png (private evidence; not included)<br>[attack-primary-01.png](../evidence/native-dual-primary.png)<br>attack-secondary-02.png (private evidence; not included)<br>periodic-0057.png (private evidence; not included)<br>periodic-0069.png (private evidence; not included)<br>periodic-0088.png (private evidence; not included) |
| sbx-candidate07-life01 | Dual off/on, switching to single131 and long139, returning to original staff, and final dual reentry execute. Both blades return after reignition. | periodic-0023.png (private evidence; not included)<br>periodic-0025.png (private evidence; not included)<br>periodic-0027.png (private evidence; not included)<br>periodic-0029.png (private evidence; not included)<br>periodic-0033.png (private evidence; not included)<br>life-finish.png (private evidence; not included) |
| sbx-candidate07-extras01 | Talisman activates/expires; Object Throw activation/release/bubble guard execute. A private500-health actor falls to250 after actual primary and alternate saber inputs. | route-external.png (private evidence; not included)<br>periodic-0020.png (private evidence; not included)<br>periodic-0021.png (private evidence; not included)<br>periodic-0023.png (private evidence; not included)<br>periodic-0038.png (private evidence; not included) |
| sbx-candidate09-smoke01 | Final Push script activates and timer resets; native F3 goggles activate with brighter green view and battery drain. | route-external.png (private evidence; not included)<br>periodic-0033.png (private evidence; not included)<br>periodic-0073.png (private evidence; not included)<br>[goggles-active.png](../evidence/native-goggles-active.png)<br>goggles-off.png (private evidence; not included) |
| sbx-candidate08-skinsoft01 | Exact optional193-MAT layer repairs random texture corruption in representative Mara/Yoda base and dual models in the dark original room. | periodic-0033.png (private evidence; not included)<br>periodic-0037.png (private evidence; not included)<br>software-yoda-dual.png (private evidence; not included) |
| sbx-candidate09-skinbright01 | Final candidate09 plus unchanged optional layer renders coherent Mara and Yoda base/dual textures under full sector light. Both dual blades are visible. Default Object Throw154 availability is1 without grant. | [route-external.png](../evidence/software-mara-bright.png)<br>periodic-0017.png (private evidence; not included)<br>periodic-0021.png (private evidence; not included)<br>periodic-0024.png (private evidence; not included)<br>[software-full-light-yoda-dual.png](../evidence/software-yoda-dual-bright.png) |

## Limits and interpretation

- **sbx-base-02:** Private SP diagnostic grants raw inventory bins125/131/139; no connected multiplayer.
- **sbx-candidate07-render02:** Native menu toggle proves3D mode; registry request alone did not enable it. Wine llvmpipe, not a physical GPU. Trails-off attacks and flying saber projectile were not established.
- **sbx-candidate07-life01:** Single and long were selected unlit in this run. Death/respawn, saved games and campaign transitions were not tested.
- **sbx-candidate07-extras01:** No diagnostic DamageThing call. One stationary actor and input sequence, not balance validation. Object Throw physical debris movement was not exercised.
- **sbx-candidate09-smoke01:** Push target was not accepted, so mana stayed200; costs, reach and physical push are source-reviewed only. The goggles-off filename does not prove off: that capture remains active/green. No goggles-off acceptance.
- **sbx-candidate08-skinsoft01:** Native indexed light-table shading makes skin ochre in this dark room. Followup full-light control distinguishes shading from corrupt textures.
- **sbx-candidate09-skinbright01:** Only the private probe adds SetSectorLight(currentSector,1.0,0.0). Indexed palette colors and light-table shading differ from16-bit originals. Representative skins, not every skin/level.

Dual gameplay was tested on07. Final09 was compiled/executed for smoke and final representative software skin checks. Root packaging audit separately proves unchanged dual code/model/material bytes and08+patch/09+patch equality; this report does not substitute for that proof.

The optional193-MAT layer repairs software texture corruption, but conversion to the native indexed palette cannot promise identical16-bit color. The dark-room ochre tint was traced to the exact native01narsh light table. A private full-sector-light control with unchanged texture bytes restores pale Mara skin and pale yellow-green/olive Yoda. See [palette calculations](software-yoda-palette-evidence.json) and the final bright case screenshots.

The remaining untested scope is explicit:

- Connected multiplayer, remote-client synchronization and checksum exchange.
- Full campaign or normal character-selector workflow.
- All178 skins and every saber color/animation combination.
- Physical GPU/Windows driver behavior and audible sound.
- Death/respawn, save/load and campaign lifecycle.
- Trails-off actual attacks and a visible thrown-saber flight.
- Object Throw physical debris handling.
- Force Push mana costs, physical reach/force and target immunities in runtime.
- Goggles toggleoff/death cleanup.

## Identity and shutdown

| Layer | SHA256 |
|---|---|
| base | `49c2d136cffb6b6108ea29165d1245262713a7ff9ace472654768ee0e3e0c449` |
| candidate07 | `811d75ae4530ace2977395fee1c4db090c1bf3df020a1bcecb29302aa05be9cf` |
| candidate08 | `df5ba92b0391dc46c5da6f5b5e8f9dc14ab3cfe6616f15492afb34125ea9e7d9` |
| candidate09 | `05ba963a79d12aba847509fecb3c51d8d4bf770f2d1cb780cabe6b9a648c1479` |
| optional_software | `7ec0c6cdd37af43eb7d036b60c6ecfa0194a24fe949e08deeb8af418279a418a` |

19 recorded task-owned lanes are stopped; no live task Wine prefix, Xvfb or private audio process remains. Cleanup used exact task-owned prefixes and child handles, with no user application or other project process affected. [Stopped-state audit](stopped-state.json) preserves the checks.

Complete hashes, scene manifests, case reports and exact image paths are in [FINAL-RETAIL-VALIDATION.json](FINAL-RETAIL-VALIDATION.json). Historical failed candidates remain documented in review-notes.json (private evidence; not included).

**Keep this runtime directory private.** It contains owned stock test material and must not be included in the mod package.

Public copy: absolute workspace paths have been removed. Raw fixture evidence labeled private is not included; packaged captures and reports use relative links. See [public edition context](../../PUBLIC-EDITION.md).
