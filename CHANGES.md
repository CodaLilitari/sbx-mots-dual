# SBX MotS Dual Sabers — Special Edition changes

## v1.2.0 Special Edition — 26 October 2026

- Package the complete effective SBX base plus conversion into one deterministic GOO, with a separate complete software-renderer edition. Finished gameplay needs only the selected GOO and ordinary MotS.
- Validate file references across every packaged resource against stock MotS alone. Preserve winner precedence, source hashes and archive round-trip checks.
- Replace inherited missing `cm60142.wav` with the original JK equivalent for the same actor response and reuse the already bundled `i00mn13z.wav`. This is an explicit fallback; all other actor bytes remain intact.
- Pass the caller's `--jk-res` argument through reconciliation instead of falling back to the historical workstation path.
- Match the supplied v17 archive against merge !1. Current original-executable results are recorded in `STANDALONE-VALIDATION.md`.
- Add Special Edition beneath the original SBX logo. Move that logo upward 17 pixels without resampling; preserve the palette and all pixels outside the right title block. No other GOO member changes from the tested standalone gameplay build.

## Historical overlay releases


The historical v1.0.0 release is an overlay for the original **SBX-MotS v3.0**. The v1.0.0 main package has **602 game resources: 142 changed base paths and 460 additional paths**. It includes no byte-identical base members, complete base archive, retail executable or retail resource archive.

## v1.1.0: SBX Dual Sabers 17

The builder now takes **SBX Dual Sabers 17** (`SBX Dual Sabers.gob`, SHA-256 `b0ad90b06fc76efd6641d286ff11a27c7f66b94db05c4b33a53fb1287f9e97e6`, 25 October 2026) instead of the 22 October release (`eb34c785…`). The main overlay grows to **651 game resources: 165 changed base paths and 486 additional paths**, still with no byte-identical base members. The optional software texture layer is unchanged (193 MAT files, `7ec0c6cd…`). Two clean builds from the same inputs produced the same overlay, `5c8b0d3b7d8ec0b539614b6d9083fc1a7b1837ed4f08ec4ca28b1a5f27a130f1`.

