# Remaining JK 3.0 to JK 3.1 COG audit

The comparison uses effective resources. When JK 3.0 has no COG override, the baseline is the corresponding file from the owned retail `Res2.gob`. Candidate 07 findings are retained below; final candidate 08 dispositions are recorded after the table. Exact hashes, executable diffs, and original line evidence are in `remaining-cog-delta-matrix.json`.

| COG | Actual upstream change | Candidate 07 disposition |
|---|---|---|
| `weap_raildet` | No executable change between 3.0 and 3.1. Both use selection priority 700 instead of retail 900. | MotS already uses 700 in all four ordinary selection paths. Its native alternate fire and selection behavior remain. |
| `force_push` | Moves bin 30 to 38; introduces costs 30/50/60 based on Jedi level 20; excludes target type flag 8; exempts both Light and Dark Surge from mana consumption. | MotS already uses bin 38. The costs, invulnerability filter, and Light Surge exemption were omitted in candidate 07. Parent has chosen to port them. Native MotS actor/player target scope, rank-dependent range, and force magnitude remain deliberate target-specific choices. |
| `force_saberthrow` | Corrects the active-bin check, selected label, and cleanup from bin 22 to 37. | MotS already uses 37 and native weapon COG bins 125/131/139. Bubble cancellation is retained. |
| `glowcolor` | Caches the local player at startup and adds selected label 55 for the JK inventory relocation. | MotS already has dedicated action bin 116 and all three native weapon dispatches. No color capability is missing. |
| `saberdamage` | Caches the local player at startup and adds selected label 56. Toggle behavior is unchanged. | MotS already has dedicated action bin 144 and dispatches to all three saber COGs. |
| `item_bacta` | Adds a local-player startup cache and selected label 40. Healing and consumption are unchanged. | MotS already heals 30, respects the health cap, consumes a charge, and clears availability when empty. Native source-player events and controls are retained. |
| `item_fieldlight` | Adds startup and selection handlers. Lamp behavior and the 1.5-second battery pulse are unchanged. The item is restored after JK 3.0 repurposed its slot. | MotS already provides the field light in bin 42, with its native controls and battery behavior. |
| `item_irgoggles` | Adds startup/selection handlers and respawn cleanup; changes `EnableIRMode(0.3, 1)` to `(1.0, 1)`. | MotS already has functioning goggles and respawn cleanup, but candidate 07 retains 0.3. Parent has chosen the exact 1.0 enhancement while preserving native controls and drain. |
| `toggletrails` | Adds an inventory dispatcher that sends `user5` to all three sabers and prints selected label 57. | MotS already has the dispatcher at action bin 118. The overlay separately ports immediate steady-blade restoration when the preference changes. |
| `weap_bryar` | The new override changes retail selection priority 500 to 200 only. | MotS already uses 200 and retains its native alternate fire and SBX projectile trigger. |

Additional Push interaction findings:

- `GetItemFlags` is an alias of the shared type-flag getter. For actors and players it returns actor flags; upstream bit 8 means invulnerability. With MotS's actor/player mask, `GetActorFlags(victim) & 8` expresses the same check directly.
- Talisman and native Super Shield use thing flag 4 for magnetic sealing. MotS Push calls `ApplyForce` directly, so the actor's Talisman `SkillTarget` rejection does not protect it. The final implementation uses an explicit player-type/Talisman inventory filter, alongside the actor-invulnerability filter, rather than changing every magnetically sealed actor's behavior.
- The inherited Push loop advances past a rejected target, then can act on the next target without rerunning the complete filter. To make the new exclusions reliable, apply force only inside the eligibility branch and advance exactly once per iteration.
- JK 3.0 and 3.1 both search all thing types; MotS searches actors and players only. Preserving the MotS scope is an explicit compatibility choice and must not be described as complete parity with all JK Push behavior.

These are source and control-flow findings. They do not establish native gameplay or connected multiplayer acceptance.

## Final candidate 08 dispositions

Archive SHA-256: `df5ba92b0391dc46c5da6f5b5e8f9dc14ab3cfe6616f15492afb34125ea9e7d9` (600 members).

All reported patch findings are resolved at source/static-review level. Push now has the upstream 30/50/60 Jedi-level costs, actor invulnerability exclusion, and both Surge exemptions. Its target loop advances once per iteration and applies force only inside the complete filter. A player-type guard precedes the Talisman inventory check, preventing direct native Push from bypassing that protection. Mana is reread for each affected victim. Native MotS actor/player scope, power rank, range, force magnitude, and bubble lifecycle remain.

The goggles enhancement changes only the first `EnableIRMode` argument from 0.3 to 1.0; every other MotS 3.0 byte remains. Object Throw now cancels on EWEB entry during both holding and release. The 178 model variants, static templates, and dual visual scripts are byte-identical to the independently checked candidate 07 versions.

The detailed final review is `candidate08-independent-review.json`. This accepts the reported source patches and static contracts, not native gameplay, connected multiplayer, or the optional software-texture conversion.
