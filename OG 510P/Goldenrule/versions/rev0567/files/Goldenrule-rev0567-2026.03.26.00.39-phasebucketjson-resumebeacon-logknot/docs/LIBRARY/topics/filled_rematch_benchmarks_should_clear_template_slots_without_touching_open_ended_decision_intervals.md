# Filled rematch benchmarks should clear template slots without touching open-ended decision intervals

The first endogenous rematch-world benchmark should be treated as an in-place fill operation on one retained seed artifact, not as permission to grow a new sidecar family of occupancy, tempo, ranking, or semantics notes.

The important subtlety is that a blanket “no nulls anywhere” rule is wrong. The copied compact decision bundle legitimately carries open-ended `end_delay: null` intervals, and those nulls are part of the standing phase-3 contract rather than unfinished benchmark work.

So the right completion gate is narrower and more useful:

1. replace all world-dependent `TEMPLATE_*` strings,
2. replace all world-dependent null telemetry fields,
3. flip the five world-dependent section statuses from `pending_fill` to `filled`, and
4. leave the copied compact decision bundle alone unless the compact decision contract itself is intentionally revised upstream.

That keeps the archive compact while making publishability machine-checkable. The next inheritor should clear the fill slots already named in the seed artifact and use the completion gate to reject accidental placeholder carryover, not to scrub away meaningful open-ended intervals.