- **Reverse grip.** The Sith saber's stance action now cycles **staff → Sariss → dual/Boc → reverse grip → staff**. Both sabers are held blade-down, each blade leaving the little-finger side of the fist. The stance has its own stand (prepared locally from the add-on's `rg_antidle.key` through the recipe's new `own` section) with SBX's own legs, and its own attacks: standing, forward, left, right and back, and a cyclone each way when turning fast. Second fire is a coil, a hop and a whole turn in the air; the hop starts 0.17 s in, only on the ground and still in this stance, and is cancelled when the weapon cannot start the attack. Running flat out for about half a second switches to the dash puppet (`ky_rgd.pup`) until the player slows down.
- **Retail blade turn.** Dual Sabers 17 turns the blades in the browser with an engine flag (jk flag `0x200`) that JKM.EXE does not have. Here the reverse grip's persistent upper idle, `rt_rgupper.key`, also carries one constant entry for each grip anchor (`sbxd_left_grip`, `sbxd_right_grip`): yaw 180, the hilt turned end over end about its own middle, as the engine's grip code does. No model, track, flag or hotkey is added; the controller swaps the upper idle when the stance changes between Boc's and the reverse grip. The anchor positions come from SBX Kyle; for 175 of the 178 player models they are within 0.0001 units of the model's own value, and within 0.000708 for the other three (`mara`, `callista`, `kyst`).
- **Attack timing.** As in Dual Sabers 17: Boc's chop plays 1.1 times as fast as his own and his cut 1.4 times; the Sith Sabers left and right cuts 1.3 times, the back cut 1.07 times and the heavy cut at its own speed (all were 1.5 times). The twin spinning slashes take 1.05 s turning left and 0.8 s turning right.
- **Heavy cut.** Dual Sabers 17's second fix: two thirds of the way through, the left blade no longer snaps about 55 degrees in an instant.
- **Footsteps.** SBX 3.1's walk, walk-back and strafe keys carry saber damage markers instead of the original game's footstep markers, and SBX-MotS v3.0 ships the same 23 keys byte for byte, so walking is silent in every stance. The builder adds the footstep frames from Dual Sabers 17's `misc/keymarkers.dat` to those 23 keys (`tools/build_footsteps.py`, the same rules as OpenJKDF2's loader) and to the walks it prepares for Boc's stance and the reverse grip. Only the marker sections change.
- **Builder.** The pinned retarget source moves from `ac698316` to OpenJKDF2 `8ccc356c` (the recipe's `own` section, the marker table and its rules). The key baker was rebuilt from it with mingw-w64 GCC 13 on Ubuntu (zero warnings); its receipt records the new hashes. The recipe check now expects 23 retarget and 14 own rules.
- **Not carried over**, as browser-only: the 0.01 s `rt_*.key` stand-ins (retail gets the prepared keys), the add-on's own `misc/keyretarget.dat` and `misc/keymarkers.dat` (used at build time instead), the browser's skin-list merging with Continuum, and the browser lobby notes.

Native resource budgets after the change: `saberstance.cog` 44, `sbxd_view.cog` 4, `client_weapons.cog` 22 and `weap_sithsaber_m.cog` 123 of 128 references. See `RETAIL-VALIDATION.md` for what has and has not been run.

The rest of this file describes v1.0.0, all of which v1.1.0 keeps.

## Dual sabers

- Uses original MotS COG verbs and native KEY/PUP/3DO resources. The browser runtime converter is run offline against explicit local inputs; no custom engine is required to load the result.
- Adds a third Sith-saber stance through the existing stance action: staff, Sariss, dual/Boc. No additional action hotkey is required.
- Prepares dual variants for all **178 merged player models**, preserving their original visible meshes and animated skeleton transforms.
- Uses hilt-only geometry and two native visible saber polylines. The ten colors remain available. Dual mode intentionally differs from the browser mesh/fan rendering; non-dual saber fans remain.
- Uses full-duration attack cooldowns, checks failed key allocation, and avoids stale attack-track handles to fit the original engine's four animation tracks.
- Repairs inherited native resource-reference overflow, static model capacity pressure, and broken hierarchy links exposed by original-executable testing.

## SBX 3.0 / 3.1 reconciliation

The direct JK archive comparison found **174 added, 155 changed and 30 removed paths**, with **1,515 identical paths**. The accompanying audit records how these map onto native MotS rather than replacing MotS scripts with JK scripts.

- Preserves all **676 original MotS model registry rows**, their order, sound choices and class roles. Adds 52 rows for 13 missing skins, yielding 728 rows and 178 unique models.
- Adds the missing skins including Yoda, Mara, Callista, Angel variants, Bartender, Adi Gallia variant, Hal, Luuz, Mikos, Obi-Wan variant, Toko Hikaru and Yarah. Carries 29 shared model revisions. Solomon remains alongside Mikos.
- Preserves MotS-only resources and accounts for all 30 paths removed by JK 3.1. Removed Force Halt audio is retained as an unassigned resource.
- Carries compatible audio/material fixes, immediate trail toggles, unconditional throw/timer cleanup when trails are disabled, startup hum initialization, stance recovery and saber selection order.
- Adds inventory-selectable object Force Throw and an optional Sith Talisman pickup without replacing native MotS Force powers or Super Shield.
- Ports the brighter goggles effect, stronger/shorter Force Blinding, Push's potential-based costs and Surge exemptions, and Destruction self-damage through namespaced native templates.
- Fixes MotS Force Defense's reversed multiplier and Bryar's wrong inventory-bin lookup. Push's repaired iteration applies the full target filter to every candidate, including invulnerability and explicit player Talisman protection. Object Throw cancels if the player enters the EWEB while holding or releasing it.
- Preserves native MotS weapon/rank/control contracts, native Push actor/player target scope and force magnitude, native Saber Throw costs, and native Surge/Power Boost balance where JK's different design would remove or change MotS capability. These are explicit compatibility choices, not a claim of identical JK/MotS behavior.

The detailed tables are `docs/audit/reconciliation.md`, `weapon-class-feature-matrix.md`, and `remaining-cog-delta-matrix.md`.

## Bonus texture repairs

- The main overlay repairs missing RGB565 mip tails in `mwdchest.mat` and `mwdback.mat`. Every existing source byte and all full-resolution artwork are retained; only the four absent lower-resolution levels are reconstructed.
- The optional software patch converts **193 active 16-bit materials / 195 texture records** to native indexed color. It retains both two-cell animations, dimensions, mip chains and transparency semantics.
- Ordinary textures use stable, normally shaded entries shared by the inspected native map palettes. Emissive blade textures use a separate palette profile. This avoids accidentally making skin and clothing glow in darkness.
- Indexed color has lower color precision, especially for saturated blues, and mild ordered dithering can add grain. Native lighting ramps can also turn olive green brown in dim sectors; the source artwork and original level colormaps are preserved. Bright-sector runtime controls distinguish this lighting behavior from the repaired texture corruption. The main overlay keeps the original RGB565 artwork available for accelerated rendering.

## Scope and known differences

First-person presentation remains the original staff view; use third person for two separate sabers. The Talisman template is available for custom maps and is not inserted into existing campaign maps. Keep the upstream precaution of extinguishing the saber before saving. Connected multiplayer, campaign completion, every selectable skin and every Force interaction have not been exhaustively tested. See `RETAIL-VALIDATION.md` for the actual original-executable evidence.
