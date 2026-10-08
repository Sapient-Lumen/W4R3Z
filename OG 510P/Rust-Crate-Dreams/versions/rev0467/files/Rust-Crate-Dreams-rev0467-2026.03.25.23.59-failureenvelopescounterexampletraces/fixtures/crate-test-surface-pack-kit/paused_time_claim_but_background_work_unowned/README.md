# Scenario family — paused time claim, but background work is still unowned

This fixture family exists for async crates that claim deterministic timeout / retry testing because they use Tokio paused time.

It is meant to catch support drift such as:

- the crate documents `#[tokio::test(start_paused = true)]`,
- but representative tests spawn background work that is never joined or aborted,
- or the maintained test recipe only works with the current-thread runtime,
- or the official scenario corpus assumes auto-advance without stating that assumption.

A good test-surface pack should make four things explicit:

1. whether paused time is an **officially supported** seam or just a best-effort recipe,
2. whether the supported recipe requires the current-thread runtime,
3. whether spawned tasks must be owned / aborted / joined for the scenario to stay deterministic,
4. and whether the scenario witness was observed or only declared.

This family keeps “Tokio has paused time” separate from “the crate publishes a trustworthy deterministic-time contract for downstream tests”.
