# Scenario family — minor release silently moves a public item behind a feature

This fixture family exists for release reviews where a public item still exists somewhere, but no longer exists in the default or previously documented slice.

It is meant to catch support drift such as:

- a previously public item becomes available only under a new feature,
- an optional dependency is hidden or renamed and the public feature story shifts,
- the docs page still suggests broad availability while the real matrix narrowed,
- and coarse API diff tools miss the fact that the break is conditional rather than universal.

A good availability ledger should make four things explicit:

1. that the diff is **SemVer-relevant** even if the item was not removed everywhere,
2. that the class changed from `stable_public` to `requires_feature` or `requires_feature_and_target`,
3. that the origin/fidelity story for the new slice is visible,
4. and that doctor mode raises `item_moved_behind_feature` instead of burying the change in prose.
