# Rematch-Proxy Cache Plan Manifest

The current leave/rematch proxy is now precise enough to support a provisional canonicalization planner, not just informal advice.

What the local reports jointly imply:
- zero-noise deterministic semantics need `17` exact support-regime buckets and an exact unroll cap of `h=3`
- opponent tremble collapses to `1` bucket at `h=2`
- focal tremble collapses to `2` buckets at `h=2`, separated entirely by whether the entrant can initially defect
- bilateral tremble collapses to `1` bucket at `h=1`

Against the inherited naive plan of keying on the full entrant support signature and unrolling to `h=50`, that shrinks proxy-local key-depth budget from `12150` slots to:
- `51` in zero-noise (`238.2x` smaller)
- `2` in opponent tremble (`6075x` smaller)
- `4` in focal tremble (`3037.5x` smaller)
- `1` in bilateral tremble (`12150x` smaller)

Implication for the inheritor:
- do not implement rematch canonicalization as a full-signature cache plus a legacy global horizon
- compile a world-local planner instead: noise mode first, then the smallest validated discriminator for that mode, plus the smallest exact horizon
- keep the current proxy planner as scratch only; regenerate it whenever entrant support, tremble semantics, outside-option timing, or memory depth changes

Operational note:
- the machine-readable scratch artifact for this pass is `artifacts/reports/rematch_proxy_cache_plan_snapshot_20260306.json`
- in the current proxy, zero-noise still needs an explicit `support_signature -> support_regime_id` lookup table; the noisy modes do not

Contract note:
- the current scratch planner is now backed by a lightweight schema and validator:
  - `schemas/canonicalization_plan.schema.json`
  - `scripts/test/check_rematch_cache_plan_contract.py`
- treat that pair as a temporary bridge between research reports and engine metadata: it keeps the planner machine-checkable before rematch worlds expose planner fields natively
- the contract is intentionally narrow: it checks exact mode rows, cache keys, horizons, and regime coverage for the current proxy rather than pretending to define a final cross-world standard
