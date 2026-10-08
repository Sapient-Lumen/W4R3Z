---
id: P-0468
title: Cargo Resolver Explanation Kit — feature-cause chains, version-choice receipts, and lockfile-aware why-bundles
status: idea
domains: [cargo, resolver, features, tooling, devtools, ci]
last_reviewed: 2026-03-16
evidence:
  - https://doc.rust-lang.org/cargo/reference/resolver.html
  - https://doc.rust-lang.org/cargo/reference/features.html
  - https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
  - https://doc.rust-lang.org/cargo/reference/registry-index.html
  - https://doc.rust-lang.org/cargo/commands/cargo-tree.html
  - https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
  - https://rust-lang.github.io/rust-project-goals/2025h1/pubgrub-in-cargo.html
  - https://docs.rs/guppy/latest/guppy/
  - https://docs.rs/cargo-hakari/latest/cargo_hakari/
  - https://github.com/rust-lang/cargo/issues/14021
  - https://github.com/rust-lang/cargo/issues/11261
  - https://github.com/rust-lang/cargo/issues/12546
  - https://github.com/rust-lang/cargo/issues/14415
---

# Problem

Cargo already has real resolver substrate, but the explanation workflow is still fragmented.

Official docs now make the split unusually clear:

- the resolver docs explain heuristics, lockfile influence, resolver versions, feature behavior, and MSRV-aware version preference,
- `cargo tree` can show reverse edges, enabled features, and duplicate versions, but it explicitly says its view is only *pretty close* to what Cargo will build and does not guarantee exact equivalence,
- `cargo metadata` is stable graph context but the Cargo plumbing goal explicitly says it excludes feature resolution,
- `--unit-graph` can expose Cargo's internal build-unit graph and provide a way to get feature-resolution-adjacent results, but it remains unstable,
- and unstable `resolver.feature-unification` modes are creating a sharper policy surface for why the same workspace may intentionally build dependencies in more than one way.

At the same time, existing ecosystem tools still prove the gap is not “no one can query Cargo graphs.”
`guppy` already parses `cargo metadata` and provides graph + feature-query APIs, while `hakari` uses `guppy` to simulate Cargo builds and reason about repeated feature sets in workspaces.
Those are valuable substrate and prior art.
What they do **not** yet provide is one boring, portable, review-oriented explanation bundle for:

- why this feature is active,
- why this version was chosen,
- why one package version built more than once,
- why the graph changed after a manifest / workspace-selection / policy change,
- which parts of the explanation are direct Cargo facts versus conservative inference,
- whether a feature state belongs to a normal, build/proc-macro, or dev lane and whether any human-facing view merged those lanes,
- whether target-specific dependency clauses were actually in scope for the selected build or merely visible in an all-target graph export,
- and where the explanation is only **selection-sensitive** or **manual-review-required** because Cargo’s human views are close but not exact.
- which packages participated in feature unification and whether policy changes, not manifest changes, explain the result.
- what the subject explicitly asked to enable or keep off, and why the effective feature state still differed.
- which manifest or workspace-inherited dependency declaration actually authored the effective feature/default-feature policy, and where that answer remains conservative because inheritance or target-specific behavior is ambiguous.
- which feature-like names are public, implicit, hidden by `dep:`, or only conditionally meaningful because weak forwarding requires some other activation path.
- which dependency key, package name, rename field, and registry/index identity actually referred to the dependency being explained, and whether workspace inheritance or registry publication made that answer less direct.

So the missing crate is not a new resolver, not a graph visualizer, and not a replacement for `guppy` or `cargo hakari`.

The missing crate is a **resolver explanation kit**: a Cargo-adjacent crate that turns Cargo’s scattered resolver surfaces into a compact, reviewable “why” artifact with explicit evidence boundaries.


# 2026-03-08 implementation refresh — feature-unification policy and participant scope

This proposal is more implementation-ready again because current Cargo docs and issue history make one more boundary explicit: **resolver answers depend not only on manifests and targets, but also on which packages were allowed to participate in feature unification**.

Four details especially matter now:

