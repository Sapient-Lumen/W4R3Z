# Public trace capture — current path for rev0097

This directory contains the Hugging Face attention-trace capture helper, but operators should not call it first. The current public TinyLlama lane is gated by:

```bash
python tools/public_trace_readiness_gate.py --local-only
```

After source/license review in an environment allowed to download the locked snapshot:

```bash
ALLOW_DOWNLOAD=1 python tools/public_trace_readiness_gate.py --download --strict
ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

The readiness gate composes source lock, run-packet validation, environment preflight, Transformers/Llama eager-attention surface probing, exact HF snapshot materialization, capture-source checks, and active-surface checks. This README used to describe an older rev0049 local helper; rev0097 refactors it so it no longer bypasses the current stop/go path.

Direct helper invocation remains for debugging only. Public acceptance still requires post-transform Q/K/V, prompt and generated-token digests, exact greedy cached-decode length, mask/active-key/position/KV-group/RoPE/probability contracts, dense parity, immutable model/tokenizer revisions, and named-hardware timing before promotion.
