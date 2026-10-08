---
id: P-0489
title: Cargo Build-Dir Consumer Transition Kit — consumer inventories, path contracts, and upgrade-safe transition receipts
status: idea
domains: [cargo, build, ci, tooling, devtools, migration]
last_reviewed: 2026-03-23
evidence:
  - https://doc.rust-lang.org/cargo/reference/build-cache.html
  - https://doc.rust-lang.org/cargo/reference/config.html
  - https://doc.rust-lang.org/cargo/reference/external-tools.html
  - https://doc.rust-lang.org/cargo/reference/build-scripts.html
  - https://doc.rust-lang.org/cargo/reference/environment-variables.html
  - https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
  - https://doc.rust-lang.org/beta/releases.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html#build-dir-new-layout
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
  - https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html
  - https://github.com/rust-lang/rust-analyzer/issues/20150
---

# Problem

Cargo’s story is now clearer than it used to be:

- `build.build-dir` is a real stable configuration surface,
- intermediate artifacts are explicitly described as internal to Cargo and rustc,
- release notes now warn that tools depending on build-dir internals may break as users change layout,
- nightly Cargo has `-Zbuild-dir-new-layout`,
- and the build-dir-layout / user-wide-cache goals explicitly say tooling that accesses intermediate artifacts needs a transition path.

That is healthy upstream progress.
It also creates a sharper ecosystem seam.

A lot of real Rust tooling still sits *near* Cargo internals:

- CI scripts scrape `target/debug/deps` for rlibs or dep-info,
- packaging helpers walk `target/<triple>/<profile>/build` looking for build-script outputs,
- local tools assume profile names or target-directory conventions,
- editor / wrapper tooling infers behavior from current layout accidents,
- and support engineers still debug “Cargo upgrade broke our helper script” by manually diffing directories.

Today, Cargo gives important substrate, but not the whole migration workflow:

- build-cache docs explain the split between final and intermediate artifacts,
- config docs document `build.build-dir`,
- build-script docs and environment-variable docs explain `OUT_DIR`, `CARGO_BIN_EXE_<name>`, and related safer surfaces,
- external-tools JSON exposes produced artifacts and build-script execution data,
- and project-goal docs explain why layout rework exists.

What is still missing is a **receiver-facing transition crate** that can answer:

- what workflow each local tool or script was really trying to accomplish,
- which local tools or scripts still rely on Cargo internals,
- which of those assumptions have an available stable adapter,
- which assumptions are only conditionally safe,
- how an old observation compares to a new Cargo layout or new `build-dir` mode,
- and what bundle a maintainer can hand another maintainer instead of saying “we scrape `target/` somewhere.”

The missing crate is not another cache manager.
The missing crate is not another artifact producer.
The missing crate is a **Cargo Build-Dir Consumer Transition Kit**: a library and cargo-adjacent tool that inventories build-dir consumers, derives conservative path contracts, and emits **transition receipts** for layout migration.

# What it provides

## Core bundle for 0.1

- `consumer-inventory.manifest.json` — declares local scripts, helpers, CI steps, adapters, or support workflows that touch Cargo outputs.
- `layout.snapshot.json` — normalized observation of target-dir/build-dir roots, profile partitions, target partitions, and discovery provenance.
- `consumer-audit.report.json` — flags dependence on `deps/`, `build/`, profile-name assumptions, dep-info scraping, build-script-output scraping, or final-artifact confusion.
- `consumer-need.report.json` — states what the consumer was really trying to do: integration-test binary, build-script-owned output, final artifact, user-requested artifact, dep-info, or only a guessed topology path.
- `path-contract.json` — small abstract contract for common needs such as `final_artifact`, `dep_info`, `build_script_out`, `integration_test_binary`, `manual_review_required`, and `no_safe_contract`.
- `adapter-plan.json` — suggested next moves such as `switch_to_artifact_handoff`, `use_build_script_json`, `use_out_dir_contract`, `use_cargo_bin_exe`, `support_both_layouts`, `keep_scraping_for_now`, or `blocked_on_upstream`.
- `adapter-authority.receipt.json` — states what source class actually justifies the adapter claim: Cargo docs, release notes, official testing guidance, unstable docs, a project-goal note, or only a local heuristic / issue-thread workaround.
- `adapter-viability.report.json` — per-consumer viability facts for the chosen adapter: whether it is documented on stable, documented only for a newer Cargo floor, nightly-only, heuristic-only, or still blocked on upstream; plus fallback and dual-support pressure.
- `windowed-viability.matrix.json` — a compact version / channel / layout-mode matrix so a receiver can see which claims hold on legacy layout, custom `build.build-dir`, or `-Zbuild-dir-new-layout` rehearsal.
- `transition.receipt.json` — records Cargo/toolchain/build-dir mode, consumer findings, chosen adapters, residual risks, and redaction policy.
- `rehearsal-support-bundle.manifest.json` — portable inventory joining need, authority, viability, and transition artifacts for issue reports and CI rehearsals.
- `transition.diff.json` — compares two receipts and classifies `layout_changed`, `consumer_became_risky`, `adapter_added`, `adapter_removed`, `risk_reduced`, `manual_review_required`, and `safe_noop`.
- `*.builddirbundle.zip` — portable audit bundle for CI maintainers, tool authors, or Cargo-upgrade rehearsals.

