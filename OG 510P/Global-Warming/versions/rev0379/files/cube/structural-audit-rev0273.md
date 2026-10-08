# Structural audit — rev0273

## Purpose

rev0273 audits the archive after the recovery-rail revision and adds the bad-day operating layer: scarcity priority, mutual aid, critical spares, maintenance debt, behavioral health, civic continuity, reentry access, and compound scenario loadcases.

## Findings repaired

- The older numbered canon still lacked external front matter. rev0273 backfills machine-readable front matter across all numbered markdown files.
- File `152` had a non-standard H1 (`152.` instead of `152 —`). rev0273 normalizes it.
- The cube schema lacked fields for priority, scarcity, mutual aid, inventory posture, maintenance state, civic legitimacy, and scenario loadcases. rev0273 adds them.

## New structural tests

A service floor now needs to answer:

1. What scarce resource limits it?
2. Who receives scarce restoration first?
3. What mutual-aid path exists if local capacity is exhausted?
4. Which critical spares and consumables determine restoration time?
5. What baseline maintenance debt could make the shock worse?
6. What behavioral-health or psychosocial recovery path is required?
7. What civic or election-continuity obligation is implicated?
8. What reentry or credentialing path could block care, repair, or resident return?
9. Which compound loadcase has actually been tested?

---
Citations point to `sources/register.md`.