1. Cargo unstable docs define `resolver.feature-unification` with explicit `selected`, `workspace`, and `package` modes, and document `selected` as the default.
2. Resolver docs still say dependency features are unified across multiple selected workspace packages, and that separate invocations are needed when users want to avoid that behavior.
3. The tracking issue for workspace feature-unification still has unresolved questions about how investigative surfaces like `cargo tree` should represent package mode.
4. The long-running “feature selection depends on compiled package set” issue remains open, which means package-set sensitivity is still real substrate rather than a historical quirk.

That means the crate should now freeze one more artifact lane instead of burying it inside generic notes:

- one **`unification-scope.report.json`** that records which packages were selected, which packages participated in feature unification, and whether policy changes explain the observed result.

# 2026-03-08 implementation refresh — feature intent and suppression truth

This proposal is more implementation-ready again because current Cargo docs and issue history make one more boundary explicit: **the crate must preserve not only which features are active, but also what the subject explicitly asked Cargo to keep off**.

Five details especially matter now:

1. Cargo features docs warn that `default-features = false` may still fail to keep defaults off if another dependency path enables them.
2. The same docs say `--no-default-features` applies to the selected packages, not necessarily every dependency edge in a workspace.
3. Resolver docs still say dependency features unify across multiple selected workspace packages.
4. The workspace feature-unification tracking issue is still open.
5. Open issues still show that `--bin`, `-p`, and workspace-root selection can produce different effective feature stories.

That means the crate should now freeze one more artifact lane instead of burying it inside generic feature notes:

- one **`feature-intent.report.json`** that records positive feature requests, negative feature intent, subject scope, and whether workspace pressure overrode that intent.

# 2026-03-08 implementation refresh — workspace dependency inheritance and manifest-origin truth

This proposal is more implementation-ready again because current Cargo docs, issue history, and release notes make one more receiver-facing boundary explicit: **the effective dependency policy may have been authored partly by `[workspace.dependencies]`, partly by the member manifest, and partly by target-specific inherited edges**.

Five details especially matter now:

1. Cargo workspace docs say features declared in `[workspace.dependencies]` are additive with member dependency features.
2. The dependency-spec docs still say inherited dependencies cannot use keys other than `optional` and `features`, with `default-features` named as an example.
3. Cargo issue history shows member-level `default-features = false` can be neutralized unless the workspace definition also disables defaults.
4. Rust release notes document the converse case too: when a workspace dependency disables defaults, a member inherited dependency with `default-features = true` will enable them again.
5. Cargo issue history also shows target-specific inherited dependencies can still be where feature/default-feature behavior becomes conservative or manual-review territory.

That means the crate should now freeze one more artifact lane instead of burying it inside generic feature notes:

- one **`dependency-origin.report.json`** that records where an effective dependency policy came from, which parts were inherited, which parts were local, whether default-feature intent was additive / neutralized / re-enabled, and whether target-specific inheritance kept the answer conservative.

# 2026-03-08 implementation refresh — feature origin, hidden aliases, and weak forwarding truth

This proposal is more implementation-ready again because current Cargo docs, registry-index docs, changelog notes, and issue history make one more receiver-facing boundary explicit: **the crate must preserve not just that a feature-like thing was active, but what kind of authored feature syntax produced that state.**

Six details especially matter now:

1. Cargo features docs say optional dependencies automatically create implicit feature aliases.
2. The same docs say any `dep:` use suppresses that implicit alias.
3. The same docs say `pkg/feat` activates an optional dependency while also forwarding a dependency feature.
4. The same docs say `pkg?/feat` forwards a dependency feature only if something else already activated the optional dependency.
5. Registry-index docs still preserve namespaced and weak dependency syntax in `features2`, which means authored feature syntax is durable package metadata rather than a throwaway parser detail.
6. Cargo issue history says current investigative surfaces can still lose that author intent or produce confusing errors in `dep:` / `pkg/feat` / `pkg?/feat` edge cases.

That means the crate should now freeze one more artifact lane instead of burying it inside generic feature notes:

