# Credits, source provenance and redistribution scope

This is the attribution record for the retail MotS overlay and its reproducible builder. It distinguishes statements found in the supplied source documents from independently checked file provenance. It does not grant new rights over the original mods or game data, certify an undocumented permission, or replace the original readmes and licenses.

## Current conversion

Prepared by **Coda (Codex Lily), collaborating with Andrei**: source comparison, MotS-specific reconciliation, offline build orchestration, native dual-saber integration, model variants, local animation preparation, validation tooling and documentation. Existing creators retain credit for their work. The current task does not claim authorship of SBX, Sith Sabers, Boc's animations, or the upstream retarget implementation.

## Saber Battle X

**ShadowX** is identified as the author of SBX-MotS v3.0 and SBX-JK v3.1 by their packaged `patchinfo.txt` files. The SBX-JK v3.1 documentation, dated **2/3/02 as written in that document**, also names ShadowX and supplies the fuller credits and permission text. The build uses SBX-MotS v3.0 as its base and compares SBX-JK v3.0 with v3.1 to identify additions, revisions and removed material.

The v3.1 document permits using the mod as a base or incorporating its features with due credit. Its distribution paragraph also requires including the document unmodified and prohibits charging beyond incidental online costs. These are verified statements in the inspected document; this summary does not extend them to unrelated third-party material or substitute for retaining the source document when distributing the original mod.

The following credits are carried forward from ShadowX's v3.1 document. They are the original author's attribution account, not a newly performed authorship audit of each individual asset:

| Contributor as credited | Work described by the source document |
| --- | --- |
| Jamontoast, Van Shourt, Deathbane27, Darth Haun | Glowsaber 3.0, SBX's foundation |
| Dark Shadow, Sithsaber Glow Edition | 3D crossbow bolt and repeater-ball models |
| Kageboushi Gen | Jedi skins and related meshes/textures; secondary credits name Al MacDonald, Origins, LucasArts and the Guardians of the Galaxy Saber Mod |
| Al MacDonald | Numerous skins and texture foundations; ShadowX describes subsequent fixes and changes |
| Obi-Wan of the Jedi Order | Kyle skin, multiplayer background, and some Jedi Council models/textures |
| Marc Sauve | Tales of the Jedi-era skins and Exar Kun torso textures |
| Millennium | Millennium skin |
| OrBitR_Dragon | Original Medieros skin |
| Unnamed author of the BFP2 Thrawn skin | Thrawn skin source; the inspected document does not supply a name |
| RS_Thrawn | RST skin based on Admiral/Thrawn skins |
| Obsidian{DBC} | Crimson Guard source later changed into FORCELORD |
| SavageX | Imperial Officer textures and the mesh used for Callista/Mara |
| Al MacDonald, J_Anakin, NJO_QuiGon, Kageboushi, J_Obi | Callista/Mara texture contributions as credited by ShadowX |
| Carnage | Bar Tender skin |
| Hal | Hal skin |
| TIE | Vader textures/skin, jumping animation, Darth Maul skin, and some Jedi Council work |
| Sandcrawler Productions; Fardreamer, identified as owner | Flip sound, rolls, Force Jump Flip/Heal Other components, Sith hilt and other saber handles; ShadowX reports approval under their license |
| Ben Burtt | Sith-saber swing sound sources, subsequently modified by ShadowX |
| RS_Dragon | Basis of the SBX title-screen layout |
| EAH_CL0wN | Item-inventory icons used for SBX functions |
| Original alpha and beta testers | Testing acknowledged by ShadowX |

ShadowX also describes his own modeling, texture, sound and code work and credits LucasArts source meshes/textures. The full original document remains the authoritative detailed attribution account; the table is a reading aid, not a replacement for it.

## Supplied SBX Dual Sabers test add-on

The supplied **SBX Dual Sabers (test version)** readme identifies the underlying SBX-JK v3.1 work as ShadowX's. It does **not separately name the author of the add-on itself**, so this record does not infer one from that phrasing.

Its credits state:

- Changed SBX scripts are derived from ShadowX's work. Twin spinning attacks use the spin and leg movement of his `spinl.key` and `spinr.key`.
- Left, right, back and heavy twin-saber attacks, and the arm motion in the twin spins, derive from **Sith Sabers by EAH_CL0wN**. The readme says they are **used with permission**.
- The forward cross-cut was made for the supplied add-on.
- Jedi Knight, Boc and his animations are credited to **LucasArts**.

