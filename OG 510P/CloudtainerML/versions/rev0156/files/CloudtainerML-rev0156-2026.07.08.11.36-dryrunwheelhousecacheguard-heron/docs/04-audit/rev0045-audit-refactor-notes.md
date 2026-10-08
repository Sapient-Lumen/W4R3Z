# rev0045 audit/refactor notes

This revision refactors the attention compiler core so selection contracts are explicit and testable. The new invariant is: mass-aware selectors may use QK scores and score-only certificates, but may not inspect V vectors or dense attention outputs.

Added audit:

- `tools/mass_certified_attention_audit.py`

Audit checks:

- current mass-certified artifact exists and has the expected kind;
- row-level selector metadata reports no `selection_uses_values` or `selection_uses_dense_output`;
- score-only mass certificates match evaluation mass within tolerance;
- AST-level source check verifies the selector functions do not reference forbidden value/output symbols;
- synthetic and tiny-trace summaries are exposed separately so broad-regime failures cannot be hidden by toy-trace success.

`tools/current_scientific_run_audit.py` and `tools/evidence_integrity_audit.py` now understand the mass-certified artifact rather than requiring every revision to rerun the earlier attention-row benchmark.