- one **`feature-origin.report.json`** that records whether a feature-like name is explicit, implicit, hidden by `dep:`, forwarded strongly, forwarded weakly, or still manual-review-required.

# 2026-03-08 implementation refresh — dependency identity, rename surface, and registry truth

This proposal is more implementation-ready again because current Cargo docs, registry-index docs, metadata docs, and issue history make one more receiver-facing boundary explicit: **the crate must preserve not just why a dependency participates, but which name surface actually identified it.**

Six details especially matter now:

1. Dependency-spec docs say renamed optional dependencies use the **dependency name**, not the package name, for feature syntax, and the same applies to transitive dependency-feature forwarding.
2. `cargo metadata` docs say the `packages` array reproduces manifest information while the `resolve` graph can be target-filtered, which means identity and scope need to stay separate.
3. Registry-index docs say renamed dependencies are represented differently across publish API / index / `cargo metadata`: the alias and original package name swap fields depending on the surface.
4. The original rename-dependency tracking issue explicitly called out `cargo metadata` support and CLI feature-namespace ambiguity as real implementation concerns, not solved background detail.
5. Open issue history says dependencies inherited from `[workspace.dependencies]` still cannot simply be renamed from the member side.
6. Recent issue history shows renamed + gated dependencies can still fall into private-registry / publish / verification edge cases where another person needs a compact identity explanation instead of a vague missing-package error.

That means the crate should now freeze one more artifact lane instead of burying it inside generic feature notes:

- one **`dependency-identity.report.json`** that records the local dependency key, original package name, rename state, feature-reference token, metadata/index identity surfaces, and whether the answer stays exact, conservative, or manual-review-required.

# 2026-03-08 implementation refresh

This proposal is now more buildable than when it first landed.

The key reason is that the official Cargo surface now supports a much sharper layering story:

1. `cargo metadata` is stable context and graph identity.
2. `cargo tree` is human-facing investigative substrate for feature and duplicate inspection.
3. `--unit-graph` and future plumbing commands are the likely path for richer machine-readable feature-resolution inputs.
4. `resolver.feature-unification`, resolver-version changes, and `resolver.incompatible-rust-versions` are policy inputs that must be pinned explicitly in any explanation bundle.
5. Existing crates like `guppy` / `hakari` are proof that graph simulation and workspace-feature reasoning are feasible, but they are not themselves the missing support artifact.
6. The next sharpened boundary is now explicit: dependency-kind lane truth and target/platform coverage truth still are not frozen into one boring review artifact.

That means this crate should own the **receiver-facing receipt layer**:

- short cause chains,
- version-choice receipts,
- duplicate-build grouping,
- lane-partition and platform-coverage reports,
- graph-diff explanations,
- explicit unknowns,
- capture-scope locks,
- and a schema that other tools can reuse without pretending Cargo already stabilized every underlying detail.


# 2026-03-16 implementation refresh — complete-output fixtures and proof-carrying explanation bundles

This proposal is more implementation-ready again because current official Cargo direction sharpens a boundary the archive had still left too fuzzy: **the resolver lane now needs a receiver-facing fixture pack, not more conceptual prose**.

Four details matter here:

1. The PubGrub-in-Cargo project goal says future resolver components should have **complete output** with enough associated information to determine that the resolver made the right decision.
2. Current resolver docs still say Cargo resolves `Cargo.lock` as if all workspace features are enabled and then runs a second pass for actual compile-time features, which means a usable explanation bundle must pin which pass and scope a report is about.
3. Current unstable docs now define `resolver.feature-unification` precisely enough to distinguish `selected`, `workspace`, and `package` policy, including the fact that `package` mode may prefer duplicate builds over one merged feature set.
4. Current `cargo tree` docs still say their output is only *pretty close* to the build plan, which means a worthy crate must freeze exactness, approximation, and manual-review boundaries in machine-readable artifacts rather than implying tree output is the truth.

That combination sharpens the missing crate again.
The worthy contribution is not “a nicer dependency tree.”
It is a **proof-carrying resolver explanation kit** that can hand another human or tool:

