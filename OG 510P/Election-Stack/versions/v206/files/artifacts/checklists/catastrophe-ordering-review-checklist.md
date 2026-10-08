# Catastrophe ordering review checklist (C1..C5)

Use this checklist when proposing a protocol/tooling change, adding a new public surface, or changing UX.
It keeps the archive’s priority ordering explicit and prevents “availability-first” instincts from silently
increasing worst-case outcome risk.

Reference: `artifacts/registries/catastrophe-classes.csv`.

## 1) Classify the *worst credible* failure
- ☐ If this change fails under active attack, what is the worst credible catastrophe class it enables (C1..C5)?
- ☐ Did we accidentally trade a loud failure (C4) for silent manipulation or ecosystem capture (C1/C2)?

## 2) C1 — Silent outcome manipulation
- ☐ Does any new trust or discretion point allow outcome-affecting changes without a portable proof of misbehavior?
- ☐ Is there an explicit evidence object that would be produced when the change fails (fork proof, drift proof, mismatch proof)?

## 3) C2 — Verification-ecosystem capture
- ☐ Does the change rely on a single monitor cohort, vendor, or channel (monoculture risk)?
- ☐ If the adversary shapes routing/cohorts (docs `127–130`), do we still have detectable anomalies (coverage reports, beacons, path correlation)?

## 4) C3 — Irrecoverable ambiguity
- ☐ Are we creating states where observers can no longer determine what happened (missing receipts, missing manifests, unverifiable “confirmed” UX)?
- ☐ Are deadlines/PublicationContract triggers updated so “missingness” becomes portable (suppression reports + beacons)?

## 5) C4/C5 — Loud failure and non-lying UX
- ☐ On failure, do user-facing and public-facing surfaces fail *loudly* (NOT RECORDED / “evidence unavailable”) rather than implying success?
- ☐ Are any caches, retries, or fallback mirrors constrained so they cannot mask evidence loss or serve stale “success” states?

## 6) Register updates (minimum)
- ☐ If the change introduces a new failure mode: add/update hazards in `artifacts/hazards/hazard-register.csv` (including CatastropheClass).
- ☐ If the change affects response: add/update drills in `artifacts/registries/drill-scenarios.csv` and/or a checklist/playbook.