## CLI shape

- `cargo build-dir-transition scan` — observe one workspace/build and emit the core bundle.
- `cargo build-dir-transition doctor` — explain which consumers are likely to break and what safer surface exists.
- `cargo build-dir-transition diff <old> <new>` — compare old/new receipts across Cargo versions, `build.build-dir` changes, or `-Zbuild-dir-new-layout` rehearsals.
- `cargo build-dir-transition redact` — rewrite existing bundles for issue sharing without leaking local paths or proprietary tool names.

# What the crate should provide other people

1. **A boring inventory** of which workflows still depend on internal Cargo layout.
2. **One consumer-need report** so a receiver can tell whether a helper really wants a binary, build-script-owned output, a final artifact, dep-info, or only a guessed topology path.
3. **A conservative path-contract layer** so downstream helpers stop pretending `target/debug/deps` is a public API.
4. **An adapter plan with an authority receipt** pointing to safer existing surfaces while making the source class for that advice explicit.
5. **One honest windowed-viability matrix** so a maintainer can tell whether advice is stable now, stable only above a Cargo floor, nightly-only, heuristic-only, or still blocked on upstream.
6. **A diffable transition + rehearsal bundle** for Cargo upgrades, `build.build-dir` adoption, or `-Zbuild-dir-new-layout` trials.
7. **A machine-readable migration guide** that can be attached to issues and CI reviews.

# Who it is for

- tool authors consuming Cargo intermediate outputs
- CI/build engineers maintaining scripts around `target/` or `build-dir`
- workspace maintainers adopting `build.build-dir` or rehearsing layout changes
- support engineers debugging “Cargo upgrade broke our helper” incidents
- editor / wrapper authors who need to know whether they are still relying on fragile paths

# User stories

- **Tool author**: “Tell me every place our tool still assumes Cargo’s current layout and whether a safer adapter exists today.”
- **CI owner**: “Rehearse a new `build.build-dir` mode and attach one receipt to the migration PR.”
- **Workspace maintainer**: “Diff old and new observations without hand-walking target/build directories.”
- **Support engineer**: “Hand another maintainer one bundle showing whether the breakage is a layout change, a consumer assumption, or a missing stable handoff surface.”

# Prior art (and why it is insufficient)

- Cargo build-cache docs clearly split final vs intermediate artifacts and explicitly warn that build-dir layout is internal. Good warning, not a migration bundle.
- Config docs make `build.build-dir` real and stable. Good control surface, not a consumer audit.
- Build-script docs and environment-variable docs document `OUT_DIR`, `CARGO_BIN_EXE_<name>`, and related safer pathways. Good point solutions, not a whole-workspace transition map.
- External-tools JSON exposes produced artifacts and build-script-executed data. Good substrate, not a policy/conservative-contract layer.
- Build-dir-layout and user-wide-cache goals explicitly say tooling needs a transition path. Good motivation, not a receiver-facing crate.
- rust-analyzer’s build-dir support discussion shows real downstream tools are already adapting to this changing world. Good signal, not a reusable migration kit.
- The archive already has **P-0471 Cargo Artifact Handoff Kit**. That is about *final* produced artifacts.
- The archive already has **P-0490 Cargo Lock Contention Witness Kit**. That is about *live waits and who blocked whom*.
- The archive already has **P-0494 Cargo Compile-Time-Deps Workflow Kit**. That is about *tool-workflow parity and fallback*.

What remains missing is the **consumer-inventory / path-contract / transition-receipt** layer.

