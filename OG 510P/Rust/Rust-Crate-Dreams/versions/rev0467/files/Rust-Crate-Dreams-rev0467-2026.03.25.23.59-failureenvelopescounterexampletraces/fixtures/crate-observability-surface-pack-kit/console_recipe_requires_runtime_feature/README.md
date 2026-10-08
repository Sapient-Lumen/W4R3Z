# Scenario family — console / runtime recipe requires explicit instrumentation support

This fixture family exists for async crates whose observability story includes tokio-console-style or runtime-introspection signals.

It is meant to catch support drift such as:

- the crate advertises runtime or task signals as part of its operability story,
- but those signals only appear when a runtime feature like Tokio's `tracing` support is enabled,
- or the recipe requires an extra layer/subscriber or cfg posture,
- or the contract implies generic runtime support when the recipe is actually runtime-specific.

A good observability pack should make four things explicit:

1. whether the runtime-introspection signals are part of the crate's **official** observability surface or just an advanced recipe,
2. which crate features, layers, or cfg/runtime assumptions are required,
3. whether the recipe works on the default subscriber path or only under a named console path,
4. and where portability stops and manual review begins.

This family keeps “the runtime can emit useful signals” separate from “the crate publishes a trustworthy activation contract for those signals”.
