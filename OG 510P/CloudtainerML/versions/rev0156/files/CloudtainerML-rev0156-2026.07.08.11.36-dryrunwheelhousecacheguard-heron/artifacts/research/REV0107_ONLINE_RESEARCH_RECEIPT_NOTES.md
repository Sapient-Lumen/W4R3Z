# Online research receipt notes — REV0107

Status: `research_applied_to_receipt_gate`  
Promotion allowed: `false`

This revision uses current public documentation to justify a narrow execution change: the selector-entry verdict now emits a receipt binding the exact NPZ, provenance JSON, verifier code, and evaluator code. This is not a new registry; it is a replay/evaluation guard.

## Applied sources

- Hugging Face Transformers generation docs: generation length, strategy, cache implementation, and inherited config are explicit replay variables.
- Hugging Face KV cache docs: dynamic/static/offloaded/quantized caches can differ, so the trace lane must keep `cache_implementation="dynamic"` and record it.
- Hugging Face attention backend docs: backend selection is an explicit runtime surface, so the verifier code and backend identity belong in the evidence chain.
- PyTorch reproducibility docs: reproducibility can vary across release, platform, and device; file/tool hashes are part of a meaningful handoff.
- PyTorch CUDA Event docs: timing evidence needs explicit event/synchronization semantics and remains separate from selector evaluation.

## Resulting change

`tools/public_trace_evaluation_verdict_audit.py` now writes `artifacts/probe-results/REV0107_PUBLIC_TRACE_EVALUATION_RECEIPT.json`, and `tools/public_trace_selector_entry_gate.py` refuses selector entry unless that receipt says the public verifier accepted the exact bundle.