- one capture lock,
- one small family of reusable report schemas,
- one explicit exactness/approximation receipt,
- and one scenario corpus that keeps Cargo policy, member selection, and investigative-surface blur reviewable.

So this pass treats the proposal as a fixture-first lane and freezes one more requirement:

- the crate must ship a **schema + scenario corpus** for mixed-MSRV version choice, workspace-wide feature pressure, and inherited/renamed dependency-policy drift instead of leaving those stories buried in prose examples.

# What it provides

- `resolve-why.lock` — pins Cargo version, resolver version, `resolver.incompatible-rust-versions` policy, feature-unification mode, selected workspace packages, target assumptions, and capture scope.
- `feature-causes.json` — explains which package/feature edges caused each resolved feature to become active.
- `version-choices.json` — explains chosen versions, lockfile influence, resolver-policy influence, MSRV preference/fallback, and rejected-alternative visibility when available.
- `duplicate-builds.json` — groups repeated builds of the same package version by target kind, feature split, host/target separation, or workspace/policy split.
- `lane-partition.report.json` — explains whether normal/build/proc-macro/dev lanes were observed separately or merged in the investigative surface.
- `platform-coverage.report.json` — records which target-specific clauses were actually in scope for the selected build.
- `unification-scope.report.json` — records which packages participated in feature unification and whether `selected`, `workspace`, or `package` policy explains the observed result.
- `feature-intent.report.json` — records positive feature requests, negative feature intent, and whether workspace pressure overrode the subject.
- `dependency-origin.report.json` — records whether an effective dependency policy came from a workspace dependency, a member dependency, a target-specific inherited edge, or a conservative merge of those sources.
- `feature-origin.report.json` — records whether a feature-like token was explicit, implicit, hidden by `dep:`, or weakly forwarded, and whether it activated a dependency directly or only conditionally.
- `dependency-identity.report.json` — records the local dependency key, original package name, feature-reference token, metadata/index field mapping, and whether rename/inheritance/registry quirks keep the answer conservative.
- `resolution-diff.report.json` — categorized explanation of what changed between two captures.
- `resolver-choice.receipt.json` — exact commands, data sources, build-equivalence claims, schema versions, caveats, and manual-review flags used to produce the bundle.
- `cargo resolve-why capture` — materializes one explanation bundle for the current workspace or selected package set.
- `cargo resolve-why explain <pkg>` — prints the shortest useful cause chain for one package, feature, or duplicate-build group.
- `cargo resolve-why diff <old> <new>` — explains *why* the resolved graph changed, not just that it changed.
- `*.resolvewhybundle.zip` — portable artifact for CI, code review, support, or “why did Cargo do this?” debugging.

# What the crate should provide other people

1. **A boring explanation layer** above resolver docs, tree output, and evolving plumbing output.
2. **Machine-readable cause chains** for feature activation and version/duplicate-build outcomes.
3. **Version-choice receipts that stay honest about MSRV heuristics** in mixed-Rust-version workspaces.
4. **Lane-partition reports** so another person can tell whether a claim is about a normal, build/proc-macro, or dev feature lane.
5. **Platform-coverage reports** so target-specific dependency clauses are recorded as in-scope, out-of-scope, or all-target-graph-only.
6. **Unification-scope reports** so another person can see which workspace members were allowed to influence the resolver answer.
7. **Feature-intent reports** so another person can tell what the subject explicitly asked Cargo to keep on or off.
8. **Dependency-origin reports** so another person can tell whether a feature/default-feature state came from `[workspace.dependencies]`, the member manifest, or a target-specific inherited edge.
9. **Feature-origin reports** so another person can tell whether a feature-like name was public, implicit, intentionally hidden, or only conditionally meaningful through weak forwarding.
10. **Dependency-identity reports** so another person can tell which local dependency key, package name, and rename surface actually referred to the same thing across manifests, metadata, and registry publication.
11. **A review artifact** maintainers can attach to PRs or CI when graph choices change unexpectedly.
12. **A shared vocabulary** for IDEs, CI systems, and Cargo-adjacent tools.
13. **An honest boundary** between observed Cargo facts, unstable richer imports, and conservative reconstruction.
14. **Selection-scope locks** so “workspace build succeeded” versus “member build failed” can be explained instead of hand-waved.

