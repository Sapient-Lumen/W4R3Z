# Mission audit — REV0108

Status: `pass_with_blockers`  
Promotion allowed: `false`  
Public/pretrained trace loaded: `false`  
GPU fused-kernel timing measured: `false`

## What changed

REV0108 closes a handoff/evidence-integrity hole at the end of the public trace lane. REV0107 made selector entry depend on an evaluation receipt, but the receipt still risked being treated as a path-bound ticket: if files were moved, renamed, or copied without the matching evidence, a later operator could misread the receipt. This revision turns the receipt into a content-addressed subject set and makes selector entry verify actual file hashes at evaluation time.

## Why this is riskiest now

The capture lane is already heavily gated: immutable model/tokenizer revision, prompt/token digests, generated-token count, eager backend, dynamic cache, local snapshot identity, device/dtype/timing provenance, acceptance-bundle completeness, verdicting, and receipt emission. The remaining endgame risk is not another doctrine rule; it is a brittle handoff where evidence is moved between machines, directories, or archives. REV0108 makes that movement safe only when the actual NPZ/provenance bytes match the receipt digests.

## Concrete changes

- `tools/public_trace_evaluation_verdict_audit.py` now emits `public_trace_evaluation_receipt_v2` with `evidence_subjects`, `evidence_subject_set_sha256`, and `receipt_identity_errors`.
- `tools/public_trace_selector_entry_gate.py` now accepts optional `--trace-npz` and `--provenance-json` overrides and verifies actual file hashes against the receipt before opening selector/cost evaluation.
- `tools/public_trace_receipt_relocation_audit.py` proves the positive and negative cases: matching relocated files pass, tampered relocated files fail, and old v1/missing-subject receipts fail.
- `tools/revision_metadata_coherence_audit.py` and `tools/smoke_validate.py` now reject stale nested `counts.revision_number`, fixing the rev0107 defect where top-level metadata was current but a nested counter still said 106.
- Current launch wrappers now route through REV0108 and pass explicit NPZ/provenance paths into the selector-entry gate.

## Online research basis

- SLSA provenance treats provenance as an attestation about produced artifacts and their build context, so the receipt should bind to artifact digests instead of path names.
- in-toto attestation statements bind predicate metadata to subject artifacts, and link predicates use ResourceDescriptor-style names/digests. REV0108 mirrors this with semantic subject names and SHA-256 digests.
- PyTorch reproducibility guidance warns that reproducibility can vary across releases, platforms, and devices; receipt-bound tool/evidence hashes are therefore more valuable than prose lineage.

## Remaining blockers

- The real public TinyLlama NPZ/provenance pair is still absent in this cloudtainer.
- Selector/cost evaluation remains blocked until a v2 receipt accepts the bundle and the actual NPZ/provenance files match the receipt digests.
- Promotion remains blocked until named-hardware sparse-vs-dense timing exists.
