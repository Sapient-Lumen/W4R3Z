---
id: P-0490
title: Cargo Lock Contention Witness Kit — root-sharing reports, lock-wait receipts, and mitigation bundles
status: idea
domains: [cargo, build, workspace, ide, ci, devtools]
last_reviewed: 2026-03-22
evidence:
  - https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
  - https://doc.rust-lang.org/cargo/reference/build-cache.html
  - https://doc.rust-lang.org/cargo/reference/environment-variables.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
  - https://doc.rust-lang.org/cargo/reference/unstable.html#build-dir-new-layout
  - https://rust-analyzer.github.io/book/faq.html
  - https://rust-analyzer.github.io/book/configuration
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
  - https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
---

# Problem

Rust developers do not just suffer from slow builds. They also suffer from **builds that cannot make progress because another tool is holding the relevant lock or cache root**.

Recent official material makes that seam sharper:

- the compiler performance survey explicitly calls out IDE/Cargo blocking and target-directory contention as a meaningful daily problem,
- the rust-analyzer FAQ now very explicitly documents that rust-analyzer and manual Cargo commands can block one another and suggests a separate target directory as a workaround,
- rust-analyzer configuration now exposes `cargo.targetDir` precisely to avoid lock contention at the cost of duplicated artifacts,
- Cargo’s own docs and internals show that global package/index caches are actively locked to coordinate multiple Cargo processes,
- and Cargo’s newer build-dir-layout work says the point of the new layout is partly to unblock **caching and locking improvements**.

That means the missing crate is not another profiler and not another cache implementation.

The missing crate is a **Cargo lock contention witness kit**: a crate and cargo-adjacent tool that turns “Cargo is waiting on something” into a portable **wait receipt, collision diagnosis, and mitigation bundle**.

## 2026-03-08 topology refresh

The frontier is now sharper than it looked on first draft because current docs make three different root classes explicit enough to model separately:

- Cargo now documents **target-dir** versus **build-dir** directly: final end-user artifacts live in the target directory, while intermediate compiler/build-script artifacts live in the build directory.
- rust-analyzer documents a dedicated `cargo.targetDir` escape hatch and also exposes override-command / wrapper-related workflow knobs, so tool-role and command-shape drift are no longer invisible folklore.
- Cargo’s wrapper docs say `RUSTC_WORKSPACE_WRAPPER` affects the filename hash so wrapper-produced artifacts are cached separately, which means a workspace can simultaneously suffer from **shared-root waiting** and **cache-mode / wrapper splits**.

That means the missing crate should not just emit a single wait receipt. It should also export a compact **root-sharing topology** and an optional **wrapper-context receipt** so another person can tell whether the problem was:

1. a live wait on a shared root,
2. a build-dir or package-cache lane that remained shared even after target-dir changes,
3. or a wrapper-induced cache split that makes contention and duplicated work harder to reason about.


## 2026-03-16 implementation refresh — exactness, session links, and root-sharing honesty

The official substrate is now strong enough that this proposal should freeze two more receiver-facing contracts.

### 1. Target-dir changes are not the same thing as shared-root truth

Current Cargo docs explicitly distinguish **target-dir** (final artifacts) from **build-dir** (intermediate artifacts), and the March 13, 2026 build-dir-layout-v2 call-for-testing says teams should exercise anything touching `build-dir` / `target-dir` with the new layout. That same post says Cargo 1.91 already lets users separate where intermediate build artifacts live while final artifacts stay in `target-dir`.

That means a worthy crate should no longer treat “rust-analyzer uses a different target dir” as a complete explanation. The bundle should say which roots were actually shared and which were only assumed to be shared.

### 2. Cargo build-analysis creates a useful optional support seam, not perfect blocker identity

Cargo’s unstable docs now expose persisted sessions plus `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds`. That gives this crate an **optional imported-session lane**: a way to say which Cargo session overlapped the witness window and what root/toolchain/workspace facts were corroborated there.

But it does **not** magically prove which process held a lock. A session link is supporting context, not PID certainty.

### 3. The crate needs an explicit exactness ledger

A buildable version of this crate should now export:

