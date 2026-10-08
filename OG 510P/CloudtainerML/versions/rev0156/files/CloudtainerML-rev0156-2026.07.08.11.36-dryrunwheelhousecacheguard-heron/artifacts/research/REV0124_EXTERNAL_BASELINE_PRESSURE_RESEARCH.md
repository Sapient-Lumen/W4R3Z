# REV0124 external baseline pressure research

Status: `research_recorded_no_promotion`  
Promotion allowed: `false`

This pass was aimed at reducing risk, not expanding doctrine. The online pressure is that the sparse-attention lane must compete against current exact and semi-flexible attention systems, not a toy dense reference.

## Evidence-lane implication

Transformers offline evidence should be pre-materialized and local/cache-only at capture time. Hugging Face's docs point to cached/downloaded files for offline use, and snapshot dry-runs can report commit/file/size/cache/download status before materialization. Therefore rev0124 makes the live evidence capture wrapper local-only: `ALLOW_DOWNLOAD=1` belongs to `PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh`, not to the final capture command.

## Baseline pressure

PyTorch SDPA, FlexAttention/BlockMask, vLLM PagedAttention, Transformers cache strategies, FlashAttention, and xFormers all raise the bar. A future sparse claim should be treated as unproven until it has:

1. the real TinyLlama trace and selector/evaluation receipts;
2. named-hardware timing;
3. a baseline bracket against the installed exact attention backend and at least one flexible/block or serving-cache baseline where available;
4. explicit cache/layout compatibility notes for prefill vs cached decode.

## Source basis

- Hugging Face Transformers installation/offline docs: `https://huggingface.co/docs/transformers/en/installation`
- Hugging Face Hub download/dry-run docs: `https://huggingface.co/docs/huggingface_hub/en/guides/download`
- PyTorch SDPA docs: `https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html`
- PyTorch FlexAttention docs: `https://docs.pytorch.org/docs/stable/nn.attention.flex_attention.html`
- PyTorch FlexAttention inference blog: `https://pytorch.org/blog/flexattention-for-inference/`
- vLLM PagedAttention design: `https://docs.vllm.ai/en/latest/design/paged_attention/`
- Transformers KV cache docs: `https://huggingface.co/docs/transformers/en/kv_cache`
- FlashAttention README: `https://github.com/dao-ailab/flash-attention`
- xFormers optimized ops docs: `https://facebookresearch.github.io/xformers/components/ops.html`