# 2026-03-23 need / authority refresh — the missing value is no longer just “an adapter exists”

The March 2026 testing post and the current Cargo docs now make one more design boundary explicit.
It is not enough to say:
- a helper scraped a fragile path,
- a safer adapter was suggested,
- and the migration therefore exists.

A serious crate in this lane now needs to keep four truths distinct:

1. **consumer need** — what the workflow was really trying to accomplish,
2. **adapter authority** — what source class actually justifies the replacement advice,
3. **windowed viability** — which Cargo / channel / layout windows the advice really covers,
4. **rehearsal bundle truth** — how those facts travel together for legacy-vs-new-layout rehearsals.

Why this matters:
- the testing post names concrete failure modes, but not every failure mode has the same authoritative replacement surface;
- `CARGO_BIN_EXE_*` is a much stronger answer when the real need is an integration-test binary than when a consumer is really asking for an arbitrary compiler-oriented artifact;
- `OUT_DIR` is strong when the consumer owns build-script-generated output, but weak when the helper is really trying to recover workspace topology;
- and nightly-only routes like `--artifact-dir` or new-layout rehearsal should not be marketed as timeless stable migration truth.

So **P-0489** should now explicitly own:
- `consumer-need.report.json`,
- `adapter-authority.receipt.json`,
- `windowed-viability.matrix.json`,
- and `rehearsal-support-bundle.manifest.json`

above the earlier inventory / path-contract / adapter-plan / transition-receipt lane.

# 2026-03-16 call-for-testing refresh — failure modes are now concrete

This proposal is materially stronger now because Cargo's March 2026 call for testing on **Build Dir Layout v2** stops speaking in vague warnings and names concrete downstream breakage families.

The official post says five things that matter a lot for crate design:

1. Cargo still treats the build-dir layout as internal-only, **but many projects rely on unspecified details because features are missing today**.
2. Rust maintainers are explicitly asking people to run **tests, release processes, and anything else touching build-dir/target-dir** under `-Zbuild-dir-new-layout`.
3. The post lists concrete failure modes and partial adapter advice instead of abstract “tooling may break” language.
4. Some of that advice is **version-windowed** rather than timeless: for `[[bin]]` path inference from tests, the post recommends `std::env::var_os("CARGO_BIN_EXE_*")` for Cargo 1.94+ while preserving fallback pressure for older Cargo.
5. Cargo's 1.94 changelog now notes that Cargo's own testsuite was reworked to use `CARGO_BIN_EXE_*`, which makes that adapter a stronger authority class than a local convention.

That means **P-0489** should now be read less as a generic migration essay and more as a crate that emits one boring bundle for specific consumer families the ecosystem can already recognize — and that also records **whether the recommended adapter is actually viable in the caller's Cargo window**:

- **bin-path inference from test paths** → often the sharper adapter is `CARGO_BIN_EXE_*`, possibly with an older-Cargo fallback lane.
- **build-script / helper inference of target-dir from binaries or `OUT_DIR`** → often the sharper answer is an explicit build-script-owned contract, not another round of path guessing.
- **user-requested artifact lookup from `rustc` outputs** → often the sharper answer is a conservative handoff contract or `manual_review_required`, not a fake promise that Cargo internals are stable.

That concrete failure-mode vocabulary improves the crate in three ways:

- it makes the first fixture pack more honest,
- it makes adapter planning less hand-wavy,
- and it gives maintainers a way to attach one receipt to an upstream issue instead of a screenshot of a broken `target/` guess.

# Main design rule

Treat Cargo’s current layout as **observable substrate**, not **public contract**.
The crate should help people move off fragile assumptions without pretending every use case already has a perfect stable replacement.

# Design goals

1. **Internal-layout honest** — never imply that today’s intermediate paths are stable API.
2. **Consumer-first** — describe what local tools and scripts need, not just how Cargo stores files.
3. **Adapter-first** — prefer safer existing surfaces when they actually fit.
4. **Transition-friendly** — make Cargo upgrades rehearseable before they break CI.
5. **Conservative** — preserve observed fact versus suggested inference.
6. **Distinct from cache policy** — stay focused on migration, not GC, leasing, or cache governance.

# Strongest current artifact contract

A worthy 0.1 should probably hand another person:

