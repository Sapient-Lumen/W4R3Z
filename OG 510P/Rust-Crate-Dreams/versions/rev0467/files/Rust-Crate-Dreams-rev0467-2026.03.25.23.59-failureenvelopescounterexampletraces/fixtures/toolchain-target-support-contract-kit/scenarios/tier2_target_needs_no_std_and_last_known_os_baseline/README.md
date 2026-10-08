# Scenario — tier2 target needs `no_std` posture, tested-environment truth, and blocker disclosure

A target can exist in Rust’s target taxonomy and still leave a downstream team with unresolved adoption questions.
This scenario models a project that can **compile** for a Tier 2 target, but still needs to tell another team:

- that the lane is effectively `compile_only`,
- that the target is `no_std` only,
- what the last known tested environment was,
- which external prerequisites remain,
- and which blockers still prevent a stronger support class.

The point is to keep “target exists”, “project supports target”, and “review-ready target lane” from collapsing into one fake support verdict.
