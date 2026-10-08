---
id: P-0486
title: Debuggability Support Contract Kit — support-posture receipts, symbol-sidecar manifests, and debugger-ready release bundles
status: idea
domains: [debugging, cargo, rustc, release, symbols, ci, support, tooling]
last_reviewed: 2026-03-22
evidence:
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
  - https://doc.rust-lang.org/cargo/reference/build-cache.html
  - https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
  - https://doc.rust-lang.org/cargo/reference/profiles.html
  - https://doc.rust-lang.org/rustc/codegen-options/index.html
  - https://doc.rust-lang.org/reference/attributes/debugger.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html#profile-trim-paths-option
  - https://doc.rust-lang.org/cargo/CHANGELOG.html
needs:
  - Teams need a stable way to state whether a build is interactive-debugger friendly, backtrace-only, or crash-symbolication-only.
  - Release and support engineers need one portable bundle that says where symbols and sidecars are and what changed between builds.
  - Tooling authors need a boring schema above Cargo/rustc/platform differences instead of custom heuristics per debugger and OS.
risks:
  - The crate could sprawl into a debugger launcher, crash backend, or full source-packaging system.
  - Platform differences are real; the first vocabulary must stay conservative and allow manual-review outcomes.
  - Path-hygiene and sidecar data can reveal private workspace structure; redaction must be first-class.
---

# Problem

Rust’s debugging story is no longer blocked on one missing primitive.
The substrate is already real, but maintainers still lack a **boring support contract** for what a given build actually promises.

Today the relevant facts are scattered across:

- Cargo profile settings like `debug`, `split-debuginfo`, and `strip`,
- platform-specific `rustc` behavior for embedded versus sidecar debuginfo,
- stable `#[debugger_visualizer]` assets,
- optional path-hygiene controls such as `trim-paths`,
- and whatever artifact/archive discipline a release engineer happened to remember that day.

That produces recurring support ambiguity:

- Is this build actually suitable for an interactive debugger, or only for backtraces?
- Did Windows/MSVC produce a `pdb`, did macOS produce a `dSYM`, or did Linux emit `dwo` / `dwp` sidecars?
- Did a release profile quietly become weaker because `debug = 0` and stripping behavior changed?
- Are debugger visualizers present and embedded, or merely expected to exist somewhere else?
- Did path sanitization improve privacy while making source lookup harder?

The 2025 State of Rust survey still shows debugging as a notable productivity problem, and the 2026 debugging survey is explicitly asking about debugger support quality, visualizers, async debugging, and expression evaluation.
So the sharper gap is no longer “invent a debugger.”
It is a **portable debuggability support contract** above the existing substrate.

# What it provides

- `debuggability-policy.toml` — intended support posture per profile/target (`interactive_debugger`, `backtrace_only`, `crash_symbolication_only`, `internal_only`).
- `debuggability.receipt.json` — normalized facts from one build: profile settings, observed debug mode, split strategy, strip mode, path-hygiene hints, capture sources, and artifact inventory.
- `symbol-layout.manifest.json` — explicit mapping from each primary artifact to `pdb` / `dSYM` / `dwo` / `dwp` / embedded-debug equivalents.
- `visualizer.manifest.json` — debugger visualizer assets, backend targets, embedding mode, and confidence.
- `support-posture.report.json` — conservative verdict for what downstream users and support engineers can actually expect.
- `debuggability-drift.diff.json` — compares two receipts and classifies improvements, degradations, ambiguous drift, and manual-review zones.
- `support-class.policy.json` — explicit meaning and minimum evidence for `interactive_debugger`, `backtrace_only`, `crash_symbolication_only`, and review-only lanes.
- `artifact-handoff.manifest.json` — canonical/copy/archive paths and retention expectations for primary artifacts and symbol sidecars.
- `debugger-backend-coverage.report.json` — debugger-family / OS / version coverage plus capability ceilings for symbol loading, visualizers, async debugging, and expression evaluation.
- `backend-observation.receipt.json` — exact checked debugger-family / version / capability observations without pretending artifacts imply portable support.
- `source-lookup-impact.report.json` — path-hygiene and source-lookup consequences kept separate from broad debugger posture.
- `source-material.manifest.json` — source archive / sysroot-source / remapped-prefix lookup materials plus share posture.
- `debug-support-bundle.manifest.json` — portable review handoff for posture, sidecars, backend evidence, and source materials.
- `cargo debug-contract capture` — inspect a built artifact set and emit a receipt bundle.
- `cargo debug-contract diff <old> <new>` — compare two builds or releases.
- `cargo debug-contract doctor` — flag suspicious combinations like missing sidecars, policy weaker than intended, or visualizer/backend mismatches.
- `*.debugcontract.zip` — portable handoff bundle for CI, support, release review, or downstream integrator use.

