# Structural audit rev0323

Rev0323 moves the Beaver Valley emergency-preparedness branch from escrow intent to packet-import mechanics.

## Concrete correction

The package had a metadata defect: `cube/schema.json` in rev0322 still described rev0321. Rev0323 fixes the schema revision, latest file, scoped SQLite mirror, and adds a validation check so this does not silently recur.

## Query route after rev0323

`public/source clock → escrow slot → field packet template → packet manifest → validator → adjudication board → CAP/retest/verifier → public claim gate`

The old universal nuclear crossproduct tables remain compatibility artifacts. They are not local evidence and are not allowed to close emergency-readiness claims.

## Open risk

No real/anonymized June 2026 exercise packet has been imported. The most important next action is to load actual alert, decision, message, evaluator, CAP/retest, EN58200, and public-meeting packets through the rev0323 validator.