# Persona / who it’s for

- workspace maintainers
- CI and release engineers
- developers confused by feature-resolution surprises
- Cargo-adjacent tool authors

# Users & user stories

- **Library maintainer**: “Tell me why this optional dependency is active even though I never enabled it directly.”
- **Workspace owner**: “Explain why the same crate version was built twice and whether we can collapse that split.”
- **Reviewer**: “Show me what changed in resolution after this manifest edit, and why.”
- **Release engineer**: “Why did the lockfile move to this version, and was it a policy, resolver, or manifest effect?”
- **Mixed-MSRV workspace owner**: “Did Cargo choose this lower version because of one member’s `rust-version`, and is that a heuristic or a hard floor?”
- **Support engineer**: “Why did `cargo check --workspace` pass but `cargo check -p user1` fail?”
- **Tool author**: “Reuse one reason schema instead of parsing tree output, lockfile diffs, and unstable JSON separately.”

# Prior art (and why it’s insufficient)

- The Cargo resolver docs explain the model and even include troubleshooting commands, but they are not a reusable artifact.
- `cargo tree -e features`, `cargo tree --invert`, and `cargo tree --duplicates` are useful, but still mostly a human-inspection workflow and explicitly not guaranteed to equal the exact build plan.
- `cargo metadata` is stable and useful, but the Cargo plumbing goal explicitly notes that it excludes feature resolution.
- `--unit-graph` can expose build-unit and feature-resolution-adjacent information, but it is still unstable substrate rather than a stable review bundle.
- `guppy` gives excellent programmatic graph access and Cargo-build simulation, but it starts from `cargo metadata` and is not itself a portable “why did this happen?” receipt format.
- `cargo hakari` is excellent at workspace feature unification and repeated-feature-set reasoning, but it is an optimization/workspace-hack tool, not a general-purpose explanation bundle for arbitrary teams and review workflows.
- Real issue reports show that workspace-wide builds can mask feature omissions or selection-sensitive failures, which means a usable crate must freeze command scope and evidence boundaries, not just dependency edges.

What remains missing is a **cause-chain / version-choice / duplicate-build / diffable receipt layer** that tools can consume and humans can review.

# Design goals

1. **Explanation-first** — the output must answer “why”, not merely serialize the graph.
2. **Resolver-honest** — preserve unknowns and do not pretend Cargo exposed more than it actually did.
3. **Version-choice-aware** — lockfile and policy influence must be first-class, not a footnote.
4. **MSRV-aware** — mixed `rust-version` workspaces must be first-class, not buried in a troubleshooting appendix.
5. **Duplicate-aware** — repeated builds of the same package version must be first-class.
6. **Lane-explicit** — normal/build/proc-macro/dev differences must be visible whenever they matter.
7. **Platform-explicit** — target-specific clauses must say whether they were selected, omitted, or only visible in an all-target graph.
8. **Diff-friendly** — a changed resolution should come with categorized reasons.
9. **Selection-sensitive** — command/member/target scope must be pinned so “same workspace, different outcome” is explainable.
10. **Cargo-adjacent** — wrap stable and evolving Cargo outputs rather than reimplementing the resolver.
11. **Import-friendly** — treat `cargo tree`, `cargo metadata`, `--unit-graph`, and future plumbing outputs as substrate, not competition.

# MVP surface

- Minimal types:
  - `ResolveWhyLock`
  - `FeatureCause`
  - `VersionChoice`
  - `DuplicateBuildGroup`
  - `LanePartitionReport`
  - `PlatformCoverageReport`
  - `UnificationScopeReport`
  - `FeatureIntentReport`
  - `DependencyOriginReport`
  - `FeatureOriginReport`
  - `ResolutionDiffReport`
  - `ResolverChoiceReceipt`
  - `ResolveWhyBundle`
