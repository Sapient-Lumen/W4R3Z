# Gap: Change impact, rebuild scope, and relinkability

Rust is getting closer to a world where **not every edit should force reverse dependencies to recompile**.
But the ecosystem still lacks a portable, reviewable way to say:
- what changed,
- which semantic boundary that change crossed,
- which units truly needed recompilation,
- which units only needed relinking,
- and which rebuilds happened only because current tooling is conservative.

Today, those truths are split across:
- Cargo fingerprint logic,
- raw rebuild reasons and build-analysis experiments,
- public-API and semver tools,
- compiler incremental-query machinery,
- build-script invalidation heuristics,
- and maintainer folklore about “harmless” edits.

That split leaves users with a common bad experience:
1. **an edit seems obviously local**,
2. **Cargo still rebuilds more than expected**,
3. **diagnostics explain the symptoms but not the semantic boundary**,
4. **future relink-oriented work has no shared artifact boundary to target**.

## Why this matters now
The upstream signals are unusually direct.

- The 2025H2 **Relink don’t Rebuild** goal is explicit: Rust wants Cargo and rustc to avoid rebuilding reverse dependencies for changes that do not affect a crate’s public interface. The examples are exactly the kinds of edits users routinely expect to be local: comment changes, formatting, reordering impl items, or adding a `dbg!` in a non-inlinable function.
  - https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- Cargo’s unstable build-analysis work now records rebuild reasons and persists them on disk with `cargo report rebuilds`, which means “why did this rebuild?” is becoming a first-class machine-facing seam rather than only a debugging log.
  - https://doc.rust-lang.org/beta/cargo/reference/unstable.html
- Cargo’s FAQ still says that after-the-fact rebuild debugging has historically been weak and that users often have to inspect fingerprint logs and “connect some dots” themselves.
  - https://doc.rust-lang.org/cargo/faq.html
- Cargo’s fingerprint docs make the core limitation explicit: change tracking mixes fingerprints, mtimes, dep-info anchors, and selective environment capture, and it intentionally balances completeness against complexity and performance.
  - https://doc.rust-lang.org/beta/nightly-rustc/cargo/core/compiler/fingerprint/index.html
- rustc’s incremental-compilation guide explains why naive dependency tracking produces false positives and why the compiler uses the red-green algorithm to distinguish “potentially affected” from “actually changed”.
  - https://rustc-dev-guide.rust-lang.org/queries/incremental-compilation-in-detail.html
- Cargo build scripts remain a major invalidation seam because, unless they emit explicit `rerun-if-*` instructions, Cargo conservatively treats broad package changes as reasons to rerun them.
  - https://doc.rust-lang.org/cargo/reference/build-scripts.html

Taken together, that means the missing contribution is **not** merely a faster compiler or a prettier rebuild log.
It is a shared contract for **change-impact evidence**.

## What is missing
Rust has tools that answer adjacent questions:
- **Public API Kit** can say what changed in a public surface.
- **Build Cache Kit** can say whether an artifact was reused, duplicated, or rebuilt.
- **Build Doctor Kit** can diagnose slow workflows and bottlenecks.
- **Compile-Time Capabilities Kit** can explain why build scripts or proc-macros reran.

But Rust still lacks a portable layer that says:
- this was the **concrete source/config/environment change slice**,
- this was its **semantic impact classification**,
- this was the **required rebuild scope**,
- this was the **relink opportunity that current tooling missed or used**,
- and this was the **confidence/evidence strength** behind that claim.

That layer matters because otherwise every future tool will keep inventing its own hidden model of “what kind of edit was this?”

## Desired contribution shape
The worthy contribution here is a **Change Impact Kit**:
- one `impact-subject/v0` describing the before/after build subject,
- one `change-slice/v0` describing what concretely changed,
- one `impact-classification-report/v0` describing which semantic boundary the change crossed,
- one `rebuild-scope-report/v0` describing which units/actions are actually required,
- one `relink-opportunity-report/v0` describing which downstream artifacts could be reused or relinked,
- one `impact-diff-report/v0` comparing expected vs observed outcomes,
- and one `impact-pack/v0` that other kits can attach or consume.

## What a good solution would make possible
A good v1 would let a maintainer or tool answer questions like:
- “This edit changed docs only; why did the dependency graph rebuild anyway?”
- “This crate body changed but its public boundary did not; which reverse dependencies were conservative rebuilds?”
- “This build-script reran because of broad invalidation; how much downstream work did that force?”
- “Which rebuilds were unavoidable and which were missed relink opportunities?”
- “Did this change move from `local-recompile` to `reverse-dep-recompile` because of a real interface change or because the current lane lacks finer-grained evidence?”

## Early pilot cases
1. **Doc/comment-only change**
   - should usually classify as no semantic interface change;
   - report whether rebuilds were conservative or avoided.
2. **Function-body change in a non-inlinable item**
   - should often permit reverse-dependency reuse/relink rather than recompilation.
3. **Public-signature or layout-affecting change**
   - should classify as a real interface boundary change with broader rebuild scope.
4. **Build-script-triggered churn**
   - should separate “real semantic need” from “rerun-if policy was too broad”.
5. **Config/feature/target/toolchain change**
   - should classify as environment/build-context impact instead of source-only impact.

## Why this is broader than a perf nicety
This seam is strategically important because it connects several archive winners:
- **Build performance**: it turns rebuild complaints into reviewable evidence.
- **API evolution**: it distinguishes public-surface changes from implementation-only churn.
- **Caching**: it clarifies whether a miss is a topology/reuse problem or a true impact problem.
- **CI/test selection**: it gives downstream systems a better basis for scoping follow-on work.
- **future Cargo/rustc convergence**: it gives relink-oriented work a portable boundary instead of leaving it as one internal optimization.

## Boundaries
- **Not Public API Kit:** public-surface diffs are one important signal, but change impact must also represent non-API changes, config/environment changes, and build-script invalidation.
- **Not Build Cache Kit:** cache/reuse is about persisted artifacts and reuse verdicts; change impact is about classifying the edit and the required action scope.
- **Not Build Doctor Kit:** diagnosis can consume impact reports, but should not redefine the change-impact facts.
- **Not Compile-Time Capabilities Kit:** compile-time unit authority and invalidation surfaces remain there; Change Impact Kit consumes them when they explain churn.
- **Not Semantic Context Kit:** semantic inputs remain there; this kit publishes actionable judgments about changes between two concrete states.

## The deeper lesson
Rust’s incremental story has been learning the same lesson in multiple places: **potentially affected** is not the same as **actually changed**.
The compiler knows this.
Cargo is beginning to expose more rebuild evidence.
The ecosystem still needs a first-class artifact boundary so that understanding can travel outside internals and into ordinary workflows.
