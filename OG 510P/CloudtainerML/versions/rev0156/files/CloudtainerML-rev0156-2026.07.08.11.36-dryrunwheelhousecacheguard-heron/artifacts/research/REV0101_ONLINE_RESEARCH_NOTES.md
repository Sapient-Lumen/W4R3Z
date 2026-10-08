# Online research notes — REV0101

Purpose: verify whether generation cache implementation is a real semantic risk for the public TinyLlama cached-decode trace.

Findings:

1. Hugging Face generation exposes `use_cache` and `cache_implementation`. The documented implementations include `dynamic`, `static`, `offloaded`, `offloaded_static`, and `quantized`. If unspecified, the model default is used, often `DynamicCache`, but this is not an explicit trace contract.
2. Hugging Face cache strategy docs show offloading can be configured through `GenerationConfig` or directly in `generate()`, which means an operator or model config can change cache behavior without changing the visible prompt or decode length.
3. The cache explanation says cache classes/layers can differ in how sequence length is handled and updated. For a trace whose row positions, active-key lengths, and valid-key masks are acceptance-critical, the cache implementation should be recorded and constrained.
4. AttentionInterface docs confirm attention backend identity is similarly configurable, reinforcing the existing `ATTENTION_IMPLEMENTATION=eager` requirement.

Sources:

- https://huggingface.co/docs/transformers/en/main_classes/text_generation
- https://huggingface.co/docs/transformers/kv_cache
- https://huggingface.co/docs/transformers/cache_explanation
- https://huggingface.co/docs/transformers/en/attention_interface

Action taken: rev0101 requires `cache_implementation="dynamic"` as an explicit `generate()` argument for the public evidence lane. Static/offloaded/quantized caches are deferred to named-hardware timing/baseline lanes.
