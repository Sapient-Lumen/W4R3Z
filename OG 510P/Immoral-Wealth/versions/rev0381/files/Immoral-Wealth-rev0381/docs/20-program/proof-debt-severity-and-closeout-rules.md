---
status: program_spec
claim_kind: evidence_governance
route_role: certification_core
canonical_anchor: false
route_refs:
- certification_core
- source_governance_core
supersedes: null
depends_on:
- evidence-claim-binding-and-refresh-cadence.md
- ../../cases/EVIDENCE_LEDGER.json
source_refresh_due: 2027-03-31
---

# Proof-debt severity and closeout rules — rev0355

## Severity ladder

`low` proof debt is useful refinement. It cannot reverse a verdict by itself.

`medium` proof debt can change field readings, but the current verdict can stand if the evidence gap is disclosed.

`high` proof debt blocks comfort certification and requires a concrete next-evidence lane.

`blocking` proof debt means the case cannot move beyond seed/provisional or emergency/watch status until the missing evidence is produced or the doctrine is narrowed.

## Closeout checklist

A proof-debt item is closed only when:

1. the evidence source is in `SOURCES.json` with date, accessed, type, role, and refresh due;
2. the source appears in the relevant scoreboard object as `source_ids`;
3. the source edge appears in `cases/EVIDENCE_LEDGER.json`;
4. the case memo states how the evidence changed the field, gate, or waterfall; and
5. any prior `missing` reading is changed or explicitly retained with a narrower reason.

## Gate 20 special rule

For public-balance-sheet cases, high or blocking proof debt must name the missing waterfall: claimant perimeter, maximum exposure, expected loss, stress scenario, funding source, loss sharing, public upside, ordinary-claimant protection, or sunset/review.[S357][S358][S400]

## rev0321 carry-forward

rev0321 keeps these proof-debt closeout rules active and extends them to remedy-operability proof debt: delay, lockout, claim abandonment, collective-redress loss, and restoration failure.