- **`evidence-source.receipt.json`** — which facts came from Cargo stderr, Cargo config/env inspection, rust-analyzer config, best-effort process observation, imported build-analysis sessions, or manual notes.
- **`exactness.report.json`** — which high-value claims are `observed_directly`, `normalized_observed`, `conservative_inference`, or `manual_review_required`.
- **`build-analysis-session.link.json`** — optional linkage to one imported Cargo build-analysis session, explicitly marked as supporting context rather than blocker attribution.

Those three artifacts are what keep the crate from bluffing when the receiver asks the hardest questions: “which root was actually shared?” and “how sure are you that this session is the blocker?”



## 2026-03-22 implementation refresh — root authority, actor command lanes, wait windows, and mitigation cost

The current official substrate makes four receiver-facing gaps much sharper than this proposal originally modeled.

### 1. Root paths need an authority receipt, not just a guessed manifest

Cargo now documents **target-dir** and **build-dir** as separate user-facing roots, with different configuration and environment-variable routes. rust-analyzer independently exposes `cargo.targetDir`, which can point to a dedicated rust-analyzer-only lane or a subdirectory of the existing target tree.

That means a worthy crate should promote **`root-authority.receipt.json`** into first-class status.
It should record, for each relevant root, whether the path came from:

- Cargo defaults,
- Cargo config (`build.target-dir`, `build.build-dir`),
- environment variables (`CARGO_TARGET_DIR`, `CARGO_BUILD_BUILD_DIR`),
- a rust-analyzer-specific target-dir override,
- a CLI override,
- or manual annotation.

Without that receipt, a bundle can easily misdiagnose a contention story by treating a guessed default path as observed truth.

### 2. Actor roles are not enough; the command lane matters

Current rust-analyzer docs make the actor command shape explicit enough to model separately:

- the default base invocation is `cargo check --quiet --workspace --message-format=json --all-targets --keep-going`;
- build scripts / proc-macros can be routed through override commands and `per_workspace` versus `once` invocation strategies;
- rust-analyzer can use `RUSTC_WRAPPER=rust-analyzer`;
- Cargo also has the permanently-unstable `--compile-time-deps` lane intended for tools like rust-analyzer.

That means the crate should promote **`actor-command-lane.receipt.json`** into first-class status.
A support bundle should tell another person not just “editor_check was running,” but whether that actor was:

- workspace-wide or package-narrow,
- all-targets or narrower,
- build-script/proc-macro-only,
- wrapper-mediated,
- and per-workspace versus once.

### 3. Waits need a bounded window, not only a class label

The official Cargo direction now makes lock improvements an active moving target. Build-dir-layout-v2 and Cargo 1.93 development notes both say the split between build-dir and artifacts-dir is meant to reduce specific lock-contention classes, especially `cargo check`-style overlap.

That means the crate should promote **`wait-window.receipt.json`** into first-class status.
It should record:

- when the wait was first observed,
- when it ended or became unknown,
- which command phase was stalled,
- whether blocker identity was direct, supporting-session-only, inferred, or unknown,
- and whether the evidence window predates or postdates any imported build-analysis session.

### 4. Mitigations need a cost report, not just a recommendation string

The rust-analyzer configuration docs now say `cargo.targetDir` prevents lock contention **at the expense of duplicating build artifacts**. Cargo’s build-dir-layout work also makes it clear that some future locking relief is being designed upstream, which means today’s workaround may be costly and temporary rather than universally right.

That means the crate should promote **`mitigation-cost.report.json`** into first-class status.
A serious witness bundle should spell out whether the suggested fix:

- duplicates artifacts,
- fragments caches,
- changes editor or CI workflow semantics,
- narrows diagnostic/build scope,
- or depends on unstable / upstream-evolving behavior.

### 5. The lane now wants one compact support manifest

A buildable 0.1 should also export **`contention-support-bundle.manifest.json`** so another tool or person can consume the witness without guessing which receipts are expected.

# What it provides

