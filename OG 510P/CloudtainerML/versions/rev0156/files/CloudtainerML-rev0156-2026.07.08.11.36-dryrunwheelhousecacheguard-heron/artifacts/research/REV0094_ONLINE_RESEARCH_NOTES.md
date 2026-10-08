# Online research notes — REV0094

Generated: 2026-07-06T11:23:00Z  
Purpose: support the risk-first trace/timing lane. These notes are not promotion evidence.

## Target checkpoint choice

The current risk is not knowing whether the public-trace capture can run against an immutable real checkpoint. rev0094 therefore chooses one concrete target instead of leaving the next turn with a generic `MODEL_ID` placeholder:

- `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- full observed Hugging Face commit: `fe8a4ea1ffedaf415f4da2f062534de366a451e6`
- reviewed license label from the model tree: `apache-2.0`
- source URL: `https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/tree/fe8a4ea1ffedaf415f4da2f062534de366a451e6`

A 1.1B Llama-family checkpoint is a practical trace target because it should exercise Llama-style RoPE/KV/cache/mask behavior without requiring a very large hardware footprint just to generate trace rows. It is not chosen as a performance baseline.

## External findings that change the work plan

1. Hugging Face generation/cache docs distinguish token-count controls, cache implementations, `use_cache`, greedy decoding, beam count, and output sequence count. The rev0094 run packet therefore requires exact generated-token accounting, `num_beams=1`, `num_return_sequences=1`, `do_sample=false`, and cache use.
   - https://huggingface.co/docs/transformers/en/main_classes/text_generation
   - https://huggingface.co/docs/transformers/en/cache_explanation

2. Hugging Face attention backends and mask construction are configurable. The capture lane must use or prove semantic equivalence to the backend/mask implementation; otherwise `attention_mask=None` or backend-specific 4D mask changes can silently invalidate the trace.
   - https://huggingface.co/docs/transformers/en/attention_interface

3. PyTorch SDPA/Flash/Flex/PagedAttention work makes the timing lane harder, not easier. IO, cache layout, mask/block construction, kernel choice, and value-path traffic are part of the claim. A sparse trace replay does not imply an end-to-end speedup.
   - https://docs.pytorch.org/docs/2.12/generated/torch.nn.functional.scaled_dot_product_attention.html
   - https://pytorch.org/blog/flexattention/
   - https://pytorch.org/blog/flexattention-for-inference/
   - https://docs.vllm.ai/en/latest/design/paged_attention.html
   - https://arxiv.org/abs/2205.14135
   - https://arxiv.org/abs/2307.08691
   - https://arxiv.org/abs/2309.06180

## Resulting policy

No further doctrine-only trace gate should be added unless it catches a newly discovered source defect. The next material step is:

```bash
ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/REV0094_RUN_TINYLLAMA_PUBLIC_TRACE.sh
```

Run it only in an environment where download/source/license review is acceptable, `transformers` is installed, and the model/tokenizer revisions can be pinned. After accepted trace capture, move immediately to named-hardware timing against SDPA/Flash/Flex/Paged-style baselines.