# What the crate should provide other people

1. **A stable support-posture vocabulary** instead of ad hoc guesses from `Cargo.toml` and file listings.
2. **A compact receiver-facing bundle** that says where symbols live, what the build supports, and what the important caveats are.
3. **A policy gate** for teams that want to assert “release builds must remain at least crash-symbolication-capable” or “debug SDK builds must remain interactive-debugger friendly.”
4. **A handoff manifest** so release engineers can tell whether copied or archived artifacts preserved the promised debugger posture.
5. **A backend-coverage report** so `pdb` / `dSYM` / `dwo` presence and NatVis/GDB assets do not masquerade as uniform support across debugger families, versions, or advanced capabilities.
6. **An exact backend-observation receipt** so one checked debugger lane is visible as one checked debugger lane, not a global promise.
7. **A source-lookup impact report** so privacy-oriented path changes do not quietly get mistaken for “debugging is broken” or “debugging is fine”.
8. **A source-material manifest** so release/support teams know what lookup material exists, where it lives, and whether it is safe to share.
9. **A portable debug-support bundle** so posture, sidecars, backend evidence, and source materials survive review handoff together.
10. **A reusable library surface** so other tools do not all reinvent the same platform heuristics.

# Persona / who it’s for

- maintainers shipping Rust CLIs, daemons, desktop apps, SDKs, or libraries with native artifacts
- release engineers who must archive the right symbol sidecars
- support engineers handling “I can’t debug this build” or “symbols are missing” incidents
- teams balancing privacy/size against debugger usefulness
- tooling authors who need a stable debuggability receipt

# Users & user stories

- **Release engineer**: “Tell me exactly which sidecars I must preserve on each target.”
- **Support engineer**: “Give me one bundle that says whether this build is interactive-debugger friendly, backtrace-only, or weaker than policy.”
- **Maintainer**: “Block this release if we silently lost a `pdb`, `dSYM`, or required visualizer asset.”
- **Security/privacy reviewer**: “Show me how path sanitization changed what the artifact reveals without hand-inspecting binary details.”

# Prior art (and why it’s insufficient)

- Cargo profiles already expose `debug`, `split-debuginfo`, and `strip`.
- `rustc` already documents platform-specific sidecar and strip behavior.
- Rust already supports stable `#[debugger_visualizer]` assets.
- `trim-paths` is emerging as a real path-hygiene surface.
- The archive already has **P-0493** and **P-0491**, but those are narrower follow-on crates for source-path diagnosis and visualizer compatibility.

What remains missing is the **joined release/support artifact** that says:
“this is the debugging posture this build actually offers, this is where the relevant artifacts are, and this is how that posture drifted.”

## 2026-03-08 upstream-fit refresh

This proposal is now **more buildable** because the official substrate is explicit enough to narrow the crate.

Four current facts especially matter:

