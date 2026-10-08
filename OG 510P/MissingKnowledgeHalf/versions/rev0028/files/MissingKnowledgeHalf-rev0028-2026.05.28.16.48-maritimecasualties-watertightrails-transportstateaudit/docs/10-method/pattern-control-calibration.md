# Pattern-control calibration

Revision: rev0017

Rev0016 made pattern red-team scaffolds explicit. Rev0017 begins using them.

A pattern candidate must not grow only by adding dramatic support cases. It needs calibration records:

1. **Support cases**: records that originally justified the pattern.
2. **Positive controls**: additional cases that should fit the pattern but were not used to create it.
3. **Negative controls**: superficially adjacent cases that should *not* fit the pattern.
4. **Caught-before-harm controls**: cases where the same hazard was intercepted by a good interface, review, simulation, alarm, checklist, culture, or authority structure.
5. **Rollback triggers**: conditions under which the pattern is split, demoted, merged, or retired.

Rev0017 adds `MKH-ENG-0020` Air Canada Flight 143 / Gimli Glider as the first positive control for `MKH-PAT-0001`. This does **not** mature the pattern. It only tests whether the pattern can recognize another unit/representation-boundary case outside the original promotion set.

The deeper rule: patterns are not rewards for finding similarities. They are tools that earn trust by surviving dissimilarity, counterexamples, and scope limits.
