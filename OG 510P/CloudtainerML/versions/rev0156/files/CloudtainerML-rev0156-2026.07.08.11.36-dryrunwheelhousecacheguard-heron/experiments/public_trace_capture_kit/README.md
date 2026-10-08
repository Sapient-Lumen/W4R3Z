# Frozen rev0074 public trace capture kit

This directory is retained as historical evidence for the rev0074 capture-kit dry run. Its runner is pinned to `rev0074` so it cannot silently inherit a later `CUBE-META.json` revision and mint a current-labelled artifact.

Do **not** use its generated `public_trace_claim_v1` schema or projection-hook command as the current public-evidence path. The current rev0076 contract is:

1. capture verified post-model-transform Q/K/V rather than raw projection outputs;
2. record exact attention scale, score bias/mask, and supported score transform;
3. include a dense reference output that the gate recomputes;
4. pin immutable model, tokenizer, and trusted-code revisions; and
5. validate with `public_trace_gate_surrogate.py` and the rev0076 acceptance preflight.

Historical reruns should occur only in a scratch copy and must not overwrite retained rev0074 artifacts.
