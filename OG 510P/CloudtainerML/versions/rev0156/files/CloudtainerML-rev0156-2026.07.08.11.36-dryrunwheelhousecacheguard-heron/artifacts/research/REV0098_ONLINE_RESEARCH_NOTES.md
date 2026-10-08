# Online research notes — REV0098

Status: `execution_relevant`  
Promotion allowed: `false`

## Sources checked this turn

- Hugging Face TinyLlama model page: `https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0` — confirms TinyLlama adopts the Llama 2 architecture/tokenizer family and remains a reasonable small public Llama-family target for trace capture.
- Hugging Face Transformers attention backend docs: `https://huggingface.co/docs/transformers/en/attention_interface` — current docs describe backend-specific mask conventions. The important operational consequence is that `eager`, `sdpa`, `flash_attention_2`, and `flex_attention` cannot be treated as interchangeable trace surfaces.
- Hugging Face Hub download docs: `https://huggingface.co/docs/huggingface_hub/en/guides/download` — `snapshot_download` remains the correct path to materialize a repo at a specific revision into cache before offline capture.
- Hugging Face Transformers KV-cache docs: `https://huggingface.co/docs/transformers/en/kv_cache` — cache type changes are part of generation/runtime semantics and later timing claims must report them.
- PyTorch SDPA docs: `https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html` — SDPA is a Q/K/V attention primitive with optional mask/dropout and backend acceleration; it is a dense baseline path, not the current eager capture hook.

## Change forced by research

The cube needed a backend identity probe, not another registry rule. rev0098 therefore adds `tools/public_trace_backend_identity_probe.py`, blocks non-`eager` trace capture, records SDPA/CUDA backend facts, and keeps SDPA/Flash/Flex in the later timing/baseline lane.
