# rev0048 audit/refactor notes

The attention compiler core now exposes
`guarded_mass_aware_compiler_points_for_row`, a shared selector panel for trace
experiments.  This reduces silent divergence between probes and keeps value-read,
score-read, mass-certificate, value-norm metadata, and oracle-leakage fields
consistent.

The new `public_trace_gate_audit.py` checks that the default artifact is labeled
as surrogate-only, that no selector reads V vectors or dense outputs before
selection, and that the surrogate suite still exposes broad-row and value-tail
failure modes.