- `contention-policy.toml` — declares which processes and roots the team cares about (`cargo`, `rust-analyzer`, `nextest`, custom wrappers, CI helpers), how much process inspection is allowed, and whether the workflow is advisory or blocking.
- `cache-root.manifest.json` — normalized view of target-dir, build-dir, package-cache roots, wrapper context, workspace identity, and toolchain facts.
- `root-authority.receipt.json` — records how each root path was determined (`default`, Cargo config, environment variable, rust-analyzer target-dir override, CLI override, or manual note) and how strong that path claim is.
- `root-sharing.report.json` — a tiny topology report that states which tool roles share which roots (`target_dir`, `build_dir`, `package_cache`, `index_cache`), whether that sharing is intended, and which roots are isolated.
- `lock-wait.receipt.json` — records one observed wait: what command stalled, which root or lock class was involved, how long it waited, which observation source saw it, and whether the blocker was known, inferred, or unknown.
- `wrapper-context.receipt.json` — optional wrapper/cache-mode facts (`RUSTC_WRAPPER`, `RUSTC_WORKSPACE_WRAPPER`, rust-analyzer wrapper usage, nested wrapper chains, and cache-hash-separation hints).
- `actor-command-lane.receipt.json` — records which concrete command shape each observed actor used (workspace versus package scope, all-targets versus narrower, build-scripts/proc-macros lane, compile-time-deps lane, wrapper posture, and invocation strategy).
- `process-role.snapshot.json` — optional local snapshot of observed contender roles (`editor_check`, `manual_build`, `test_runner`, `doc_build`, `proc_macro_bootstrap`, `ci_job`, `dependency_fetch`, `unknown_process`) and how confidently those roles were identified.
- `wait-window.receipt.json` — bounded timeline for the observed wait, including start/end, stalled phase, overlap with imported sessions, and blocker-identity exactness.
- `evidence-source.receipt.json` — records whether each fact came from Cargo stderr, Cargo config/env inspection, rust-analyzer config, process observation, an imported build-analysis session, or manual annotation.
- `exactness.report.json` — records which claims are direct observations, normalized observations, conservative inferences, or still require manual review.
- `build-analysis-session.link.json` — optional supporting context linking the witness to one imported Cargo build-analysis session without claiming that the session itself proves blocker identity.
- `collision-diagnosis.report.json` — classifies the contention as `shared_target_dir`, `package_cache_lock`, `build_dir_collision`, `wrapper_mismatch`, `cache_mode_split`, `editor_manual_conflict`, `manual_review_required`, or `unknown_wait`.
- `mitigation.plan.json` — suggests concrete next steps such as `separate_ra_target_dir`, `move_build_dir`, `pin_wrapper_policy`, `serialize_specific_jobs`, `accept_duplicate_artifacts_for_parallelism`, `review_package_cache_activity`, `try_compile_time_deps`, or `accept_wait_and_document`.
- `mitigation-cost.report.json` — receiver-facing trade-off report for each recommended mitigation: artifact duplication, cache fragmentation, workflow disruption, scope narrowing, and upstream-volatility exposure.
- `contention-support-bundle.manifest.json` — compact manifest naming the receipts in one support bundle and whether any claim still requires manual review.
- `contention.diff.json` — compares two runs or two machines and highlights contention regressions/improvements.
- `cargo contention-witness snapshot` — capture one contention witness bundle.
- `cargo contention-witness doctor` — explain why the current workspace/toolchain/editor setup is likely to block.
- `cargo contention-witness attach-session <session-id>` — attach one Cargo build-analysis session as supporting context for the witness bundle.
- `cargo contention-witness audit-exactness <bundle>` — summarize which claims were observed directly, normalized, inferred, or still manual-review-only.
- `cargo contention-witness explain-costs <bundle>` — render the mitigation-cost report in a human-readable form.
- `cargo contention-witness diff <old> <new>` — compare two contention receipts.
- `*.contention.zip` — portable support artifact for CI, IDE setup docs, or performance triage.

# What the crate should provide other people

1. **A boring answer to “who is blocking this build, on which root?”** instead of folklore about Cargo locks.
2. **A compact artifact** that support engineers and teammates can read without replaying the failure live.
3. **A topology report** that says which roles share or isolate target-dir, build-dir, and package-cache lanes.
4. **A mitigation vocabulary** for the common trade-offs: separate target dirs, duplicated artifacts, wrapper alignment, isolated build-dir lanes, or serialized jobs.
5. **A distinction between blocking and rebuilding** so teams stop conflating “this rebuilt too much” with “this waited on another process.”
6. **A bridge** between official Cargo/rust-analyzer substrate and ordinary local/CI troubleshooting.

