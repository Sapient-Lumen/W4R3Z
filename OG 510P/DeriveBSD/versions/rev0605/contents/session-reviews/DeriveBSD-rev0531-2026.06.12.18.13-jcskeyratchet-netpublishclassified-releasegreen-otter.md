# DeriveBSD-rev0531-2026.06.12.18.13-jcskeyratchet-netpublishclassified-releasegreen-otter session review

## What changed

- Made the canonical JSON hashing posture executable instead of prose-only. `tools/cube_digest_lib.py` now owns the restricted-JCS/I-JSON digest helper, duplicate-key strict loader, UTF-16 object-member ordering, safe-integer numeric admission, and explicit rejection of floats, NaN/Infinity tokens, lone surrogates, and non-string in-memory object keys.
- Added `tools/check_canonical_json_digest_contract.py` to release-critical hygiene. The check carries sample canonicalization vectors, the RFC-style UTF-16 ordering regression where Python code-point sorting is wrong, negative admission vectors, and a ratchet on legacy local digest helpers.
- Refactored digest users beyond the first representative set: release transparency, keyless identity, content origin, and supplychain verification now use `cube_digest_lib.canonical_digest`. The local-helper ratchet is now 60 files.
- Added `tools/check_net_publish_session_schema_classification.py`, proving `spec/net.publish.session.schema.json` is a const-heavy runtime policy mesh with dynamic session/endpoint/authority/relay/digest fields, not an exact fixture schema needing a split.
- Refreshed `CHANGELOG.md`, `README.md`, `docs/00-index.md`, `docs/80-canonical-json-hashing-jcs.md`, `adrs/ADR-0022-canonical-json-jcs.md`, current hygiene/schema docs, generated docs, and the canonical hygiene ledger example.

## Verification

- Release-critical hygiene ledger: {'failed': 0, 'passed': 36, 'timed_out': 0} across 36/36 checks, run_complete=True, result=passed, check_budget_status=completed-within-check-budget.
- Schema-cube-audit hygiene ledger: {'failed': 0, 'passed': 3, 'timed_out': 0} across 3/3 checks, run_complete=True, result=passed.
- Targeted checks rerun after ledger refresh: consistency, canonical JSON digest contract, net.publish classification, release transparency, keyless identity, content origin, supplychain verification, and bytecode cleanliness.

## Remaining risk

- The canonicalization profile is deliberately restricted. It does not claim arbitrary JSON RFC 8785 JCS number support; hash-bound v1 objects still reject floats and unsafe integers.
- 60 legacy local digest-helper files remain. This cut starts the ratchet rather than trying a dangerous whole-cube rewrite.
- The cloudtainer still cannot replace actual FreeBSD host proof for the removable-media/post-detach worker path.
- The front door is still too large for humans; the budget check prevents runaway but does not create a small operating surface.
