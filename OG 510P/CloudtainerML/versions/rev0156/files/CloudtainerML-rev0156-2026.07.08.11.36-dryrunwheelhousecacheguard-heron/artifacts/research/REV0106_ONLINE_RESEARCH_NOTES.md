# Online research notes — REV0106

Purpose: focus the turn on the riskiest remaining completion path: an accepted public trace bundle that can actually be evaluated without being mistaken for promotion.

## Sources reviewed

- Hugging Face Transformers generation docs, `main_classes/text_generation`: `max_new_tokens`, `min_new_tokens`, `do_sample`, `num_beams`, `use_cache`, `cache_implementation`, `cache_config`, and GenerationConfig default inheritance are explicit moving parts for reproducible generation.
- Hugging Face Transformers generation utility docs: `generate()` output can include generated sequences, prediction scores, attentions, hidden states, and past-key-values. That makes a separate verdict layer useful: ordinary generation output is not automatically an evaluable trace bundle.
- Hugging Face KV cache docs: dynamic/static/offloaded/quantized caches can change decode and timing behavior; the current trace lane correctly remains pinned to `dynamic` cache while timing variants belong to a later baseline lane.
- PyTorch reproducibility docs and `torch.use_deterministic_algorithms`: reproducible replay depends on software/hardware execution choices and is not guaranteed by seed-setting alone.
- PyTorch CUDA event docs: hardware timing requires explicit event/synchronization semantics and must not be inferred from trace-capture elapsed wall time.

## Applied change

The cube now has an evaluation-verdict gate. The operator path can no longer slide from “capture produced files” into “selector evaluation” unless `validate_public_trace_provenance` accepts the NPZ/provenance pair. If accepted, the verdict is still `accepted_for_selector_evaluation_not_promotion`; named hardware timing remains blocked.
