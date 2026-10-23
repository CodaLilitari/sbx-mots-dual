# SBX Dual Sabers for retail MotS — conversion notes

This is an overlay for the original **SBX-MotS v3.0**. The main package has **602 game resources: 142 changed base paths and 460 additional paths**. It includes no byte-identical base members, complete base archive, retail executable or retail resource archive.

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
