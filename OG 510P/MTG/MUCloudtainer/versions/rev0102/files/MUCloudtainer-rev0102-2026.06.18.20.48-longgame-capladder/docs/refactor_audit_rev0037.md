# rev0037 refactor/audit

## New seams

```text
src/muc5/action_label_compare.py
  matched fixed-vs-adaptive label audit over the same branch-outcome matrix

src/muc5/cpp_segment_benchmark.py
  segment-vs-one-action C++ transport benchmark under Python signatures
```

## Why this refactor matters

The previous adaptive labeler generated labels and trained a policy in one revision-specific script.  rev0037 separates a reusable audit question:

```text
Given identical public situations and branch outcomes, did label allocation change the label?
```

That audit can now be reused before trusting future adaptive/racing labelers.

## Audit conditions

rev0037 checks:

```text
matched label rows exist
fixed_equal and adaptive_race methods share the same sampled situations/actions
branch games have zero truncations in the smoke run
branch C++ transition checks have zero skipped events and zero mismatches
segment benchmark has zero skipped events and zero mismatches
rev0037 required docs/scripts/tests exist
```

## Pushback

The audit says adaptive racing matched fixed labels in one smoke panel.  It does not prove adaptive labels are always safe.  It gives us a harness to detect when they are not.