- Cargo documents `debug`, `split-debuginfo`, and `strip`, and warns that Cargo and `rustc` can have **different defaults** for `split-debuginfo`.
- `rustc` documents that `strip = debuginfo` can leave backtraces mostly intact while making interactive debugging ineffective.
- stable `#[debugger_visualizer]` means embedded NatVis/GDB assets are a real language surface, not a speculative wishlist.
- Cargo’s changelog records subtle behavior shifts like “disabling debuginfo now implies `strip = "debuginfo"` when `strip` is not set”, which is exactly the kind of release-contract nuance ordinary teams fail to track manually.

That means this crate should **not** try to become a debugger or a giant debug-session orchestrator.
It should own the boring layer above the substrate:

- a stable receipt,
- a stable symbol-layout manifest,
- a conservative support-posture report,
- and a diff artifact another human can review.

## 2026-03-16 support-contract refresh — location churn is not the same as support truth

This proposal is stronger now for two reasons.

### 1. The official debugging push is explicitly cross-backend and regression-aware
The 2026 debugging survey says Rust should support multiple debugger families across operating systems, quality visualizers, async debugging, and expression evaluation, while also noting that the experience can regress as debugger versions and Rust internals change.

That favors a **support contract** crate even more strongly.
The missing value is not another debugger frontend; it is the boring receipt that tells another maintainer what this build can honestly support right now.

### 2. Cargo is making artifact-location assumptions more visible
Cargo now documents a clearer split between **target-dir** for final artifacts and **build-dir** for intermediate artifacts, and the March 2026 Build Dir Layout v2 call-for-testing explicitly says many projects still rely on internal details because some higher-level features are missing.

That matters here because debuggability is partly about **where sidecars and symbols are**, but P-0486 must not become a build-dir migration crate.
Its sharper job is to emit a bundle that stays useful even when workspace layout, build-dir settings, or artifact copy strategy changed:

- where the primary artifact lives,
- where symbol sidecars live,
- whether the support posture is still `interactive_debugger`, `backtrace_only`, `crash_symbolication_only`, or weaker,
- and whether the handoff is missing sidecars or visualizer assets.

A build can move around the filesystem without changing its support posture; conversely, a build can keep a familiar path while silently losing the symbol state that made it supportable.
That distinction is exactly why this proposal remains valuable.

## 2026-03-22 artifact-completeness refresh — artifact-rich builds still need exact backend evidence and source-material accounting

This proposal is stronger now because the remaining missing value has become narrower and more reviewer-facing.

Three current facts especially matter:

- the 2026 debugging survey says Rust still lacks uniform debugger support across debugger families, operating systems, async debugging, and Rust expression evaluation;
- current Cargo / `rustc` docs keep symbol layout and strip behavior explicit enough that artifact richness can be observed without guaranteeing portable debugger success;
- Cargo’s build-cache docs and the Build Dir Layout v2 call-for-testing make it even clearer that artifact routes and internal layout are moving targets, so exported support bundles must not depend on path folklore alone.

That means `0.2` for this crate should add three more review objects:

- one **backend-observation receipt** for exact checked debugger lanes,
- one **source-material manifest** for lookup materials and share posture,
- and one **portable debug-support bundle** that keeps posture, sidecars, backend evidence, and source materials joined without flattening them.

A build can have healthy symbols, embedded visualizers, and even one successful debugger session while still lacking portable evidence for other debugger families or for advanced capabilities like async inspection and Rust expression evaluation.
That is exactly why these artifacts belong here.

# Design goals

1. **Support-contract-first** — optimize for release, support, and CI handoff.
2. **Platform-honest** — keep Windows/MSVC, macOS, Linux/ELF, and other target differences visible.
3. **Artifact-aware** — sidecars, embedded assets, and missing pieces must be first-class.
4. **Diffable** — accidental debugger regressions should be reviewable.
5. **Conservative** — when evidence is partial, emit `manual_review_required`.
6. **Stack-aware** — keep broad posture separate from P-0493 source-path diagnosis and P-0491 visualizer conformance.

