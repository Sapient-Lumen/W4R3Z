# rev0341 — strict positive evidence proof gate promotion refactor

Generated: 2026-06-18T22:06:00Z.

## What changed

The riskiest unfinished path was not another doctrine registry. It was the positive evidence path: rev0340 proved signature verification and adapter binding, but the smoke bundle was narrow and did not exercise the strict model-input source or authority-source proof gates.

rev0341 expands the sandbox positive path to the full GC-001 default selected route set. The smoke bundle now verifies 22 adapter-bound evidence records: 5 records that require strict model-input source proof and 17 records that require strict authority evidence/source proof.

The replay ledger now records strict gate flags and proof hashes (`input_source_record_hash`, `input_source_manifest_hash`, `authority_evidence_record_hash`, `authority_source_record_hash`, and `authority_source_manifest_hash`) in the truth boundary. Promotion independently re-checks those fields for the relevant adapter classes instead of relying on a broad external-attestation label.

The smoke key is now deterministic and explicitly public/test-vector only. That removes hidden random drift from the harness without turning the test key into a production trust root.

## Audit/refactor surface

- `tools/build_signed_external_evidence_smoke_bundle.py` now builds strict sandbox evidence for the full default route set.
- `tools/build_evidence_replay_ledger.py` binds strict proof hashes and gate flags into replay records and summaries.
- `tools/promote_decision_release.py` requires strict proof gates for model/floor/no-go and current-law/jurisdiction adapter classes before promotion mechanics can pass.
- `tools/audit_positive_external_evidence_path.py` verifies the full strict sandbox path and separately proves that non-default route-limit bundles remain blocked outside sandbox mode.
- `tools/audit_evidence_replay_ledger.py` and `tools/audit_decision_promotion_gate.py` now audit the strict proof counts and truth-boundary fields.

## Boundary kept

This is still not a production finalization path. The signed GC-001 bundle is a sandbox proof of mechanics, not a claim that its legal, jurisdictional, quantitative, delivery, or no-go facts are true in the world. The built-in release scope remains held unless production external evidence is ingested through trusted roots and valid scope-wide attestations.

## Validation facts

- Positive external evidence path: 22/22 adapter records verified.
- Strict model-input source proofs: 5/5.
- Strict authority evidence/source proofs: 17/17.
- Built-in replay strict model-input proof records: 0/859.
- Built-in replay strict authority proof records: 0/865.
- Production promoted built-in cases: 0.
- Built-in held cases: 122.

## Remaining highest-risk gap

The next substantive step is a real external evidence ingress package: production trust roots, key rotation, revocation, transparency inclusion checks, and at least one non-sandbox evidence bundle whose source, producer, verifier, and effective-date claims can be checked without relying on archive-generated facts.
