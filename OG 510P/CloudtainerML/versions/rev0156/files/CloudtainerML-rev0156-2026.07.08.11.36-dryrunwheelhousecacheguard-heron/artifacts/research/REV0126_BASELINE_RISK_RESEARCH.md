# REV0126 baseline/runtime risk research

Status: `research_only_non_promotional`

## Online-grounded constraints

- Transformers offline/firewalled operation requires files to be downloaded and cached ahead of time. The package should therefore keep snapshot preparation and local-only capture as distinct phases. Source: https://huggingface.co/docs/transformers/en/installation
- Hugging Face Hub download tooling supports dry-run planning and programmatic `snapshot_download(..., dry_run=True)`, including filtered downloads. The cube should keep using a dry-run/materializer lane before capture. Source: https://huggingface.co/docs/huggingface_hub/en/guides/download
- Transformers attention backends expose `attn_implementation` with eager, SDPA, FlashAttention, FlexAttention, and paged variants, and custom backends must preserve mask behavior. Trace capture must therefore pin and audit `eager` semantics instead of assuming backend equivalence. Source: https://huggingface.co/docs/transformers/en/attention_interface
- Safetensors metadata can be parsed from headers/HTTP ranges, which is useful for structural validation, but it is not the same as authenticating the local full weight bytes. Source: https://huggingface.co/docs/safetensors/en/metadata_parsing

## Current pressure on the sparse claim

The sparse-attention performance claim remains unpromoted until it beats installed exact/baseline systems on named hardware. The baseline bracket must include, at minimum, exact eager/SDPA semantics for trace fidelity, FlashAttention-style exact IO-aware attention, FlexAttention/block-mask variants where available, and page/KV-cache-aware serving baselines where installed.

## Operational implication

Rev0126 does not try to expand the baseline registry. It fixes a live wrapper path that could prevent the corrected runtime from ever reaching the trace capture. Once a real trace exists, the next useful baseline work is named-hardware timing, not another static taxonomy.