## 0.1 artifact contract

A credible 0.1 should hand another person seven tiny files plus notes, not one giant debug dump:

- `cache-root.manifest.json` — which roots were in play (`target_dir`, `build_dir`, `package_cache`), which tool/workspace owned them, and whether the paths were observed directly or inferred from config.
- `root-sharing.report.json` — whether those roots were shared, isolated, or mixed across roles such as `editor_check`, `manual_build`, and `ci_job`.
- `root-authority.receipt.json` — where each root path claim came from and whether it was directly observed or inferred.
- `lock-wait.receipt.json` — the stalled command, wait duration, lock scope, affected root, observation provenance (`cargo_stderr`, `process_sample`, `config_scan`, `manual_annotation`), and confidence level.
- `actor-command-lane.receipt.json` — the command family/scope/invocation shape for the main observed actor or imported supporting actor.
- `wait-window.receipt.json` — the bounded time window and exactness of the wait claim.
- `collision-diagnosis.report.json` — a conservative class (`shared_target_dir`, `package_cache_lock`, `build_dir_collision`, `wrapper_mismatch`, `cache_mode_split`, `manual_review_required`, `unknown_wait`) plus the concrete facts that support it.
- `mitigation.plan.json` — 1–3 next actions with stated trade-offs rather than one “magic fix.”
- `mitigation-cost.report.json` — what each proposed mitigation costs in artifact duplication, cache reuse, workflow disruption, and volatility.
- `evidence-source.receipt.json` — the evidence lanes consumed and whether they were direct imports, normalized extracts, or manual notes.
- `exactness.report.json` — the exactness class for the high-value claims in the bundle.
- `contention-support-bundle.manifest.json` — bundle inventory and final manual-review flag.

`wrapper-context.receipt.json` and `build-analysis-session.link.json` should remain optional overlays whenever wrapper-induced cache separation or imported Cargo sessions materially explain the result.

## Suggested crate split

The archive should now treat this proposal as a **small stack**, even if it ships under one cargo subcommand:

- `contention_core` — schema types, redaction, diffing, and report rendering
- `contention_topology` — root-sharing and wrapper-context normalization above Cargo/rust-analyzer config and env surfaces
- `contention_capture` — optional local capture adapters for Cargo output, config inspection, and best-effort process observation
- `cargo-contention-witness` — CLI front-end that writes bundles and explains mitigations

That split keeps the receiver-facing artifact stable even if local capture techniques change.

# Persona / who it’s for

- workspace and monorepo maintainers
- developers who use rust-analyzer plus terminal Cargo commands all day
- CI/build engineers
- tool authors integrating nextest, bacon, custom watchers, or editor-side checks with Cargo

# Users & user stories

- **Developer**: “Tell me whether rust-analyzer, another terminal command, or the package cache is what I am actually waiting on.”
- **Workspace maintainer**: “Show me whether this shared target-dir setup is causing a real collision or just broad rebuilds.”
- **Support engineer**: “Give me one artifact that explains the wait and the likely mitigation.”
- **Tool author**: “I need a stable diagnosis/report format without scraping Cargo internals blindly.”

# Prior art (and why it’s insufficient)

- Cargo’s internal cache-lock machinery is real, but it is not a maintainer-facing diagnosis artifact.
- rust-analyzer already documents the separate-target-dir workaround, but that is a single mitigation, not a portable witness bundle.
- The archive already has **P-0436 Target-Dir Lease & Shared Cache Coordination Kit**. That proposal is about **policy, leases, and cleanup** for shared caches.
- The archive already has **P-0469 Cargo Rebuild Explanation Kit**. That proposal is about **why work was recompiled**.
- The archive already has **P-0480 Cargo Global Cache Policy & GC Receipt Kit** and **P-0489 Cargo Build-Dir Consumer Transition Kit**. Those are about **storage governance** and **tool migration off internal build-dir assumptions**.

What remains missing is the **live blocking witness** that answers: “which root, which role, what wait, and what mitigation?”

# Design goals

