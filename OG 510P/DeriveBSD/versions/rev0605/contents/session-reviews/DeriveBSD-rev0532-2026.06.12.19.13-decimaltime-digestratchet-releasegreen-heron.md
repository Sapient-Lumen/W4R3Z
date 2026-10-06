# DeriveBSD-rev0532-2026.06.12.19.13-decimaltime-digestratchet-releasegreen-heron session review

## What changed

- Fixed a real canonical-digest defect found during refactor: hash-bound `time.sync.snapshot`, `time.sync.receipt`, and `time.event` examples no longer carry JSON floating-point millisecond measurements. Their schemas now use decimal strings for hash-bound millisecond values.
- Recomputed the dependent `spec/examples/incident.bundle.json` time-sync snapshot/receipt digests after the time-evidence encoding change.
- Refactored a substantial checker cluster onto `tools/cube_digest_lib.py`: attestation, breakglass, lease, reset, support-session, time-sync, trust-bundle, UEFI, and related bundle/contract checks now use shared restricted-JCS digest helpers instead of local sorted-JSON helpers.
- Ratcheted `tools/check_canonical_json_digest_contract.py` from 60 remaining legacy local digest-helper checker files to 26, and added no-float assertions for the hash-bound time evidence examples and schemas.
- Refreshed r563 docs, generated docs, generated schema/checkset examples, and the canonical hygiene ledger example while keeping `docs/00-index.md` within its existing front-door line budget.

## Verification

- Release-critical hygiene ledger: {'failed': 0, 'passed': 36, 'timed_out': 0} across 36/36 checks, run_complete=True, result=passed, check_budget_status=not-enforced.
- Schema-cube-audit hygiene ledger: {'failed': 0, 'passed': 3, 'timed_out': 0} across 3/3 checks, run_complete=True, result=passed.
- Targeted reruns included canonical JSON digest contract, time-sync bundle, time degraded-response boundary, schema lint/example validation, generated-doc/artifact version checks, front-door budget, breakglass resumption joins, and the refactored attestation/breakglass/lease/reset/support/time-sync/trust/UEFI digest check cluster.

## Remaining risk

- The cloudtainer still cannot provide the missing real FreeBSD host-smoke proof for the removable-media/post-detach Capsicum worker path.
- `derivebsd-jcs-ijson-no-float-v1` intentionally remains a restricted profile; it still does not claim full arbitrary-number RFC 8785 JCS support.
- 26 local digest-helper checker files remain after this cut; continue reducing them in small, validated clusters.
- The front door remains heavy. This cut avoided worsening the line budget, but a future pass should delete/condense older sediment rather than only fitting inside the ratchet.
