# Runtime research notes — REV0081 mask-fidelity capture

## Finding 1 — custom attention backends can lose masks

Source: https://huggingface.co/docs/transformers/en/attention_interface

Hugging Face documents that a custom `attn_implementation` name should have a matching `AttentionMaskInterface` registration. If it does not, Transformers can skip mask creation and pass `attention_mask=None` to attention layers. For CloudtainerML, this means a custom capture backend could accidentally validate unmasked causal semantics.

## Finding 2 — Llama eager attention is the right score-input seam only if mask semantics are preserved

Source: https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama/modeling_llama.py

Current Llama code applies rotary position embeddings to query/key before dispatching through the attention interface. Eager attention then repeats KV heads, computes scaled QK scores, adds the attention mask, softmaxes, and multiplies by V. This is the seam CloudtainerML needs, but only with the original mask formatter preserved.

## Finding 3 — public issue pressure confirms the seam is not theoretical

Source: https://github.com/huggingface/transformers/issues/40362

A Hugging Face issue reports changed Llama behavior when registering a custom AttentionInterface backend. The cube should not bet a public/pretrained claim on that seam. rev0081 therefore avoids new backend registration and temporarily overrides built-in `eager` instead.

## Change driven by research

- Stop using `cloudtainer_trace_eager` as a custom backend.
- Temporarily override built-in `eager` and restore it after capture.
- Require `attention_mask_backend_preserved=true` and `custom_attention_backend_used=false` in public trace provenance.
- Require `mask_challenge_exercised=true` from at least one causal/padding mask row.
- Serialize causal `-inf` mask entries as a finite negative sentinel so the NPZ remains portable while preserving softmax semantics.

## Remaining execution blocker

The research/refactor removes a false-positive path, but it does not create public evidence. The next real step is still a captured immutable public Llama-family checkpoint and named-hardware timing.