1. **Blocking-first** — explain waiting and lock contention, not general build slowness.
2. **Conservative observation** — prefer facts Cargo and surrounding tools already expose over fragile private internals.
3. **Mitigation-aware** — always connect diagnosis to a limited set of concrete next moves.
4. **Role-oriented** — classify contenders by workflow role, not just PID.
5. **Privacy-respecting** — allow path and process-name redaction while keeping the witness useful.

# MVP surface

- Minimal types: `ContentionPolicy`, `CacheRootManifest`, `RootSharingReport`, `LockWaitReceipt`, `WrapperContextReceipt`, `ProcessRoleSnapshot`, `CollisionDiagnosisReport`, `MitigationPlan`, `ContentionDiff`, `ContentionBundle`
- Minimal functions:
  - `capture_contention_witness()`
  - `discover_cache_roots()`
  - `summarize_root_sharing()`
  - `capture_wrapper_context()`
  - `classify_collision()`
  - `suggest_mitigation_plan()`
  - `diff_contention_receipts()`
- Feature flags:
  - `cargo`
  - `rust-analyzer`
  - `serde`
  - `process-observe`
  - `markdown`

# Compatibility story

- Must stay useful even when process inspection is unavailable or disabled; root/wait facts alone should still produce value.
- Must understand today’s `target-dir` / `build.build-dir` / wrapper knobs.
- Should record rust-analyzer-specific target-dir separation when present.
- Should remain useful as Cargo’s build-dir layout evolves, because the blocking witness lives above exact path shapes.
- Can optionally record whether `--compile-time-deps`-style tool workflows are in play, but should not require unstable commands.

# Conformance & fixtures

- one fixture with rust-analyzer and manual `cargo build` sharing a target dir and contending on the same root
- one fixture with a separate rust-analyzer target dir where the chosen mitigation is “accept duplicate artifacts for independent progress”
- one fixture with package-cache lock waits during dependency fetch/update
- one fixture where build-dir is separated but the target-dir still remains shared, to prove target/build roots must stay distinct
- one fixture where wrapper hash separation or rust-analyzer wrapper usage causes a `cache_mode_split` / `wrapper_mismatch` diagnosis
- one fixture with an imported Cargo build-analysis session that helps corroborate context but still does not prove blocker identity
- one fixture with the new build-dir layout enabled where the right answer stays explicitly `manual_review_required`
- one fixture with insufficient local observation where the right answer is explicitly `manual_review_required`
- goldens for `editor_manual_conflict`, `shared_target_dir`, `build_dir_collision`, `package_cache_lock`, `cache_mode_split`, `wrapper_mismatch`, `manual_review_required`, and `unknown_wait`

# Path to boring stability

- Freeze the wait/role/mitigation vocabularies before adding heavy active orchestration.
- Start with witness capture and diff, not process killing or scheduling.
- Keep the mitigation list short and explicit.
- Treat imported Cargo sessions as supporting context, not blocker proof.
- Treat unknown blockers as first-class output, not silent failure.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that capture one lock/contention witness, classify the blocker and collided root conservatively, and emit a small mitigation bundle that explains whether the next move is separate target dirs, cache-root changes, package-cache review, wrapper alignment, or simply accepting/documenting a wait.

# De-risk plan

1. Start with read-only witness capture and conservative classification.
2. Treat process-role detection as best-effort metadata, not required truth.
3. Validate the taxonomy on one rust-analyzer-heavy workflow, one CI workflow, and one package-fetch case.
4. Keep rebuild explanations out of scope unless they are directly part of a lock-wait witness.
5. Prefer root-level attribution and mitigation trade-offs over PID-level certainty.

# Non-goals

- Not a scheduler for Cargo processes.
- Not a general build profiler.
- Not a replacement for Cargo cache design work.
- Not a promise that every wait can be attributed to one specific PID on every platform.

# Architecture & API sketch

```rust
pub enum CollisionClass {
    SharedTargetDir,
    PackageCacheLock,
    BuildDirCollision,
    WrapperMismatch,
    CacheModeSplit,
    ManualReviewRequired,
}

pub fn capture_contention_witness(root: &Path, policy: &ContentionPolicy) -> Result<LockWaitReceipt>;
pub fn classify_collision(receipt: &LockWaitReceipt) -> CollisionDiagnosisReport;
pub fn suggest_mitigation_plan(report: &CollisionDiagnosisReport) -> MitigationPlan;
pub fn diff_contention_receipts(old: &LockWaitReceipt, new: &LockWaitReceipt) -> ContentionDiff;
```