The separate **Sith Sabers** readme names **EAH_CL0wN** and additionally credits **Al McDonald** for Vader materials, using that spelling. Its permission section says authors may not use the level as a base and permits distribution of the unmodified package with its readme and without charge beyond incidental online costs. The supplied Dual Sabers readme's more specific permission claim is retained as **the add-on author's testimony**. No independent permission correspondence was supplied or verified in this conversion task, and this record does not invent or broaden that permission.

Both original readmes are retained unmodified under `docs/original/` in every public package. The Builder ZIP contains tools and documentation, not game animation files. The separate main overlay includes the attack and locally prepared animation resources needed for this conversion; their source provenance and the permission testimony above remain applicable.

## Retarget implementation and headless helper

The animation baker uses the pinned upstream **OpenJKDF2 `sithKeyRetarget.c`** implementation with a local headless adapter. The associated source license identifies **OpenJKDF2 contributors** and grants permission to use, copy, modify and distribute the software without fee, with its warranty disclaimer. The exact license is included at [`docs/licenses/OpenJKDF2-LICENSE.md`](docs/licenses/OpenJKDF2-LICENSE.md); retain it and the pinned source with the builder.

- Pinned upstream commit: `ac698316da694490e233907709a1a4422fb6802f`
- Pinned retarget source SHA-256: `e9b9e85cbc0d460b4efcca10f637ed752e01696770fc01c69b1c01b2b7730864`
- Adapter executable SHA-256 recorded in its build receipt: `c010680201bdbce7fb3b8c7f8a1d5a1f96c894cd087d1e53027540d0b9223ea9`

The build receipt records a source transformation that removes include directives and joins the pinned implementation with the local adapter prefix and writer suffix. The Python wrapper verifies the source and helper hashes before running the helper. This establishes which implementation is used; its software license does not provide a license to redistribute the game animations it processes.

The source Dual Sabers readme refers to browser menu build `ba4df7d0`. That historical runtime label is not substituted for the pinned implementation commit above, and this retail conversion does not require that browser game.

## LucasArts/Lucasfilm game data

Jedi Knight: Dark Forces II, Mysteries of the Sith, Boc, their original models/animations, audio, icons, scripts and other game resources belong to their respective rights holders. The original source documents identify LucasArts/Lucasfilm and include this notice:

> THIS MODIFICATION IS NOT MADE, DISTRIBUTED, OR SUPPORTED BY LUCASARTS ENTERTAINMENT COMPANY. ELEMENTS TM & (C) LUCASARTS ENTERTAINMENT COMPANY.

The same absence of LucasArts endorsement applies to this conversion. Owned `Res2.gob`, `Res1hi.gob`, `JKMRES.GOO` and `JKMSNDLO.GOO` are explicit local build inputs and are not included in the source-builder delivery.

## Public release scope

This public release, prepared at Andrei's request, consists of an on-top game-resource overlay, an optional software-renderer texture layer, and a separate reproducible builder. It requires the user's own MotS installation and the original SBX-MotS v3.0 base. The main overlay contains 602 changed/additional resources; the optional layer contains 193 MAT files. Neither includes a complete base mod, retail executable or retail game archive.

The overlay includes copied or adapted mod/game resources, including generated KEY animations, models, audio, icons, textures and scripts. Reconciliation derives 40 JK WAVs, two JK icons and an adapted MotS Super Shield COG; assembly also prepares native blade materials and dependencies. These resources are credited to their sources. Generating, transforming or renaming a file does not make it wholly newly authored or grant a new blanket license over it. The original documents' permission text and attributed testimony remain unchanged.

The Builder ZIP contains conversion tools, documentation, the pinned software implementation, its helper/build receipt and software license notices. It takes explicit local mod/game inputs. The entire build tree is not a release package: source archives, extracted inputs, private runtime fixtures and the convenience `local-mod/SBX-Dual` folder containing the unchanged full base GOO are excluded. Use only the separately packaged release artifacts.

This public documentation edition supersedes the earlier local-delivery instructions that described all generated resources as private and only the builder as shareable. It changes packaging documentation and public receipt paths, not the tested game resources, builder tools, original readmes or license. The public-edition receipt records that equality and the prior archive identities. This file describes release scope; it is not itself a publication receipt or independent permission correspondence.

Per-file origins and hashes remain in the manifests. See `RELEASE-NOTES.md` for installation, browser expectations and the optional texture choice.

## Verification scope

The four mod archive identities, supplied attribution text, pinned retarget source/helper identity, and reconciliation inclusion decisions have been checked against local source files. Historical contributor claims and the add-on author's permission statement remain attributed testimony. Bounded original-executable tests are recorded in RETAIL-VALIDATION.md. Connected multiplayer and complete campaign acceptance remain unverified; neither this credits file nor a successful static build establishes them.
