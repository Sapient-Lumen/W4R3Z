# Gap: Resolution explainability and feature traceability are still too weak

## Summary
Cargo can usually *solve* dependency graphs, but it still does not make the outcome sufficiently **explainable, diffable, and reusable** for humans or tools.

That weakness now matters more than it used to because multiple high-value workflows depend on precise resolution answers:
- semver analysis needs to know which foreign items and dependency features are actually active,
- policy tooling needs stable evidence for why a version or feature was selected,
- large workspaces need reproducible “why did this rebuild / why is this duplicate here / why is this feature on?” answers,
- future Cargo plumbing is explicitly moving toward programmatic seams instead of ad hoc scraping.

The ecosystem has pieces of this (`cargo tree`, `cargo metadata`, unstable unit graphs, resolver work, semver tooling), but not one **portable resolution evidence layer**.

## Why now
- The Cargo plumbing goal says today’s plumbing is thin and that `cargo metadata` can include dependency resolution but **excludes feature resolution**. It also frames feature resolution as its own build phase and notes `--unit-graph` as an experiment for obtaining feature-resolution results.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- The standalone PubGrub effort exists specifically to improve Cargo’s error messages, enable richer extensions like better MSRV and CVE-aware resolution, and support a richer ecosystem of cargo extensions.
  https://rust-lang.github.io/rust-project-goals/2025h1/pubgrub-in-cargo.html
- The `cargo-semver-checks` goal reports that getting dependency **features right recursively** is still difficult and currently not available through the lockfile or a Cargo interface; cross-crate linting also depends on better crate/version provenance through Rust tooling.
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
  https://blog.rust-lang.org/2025/12/16/Project-Goals-2025-November-Update.md/
- Cargo 1.94 is actively standardizing structured reporting via `cargo report timings`, `cargo report rebuild`, and `cargo report sessions`, which is exactly the kind of seam a resolution-explanation artifact should align with.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## Concrete missing pieces
1. **Version-choice evidence**
   - Why this version?
   - Why duplicates?
   - Which requirement or pin prevented a newer or older version?
2. **Feature-activation evidence**
   - Which edge, target, dependency kind, or default caused a feature to turn on?
   - Which features differ between host/build/dev/runtime contexts?
3. **Portable reports**
   - CI and bots should diff machine-readable reports, not scrape prose or shell output.
4. **Reduced repros for resolver bugs and confusing selections**
   - A “minimized lockfile/workspace slice” is still too bespoke today.
5. **Bridges to semver / policy / workspace tooling**
   - The same resolution evidence should feed Feature Kit, Public API Kit, Policy Kit, and Workspace Governance Kit.

## Desired properties
- Works for workspaces, target-specific dependencies, build-dependencies, proc-macros, and alternative registries.
- Produces deterministic output suitable for PR diffs.
- Explains both success and failure, not just failure.
- Records enough provenance that downstream tools can trust the explanation rather than rerunning Cargo internals.
- Starts as a plugin / artifact layer instead of assuming immediate Cargo integration.
