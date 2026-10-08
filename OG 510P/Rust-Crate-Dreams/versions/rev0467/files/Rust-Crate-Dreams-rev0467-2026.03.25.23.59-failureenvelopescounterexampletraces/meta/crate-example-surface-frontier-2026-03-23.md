# Crate Example Surface frontier — 2026-03-23

This lane already knew that crates need official quickstarts, prerequisite lineage, success witnesses, and scenario coverage.
The sharper frontier after re-reading current Cargo/rustdoc/docs.rs material is that those truths still do **not** settle three review questions:

1. **Who actually authorized the “start here” path?**
2. **Which entrypoints are viable in which command families and feature states?**
3. **What is merely visible in rustdoc/docs.rs versus actually runnable and witnessed?**

## Current primary signals

- Online docs remain the preferred canonical learning reference in the 2025 State of Rust survey.
- Rust’s design-vision work says crates still need more supportive interfaces and guidance.
- API guidelines still treat examples as copied code, not decorative snippets.
- Cargo examples are first-class targets and are built under `cargo test`, but not run by default.
- Cargo target metadata still allows `required-features` to skip examples entirely.
- Rustdoc scraped examples remain unstable.
- Cargo’s scrape-examples docs still warn that dev-dependency conditions can suppress scraping unless a target opts in.
- docs.rs metadata can materially reshape visibility through features/targets/default-target, while docs.rs builds still run in a restricted sandbox.

## Sharper missing value

The worthy missing crate is not another “examples are present” index.
It is a crate-authored support layer for:

- **official-start authority** — what source or maintainer act actually blesses one path as the receiver-facing start;
- **entrypoint viability** — whether README snippets, rustdoc examples, `cargo run --example`, doctest surfaces, and guide commands are viable in the declared feature/env lane;
- **hosted visibility honesty** — what docs.rs or rustdoc show, under what flags/targets/features, and why that does not automatically prove local runnable success;
- **portable review bundles** — one small pack a reviewer or downstream adopter can inspect.

## Design guardrails

Keep these truths separate:

1. **officiality** — a maintainer or declared pack blessed this path;
2. **visibility** — a snippet/example appears in docs, rustdoc, or docs.rs;
3. **viability** — the path can build/run/test under a named command/feature/env lane;
4. **witness** — success was actually observed and recorded;
5. **support level** — official quickstart, reference example, best-effort demo, or manual-review-only.

Do not let any of the following stand in for an honest first-success answer:

- “the README has a snippet,”
- “cargo test builds examples,”
- “docs.rs shows the example,”
- “scraped examples are enabled,”
- or “the crate has an examples/ directory.”