# MVP surface

- Minimal types: `DebuggabilityPolicy`, `DebuggabilityReceipt`, `SymbolLayoutManifest`, `VisualizerManifest`, `SupportPostureReport`, `SupportClassPolicy`, `ArtifactHandoffManifest`, `SourceLookupImpactReport`, `DebuggabilityDrift`, `DebugContractBundle`
- Minimal functions:
  - `capture_debuggability_receipt()`
  - `discover_symbol_layout()`
  - `discover_debugger_visualizers()`
  - `classify_support_posture()`
  - `diff_debuggability_receipts()`
  - `derive_artifact_handoff_manifest()`
  - `derive_source_lookup_impact_report()`
- Feature flags:
  - `cargo`
  - `serde`
  - `zip`
  - `markdown`
  - `natvis`
  - `gdb`

# Compatibility story

- Must work even when the build happened elsewhere; imported binaries plus sidecars should be enough for first value.
- Must record whether debuginfo is **embedded**, **split into sidecars**, or **effectively absent**.
- Must keep backtrace usefulness separate from interactive-debugger usefulness.
- Must record path-hygiene posture as observed facts plus conservative consequences.
- Should stay useful even if Cargo stabilizes more path/debugging knobs, because the joined receipt and drift artifact still matter.

# Conformance & fixtures

- Windows/MSVC fixture with full debuginfo, expected `pdb`, and an embedded NatVis asset.
- Linux fixture using `line-tables-only` / limited debuginfo to classify `backtrace_only` rather than overclaiming interactivity.
- macOS fixture with expected `dSYM` and a release drift case where the sidecar is missing or policy is weakened.
- Linux split-DWARF fixture with explicit sidecar expectation so the crate does not flatten “Linux build” into one debug-info story.
- regression fixture where strip/path settings changed and the crate emits a conservative drift diff.
- Goldens for `interactive_debugger`, `backtrace_only`, `weaker_than_policy`, `missing_sidecar`, and `manual_review_required`.

# Path to boring stability

- Freeze the support-posture vocabulary before deep integrations.
- Start with **read-only capture and diff**, not debugger orchestration.
- Keep manual-review zones visible and explicit.
- Pilot on one Windows binary, one macOS binary, and one Linux CLI/library pair.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A library and cargo subcommand that inspect a built artifact set, emit a debuggability receipt plus symbol-layout and visualizer manifests, and diff two builds to show whether debugger support got better or worse.

# 2026-03-17 productization refresh — handoff truth and source-lookup impact stay explicit

This proposal is stronger now because the next useful move was **not** another debugging-adjacent crate.
It was to make **P-0486** buildable enough that somebody could plausibly start `0.1` this week.

Three things needed to become explicit that had still been too implicit:

- **support-class meaning** — what evidence is enough to claim `interactive_debugger` versus `backtrace_only` or `crash_symbolication_only`;
- **artifact handoff truth** — whether sidecars survived copying, packaging, or build-dir churn;
- **source-lookup impact** — how remap/trim-paths changed expectations without collapsing broad posture into full source diagnosis.

That boundary matters because current official docs now say several awkward things very plainly:

- Cargo and `rustc` can differ on `split-debuginfo` defaults.
- `strip = debuginfo` can preserve backtraces while making interactive debugging ineffective.
- Cargo now documents a change where disabling debuginfo can imply `strip = "debuginfo"` when `strip` is otherwise unset.
- Build Dir Layout v2 makes artifact location churn more visible, which is exactly why P-0486 needs a location-agnostic handoff manifest rather than more path folklore.

So the sharper `0.1` is now:

- a small local capture/check/diff/pack tool,
- a `support-class.policy`,
- an `artifact-handoff.manifest`,
- and a `source-lookup-impact.report`,

with **P-0491** and **P-0493** still treated as narrower follow-ons instead of being silently reabsorbed.

