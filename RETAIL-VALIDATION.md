# Retail MotS validation — local SBX Dual overlay

**Delivery:** 2026-10-23, candidate09, requiring original SBX-MotS v3.0. This delivery passed static validation, deterministic rebuild checks, and bounded tests in the **original MotS executable**. It is not a certification of connected multiplayer, every skin/attack combination, or a complete campaign playthrough.

## v1.1.0 (SBX Dual Sabers 17): what has been run so far

**v1.1.0 has not yet been run in the original JKM.EXE.** Everything below about v1.0.0 still describes v1.0.0's tests. For v1.1.0:

- **Build and static checks.** Two clean builds with the tools in this repository, from the same inputs, produced the same main overlay (`5c8b0d3b7d8ec0b539614b6d9083fc1a7b1837ed4f08ec4ca28b1a5f27a130f1`, 651 members) and the unchanged software layer (`7ec0c6cd…`). Layered static validation passed: 2,963 reachable resources, zero missing dependencies, zero lost or duplicate base bins, zero byte-identical base members, zero model hierarchy or capacity failures, and every changed COG within 128 references (`weap_sithsaber_m.cog` 123). The builder checks each prepared key's nodes, type, frames, rate and markers, and the reverse grip's two anchor entries.
- **OpenJKDF2 MotS mode, not the original executable.** The overlay ran in the jkdf2mp site's game (browser build cloudflare-51, tristamus/OpenJKDF2 `8ccc356c`) in MotS mode, in Chromium with software WebGL (SwiftShader, about 4 frames a second), from Steam MotS data files, installed as `INSTALL.txt` says (loose overlay beside `sbx-mots v3.goo` in one mod folder). The game hosted multiplayer maps (`mdm07_vaporator`, `mdm15_homestead`, `mdm03_canopy`). A test-only COG, added through one extra `items.dat` row and not part of any package, gave and lit the Sith saber, switched to third person and pressed the stance action every 20 seconds; attacks and movement were real keyboard input. This build does not set the browser's reverse-grip engine flag, and the anchor names don't take its automatic second-hilt path, so the blades were placed by the overlay's own keys, as in JKM.EXE.
- **Observed there:** the cycle staff → Sariss → dual/Boc → reverse grip → staff; the reverse-grip puppet trigger; in the reverse grip, both blades pointing down from the little-finger side of each fist while standing and walking; the primary attack and the hop and spin playing; no engine errors beyond the string-table count warnings the base has too. Screenshots: `docs/evidence/openjkdf2-mots-reverse-grip-*.png`.
- **Not yet observed:** the dash (at 4 frames a second the run never stayed above the dash speed long enough, so trigger 1441 never fired; its code is Dual Sabers 17's, and MotS's `walkplayer` has the same `maxthrust` 2 and `surfdrag` 3 as JK's, so the threshold carries over), footstep sounds, the four-track limit under JKM.EXE with the reverse grip's attacks, other skins in motion, and anything over a network.

## Exact artifacts

| Artifact | SHA-256 |
| --- | --- |
| Main generated GOO, equivalent to the ZIP's 602 loose game files | `05ba963a79d12aba847509fecb3c51d8d4bf770f2d1cb780cabe6b9a648c1479` |
| Optional software GOO, equivalent to the texture ZIP's 193 loose MAT files | `7ec0c6cdd37af43eb7d036b60c6ecfa0194a24fe949e08deeb8af418279a418a` |
| Required original SBX-MotS v3.0 base GOO | `49c2d136cffb6b6108ea29165d1245262713a7ff9ace472654768ee0e3e0c449` |
| Original unmodified JKM.EXE used for runtime checks | `23cd064217f904d36d896f52d3cdd17635bb85441a12e0415c0637504191d974` |

The delivery ZIP hashes are in the separate `SHA256SUMS.txt` and `DELIVERY-MANIFEST.json`. Each ZIP contains its own member manifest. GOO hashes above identify game-resource content, not the compressed delivery ZIP.

## Build and source checks

- The main overlay contains **602 game resources: 142 changed base paths and 460 additional paths**. It contains zero byte-identical base members. The unchanged SBX base GOO, retail executable and retail resource archives are excluded.
- The direct SBX-JK 3.0/3.1 comparison accounts for 174 additions, 155 changes, 30 removals and 1,515 unchanged paths. Reconciliation records explain the choices made for native MotS, including preserved MotS-only content and retained material removed from JK3.1.
- All 676 original MotS model-registry rows remain, with 52 added rows for 13 missing skins. The result has 728 registry rows and 178 unique models, with a dual variant prepared for each unique model.
- Layered validation resolves **2,937 reachable resources** with zero missing dependencies, lost/duplicate base bins, hierarchy failures, native COG reference-limit failures or loose/archive mismatches. The changed scripts were checked against the measured native verb/message registry. These checks do not substitute for a native compiler or gameplay run.
- A clean build from the original input archives, using the portable final builder tools, reproduced both final GOO archives byte-for-byte. All 20 delivered tool/vendor files match that tested tool set.
- All 193 optional indexed MAT files were structurally checked, including 195 texture records, two animated two-cell materials, transparency and mip chains. The two missing RGB565 mip tails in the main overlay are append-only repairs; every existing source byte is preserved.

## Original-executable tests

The runtime was isolated in WSL with 32-bit Wine and private Xvfb displays. Accelerated tests used Mesa llvmpipe; this is not coverage of a physical Windows GPU/driver. The test harness used owned media and private diagnostic copies of native MotS maps, plus bounded diagnostic COGs. Those diagnostic maps/scripts are not installed by this package.

| Check | Observed result and evidence scope |
| --- | --- |
| Dual rendering and controls | Both native blades render; real primary/alternate input animates them; color cycling changes both. `sbx-candidate07-render02` explicitly verified the native menu's 16-bpp accelerated mode. A requested registry setting alone was not treated as renderer proof. |
| Lifecycle | Diagnostic calls to ordinary weapon scripts extinguish both blades, relight them, select single/long sabers, return to the original two-ended staff, and re-enter dual stance with both blades. |
| Saber damage | A private stationary actor began at 500 health; real attack input reduced it to 250. The diagnostic did not call `DamageThing`. This demonstrates damage in that case, not per-attack balance or every collision direction. |
| Sith Talisman | Activation produced active=1, magnetic seal=4 and mana=0; timed expiry restored active=0 and seal=0. All Force-immunity interactions were not exercised. |
| Object Force Throw | Activation, release and bubble-blocked activation were observed. Final candidate09 reports inventory availability=1 without a diagnostic grant. The test did not perform an actual debris launch; EWEB cancellation is source-checked. |
| Brighter goggles | Candidate09 accepted the actual native F3 goggles input, displayed the brighter green view, and consumed battery from 193 to 183. A later capture named `goggles-off` still shows active goggles, so toggle-off is not accepted as proven. |
| Force Push | Candidate09 compiled/loaded and executed activation and timer reset. Its diagnostic victim did not qualify, so mana stayed 200. Potential-based cost changes, target iteration and filtering are source-checked; this test does **not** prove the cost, impulse or range against a valid victim. |
| Software texture fix | Final candidate09 with the unchanged 193-MAT patch renders coherent Mara and Yoda original/dual models in a bright-sector control, with both dual blades visible. The earlier 16-bit software-format corruption is absent in these representative checks. |

Core dual tests used candidate07. A byte comparison confirms that all dual models, keys, PUP, controller and saber COGs are unchanged in candidate09. The intervening changes affect object Throw's EWEB guard, add base overrides for Push/goggles, and append the two missing MAT mip tails. The earlier candidate08-plus-software fixture and final candidate09-plus-software fixture also have byte-identical effective game resources. See `docs/audit/final-core-equivalence.json`, `final-layer-equivalence.json`, and `FINAL-RETAIL-VALIDATION.json` for the exact distinction between cases.

## Texture color limits

The optional software patch fixes format corruption while retaining the source artwork. Indexed rendering has lower color precision and can show mild dithering. MotS's original light-table ramps can also shift hues in dim sectors: Yoda's original olive/yellow-green face quantizes closely at full light, but selected greenish indices become brown under native `01narsh.cmp` light level 32. Mara's existing 8-bit arm textures show the same warm lighting tendency and were not converted by this patch.

The final bright-sector controls render Mara with pale skin/red hair and Yoda with pale yellow-green/olive skin. The original level colormap is retained. The main overlay keeps the RGB565 texture artwork for accelerated rendering. The four-panel image in `docs/audit/software-yoda-palette-comparison.png` is an **offline palette calculation**, not an engine screenshot; the captures under `docs/evidence/` are original-executable screenshots.

## Remaining limits and installation choices

- Connected multiplayer/checksums, host/client synchronization, respawn and joining an unmodified SBX game were not tested. Use matching packages for all participants; no compatibility promise is made for mixed installations.
- Normal character-selection UI coverage, all 178 skins in motion, complete campaign progression, all Force interactions, death/respawn, audible sound and physical GPU rendering remain unverified. Actual attacks with trails off, visible thrown-saber flight, physical object-Throw debris movement and goggles toggle-off/death cleanup were not established.
- Save/load was not validated. Retain SBX's established precaution: **extinguish the saber before saving**; cycle it off/on if a loaded saber loses damage.
- Dual mode uses the native two-blade glow and full-duration attack cooldowns. The browser extension's extra mesh fans and overlapping attacks at 75% duration are not reproduced. First person keeps the staff model; third person shows both separate hilts/blades.
- The optional Talisman template is available for explicit custom-map placement. Existing campaign Super Shield pickups are preserved.
- Original string-table count/duplicate warnings occur in the source game/base too. Their presence alone is not an introduced overlay failure.

Generated receipts deliberately retain their build-time status (for example, `candidate_not_runtime_accepted` or `GENERATED_AND_STRUCTURALLY_CHECKED_NOT_RETAIL_ACCEPTED`). This document and the separate final runtime receipt supply the later, bounded runtime conclusions; the original generation receipts have not been rewritten to imply that the builder ran the game.

All 19 task-owned Wine/Xvfb lanes were stopped, and their recorded source input hashes were unchanged. The package includes reports and a small curated screenshot set; complete private runtime fixtures and their owned game data remain outside every delivery ZIP.
