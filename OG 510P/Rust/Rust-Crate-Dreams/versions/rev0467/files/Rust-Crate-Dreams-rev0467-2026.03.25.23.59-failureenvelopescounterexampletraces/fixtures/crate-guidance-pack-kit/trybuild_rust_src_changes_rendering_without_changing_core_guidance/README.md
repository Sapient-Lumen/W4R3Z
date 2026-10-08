# Scenario — trybuild rust-src changes rendering without changing core guidance

A crate uses `trybuild` to snapshot a trait-bound error.
The failure is still caught, and the core guidance remains recognizable, but the presence or absence of the `rust-src` component changes rendered standard-library snippets.

Why it matters:
- `trybuild` is a valuable snapshot harness,
- but its own docs warn that compiler rendering can differ depending on whether `rust-src` is installed,
- so a crate should usually classify this lane as `shape_stable` or `manual_review_required`, not as a forever-exact wording contract.
