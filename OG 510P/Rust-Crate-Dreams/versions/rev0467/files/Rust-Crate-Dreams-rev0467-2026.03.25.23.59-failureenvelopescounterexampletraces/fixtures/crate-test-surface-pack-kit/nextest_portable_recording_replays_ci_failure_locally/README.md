# Scenario family — portable nextest recording replays a CI failure locally, but that is not the same as a supported local recipe

This fixture family exists for crates where the best scenario witness may come from CI rather than a direct local run.

It is meant to catch support drift such as:

- a portable recording proving a failure happened, while docs imply the same scenario is easy to run locally,
- replay/import evidence being treated as identical to a first-class supported fixture,
- or a maintainer forgetting to mark record/replay features as imported or experimental substrate.

A good test-surface pack should make four things explicit:

1. whether the scenario witness came from a direct run or imported recording,
2. whether replay is cross-machine portable,
3. whether the crate treats imported replay as an official downstream recipe,
4. and where manual review still begins.
