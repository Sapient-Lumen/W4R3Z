# Kernel interface contract 0: Safety-Critical Readiness Cards

## Identity
- candidate: **Safety-Critical + Institutional Readiness Commons**
- governing kernel: `kernels/top-band-v0/safety-critical-readiness-cards.v0.md`
- governing slice: `slices/top-band-v0/safety-critical-readiness-cards.slice0.md`
- current verdict context: `deepen`
- contract codename: `safety-critical-readiness-cards/contract0`

## Contract scope
Fix the first explicit surface for **lintable readiness cards, readiness packs, and readiness diffs**.
This contract is for evidence-bearing decision support, not for certification claims.

## Public surfaces
### Commands
1. `readiness lint --cards <glob> --out <lint.json>`
2. `readiness pack --cards <glob> --subject <id> --out <pack.json|pack.md>`
3. `readiness diff --left <pack.json> --right <pack.json> --out <diff.json|diff.md>`

### Rendered/operator surfaces
- one readiness card per subject or evidence class
- one readiness pack for a bounded decision
- one lint report
- one readiness diff
- one stale-card or unsupported-state receipt when evidence is missing or outdated

## Required inputs
- card files with stable identity
- owner / steward identity
- freshness date
- evidence links
- blockers / caveats
- explicit “does not prove” clauses
- optional illustrative adopter receipts clearly marked as illustrative only

## Emitted artifact families
- `readiness-card/v0`
- `readiness-pack/v0`
- `readiness-lint-report/v0`
- `readiness-diff/v0`
- `stale-card-receipt/v0`
- `unsupported-state-receipt/v0`

Minimum readiness-card fields should include:
- subject id and scope
- target family or evidence family
- owner / steward
- freshness date
- evidence links
- known blockers
- current readiness posture
- “does not prove” clause
- review / renewal trigger

## Stable imports
Allowed stable imports:
- official Rust references for targets and project posture
- steward-authored playbooks and evidence notes
- explicit evidence links carried by the card itself

## Optional experimental imports
Allowed but caveated imports:
- illustrative adopter receipts
- draft async-runtime requirements sketches
- evolving consortium or standards notes not yet treated as settled proof

Rule: illustrative adopter evidence must never be upgraded into universal readiness proof.

## Versioning and compatibility posture
- `contract0` is card-additive.
- Unknown evidence blocks must not break readers.
- Missing required owner/freshness/evidence fields must fail lint.
- Rendered markdown may vary, but the underlying card/pack fields must remain machine-diffable.

## Negative states / receipts
The contract must preserve receipts for:
- stale cards
- missing owner or steward
- missing evidence links
- scope drift beyond supported proof
- packs that bundle illustrative adopter examples as if they were universal validation

## Proving-ground invocation
A valid proving-ground run should include:
1. one narrow target-family card;
2. one dependency-lifecycle playbook card;
3. one FFI / interop evidence recipe card;
4. one readiness diff that changes risk posture between two pack versions.

## Refused expansions
Do **not** treat `contract0` as permission for:
- certification badges,
- universal readiness claims across all criticality levels,
- tool-first qualification workflows,
- or large portal/search experiences.

## Exit criteria
This contract may widen only after:
- a small steward group can renew cards on schedule,
- at least one real institutional decision uses a readiness pack,
- and “does not prove” clauses remain visible instead of being polished away.
