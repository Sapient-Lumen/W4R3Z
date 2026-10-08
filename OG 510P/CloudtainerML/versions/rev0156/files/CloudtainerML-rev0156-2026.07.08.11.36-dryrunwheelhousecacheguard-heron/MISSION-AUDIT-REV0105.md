# Mission audit — REV0105 acceptance-bundle gate

## Risk selected

The riskiest unresolved lane is still the real TinyLlama public trace. The immediate failure mode is now more specific: a future operator may produce an NPZ and provenance JSON that look like a trace but are not complete enough to replay, gate, or evaluate.

## What changed

- Added `tools/public_trace_acceptance_bundle_audit.py`.
- Tightened the public gate's self-attestation and manifest requirements for:
  - local snapshot loader identity versus canonical HF model identity,
  - runtime device/dtype/timing provenance,
  - explicit dynamic-cache generation metadata,
  - prompt/tokenizer replay metadata,
  - generated-token exact-count metadata,
  - score/dense-reference fidelity fields.
- Fixed capture provenance to emit `prompt_token_count_min` and `prompt_token_count_max`, which the gate already expected for public manifest acceptance.
- Wired the new audit into the one-command readiness gate and smoke validator.
- Refactored top-level start guidance around capture + acceptance-bundle validation instead of registry expansion.

## What remains blocked

- No real public TinyLlama trace is captured inside this cloudtainer.
- No complete TinyLlama snapshot/runtime environment is proven here.
- No named-hardware sparse-vs-dense timing exists.
- Promotion remains disabled.

## Why this is forward momentum

REV0105 prevents a costly future false start: a capture that succeeds operationally but fails downstream because the trace artifact is incomplete. The next successful capture should immediately produce a bundle the gate can evaluate, or fail with a precise missing-field report.
