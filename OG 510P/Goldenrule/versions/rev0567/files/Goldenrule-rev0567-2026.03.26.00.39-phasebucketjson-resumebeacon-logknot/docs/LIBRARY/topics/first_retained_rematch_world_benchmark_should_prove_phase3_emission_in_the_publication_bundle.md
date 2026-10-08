# First retained rematch-world benchmark should prove phase-3 emission in the publication bundle

Local result from `artifacts/reports/rematch_world_benchmark_phase3_emission_snapshot_20260317.md`:
- the retained publication bundle now explicitly proves that the benchmark emits the copied phase-3 decision contract,
- so the inheritor can cite one compact retained receipt for `delay_contract`, `winner_contract`, and `delta_contract`,
- instead of inferring phase-3 emission indirectly from a larger compiled artifact.

## Why this matters

The archive already had the copied `compact_decision_bundle` inside the benchmark seed and compiled artifact.
That was good, but still slightly too implicit.
An inheritor reading the spine had to inspect the compiled artifact and mentally check three things:
1. is the bundle still present,
2. does it still match the standing decision contract,
3. and do all ten `SQ-017`–`SQ-026` questions still surface through the emitted delay / winner / delta sections?

Those are all machine-checkable questions.
So the publication bundle should answer them directly.

## Compact rule

Treat explicit phase-3 emission as part of the retained publication spine.
The bundle receipt should say:
- the copied bundle still matches the standing decision contract,
- which emitted sections carry the proof,
- which question ids are covered,
- and how many open-ended winner intervals remain allowed by contract.

That keeps the archive citation-first while making the first real rematch benchmark feel more like a true SG-003 emission surface and less like a large JSON blob that needs manual interpretation.
