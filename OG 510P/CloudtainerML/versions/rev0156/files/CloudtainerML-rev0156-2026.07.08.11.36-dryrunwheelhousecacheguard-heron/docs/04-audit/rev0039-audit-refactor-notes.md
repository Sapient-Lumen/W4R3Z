# rev0039 audit/refactor notes

Added `tools/sparse_index_compiler_report.py` to unify the previously separate sparse-gate, block-index, and exact-top-k lanes.

The report checks whether current artifacts have:

- primary metric
- exactness guards
- selector/block cost fields
- hard compiler fields
- block-index readiness
- temporal-top-k readiness

This prevents learned sparse gates, MiniMax-style index branches, and GVR-style selectors from being promoted under incompatible criteria.
