---
status: audit
claim_kind: source_governance
route_role: source_governance_core
canonical_anchor: false
route_refs:
- source_governance_core
- case_calibration_core
- remedy_operability_core
supersedes: rev0320
depends_on:
- ../../SOURCES.json
- source-use-register.json
- ../../cases/EVIDENCE_LEDGER.json
source_refresh_due: 2027-03-31
---

# Source ledger audit — rev0355

rev0320 turned the source ledger into an evidence graph. rev0321 preserves that graph and adds S402-S413 for remedy-operability cases.

## Current state

- Source count: 413.
- Case count: 88.
- Scoreboard count: 88.
- Schema field count: 326.

## New evidence pressure

The remedy-operability cases deliberately mix official sources and advocacy/legal-context sources. Official sources establish processing time, program-integrity pressure, identity-guidance, and legal authority. Advocacy/context sources help identify claimant-side enforcement failure modes that official data often do not measure directly.

## Remaining source debt

The next source-governance improvement should add direct claimant-outcome datasets for appeal delay, identity-proofing false negatives, manual-review latency, arbitration abandonment, and restoration after wrongful denial.
