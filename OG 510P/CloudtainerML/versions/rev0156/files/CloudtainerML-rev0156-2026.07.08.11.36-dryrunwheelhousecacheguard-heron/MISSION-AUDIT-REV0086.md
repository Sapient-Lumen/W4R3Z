# Mission audit — rev0086 probability semantics gate

## Heart of this turn

The riskiest unfinished lane is still the real public/pretrained post-transform trace. Rev0086 keeps the work execution-facing by closing another false-green seam in that trace path: dense Q/K/V parity can pass while the bundle stays silent about the probability semantics actually used by the runtime. For a Llama-family public claim, score construction alone is not enough. The trace must say and prove that the runtime path used the expected probability contract: float32 softmax probabilities in eval/no-dropout mode, after the mask/bias and GQA expansion semantics are already fixed.

## What was missing

rev0085 required phase, mask, active-key length, absolute position, and query-head to compact-KV-head ownership. It still left probability semantics underspecified. A forged or sloppy bundle could replay scores with a different probability dtype, or accidentally capture training/dropout semantics, while still shipping a dense reference array that looked plausible. That is especially dangerous because the cube is trying to decide whether sparse attention survives the real attention path, not just whether a serialized tensor file can reproduce itself.

Current Hugging Face Llama eager attention repeats compact K/V heads for grouped-query attention, adds the causal/padding mask to scaled scores, applies `softmax(..., dtype=torch.float32).to(query.dtype)`, then applies dropout only through the runtime dropout setting before the value matmul. The custom attention interface documentation also warns that custom backends need matching mask handling, and the cache documentation distinguishes physical cache storage from active tokens. Together those runtime facts make probability, mask, cache, and KV ownership one contract rather than separable paperwork.

## What changed

- Public trace claim version advanced to `public_trace_claim_v8`.
- New public probability contract: `float32_softmax_no_dropout_v1`.
- Capture exports `probability_contract`, `probability_semantics_verified`, `attention_probability_dtype`, `attention_dropout_p`, `attention_training_state`, and `dropout_applied` into both NPZ and provenance JSON.
- The gate rejects bundles that omit the probability contract, claim non-float32 probability dtype, or indicate train/dropout semantics, even if the dense attention output otherwise matches.
- New `tools/public_trace_probability_semantics_audit.py` builds a prefill+cached-decode fixture and proves the good bundle passes while the probability-label negative controls are rejected.
- Readiness and run handoff now include the probability semantics audit and generate the rev-specific cache preflight script.

## What remains blocked

This is still non-promotional. There is no accepted public checkpoint trace in the capsule, no local immutable cached Llama snapshot available here, no `transformers` dependency available in this validation environment, and no named-hardware fused/end-to-end sparse-vs-dense timing. The next valuable execution step remains: run the cache preflight/capture script against an immutable public/pretrained Llama-family checkpoint with positive cached-decode steps, then run the public gate and move directly to named-hardware timing if the trace passes.

## Waste corrected

The corrected waste is a common ML-evidence trap: accumulating more tensor files and status records while leaving an implicit numerical/runtime assumption unguarded. Rev0086 converts that assumption into an executable veto. The cube can now reject a dense-parity-compatible trace that silently used the wrong probability path, which is more valuable than another registry cleanup.
