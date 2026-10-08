# Rev0988 validation authority notes

- Aggregate GCC and sanitizer CTest wrappers that reached their orchestration timeout were not treated as terminal evidence. Every affected product test was rerun in a bounded individual or small-shard invocation, and all 43 product tests have explicit passing records under both toolchains.
- An import-created `tools/__pycache__` directory was removed before the active implementation projection was frozen. It is absent from the release tree.
- Reconstruction authority comes from a fresh extraction of the exact sealed rev0987 ZIP plus the stored binary-aware patch, not from the mutable working directory alone.
