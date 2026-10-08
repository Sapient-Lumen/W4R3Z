# Public trace acceptance preflight — rev0076

This is a fail-closed guardrail suite for future public/pretrained trace bundles. It is not public-model evidence.

The 16 adversarial cases cover post-transform tensor-stage requirements, explicit attention scale and score bias, supported score transforms, gate-recomputed dense-reference parity, forged/missing references, immutable model/tokenizer/trusted-code revisions, Q/K/V aliases, actual `d_head` accounting, score-only metadata requirements, non-finite arrays, and malformed shapes.

Run:

```bash
python experiments/public_trace_acceptance_preflight/public_trace_acceptance_preflight.py
python tools/public_trace_acceptance_preflight_audit.py
```

Use `experiments/public_trace_capture/hf_attention_trace_capture.py` only as a diagnostic producer until an architecture-aware adapter verifies post-transform score inputs and exact runtime parity. The frozen rev0072–rev0074 public-trace runners are historical controls, not the current capture path.
