# DeriveBSD-rev0589-2026.06.18.01.41-goldenthread-releasegate-otter review

Generated for version: `2026-06-18r615`

## Mission focus

Substance first: turn the r614 runtime-first cutline into an executable seam before adding more doctrine or registry surface.

## Priority changes

- Added `tools/derive_runtime.py`, a local dry-run CLI for Spec → Lock → Plan → Artifact → Activate → Explain → Rollback.
- Added `tools/check_runtime_golden_thread.py` and promoted it to release-critical hygiene.
- Checked in current evidence under `validation/runtime-golden-thread/current/`.
- Regenerated the r615 release-critical ledger as a complete 52/52 passing example.
- Regenerated stale r615 FreeBSD proof-bundle/work-order surfaces without fabricating real-host proof.
- Refactored `docs/current/runtime-golden-thread.md` so runtime receipts stay executable evidence, not premature schema families.
- Updated the executable fixture to `freebsd-15.1-amd64` so the runtime seam no longer demonstrates against a stale 14.1 target.

## Validation

- release-critical ledger: `52/52` passed; failed `0`; timed out `0`; run_complete `true`.
- schema-cube-audit profile: `3/3` passed.
- Runtime golden-thread run digest: `sha256:6c536edabe37d64f1ae4015bd7a54f6586848ff0f4390967ee9aad1bebff00ac`.

## Still red / not claimed

- Real FreeBSD host proof remains `blocked-no-real-host-proof-import` with proof_complete `false`.
- No `bectl` activation, host mutation, or bhyve launch happened in this cloudtainer.
- The resolver is still an offline fixture resolver, not authoritative package/source resolution.
