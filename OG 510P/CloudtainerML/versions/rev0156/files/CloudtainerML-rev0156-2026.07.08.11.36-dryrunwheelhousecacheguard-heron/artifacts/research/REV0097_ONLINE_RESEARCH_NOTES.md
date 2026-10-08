# Online research notes — REV0097

Purpose: support concrete readiness-gate changes, not add doctrine.

## Sources consulted

- Hugging Face Hub download guide: `snapshot_download()` downloads an entire repository at a given revision and uses the local cache internally. Observed via web: `turn390001view0` lines 123-125. URL: https://huggingface.co/docs/huggingface_hub/en/guides/download
- Transformers Auto Classes docs: `attn_implementation` can be `eager`, `sdpa`, `flash_attention_2`, or `flash_attention_3`; SDPA is default when available for torch>=2.1.1. Observed via web: `turn390001view2` line 2460. URL: https://huggingface.co/docs/transformers/model_doc/auto
- Transformers Attention Interface docs: use `attn_implementation` in `from_pretrained()` to select a backend, and models can switch backends. Observed via web: `turn390001view3` lines 126-139. URL: https://huggingface.co/docs/transformers/en/attention_interface
- Transformers GPU inference docs: SDPA is efficient/default for suitable PyTorch versions, and unsupported `output_attentions=True` can fall back to eager. Observed via web: `turn390001view5` lines 186-195. URL: https://huggingface.co/docs/transformers/main/perf_infer_gpu_one
- Transformers generation docs: `max_new_tokens`/`min_new_tokens`, `return_dict_in_generate`, `output_scores`, and greedy/beam controls define replayable generation semantics. Observed via web: `turn395095view0` lines 132-134; `turn395095view1` lines 189 and 424-428; `turn395095view3` lines 139-143. URL: https://huggingface.co/docs/transformers/en/main_classes/text_generation
- PyTorch SDPA docs define `torch.nn.functional.scaled_dot_product_attention` as the dense semantic baseline over query/key/value with optional mask/dropout. Observed via web search result `turn130349search0`. URL: https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html

## Implication for the cube

The next useful change is not another registry. It is a strict stop/go gate that refuses to run capture unless the model source, runtime attention surface, snapshot, and capture-source contracts are all current. rev0097 implements that as `tools/public_trace_readiness_gate.py`.

## Speculation

If the gate passes but the real trace still fails, the likely culprit is internal Transformers/Llama attention API drift or a subtle output-attention/backend mismatch. If the gate cannot pass in a capable environment after dependency/snapshot repair, the project should pivot to documenting the falsification framework rather than continuing sparse-attention promotion work.