1. one `consumer-inventory.manifest.json`,
2. one `layout.snapshot.json`,
3. one `consumer-audit.report.json`,
4. one `path-contract.json`,
5. one `adapter-plan.json`,
6. one `adapter-viability.report.json`,
7. one `transition.receipt.json`,
8. optionally one `transition.diff.json`,
9. and one short `notes.md`.

That is enough to answer:

- what was relying on Cargo internals,
- what evidence supports that diagnosis,
- which safer surface might replace it,
- and whether the upgrade is safe, risky, or still blocked on upstream.

# Safer adapter vocabulary the crate should prefer

The first version should aggressively reuse existing Cargo surfaces instead of inventing fantasy APIs:

- `use_cargo_bin_exe` — when the real need is “find the built integration-test binary.”
- `use_out_dir_contract` — when the real need is “consume build-script-owned outputs” rather than hard-coding `target/.../build/...`.
- `use_build_script_json` — when the real need is parsed build-script execution facts available via Cargo JSON messages.
- `use_dep_info` — when the real need is dependency tracking for external build-system integration.
- `switch_to_artifact_handoff` — when the real need is a final artifact, not an internal intermediate path.
- `keep_scraping_for_now` — when no honest adapter exists yet.
- `blocked_on_upstream` — when the gap is real and should stay explicit.
- `support_both_layouts` — when a local helper must temporarily tolerate legacy and rehearsed layouts during migration.

Every adapter claim should also carry an explicit **authority / availability class**. A named adapter is not enough; the bundle should say whether the advice is documented stable, documented but version-windowed, nightly-only, heuristic-only, or still blocked on upstream.

# MVP surface

## Types
- `ConsumerInventory`
- `LayoutSnapshot`
- `ConsumerAuditReport`
- `PathContract`
- `AdapterPlan`
- `TransitionReceipt`
- `TransitionDiff`
- `BuildDirBundle`

## Functions
- `capture_layout_snapshot()`
- `inventory_consumers()`
- `audit_consumers()`
- `derive_path_contracts()`
- `plan_adapters()`
- `diff_transition_receipts()`
- `write_transition_bundle()`

## Features
- `cargo`
- `serde`
- `path-scan`
- `ci`
- `markdown`
- `redaction`

# Compatibility story

- Stable-first: should already be useful with `build.build-dir`, build-cache docs, build-script docs, and Cargo JSON messages.
- Nightly-aware: can optionally rehearse `-Zbuild-dir-new-layout` and future fine-grain-locking changes, but must stay useful on stable.
- Cargo-library-agnostic: should prefer CLI/json surfaces over linking to Cargo internals as a library.
- Provenance-preserving: every finding should say whether it came from config, JSON messages, path scan, static script scan, or manual annotation.

# Conformance & fixtures

The fixture family should at minimum cover:

1. `deps_scrape_ci`
   - a CI helper scraping `target/debug/deps`
   - verdict should be `adapter_available` or `manual_review_required`
2. `out_dir_helper`
   - a helper scraping `target/.../build/...` where the sharper contract is `OUT_DIR` / build-script JSON
3. `new_layout_rehearsal`
   - same workspace observed under legacy layout and `-Zbuild-dir-new-layout`
   - diff should report changed risk without overclaiming breakage
4. `redirect_to_artifact_handoff`
   - proves that some consumers do not need intermediate layout at all
5. `bin_path_from_test_inference`
   - a test or harness infers a `[[bin]]` path from a `[[test]]` path
   - the crate should prefer `CARGO_BIN_EXE_*` when the Cargo version and lane allow it
   - the bundle should preserve that this adapter is version-windowed rather than timeless
6. `target_dir_from_out_dir_inference`
   - a build helper tries to recover target-dir from its own binary path or `OUT_DIR`
   - the crate should distinguish build-script-owned output from guessed workspace layout
   - the viability report should stay conservative when `OUT_DIR` is documented but the consumer need is still ambiguous
7. `rustc_user_requested_artifact_lookup`
   - a consumer wants a user-requested artifact and currently scrapes compiler-oriented locations
   - the crate should separate stable handoff possibilities from true upstream gaps
   - and it should not market a nightly-only escape hatch as a stable adapter

Goldens should preserve:

- `observed_from`
- `evidence_strength`
- `manual_review_required`
- `adapter_available`
- `blocked_on_upstream`
- `risk_reduced`
- `layout_changed`

# Path to boring stability

