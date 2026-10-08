# First retained rematch-world benchmark should copy forward the canonicalization bridge contract

Local result from `artifacts/reports/rematch_world_benchmark_canonicalization_handoff_snapshot_20260317.md`:
- the benchmark seed now carries a compact native canonicalization/planner handoff copied from the SG-003 bridge receipt,
- so future compiled benchmark artifacts can cite one embedded planner surface instead of forcing inheritors to reopen several proxy-era reports,
- while staying small enough to avoid regrowing the archive with wide canonicalization tables.

## Why this matters

The archive already had a compact canonicalization bridge receipt, but that receipt still lived *beside* the benchmark artifact family.

That meant the eventual inheritor had to remember an extra lookup rule:
1. benchmark artifact for world-dependent metrics,
2. separate bridge receipt for planner semantics,
3. older proxy reports only if the bridge looked suspicious.

That is survivable, but not ideal.

If the first retained benchmark artifact is supposed to become the main inheritor-facing surface, it should carry a tiny planner handoff natively.

## What the copied handoff keeps

Only the compact parts that matter locally:
- bridge digest and source path,
- per-mode planner kind,
- minimal exact horizon,
- recommended key fields,
- regime counts,
- zero-noise dispatch compression totals,
- invalidation triggers.

It does **not** copy:
- wide support-signature maps,
- large classifier tables,
- or older report bodies.

## Implementor rule

Treat the copied handoff as a frozen citation surface inside the benchmark seed until the engine can emit a real world-native planner manifest.

Once that exists, replace the copied bridge-derived rows with engine-owned measurements and conformance checks.
