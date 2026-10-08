# Trace run packet audit — REV0101

Status: `fail`  
Promotion allowed: `false`

## Target

- model: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- revision: `fe8a4ea1ffedaf415f4da2f062534de366a451e6`
- license: `apache-2.0`
- command: `ALLOW_NETWORK_DRY_RUN=1 ALLOW_DOWNLOAD=1 CACHE_IMPLEMENTATION=dynamic bash artifacts/capture-kit/REV0101_RUN_TINYLLAMA_PUBLIC_TRACE.sh`

## Errors

- `prompt_manifest_contract_missing`
- `token_provenance_contract_not_v2`
- `tokenizer_call_add_special_tokens_not_true`
- `tokenizer_call_padding_not_false`
- `tokenizer_call_truncation_not_false`
- `tokenizer_call_return_attention_mask_not_true`
- `tokenizer_call_return_tensors_not_pt`
- `chat_template_applied_must_be_false`
- `prompt_manifest_audit_missing_from_packet`

## Warnings

- none

## Interpretation

This audit converts the next step from a generic instruction into a concrete immutable public-model trace packet with backend/cache identity and prompt-manifest replayability. It is still non-promotional until the trace is captured and accepted by the gate.
