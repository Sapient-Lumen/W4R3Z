# Rev0765 handoff

## Authority boundary delivered

Terminal ingress retention now requires canonical-frame reconstruction, strict parent equality, an exact ordered candidate-set commitment, same-transaction audit insertion and exact deletion, and commit-gated result publication. Authority-denial retention has equivalent exact evidence identity.

## Start here

- `../../../../REVISION-NOTES-rev0765.md`
- `../../../../docs/0150-rev0765-canonical-terminal-retention-commit-truth.md`
- `../../../../ARCHITECTURE-AUDIT-rev0765.md`
- `../../../../audit/rev0765-canonical-terminal-retention-audit.json`
- `../../../../.revision-evidence/rev0765/release/validation-summary.json`

## Validation truth

A fresh build and 39/39 CTest pass are retained. The domain and lifecycle suites remain 588/0 and 49/0. The focused retention integration target passes. ASan+UBSan compiled all five changed production objects, but the complete graph did not link or run in the cloudtainer command window; see `SANITIZER-STATUS.json`. Do not restate that as a sanitizer pass.

## Next implementation boundary

Establish exact schema/table/index/trigger identity and a typed migration capability. Then move status/backpressure to a verified canonical projection cache. In parallel, extract selftests/reporting from `sync_domain.cpp` to restore sanitizer/build liveness, and add crash injection around event insert, each exact delete, commit, and restart.
