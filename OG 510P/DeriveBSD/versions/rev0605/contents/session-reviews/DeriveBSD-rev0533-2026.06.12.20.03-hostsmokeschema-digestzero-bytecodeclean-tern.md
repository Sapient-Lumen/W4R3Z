# DeriveBSD rev0533 risk-first audit

Revision target: `DeriveBSD-rev0533-2026.06.12.20.03-hostsmokeschema-digestzero-bytecodeclean-tern.zip`

## What changed

- Added `spec/removable.media.local.freebsd.host.smoke.receipt.schema.json` and `spec/examples/removable.media.local.freebsd.host.smoke.receipt.json` so the FreeBSD host-smoke seam has a schema-backed acceptance surface instead of only prose and runner simulations.
- Extended `tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py` so it verifies the host-smoke receipt schema surface while remaining runnable under `python3 -B -S`.
- Completed the digest-helper ratchet: remaining local sorted-JSON digest helpers in checker files were refactored onto `tools/cube_digest_lib.py`, and `tools/check_canonical_json_digest_contract.py` now allows zero legacy local helper files.
- Fixed a stale removable-media local-ingest digest in `spec/examples/devfs.view.plan.removable-media-local-ingest.json` that surfaced during the digest refactor.
- Repaired the workstation stale-supersession recovery front-door tokens in `README.md` so the guard is reachable from release-critical hygiene.
- Rebuilt generated schema audit, backlog, hygiene manifest, and hygiene ledger examples for `2026-06-12r564`.
- Treated Python bytecode as a packaging defect: rev0532 extracted with `tools/__pycache__` artifacts, so this revision removes them and must be packaged without transient bytecode.

## Validation notes

Targeted checks passed for the canonical JSON digest contract, FreeBSD host-smoke runner, removable-media local-ingest first cut, workstation stale-supersession recovery, schema lint, and example validation. Release-critical and schema-cube-audit ledgers are stored next to this review after the final profile runs.

## Still open

The host-smoke surface is now schema-backed and checker-enforced, but it is still not a substitute for a real FreeBSD host run. The next highest-risk external proof remains an actual non-simulated FreeBSD receipt proving kernel/userland identity, Capsicum availability, copied worker source compilation, disposable mount/device behavior, fd-only execution, and transcript capture.
