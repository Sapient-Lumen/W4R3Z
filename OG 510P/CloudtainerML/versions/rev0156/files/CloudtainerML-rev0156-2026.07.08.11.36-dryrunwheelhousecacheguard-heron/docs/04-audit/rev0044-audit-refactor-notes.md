# rev0044 audit/refactor notes

The attention metrics used by rev0044 were factored into `experiments/attention_compiler_core/attention_core.py`. New probes use the same softmax, Top-K, Top-p, sparse-output, effective-support, and byte-estimate routines.

The audit target changed from artifact existence to semantic adequacy:

- current artifacts must carry source-hash provenance;
- mass frontier rows must contain minimum-K mass fields and fixed Top-K mass;
- model trace rows must come from extracted Q/K/V scores and values, not synthetic score streams;
- exact Top-K may be selector-correct while still failing output preservation.

This is a narrow refactor, not a registry expansion.