- Minimal functions:
  - `capture_resolution_snapshot()`
  - `explain_feature_causes()`
  - `summarize_version_choices()`
  - `group_duplicate_builds()`
  - `report_lane_partition()`
  - `report_platform_coverage()`
  - `explain_unification_scope()`
  - `report_feature_intent()`
  - `report_dependency_origin()`
  - `report_feature_origin()`
  - `diff_resolution_causes()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `cargo-metadata`
  - `tree`
  - `manifest-scan`
  - `nightly-unit-graph`
  - `guppy-adapter`

# Suggested data-source layering

## Stable first
- `cargo metadata --format-version=1`
- `cargo tree --workspace --target all --all-features --edges features`
- `cargo tree --workspace --target all --all-features --duplicates`
- manifest `[features]` token scanning with preservation of `dep:`, `pkg/feat`, and `pkg?/feat` authored forms
- `cargo metadata --format-version=1` with explicit `--filter-platform` decisions when target coverage matters
- lockfile diffing
- manifest / workspace selection capture

## Optional richer imports
- `cargo +nightly ... --unit-graph -Z unstable-options`
- `-Z feature-unification`
- future plumbing-phase commands if they stabilize or mature

## Optional ecosystem adapters
- `guppy` graph import
- `hakari`-style workspace reasoning overlays for repeated feature-set diagnosis

# Compatibility story

- Works above today’s resolver docs and `cargo tree` / metadata surfaces.
- Can import richer nightly `--unit-graph` data when available.
- Can later consume official plumbing commands if Cargo stabilizes phase-oriented resolver/feature outputs.
- Must preserve whether explanations came from direct Cargo output, reconstructed cause chains, or third-party graph simulation.
- Must preserve whether the bundle is making a **close-to-build** claim or an **exact-for-this-command** claim.
- Should remain useful across resolver-version, MSRV-policy, and feature-unification evolution because the receipt layer pins those assumptions explicitly.

# Conformance & fixtures

- one fixture with **workspace feature forwarding**,
- one fixture with **package-mode feature splits**,
- one fixture with **lockfile version-choice drift**,
- one fixture with **mixed-MSRV workspace version choice**,
- one fixture where **manual review is required** because Cargo did not expose enough detail,
- one fixture where **workspace selection masks a missing feature**,
- one fixture where **normal and dev lanes appear merged in `cargo tree`**,
- one fixture where a **target-specific dependency clause is out of scope for the selected target**,
- one fixture where **workspace mode allows an out-of-selection member to influence the answer**,
- one fixture where **`default-features = false` is masked by workspace pressure**,
- one fixture where **the command subject (`--bin`) differs from the effective feature pressure source**,
- one fixture where **a workspace dependency disables defaults but a member inherited dependency re-enables them**,
- and one fixture where **target-specific inherited dependency policy stays manual-review-required**.

Goldens should prefer:
- short feature-cause chains,
- compact version-choice influences,
- duplicate-build group summaries,
- explicit selection scope,
- and explicit `manual_review_required` markers.

# Path to boring stability

- Stabilize reason categories before broadening command coverage.
- Start with read-only capture and diffing.
- Keep cause chains short and conservative.
- Prefer explicit “unknown because Cargo did not expose this” markers over speculative completeness.
- Keep third-party graph-simulation adapters optional so the core schema is not hostage to one ecosystem crate.

# Product plan

## 0.1 — stable receipt spine

Ship:
- `resolve-why.lock`
- `feature-causes.json`
- `version-choices.json`
- `duplicate-builds.json`
- `lane-partition.report.json`
- `platform-coverage.report.json`
- `unification-scope.report.json`
- `feature-intent.report.json`
- `dependency-origin.report.json`
- `resolver-choice.receipt.json`
- `notes.md`

Focus:
- stable Cargo inputs,
- short cause chains,
- manual-review markers,
- selection-scope capture,
- dependency-kind lane truth,
- target/platform coverage truth,
- and MSRV-aware version-choice explanations.

## 0.2 — richer imports without changing the user contract

Add optional support for:
- `--unit-graph`,
- `resolver.feature-unification`,
- better duplicate-build diagnosis,
- and stronger exact lane partition when richer unit/build surfaces are available.

Constraint:
- keep the receipt vocabulary stable even if richer imports remain nightly.

## 0.3 — CI and review ergonomics

Add:
- diff summaries meant for PR comments,
- `manual_review_required` exit modes,
- redaction presets,
- and stable bundle compression/import helpers.

Constraint:
- do not turn the crate into a graph warehouse or dashboard.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that explain why features, chosen versions, duplicate builds, dependency-kind lane states, and target-specific coverage are present in one resolved graph — and why that graph changed across two captures — using a compact, conservative why-bundle with explicit scope locks and manual-review boundaries.

# De-risk plan

1. Start with package/feature cause chains and version-choice receipts.
2. Add `resolve-why.lock` before broadening output types so support bundles always pin command scope and resolver policy.
3. Keep explanations conservative when Cargo does not expose enough detail.
4. Validate against real workspaces with known feature-split pain, lockfile surprises, and mixed-MSRV workspaces.
5. Add richer nightly and third-party graph imports only after the reason taxonomy settles.

# Non-goals

- Not a replacement for Cargo’s resolver.
- Not a new lockfile format.
- Not a generic graph-visualization app.
- Not a promise to reconstruct every rejected solver branch.
- Not a workspace-hack generator.
- Not a claim that one receipt can always recover the exact build truth from stable Cargo commands alone.

# Architecture & API sketch

```rust
pub struct ResolveWhyLock {
    pub resolver_version: String,
    pub incompatible_rust_versions: Option<String>,
    pub selected_members: Vec<String>,
}