See also: `meta/debuggability-support-product-plan-2026-03-17.md`.

# 0.1 boundaries

A good 0.1 should:

- inspect already-built artifacts rather than orchestrating debuggers,
- classify support posture conservatively,
- discover the obvious sidecar layouts for Linux/ELF, Windows/MSVC, and macOS,
- detect embedded visualizer assets where possible,
- emit handoff/source-lookup reports instead of pretending paths do not matter,
- and export a portable bundle with a tiny, legible vocabulary.

A bad 0.1 would try to:

- automate GDB/LLDB/WinDbg end to end,
- become a crash-reporting service,
- or solve source-path remapping and visualizer conformance in the same crate.

## Recommended 0.1 crate split

Keep the first release split between:

- `debug-contract-core` — receipt types, support-posture classification, drift logic
- `debug-artifact-discovery` — sidecar discovery, visualizer discovery, platform-specific artifact heuristics
- `cargo-debug-contract` — workspace-facing CLI, import/export, and policy gate UX

This keeps the value centered on **reviewable support artifacts**, not on debugger automation.

# De-risk plan

1. Start with receipt capture and static classification rather than any debugger automation.
2. Focus on three mainstream platform families first: Linux/ELF, Windows/MSVC, and macOS.
3. Keep the support verdict vocabulary small.
4. Treat sidecar discovery failures and platform ambiguity as first-class output instead of hiding them.

# Non-goals

- Not a replacement for GDB, LLDB, CDB/WinDbg, or IDE integrations.
- Not a full crash reporting backend.
- Not a universal visualizer test harness; that is closer to P-0491.
- Not a full source-packaging or virtual-source diagnosis system; that is closer to P-0493.
- Not a security/obfuscation guarantee.

# Architecture & API sketch

```rust
pub enum SupportPosture {
    InteractiveDebugger,
    BacktraceOnly,
    CrashSymbolicationOnly,
    ManualReviewRequired,
}

pub fn capture_debuggability_receipt(root: &Path) -> Result<DebuggabilityReceipt>;
pub fn discover_symbol_layout(receipt: &DebuggabilityReceipt) -> Result<SymbolLayoutManifest>;
pub fn discover_debugger_visualizers(receipt: &DebuggabilityReceipt) -> Result<VisualizerManifest>;
pub fn classify_support_posture(receipt: &DebuggabilityReceipt) -> SupportPostureReport;
pub fn diff_debuggability_receipts(old: &DebuggabilityReceipt, new: &DebuggabilityReceipt) -> DebuggabilityDrift;
```

Bundle draft: `debuggability-policy.toml`, `debuggability.receipt.json`, `symbol-layout.manifest.json`, `visualizer.manifest.json`, `support-posture.report.json`, `debuggability-drift.diff.json`, `notes.md`.

# Security / safety model

- Support redaction of local paths, usernames, and private workspace names in exported bundles.
- Never claim a support posture is stronger than the observed evidence supports.
- Preserve profile/target/toolchain assumptions exactly.
- Make imported-versus-observed provenance explicit.

# Maintenance & governance plan

- Track Cargo profile and path-hygiene changes closely.
- Track `rustc` sidecar/strip behavior and keep the platform matrix explicit.
- Keep the support-posture vocabulary small, stable, and reusable by P-0493 / P-0491.
- Maintain fixture goldens for Windows/MSVC, macOS, Linux, missing-sidecar drift, and policy mismatch.

# Milestones

## 0.1
- receipt capture
- symbol-layout manifest
- support-posture report
- bundle export

## 0.2
- visualizer manifest
- policy file support
- drift diff

## 1.0
- stable bundle schema
- curated cross-platform fixture corpus
- narrow downstream integrations

# Open questions

- What is the smallest useful evidence vocabulary for support-posture classification?
- How much direct binary inspection should 0.1 attempt before relying on imported build context?
- Should policy gating live in the core crate or only in the Cargo-facing wrapper?

# Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://doc.rust-lang.org/cargo/reference/profiles.html
- https://doc.rust-lang.org/rustc/codegen-options/index.html
- https://doc.rust-lang.org/reference/attributes/debugger.html
- https://doc.rust-lang.org/cargo/reference/unstable.html#profile-trim-paths-option
- https://doc.rust-lang.org/cargo/CHANGELOG.html


## 2026-03-21 backend-coverage refresh — artifacts are not the same thing as debugger-family support

This proposal is stronger now because the official Rust debugging survey makes the next missing layer much sharper.

The survey says ideal Rust debugging should support several versions of different debuggers across multiple operating systems, quality visualizers, first-class async debugging, and Rust expression evaluation.
At the same time, the stable Rust Reference only standardizes embedded visualizer assets for **NatVis** and **GDB script** inputs, while Cargo/`rustc` documentation mostly explains artifact posture (`split-debuginfo`, `strip`, sidecars, path sanitization) rather than proving any given backend/capability lane was exercised.

That means `0.1` should add one more conservative artifact above the current bundle:

- `debugger-backend-coverage.report.json`

A good first schema should let the crate say:

- which debugger families / operating systems / version windows were actually reviewed,
- whether a claim is based on a direct debugger session, artifact inference, declared assets only, or still manual review,
- which capability classes were actually in scope (`symbol_loading`, `type_visualizers`, `async_debugging`, `expression_evaluation`),
- and what the strongest **portable** claim ceiling is when evidence is narrower than the release would like.

This keeps three truths separate that are too easy to blur together:

1. **the build is artifact-rich enough to debug somehow**,
2. **a particular debugger family is plausibly supported**, and
3. **advanced debugger capabilities were directly exercised**.

Without that separation, the archive would keep letting “PDB exists”, “dSYM exists”, or “NatVis exists” masquerade as a much broader debugger-support claim than the evidence really warrants.


## 2026-03-22 capability-witness refresh — one checked lane still needs task evidence and claim ceilings

This proposal is stronger now because the next missing layer is no longer just backend-family coverage.
It is the ability to say **which user-facing debugger tasks were actually witnessed in which session scope**, and where the outward-facing claim must stop.

Current official sources make that sharper than before:

- the debugging survey says ideal Rust support spans several versions of multiple debuggers across OSes, quality visualizers, async debugging, and Rust expression evaluation;
- the rustc debugging-support guide says GDB’s Rust expression parser supports only a subset of Rust, LLDB implements slightly less than GDB, and GDB generally works better on Linux;
- the Rust Reference says embedded GDB pretty printers are not auto-loaded by default and can require safe-path or per-user configuration;
- the rustc-dev-guide keeps debugger tests lane-scoped by debugger family, version, OS, and compare mode;
- and the LLDB internals guide now documents a version-sensitive PDB-reader default change in LLDB 22.

So `0.1` should add three more conservative artifacts above the current bundle:

- `session-scope.receipt.json`
- `capability-witness.report.json`
- `claim-ceiling.report.json`

A good first design lets the crate say:

- whether evidence came from a live local process, attached process, remote target, containerized process, or post-mortem dump lane;
- which concrete tasks were actually observed (`breakpoint_hit`, `step_over`, `backtrace`, `locals_expand`, `pretty_render`, `rust_expression_eval`, `async_task_inspection`, etc.);
- and what the strongest honest outward-facing claim is after narrower evidence is considered.

This keeps four truths separate that are still too easy to blur together:

1. **the build has enough artifacts to debug somehow**,
2. **one debugger/backend/version lane was directly observed**,
3. **specific user-facing tasks were actually demonstrated**, and
4. **the portable support claim may still need to stay narrow**.

Without that separation, the archive would keep letting “we opened it in LLDB once” or “the backtrace looked fine” masquerade as a much broader debugger-support claim than the evidence really warrants.