- Stabilize the smallest useful contract vocabulary before adding automatic rewrites.
- Keep the first version read-only: inventory, audit, adapter planning, receipts, and diffs.
- Prefer explicit `unknown` / `manual_review_required` over fake precision.
- Keep redaction first-class so receipts can be attached to real issues.
- Let downstream teams curate organization-specific adapters on top of the core vocabulary.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that inventory local build-dir consumers, capture one layout snapshot, derive a conservative path contract plus adapter plan, and export a diffable transition receipt for Cargo upgrades or build-dir layout rehearsals.

# De-risk plan

1. Start with read-only observation and inventory.
2. Keep the path-contract vocabulary tiny and conservative.
3. Validate on one CI script, one build-script helper, and one final-artifact consumer that should be redirected.
4. Refuse automatic rewrites until enough scenario bundles prove the mapping is honest.

# Non-goals

- Not a replacement for Cargo’s build cache.
- Not a lease, GC, or shared-cache coordinator.
- Not a lock-contention profiler or scheduler.
- Not a promise that every intermediate artifact can already be given a stable path contract.
- Not an excuse to link to Cargo internals as a library and re-export them as “stability.”

# Architecture sketch

```rust
pub enum EvidenceStrength {
    Observed,
    StrongInference,
    WeakInference,
    ManualAnnotation,
}

pub struct TransitionReceipt {
    pub cargo_version: String,
    pub build_dir_mode: String,
    pub consumer_count: usize,
    pub risky_consumers: Vec<String>,
    pub adapters_offered: Vec<String>,
    pub overall_verdict: String,
}

pub fn capture_layout_snapshot(root: &Path) -> Result<LayoutSnapshot>;
pub fn inventory_consumers(root: &Path) -> Result<ConsumerInventory>;
pub fn audit_consumers(root: &Path, snapshot: &LayoutSnapshot) -> Result<ConsumerAuditReport>;
pub fn derive_path_contracts(audit: &ConsumerAuditReport) -> Result<Vec<PathContract>>;
pub fn plan_adapters(audit: &ConsumerAuditReport) -> Result<AdapterPlan>;
pub fn diff_transition_receipts(old: &TransitionReceipt, new: &TransitionReceipt) -> TransitionDiff;
```

Bundle draft:
`consumer-inventory.manifest.json`, `layout.snapshot.json`, `consumer-audit.report.json`, `path-contract.json`, `adapter-plan.json`, `transition.receipt.json`, optional `transition.diff.json`, `notes.md`.

# Security / safety model

- Treat repository roots, CI paths, proprietary helper names, and private package names as sensitive by default.
- Support literal, redacted, relative, and omitted path policies.
- Separate observed facts from operator annotations.
- Never label an inferred path as a stable Cargo contract.
- Keep `manual_review_required` explicit whenever the mapping is uncertain.

# Maintenance & governance plan

- Track Cargo build-cache docs, config docs, unstable build-dir-new-layout docs, and release-note warnings.
- Maintain fixture corpora for `deps/` scraping, build-script-output scraping, and artifact-handoff redirects.
- Add adapters only when backed by stable surfaces or conservative documented workflows.
- Keep schemas compact, versioned, and reviewable.

# Milestones

## 0.1
- consumer inventory
- layout snapshot
- audit report
- transition receipt

## 0.2
- path contracts
- adapter plans
- receipt diffing
- redaction support

## 1.0
- stable contract vocabulary
- curated migration corpus
- downstream adapters for common CI / tooling cases

# Open questions

- What is the smallest useful path-contract vocabulary that still helps real consumers move off directory scraping?
- Which findings can be produced from Cargo JSON/config alone, and which require static script/path scanning?
- How many adapter classes can be honest before the tool becomes too magical?
- Should the first version emit one contract per consumer or one merged workspace-wide plan with local overrides?

# Sources

- Cargo build-cache docs: https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo config docs (`build.build-dir`): https://doc.rust-lang.org/cargo/reference/config.html
- Cargo external-tools JSON docs: https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo build-script docs: https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo environment variables docs: https://doc.rust-lang.org/cargo/reference/environment-variables.html
- Rust release notes warning for build-dir consumers: https://doc.rust-lang.org/beta/releases.html
- Cargo unstable docs (`build-dir-new-layout`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-dir-new-layout
- Build-dir layout project goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- User-wide build cache goal: https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html
- rust-analyzer `build-dir` support issue: https://github.com/rust-lang/rust-analyzer/issues/20150