pub struct VersionChoice {
    pub package: String,
    pub selected_version: String,
    pub influences: Vec<String>,
}

pub struct DuplicateBuildGroup {
    pub package: String,
    pub version: String,
    pub causes: Vec<String>,
}

pub struct LanePartitionReport {
    pub subject_package: String,
    pub overall_exactness: String,
}

pub struct PlatformCoverageReport {
    pub requested_targets: Vec<String>,
    pub overall_exactness: String,
}

pub fn capture_resolution_snapshot(root: &Path) -> Result<ResolveWhyBundle>;
pub fn explain_feature_causes(bundle: &ResolveWhyBundle, package: &str) -> Vec<FeatureCause>;
pub fn summarize_version_choices(bundle: &ResolveWhyBundle) -> Vec<VersionChoice>;
pub fn group_duplicate_builds(bundle: &ResolveWhyBundle) -> Vec<DuplicateBuildGroup>;
pub fn report_lane_partition(bundle: &ResolveWhyBundle, package: &str) -> LanePartitionReport;
pub fn report_platform_coverage(bundle: &ResolveWhyBundle) -> PlatformCoverageReport;
pub fn diff_resolution_causes(old: &ResolveWhyBundle, new: &ResolveWhyBundle) -> ResolutionDiffReport;
```

Bundle draft: `resolve-why.lock`, `feature-causes.json`, `version-choices.json`, `duplicate-builds.json`, `lane-partition.report.json`, `platform-coverage.report.json`, `unification-scope.report.json`, `feature-intent.report.json`, `dependency-origin.report.json`, `resolution-diff.report.json`, `resolver-choice.receipt.json`, `notes.md`.

# Security / safety model

- Preserve exact Cargo/resolver/feature-unification/MSRV assumptions.
- Support redaction of private paths and unpublished crate names in shared bundles.
- Never present reconstructed cause chains as direct Cargo ground truth without labeling them.
- Keep unknown or unstable fields visible instead of silently normalizing them away.
- Make third-party adapter provenance explicit in the receipt.
- Preserve whether build equivalence is exact, approximate, or not claimed.

# Maintenance & governance plan

- Track Cargo resolver, `cargo tree`, `cargo metadata`, plumbing-surface, and feature-unification evolution.
- Track mixed-MSRV resolver behavior and selection-sensitive workspace issues.
- Maintain a compact reason taxonomy with versioned schemas.
- Keep fixtures for common workspace/resolver edge cases.
