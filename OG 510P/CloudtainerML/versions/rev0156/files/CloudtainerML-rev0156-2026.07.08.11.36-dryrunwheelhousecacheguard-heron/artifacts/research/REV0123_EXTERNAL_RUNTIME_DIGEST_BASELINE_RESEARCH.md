# External runtime/digest/baseline research — REV0123

Status: `research_note_non_promotional`

## Why this mattered this turn

The riskiest failure mode is not another missing registry entry. It is that a future public trace could become promotion-eligible while loading a local/mounted snapshot whose filenames and safetensors header look plausible but whose weight bytes are not the pinned TinyLlama file. Rev0123 therefore moves model byte authenticity into the public capture acceptance path.

## Source pressure

- Hugging Face Hub `snapshot_download` is the right materialization primitive because it downloads a repository snapshot at a requested revision and supports filtered file sets/local cache operation.
- Transformers offline use depends on pre-downloaded or locally cached files and `local_files_only` / offline settings, so the cube should not assume a live network during capture.
- Safetensors metadata/header parsing is intentionally cheap and useful for structure checks, but header validity is not the same as byte identity; a digest check is the needed authenticity proof.
- Transformers now has multiple attention backends (`eager`, `sdpa`, FlashAttention variants, flex attention). Public trace capture needs `eager` for replayable probabilities, while timing/baseline claims must compete with optimized exact and serving-oriented backends.
- PyTorch SDPA may call optimized CUDA kernels; FlashAttention's core pressure is IO-aware exact attention; vLLM/PagedAttention pressure is KV-cache waste and serving throughput.

## Consequence for this cube

1. Public trace acceptance must require a matching `model.safetensors` SHA-256 when the TinyLlama public claim is requested.
2. Structural snapshot checks remain useful for cheap preflight and fake/truncated-file rejection, but they are no longer sufficient for promotion.
3. Baseline timing should be treated as a separate named-hardware lane against SDPA/FlashAttention/PagedAttention-class systems rather than conflated with the `eager` trace capture lane.

## Sources captured online this turn

- https://huggingface.co/docs/huggingface_hub/en/guides/download
- https://huggingface.co/docs/transformers/en/installation
- https://huggingface.co/docs/safetensors/en/metadata_parsing
- https://huggingface.co/docs/transformers/en/attention_interface
- https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html
- https://arxiv.org/abs/2205.14135
- https://arxiv.org/abs/2309.06180