Bundle draft: `contention-policy.toml`, `cache-root.manifest.json`, `root-authority.receipt.json`, `root-sharing.report.json`, `lock-wait.receipt.json`, `actor-command-lane.receipt.json`, `wait-window.receipt.json`, `wrapper-context.receipt.json`, `process-role.snapshot.json`, `collision-diagnosis.report.json`, `mitigation.plan.json`, `mitigation-cost.report.json`, `contention-support-bundle.manifest.json`, `contention.diff.json`, `notes.md`.

# Security / safety model

- Treat process and path metadata as potentially sensitive and support redaction.
- Do not claim certainty when blockers are only inferred.
- Never require elevated privileges for basic value.
- Prefer offline/exportable witnesses over live control of other tools.

# Maintenance & governance plan

- Track Cargo build-dir-layout and cache-lock evolution.
- Track rust-analyzer documentation and config changes around target directories and check workflows.
- Keep the mitigation taxonomy stable and modest.
- Maintain fixtures for editor/manual/CI contention patterns.

# Milestones

## 0.1
- cache-root manifest
- one lock-wait receipt
- collision classification
- mitigation plan export

## 0.2
- diff support
- rust-analyzer-specific heuristics
- package-cache lock fixtures

## 0.3
- richer CI/export guidance
- redaction controls
- more explicit wrapper/cache-mode diagnoses

# Open questions

- How much high-confidence blocking attribution is possible without platform-specific process inspection?
- Should wrapper/cache-split findings live in the same witness as hard lock waits or only as adjacent warnings?
- Is there a small, stable “role” vocabulary that spans editor, CI, and terminal workflows without getting too clever?

# Sources

- Call for Testing: Build Dir Layout v2: https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo build cache docs: https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo environment variables: https://doc.rust-lang.org/cargo/reference/environment-variables.html
- Cargo unstable docs (`build-analysis`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
- Cargo unstable docs (`build-dir-new-layout`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-dir-new-layout
- Prototype Cargo build analysis goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Cargo build-dir-layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- rust-analyzer FAQ: https://rust-analyzer.github.io/book/faq.html
- rust-analyzer configuration: https://rust-analyzer.github.io/book/configuration
- Rust compiler performance survey 2025 results: https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/

## 2026-03-22 implementation refresh — package-cache lock modes, residual contention, and mitigation outcomes

The current official substrate makes three receiver-facing gaps much sharper than this proposal originally modeled.

### 1. Package-cache lock mode needs its own receipt

Cargo’s current internal `cache_lock` docs now make package/index-cache coordination unusually explicit:

- `DownloadExclusive`
- `Shared`
- `MutateExclusive`

They also say `DownloadExclusive` does **not** interfere with `Shared`, while `MutateExclusive` blocks readers and acquires both underlying locks.

That means the crate should promote **`package-cache-lock-mode.receipt.json`** into first-class status.
A support bundle should tell another person not just “package-cache activity happened,” but whether the relevant mode should actually interfere with the observed actor.

### 2. Mitigations need a residual-contention report, not just a recommendation string

Current Cargo 1.94 notes say target-dir locking still has easy-to-overlook but significant residual cases:

- `cargo clippy` can still contend on non-workspace members,
- `cargo check` and `cargo test` can still contend around proc-macros and build scripts,
- and upstream locking/layout work is still in flight.

That means the crate should promote **`residual-contention.report.json`** into first-class status.
A serious witness bundle should spell out which contention surfaces remain after a mitigation or topology change.

### 3. The lane now needs a before/after outcome diff

rust-analyzer’s separate target-dir mitigation is still explicitly a trade against duplicated artifacts.
A build-dir split can change route topology without fully resolving package-cache or proc-macro/build-script contention.

That means the crate should promote **`mitigation-outcome.diff.json`** into first-class status.
It should compare a before/after witness pair and classify whether the mitigation:

- resolved the same contention class,
- moved the contention to a narrower class,
- mostly changed artifact duplication cost,
- only changed confidence/exactness,
- or still requires manual review.
