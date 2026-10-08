# rev0342 — decision review bundle handoff promotion refactor

Generated: 2026-06-18T22:47:00Z.

## What changed

The riskiest unfinished surface was no longer the cryptographic happy path itself. Rev0341 could verify adapter-bound signatures and strict proof hashes, but it did not give a reviewer a bounded handoff artifact that could be independently re-checked without looking like final public advice.

rev0342 adds a decision review bundle exporter. The exporter builds one bounded GC-001 sandbox packet containing the public trust-store view, producer contracts, full evidence payloads needed for hash recomputation, external attestations, verifier packets, replay hashes, promotion summaries, held decision-output status, and a checklist of reviewer actions.

The bundle is deliberately non-certifying: `production_finalization_allowed=false`, `promotion_mode=sandbox_positive_path_test`, and the embedded decision output remains held even when every verifier/replay/proof gate passes. It is a handoff artifact, not a policy determination.

## Audit/refactor surface

- `tools/export_decision_review_bundle.py` creates a reviewable, hash-bound handoff packet for a signed evidence candidate.
- `tools/audit_decision_review_bundle.py` independently re-verifies each embedded evidence payload and attestation from the exported packet, checks that no private key material is exported, proves tampering breaks verification, exercises the CLI serialization path, and binds the result into `cube-index.json`.
- `tools/run_semantic_audits.py` now includes the review-bundle handoff audit in the truth-boundary group.
- `tools/build_signed_external_evidence_smoke_bundle.py` was refreshed to rev0342 naming so the active smoke producer, contract, key id, and locators no longer carry stale revision labels.

## Boundary kept

The review bundle intentionally includes enough sandbox evidence payload material for independent verification, but it still carries no production trust root, no transparency-log inclusion proof, no live-law retrieval, and no empirical model truth. It exists to make the positive path reviewable without crossing into finalization.

## Validation facts

- Decision review bundle runtime status: `decision_review_bundle_exported`.
- Review case: GC-001.
- Review adapter records: 22.
- Embedded attestations verified: 22/22.
- Strict model-input source proofs: 5/5.
- Strict authority evidence/source proofs: 17/17.
- Replay mismatches: 0.
- Finalized cases inside review bundle: 0.
- Sandbox positive-path cases inside review bundle: 1.
- Private key material exported: no.

## Remaining highest-risk gap

The next substantive step is production evidence ingress rather than more doctrine: a real trust-root configuration, key rotation/revocation material, transparency inclusion verification, and a small externally supplied non-sandbox evidence bundle that can be reviewed with the same handoff format.
