# Scenario — `no_std` / `alloc` claim with docs.rs target overlay

This scenario exists to force **P-0510** to keep separate:

- coarse `no_std` or `alloc` support claims,
- docs.rs metadata overlays,
- changing docs.rs default targets,
- and actual public support posture.

## Why it matters

A crate can be genuinely useful in `alloc`-only environments while still relying on docs.rs target or feature overlays that make the hosted docs look more capable than the default consumer experience.
That is not necessarily dishonesty, but it should not be flattened into a fully observed support claim.

## Expected artifact pressure

- `support-obligation.receipt.json` should record docs.rs metadata, target overlays, and any default-target dependence.
- `claim-class.policy.json` should allow `declared` or `manual_review_required` where the public claim outruns the observed hosted build facts.
- `profile-fidelity.report.json` should permit `partial_overlay` rather than pretending docs.rs hosting proves the full support profile.
