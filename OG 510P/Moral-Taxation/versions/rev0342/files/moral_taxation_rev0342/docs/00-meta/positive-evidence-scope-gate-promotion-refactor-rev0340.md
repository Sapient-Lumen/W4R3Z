# Rev0340 — positive evidence scope gate promotion refactor

Rev0340 addresses the riskiest unfinished edge left by rev0339: the system had strong negative gates, but no honest positive-path proof that signed, adapter-bound, externally shaped evidence could travel through execution, replay, and promotion without being confused for final public advice.

## What changed

- Added `tools/build_signed_external_evidence_smoke_bundle.py`, a bounded signed evidence-bundle generator for verifier/replay/promotion smoke tests.
- Added `tools/audit_positive_external_evidence_path.py`, which proves the positive path over GC-001 with a route limit of 1 and two adapter records.
- Refactored replay ledgers to record promotion mode, route-selection summaries, and non-default route-limit counts.
- Refactored promotion so sandbox positive-path success is separate from final promotion.
- Added a production-scope gate: a non-default route-limit ledger cannot promote outside sandbox mode.
- Removed duplicate replay/promotion lookup lines left by the rev0339 refactor.

## Boundary kept intact

The new smoke bundle uses real Ed25519 signatures, a trust store, adapter-binding hashes, replay comparison, producer contract checks, and promotion truth-boundary checks. It is still not production evidence. Its execution context is explicitly `sandbox_positive_path_test`, and the promotion packet reports:

- final promoted cases: `0`;
- sandbox positive-path cases: `1`;
- held cases inside the smoke scope: `0`.

That proves the mechanics without turning generated evidence into current law, jurisdiction clearance, model truth, or final advice.

## Risk reduced

Before this revision, a future implementer could test only failures and still leave the first real positive evidence bundle unexercised. Worse, a route-limited run could be mistaken for full finality. Rev0340 closes both gaps: the positive path is executable, and non-default route-limit promotion is blocked unless it is explicitly marked as sandbox-only.

## Still missing

The production ingress is still missing. A real deployment needs stable trust roots, key rotation, revocation distribution, transparency-log inclusion verification, external observation provenance, and full active-scope evidence coverage. Rev0340 intentionally does not claim those guarantees.
