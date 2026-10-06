# Cube audit rev0035 — admission-history integration

Current revision: rev0055

Rev0035 adds `StorageLaneAdmissionHistoryRunner`, a proof, and a contract audit. The audit/refactor focus was to keep admission history separate from retry-budget admission and circuit-breaker/bulkhead gates, while carrying forward provider-resilience model boundaries.

## Audit outcomes

- The new source is fake-provider and release-tier.
- Broad release remains browser-light.
- Future-session docs now name the new admission-history proof and its non-claims.
- The research registry has a new admission/overload family.
- `check_cube.py` now guards rev0035 storage-lane admission-history surfaces instead of only rev0035 provider-resilience model surfaces.

## Watch list

- The cube is growing; keep proof slices cheap and manifest-addressable.
- Admission history needs a model walk before OPFS spending.
- Provider-resilience model proofs remain earned but are not production resilience claims.
