# CELL-066 — Layer-Oracle Sparse Cache Sharing

Priority: P2

Status: candidate

Source IDs: SRC-0119

## Cheap first run

Two-layer synthetic support task where layer 1 selects tokens for sparse layer 2.

## Baselines

- local sparse proxy
- layer-1 oracle support
- random support
- full attention

## Metrics

- support recall
- output accuracy
- KV reuse ratio
- layer sensitivity

## Stop condition

If oracle support is unstable across seeds, keep as speculative.
