---
status: program_spec
claim_kind: evidence_governance
route_role: source_governance_core
canonical_anchor: false
route_refs:
- source_governance_core
- certification_core
- case_calibration_core
supersedes: null
depends_on:
- ../../SOURCES.json
- ../../cases/EVIDENCE_LEDGER.json
- ../00-meta/source-use-register.json
source_refresh_due: 2027-03-31
---

# Evidence-claim binding and refresh cadence — rev0355

## Rule

A source citation is not enough. A cube claim is evidence-bound only when the source is attached to a specific field, gate, exposure, or waterfall item in a scoreboard and then appears in `cases/EVIDENCE_LEDGER.json`.[S345]

## Evidence-quality levels

- `direct`: the source directly measures or legally defines the claim.
- `proxy`: the source measures a nearby condition and the inference is modest.
- `inference`: the source supports the frame but not the full claim.
- `missing`: the claim is held open as proof debt.

A comfort verdict cannot depend on a `missing` evidence edge. A blocked or watch verdict may depend on missing evidence only when the missing evidence is itself the reason certification cannot pass.

## Refresh cadence

- annual for official statistical releases, fiscal updates, public-balance-sheet reports, tax-expenditure estimates, and financial-stability registers;
- six-month review for fast-moving market structures such as stablecoins, private credit, AI load growth, and residual insurance;
- event-triggered review for hospital closures, bankruptcy, disaster-loss events, systemic backstops, or large subsidy/loan commitments.

## Source-ledger duty

`SOURCES.json` must carry `used_by_cases` and `used_by_fields`. These are generated from scoreboards in rev0320; they are not decorative bibliography fields.

## Closeout rule

Proof debt closes only when the missing edge is replaced with a direct or adequately stated proxy edge and the affected scoreboard field, evidence-debt register, and case memo are updated together.

## rev0321 carry-forward

rev0321 keeps this evidence-binding protocol active and routes it through the canonical route registry/source-governance layer.
