# FT-0089 closure — temporal coherence and stale-state composition proofs

Closed in rev0090.

## Closure evidence

- `schema/scope-composition-guard.schema.json` requires `temporal_coherence`.
- `tools/temporal_coherence.py` validates evaluation-window ordering, guard-evaluation placement, required per-surface timestamp roles, stale/unchecked input effects, and current-use coherence flags.
- `tests/mixed-layer-scope-composition.yaml` adds `stale-composed-input-cannot-remain-current`.
- `examples/negative/scope-composition-guard-stale-input-current-invalid.json` proves stale current reuse fails.
- `examples/negative/scope-composition-guard-window-order-invalid.json` proves inverted windows fail.

## Residual frontier

The helper is currently applied to scope composition. Future work should reuse it across aggregate lifecycle, replay-transparency anchor evaluation, discovery result negotiation, and policy lifecycle references.
