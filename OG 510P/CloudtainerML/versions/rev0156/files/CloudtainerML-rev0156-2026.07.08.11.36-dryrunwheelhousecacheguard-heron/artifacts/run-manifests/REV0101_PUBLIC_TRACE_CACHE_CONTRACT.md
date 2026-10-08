# Public trace cache contract — REV0101

Public score-path evidence must run cached decode through explicit Hugging Face `generate(cache_implementation="dynamic")` with no cache config. Static/offloaded/quantized caches are deferred to timing/baseline lanes after acceptance.
