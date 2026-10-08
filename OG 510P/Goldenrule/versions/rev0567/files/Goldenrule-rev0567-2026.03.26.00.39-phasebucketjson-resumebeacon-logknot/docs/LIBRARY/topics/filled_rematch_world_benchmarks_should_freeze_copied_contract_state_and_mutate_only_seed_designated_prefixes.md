# Filled rematch world benchmarks should freeze copied contract state and mutate only seed-designated prefixes

The first endogenous rematch-world benchmark should not treat the retained seed as a free-form editing surface.

The standing mutation surface is intentionally narrow:

- mutate only the **allowed mutable prefixes** already designated by the seed,
- keep the **frozen prefixes** frozen,
- leave the copied **compact decision bundle** untouched,
- and keep the publication / decision **contract pointers** stable while world sections are filled.

That rule keeps the benchmark self-contained without reopening proxy-era fanout. It also gives future inheritors one clean publication boundary: fill world telemetry in place, but do not drift the copied contracts that already explain how the benchmark should be interpreted.

Minimal takeaway: treat the benchmark fill as a controlled prefix patch, not as permission to rewrite copied contract state.
