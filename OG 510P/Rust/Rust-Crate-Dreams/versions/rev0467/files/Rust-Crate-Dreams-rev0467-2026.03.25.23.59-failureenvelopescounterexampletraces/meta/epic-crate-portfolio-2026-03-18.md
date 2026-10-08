## 2026-03-20 addendum — open table formats now look more like an epic support seam than a missing-trait complaint

The latest pass should push **P-0028 open-table-format-kit** upward in seriousness.
The reason is not merely that Rust has more lakehouse crates now.
It is that the ecosystem now has enough adjacent substrate — Iceberg DataFusion providers, delta-rs operation matrices, Hudi-rs read/query-engine integration, and DataFusion provider-extension paths — that the missing layer is newly specific and newly composable.

The sharp idea is **not** another engine and **not** another universal trait.
It is one shared layer that can publish **table-surface truth**, **capability-profile truth**, and **integration-coupling truth** with compact reviewable artifacts.

That makes **P-0028** a stronger Band A/B data-platform candidate than it looked when it was mostly “format-agnostic Rust APIs would be nice.”

## 2026-03-20 addendum — lifecycle support is more epic when it says how far shutdown got before timeout returned

The latest pass should push **P-0520 Crate Lifecycle Surface Pack Kit** upward in seriousness again.
The reason is not merely that timeouts are tricky.
It is that the ecosystem now has enough adjacent substrate — Tokio shutdown guidance, `TaskTracker`, maintainer guidance on `timeout` + `JoinHandle`, runtime timeout semantics, and live axum/hyper issue traffic — that the missing layer is newly specific and newly composable.

The sharp idea is **not** another timeout helper and **not** another supervisor.
It is one shared layer that can publish **shutdown-phase truth** and **timeout-aftermath truth** alongside activation boundaries, stop semantics, barriers, escapes, blocking-work caveats, and teardown evidence with compact reviewable artifacts.

That makes **P-0520** a stronger Band A support-surface candidate than it looked when it was still mostly “graceful shutdown support plus barrier scope.”

## 2026-03-20 addendum — lifecycle support is more epic when it says what shutdown completion actually covers

The latest pass should push **P-0520 Crate Lifecycle Surface Pack Kit** upward in seriousness.
The reason is not merely that shutdown is hard.
It is that the ecosystem now has enough adjacent substrate — Tokio shutdown guidance, `CancellationToken`, `TaskTracker`, `JoinHandle`, `JoinSet`, and live axum issue traffic — that the missing layer is newly specific and newly composable.

The sharp idea is **not** another shutdown helper and **not** another task supervisor.
It is one shared layer that can publish **activation-boundary truth**, **stop-semantics truth**, **shutdown-barrier truth**, **escape-path truth**, **blocking-work caveats**, and **teardown-evidence truth** with compact reviewable artifacts.

That makes **P-0520** a stronger Band A support-surface candidate than it looked when it was mostly “graceful shutdown support would be nice.”

## 2026-03-20 addendum — text-input now looks more like an ecosystem-support seam than a vague GUI complaint

The latest pass should push **P-0027 text-input-kit** upward in seriousness.
The reason is not merely that IME bugs exist.
It is that the ecosystem now has enough adjacent substrate — `winit` IME APIs, `cosmic-text` editing substrate, AccessKit text selection vocabulary, hidden-input fallback practice, and an emerging EditContext path — that the missing layer is newly specific and newly composable.

The sharp idea is **not** another widget toolkit and **not** another layout engine.
It is one shared layer that can publish **transaction truth**, **selection truth**, **edit-path truth**, **selection-geometry truth**, and **mirror/a11y truth** with compact reviewable artifacts.

That makes **P-0027** a stronger Band A/B product-engineering candidate than it looked when it was just “Rust GUI text input needs polish.”

## 2026-03-20 addendum — trust posture now looks more like an ecosystem-support seam than a score-theatre complaint

The latest pass should push **P-0017 Trust Lens** upward in seriousness.
The reason is not merely that typosquatting exists.
It is that the ecosystem now has enough adjacent substrate — crates.io Security tabs, Trusted Publishing posture, RustSec-first malware notifications, cargo-vet audit sharing, and fresh research on trust-cost and effect-focused review — that the missing layer is newly specific and newly composable.

The sharp idea is **not** another global score and **not** another registry-policy proposal.
It is one shared layer that can publish **identity-risk truth**, **signal-basis truth**, **assumption-register truth**, **review-debt truth**, and **policy-decision truth** with compact reviewable artifacts.

That makes **P-0017** a stronger Band A/B ecosystem candidate than it looked when it was just “trust scoring would be nice.”


## 2026-03-20 addendum — crate health now looks more like an ecosystem-support seam than a stale badge complaint

The latest pass should push **P-0011 Crate Health Contract Kit** upward in seriousness.
The reason is not merely that people want maintenance badges.
It is that the ecosystem now has enough adjacent substrate — crates.io Security tabs, broader trusted-publishing support, registry-side support/reporting flows, and even RFC discussion about mutable supported-version metadata — that the missing layer is newly specific and newly composable.

The sharp idea is **not** another popularity score and **not** a maintainer leaderboard.
It is one shared layer that can publish **maintenance-window truth**, **succession-map truth**, **support-intent truth**, and **health-check truth** with compact reviewable artifacts.

That makes **P-0011** a stronger Band A/B ecosystem candidate than it looked when it was just “maintenance metadata would be nice.”


## 2026-03-19 addendum — guidance support now looks more like an epic supportiveness seam than a nicer-errors complaint

The latest pass should push **P-0512 Crate Guidance Pack Kit** upward in seriousness.
The reason is not merely that compiler errors can be confusing.
It is that the ecosystem now has enough adjacent substrate — diagnostic attributes, rustdoc `compile_fail`, nightly doctest code checks, `trybuild`, `ui_test`, `miette`, and proc-macro guidance helpers — that the missing layer is newly specific and newly composable.

The sharp idea is **not** another renderer and **not** another compile-fail harness.
It is one shared layer that can publish **message-stability truth**, **guidance-channel truth**, **environment-sensitivity truth**, and **recipe-witness truth** with compact reviewable artifacts.

That makes **P-0512** a stronger Band A support-surface candidate than it looked when it was still mostly “crate guidance would be nice.”

## 2026-03-19 addendum — performance support is more epic when it explains what kind of run happened

The latest pass should push **P-0517 Crate Performance Envelope Pack Kit** upward in seriousness.
The reason is not merely that Rust likes fast code.
It is that the ecosystem now has enough adjacent substrate — Cargo bench/profile defaults, custom profiles, Criterion, Iai-Callgrind, Divan counters/allocation profiling, CodSpeed compatibility layers, and nextest’s benchmark/test-mode split — that the missing layer is newly specific and newly composable.

The sharp idea is **not** another benchmark runner and **not** another hosted perf service.
It is one shared layer that can publish **metric-authority truth**, **execution-intent truth**, **workload-lineage truth**, **profile-identity truth**, and **noise-class truth** with compact reviewable artifacts.

That makes **P-0517** a stronger Band A support-surface candidate than it looked when it was mostly “performance docs would be nice.”

## 2026-03-19 addendum — test support now looks more like an epic supportiveness seam than a bag of helper crates

The latest pass should push **P-0523 Crate Test Surface Pack Kit** upward in seriousness.
The reason is not merely that crates have tests.
It is that the ecosystem now has enough adjacent substrate — Tokio paused time, `rstest`, `wiremock`, `assert_cmd`, `testcontainers`, `trybuild`, `insta`, and now `cargo-nextest` record/replay and portable recordings — that the missing layer is newly specific and newly composable.

The sharp idea is **not** another runner and **not** another mocking framework.
It is one shared layer that can publish **support-level truth**, **topology-honesty truth**, **witness-lineage truth**, and **normalization-boundary truth** with compact reviewable artifacts.

That makes **P-0523** a stronger Band A support-surface candidate than it looked when it was still mostly “crate testing support would be nice.”

## 2026-03-19 addendum — persistence support is more epic when it says what path changed and what identity survived

The latest pass should push **P-0522 Crate Persistence Surface Pack Kit** upward in seriousness.
The reason is not merely that durable bytes are everywhere.
It is that Rust now has enough substrate that the missing value is newly specific: one compact support contract for **publication target**, **identity retention**, **durability boundary**, **compatibility authority**, and **recovery witness**.

The sharp idea is **not** another serializer and **not** another storage engine.
It is one shared layer that can publish what object actually changed and what assumptions another team can safely make afterwards.

That makes **P-0522** a stronger Band A support-surface candidate than it looked when it was only a “durability docs would be nice” lane.

## 2026-03-19 addendum — resource support is more epic when it explains the waiting room

The latest pass should push **P-0521 Crate Resource Surface Pack Kit** upward in seriousness.
The reason is not merely that queues and pools are everywhere.
It is that Rust now has enough substrate that the missing value is newly specific: one compact support contract for **admission order**, **backlog ownership**, **capacity shrink**, and **caller fate**.

The sharp idea is **not** another queue or pool abstraction.
It is one shared layer that can publish where waiting really happens and what another team should expect at the edge.

That makes **P-0521** a stronger Band A support-surface candidate than it looked when it was only a “capacity docs would be nice” lane.

## 2026-03-19 addition — diagnosis support now looks more like an epic supportiveness seam than a vague DX complaint

The latest pass should push **P-0525 Crate Diagnosis Surface Pack Kit** upward in seriousness.
The reason is not merely that debugging can be annoying.
It is that the ecosystem now has enough adjacent substrate — tracing, Tokio Console, runtime/task metrics, rich diagnostic codes/help/URLs, and async-friendly span traces — that the missing layer is newly specific and newly composable.

The sharp idea is **not** another logger and **not** another debugger helper.
It is one shared layer that can publish **symptom truth**, **first-inspection truth**, **instrumentation truth**, and **bundle-safety truth** with compact reviewable artifacts.

That makes **P-0525** a stronger Band A support-surface candidate than it looked when it was still mostly “crate troubleshooting support would be nice.”

## 2026-03-19 addition — joined public-release review lane

The archive should now treat **P-0483 Public API Readiness Bundle Kit** as one of the sharper core-library support candidates.
Reason: Rust now has real semver/public-surface/public-dependency substrate, but still lacks one boring release-review contract for public-surface truth, boundary drift, docs readiness, and waiver posture.

## 2026-03-19 addendum — MCP guardrails now look more like an epic deployment-support seam than an SDK gap

The latest pass should push **P-0071 MCP Guard Kit** upward in seriousness.
The reason is not merely that MCP is popular.
It is that the ecosystem now has enough adjacent substrate — official SDK tiering, a real Rust SDK, explicit authorization/security guidance, an enterprise-readiness roadmap, and even an experimental interceptor extension — that the missing layer is newly specific and newly composable.

The sharp idea is **not** another SDK and **not** a giant agent-security platform.
It is one shared layer that can publish **transport exposure truth**, **auth-boundary truth**, and **operation-guard truth** with compact reviewable artifacts.

That makes **P-0071** a stronger Band B / protocol-product-support candidate than it looked when it was just “MCP security wrappers would be nice.”

## 2026-03-19 addendum — crate off-ramp now looks more like an epic supportiveness seam than a docs footnote

The latest pass should push **P-0515 Crate Off-Ramp Pack Kit** upward in seriousness.
The reason is not merely that crates get deprecated.
It is that Rust now has enough adjacent substrate — deprecation notes, Cargo yank/update flows, crates.io Security tabs, RustSec advisories, and visible redirect-crate patterns — that the missing layer is newly specific and newly composable.

The sharp idea is **not** another advisory client and **not** another maintenance score.
It is one shared layer that can publish **successor intent truth**, **stopgap horizon truth**, and **recipe witness truth** with compact reviewable artifacts.

That makes **P-0515** a stronger Band A/B candidate than it looked when it was just “deprecation support would be nice.”

## 2026-03-19 addendum — desktop shipping now looks more like a contract/evidence seam than a raw packaging bet

The latest pass should push **P-0012 Desktop ShipKit** upward in seriousness.
The reason is not merely that Rust desktop apps need installers.
It is that the ecosystem now has enough release substrate — cargo-dist, cargo-packager, Tauri distribution/updater flows, and platform-specific signing/notarization docs — that the missing layer is newly specific and newly composable.

The sharp idea is **not** another packager and **not** another self-updater.
It is one shared layer that can publish **release identity truth**, **update-channel truth**, and **crash-symbol truth** with compact reviewable artifacts.

That makes **P-0012** a stronger Band B candidate than it looked when it was just “desktop shipping would be nice.”

## 2026-03-19 addendum — LittleFS now looks more like an adoption/evidence seam than a raw feasibility bet

The latest pass should push **P-0527 LittleFS Native Adoption Kit** into the serious portfolio.
The reason is not merely that embedded Rust needs filesystems.
It is that March 2026 changed the shape of the missing value: the ecosystem now has both a mainstream FFI-backed littlefs path and a fresh pure-Rust port.

That means the sharper missing crate is **not** simply “port littlefs to Rust.”
It is one shared layer that can publish **storage-adapter truth**, **compatibility truth**, and **power-cut truth** with compact reviewable artifacts.

That makes **P-0527** a stronger Band C / product-engineering candidate than it looked when the question was still only “could Rust have a native LittleFS someday?”

## 2026-03-19 addendum — text input now looks more like an epic crate seam than a vague GUI complaint

The latest pass should push **P-0027 text-input-kit** upward in seriousness.
The reason is not merely that text input is annoying.
It is that Rust now has enough adjacent substrate — windowing IME APIs, layout/editing crates, and accessibility text vocabulary — that the missing layer is newly specific and newly compounding.

The sharp idea is **not** another widget toolkit and **not** another text engine.
It is one shared layer that can publish **IME transaction truth**, **selection truth**, and **backend-capability truth** with replayable artifacts.

That makes **P-0027** a stronger Band B.5 candidate than it looked when it was just “IME support would be nice.”

# Epic crate portfolio map — 2026-03-18

This note exists to stop the archive from confusing “a missing crate idea” with “a worthy or epic ecosystem contribution”.
The repo now contains many plausible proposals. The useful question is not merely whether an idea is interesting.
It is whether building it would create an outsized improvement in how people actually succeed with Rust.

## What should count as a worthy or epic crate contribution

A worthy crate contribution should usually satisfy **most** of these tests:

1. **Crosses a real pain seam** that official Rust work still surfaces: discoverability, supportiveness, debugging, targets/toolchains, trust, or onboarding.
2. **Produces a reviewable artifact**, not just a clever library API. If other teams cannot inspect, diff, freeze, or carry its output, it is harder to become infrastructure.
3. **Rides existing substrate instead of replacing it**. The biggest wins often sit above Cargo, rustup, docs.rs, crates.io, tracing, testing, or protocol libraries rather than competing with them directly.
4. **Turns tacit knowledge into portable receipts**. Epic crates reduce oral tradition.
5. **Works across more than one task family** or creates a reusable pattern for many domains.
6. **Has an honest scope boundary**. “Teaching baseline”, “production baseline”, and “interop evidence” are different products.
7. **Gets stronger as the ecosystem changes** instead of going stale the moment Cargo/docs.rs/crates.io move underneath it.

## Main thesis after this pass

The highest-leverage missing crates in Rust are often **contract / workbench / evidence / decision** crates rather than raw “another parser / runtime / framework” crates.
Rust already has a lot of substrate.
What remains missing surprisingly often is the layer that helps other people **trust**, **choose**, **support**, **review**, and **carry** that substrate.

## Current priority bands

### Band A — ecosystem-multiplying crates
These help almost every Rust user, directly or indirectly.

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
   - Why it matters: turns crate choice from folklore into reviewable artifacts, and now more explicitly distinguishes ranking from freeze readiness, lock-in cost, and scoped defaults.
   - Why it is epic: it compounds across CLI, services, embedded, Wasm, GUI, data, education, and internal platform governance.

2. **The crate support-surface stack**
   - **P-0524 Example Surface Pack Kit** — now sharper as a first-success contract for official quickstarts, prerequisite lineage, docs/example linkage, and witnessed proof of life.
   - **P-0523 Test Surface Pack Kit** — now sharper as a downstream-testing contract for support levels, topology honesty, witness lineage, and normalization boundaries.
   - **P-0512 Guidance Pack Kit** — now sharper as a compile-time / early-failure contract for message stability, guidance channel, environment sensitivity, and witnessed recovery recipes.
   - **P-0525 Diagnosis Surface Pack Kit**
   - **P-0518 Observability Surface Pack Kit** — now sharper as a signal-support contract for stability, activation truth, bridge routes, schema posture, and sensitivity boundaries.
   - **P-0520 Lifecycle Surface Pack Kit** — now sharper as a crate-authored contract for activation boundaries, stop-verb truth, blocking-work caveats, teardown evidence, and drain recipes.
   - **P-0521 Resource Surface Pack Kit** — now sharper as a crate-authored contract for admission order, backlog ownership, capacity shrink, acquire fate, and pressure evidence.
   - **P-0522 Persistence Surface Pack Kit** — now sharper as a crate-authored contract for publication target, identity retention, durability boundary, compatibility authority, and recovery witness.
   - **P-0484 Toolchain & Target Support Contract Kit**
   - **P-0451 Cfg Availability Ledger Kit**
   - **P-0519 Authority Surface Pack Kit** — now sharper as a crate-authored contract for authority origin, fallback order, refusal posture, injection boundaries, and profile witness.
   - Why it matters: Rust users often do not just need code that exists; they need code they can start, debug, trust, and operate.

3. **P-0510 / P-0511 producer-side capability + interop profile crates**
   - Why they matter: once someone chooses a crate, they still need honest support/interop facts instead of vague README claims.

### Band B — shipping and adoption accelerators
These make Rust more boring to adopt in major product categories.

1. **Desktop / mobile / plugin / extension shipkits**
   - examples: desktop shipkit, Rust Android mobile kit, wasm/plugin/component kits, stable plugin host
   - Why they matter: they close the gap between “Rust can do this” and “teams can ship this repeatedly”.
   - Current sharpest concrete candidates in this band: **P-0168 Rust Android Mobile Kit**, **P-0466 Python Extension Compatibility Contract ShipKit**, **P-0206 Wasm Component Contract & Conformance ShipKit**, **P-0467 Apple XCFramework & SwiftPM ShipKit**, **P-0499 NuGet Native Interop ShipKit**, **P-0498 Node-API Package & Prebuild Contract Kit**, **P-0502 Hex Native NIF ShipKit**, **P-0500 JAR/JNI Native ShipKit**, **P-0526 R Package Native ShipKit**, and **P-0501 RubyGems Native Extension ShipKit**. Android now has enough substrate and enough explicit release-policy reality that a boring library-shipping contract would compound across app teams and SDK authors; Python now has enough PyO3/maturin/cibuildwheel substrate that the sharper missing layer is the boring compatibility contract above wheels, free-threading declarations, and accepted future packaging surfaces; Wasm components now have enough native-target, WIT, composition, and runtime substrate that the sharper missing layer is the boring contract bundle above shifting tooling lineage, versioned worlds, and composition closure; Apple SDK distribution now has enough UniFFI / `cargo swift` / XCFramework / SwiftPM substrate that the sharper missing layer is the boring contract above slices, wrapper/checksum alignment, and trust posture; NuGet native packaging now has enough RID / package-layout / probing / deployment substrate that the sharper missing layer is the boring contract above native asset inventories, loader routes, and deployment posture; Node native packages now have enough Node-API/napi-rs/npm substrate that the sharper missing layer is the boring contract above prebuild tuples, loader routing, and publish identity. Hex/BEAM native packaging now has enough Rustler/rustler_precompiled/Hex substrate that the sharper missing layer is the boring contract above checksum-file residency, NIF-version windows, and source-build fallback honesty. JVM-native packaging now has enough JNI/Maven/Central/JDK native-access substrate that the sharper missing layer is the boring contract above classifier dialect, loader residency, and native-access posture. R package distribution now has enough extendr/rextendr/base-R/CRAN substrate that the sharper missing layer is the boring contract above registration posture, DLL load contracts, and binary-versus-source install honesty. Ruby native-gem distribution now has enough Bundler/RubyGems/`rb-sys`/`magnus` substrate that the sharper missing layer is the boring contract above platform coverage, resolver routes, and extension residency.

2. **Toolchain/build/release workflow crates**
   - examples: build-dir-layout adapters, trusted-publishing tooling, SBOM/provenance bundles, cargo explainability crates
   - Why they matter: they convert tooling churn into reviewable operational workflows.

3. **Support-bundle / runtime-handoff / upgrade / off-ramp crates**
   - Why they matter: they reduce the long-tail cost of choosing Rust crates in production.

### Band B.5 — end-user product-engineering multipliers
These are not as universal as pathfinder/support-surface crates, but they can strongly improve Rust’s credibility in product-facing domains.

1. **P-0087 UI Accessibility Doctor Kit**
   - Why it matters: turns accessibility from ad hoc toolkit lore into reviewable semantic-quality artifacts.
   - Why it is epic: it compounds across desktop apps, custom canvases, editors, game UIs, and any toolkit building on AccessKit substrate.

2. **P-0027 text-input-kit**
   - Why it matters: IME/composition/selection correctness remains one of the most repeated UI pain seams.
   - Why it is epic: one shared input engine could lift many GUI stacks at once.

3. **P-0197 Text Layout & Shaping Conformance Kit**
   - Why it matters: text correctness bugs are cross-framework and costly to reproduce.
   - Why it is epic: a correctness lab above shaping/layout substrate could become shared infrastructure for editors, browsers, terminals, and GUI stacks.

### Band C — domain-defining interop workbenches
These are less universal, but can be epic inside a field.

Strong examples in the archive include:
- WebGPU CTS triage
- Fediverse ops / ActivityPub evidence
- OPC UA / industrial deployment
- Postgres extension shipkit
- scientific / media / geospatial / healthcare evidence kits

These become epic when they turn fragmented standards pain into **canonical replayable evidence** that many vendors, teams, or labs can share.

### Band D — ambitious long-horizon bets
These are still worthy, but need discipline.

Examples:
- Array API for Rust
- deterministic async labs
- local-first sync workbenches
- structured concurrency standardization
- stable plugin/component ecosystems

These can be transformative, but only if they avoid becoming giant replacement ambitions without a small artifact-bearing `0.1`.

## Variety map: where the archive is strongest versus still hungry

### Strong and compounding already
- crate choice and starter-stack governance
- support-surface truth
- evidence bundles / interop workbenches
- build / release / supply-chain review artifacts

### Still especially hungry
- polished app-shipping golden paths
- boring compatibility-contract defaults for foreign-package release surfaces (Python wheels, mobile/desktop packaging, plugin delivery)
- **UI/product-engineering support layers** such as accessibility doctoring, text input, layout conformance, and cross-framework regression truth
- richer support surfaces for debugging and runtime diagnosis
- bridges that absorb fast-moving Cargo/docs.rs/crates.io changes without forcing each team to rediscover them

## Lessons to keep from the past and present

1. **Do not mistake popularity for fitness.**
2. **Do not mistake visibility for support.** docs.rs target changes and docs-only cfgs make this easy to get wrong.
3. **Do not mistake security posture for task fit.** A crate can publish cleanly and still be wrong for the job.
4. **Do not mistake “there is a crate” for “there is a portable workflow”.**
5. **Do not try to solve discoverability with one giant blessed platform snapshot.**
6. **Do not let the archive fragment into adjacent micro-lanes without a portfolio reason.**

## Working judgment

If the archive has to choose where to spend the next increment of effort, the best default bet is still:

1. deepen **task-first crate choice**,
2. then deepen the **support surfaces** that make chosen crates survivable,
3. then invest in **domain workbenches** where replayable evidence can become a field standard.

That is the tightest current answer to “what would count as a worthy, maybe epic, Rust crate contribution?”

## 2026-03-19 addendum — observability now looks more like a contract/evidence seam than a telemetry-plumbing bet

The latest pass should push **P-0518 Crate Observability Surface Pack Kit** upward in seriousness.
The reason is not merely that Rust crates emit telemetry.
It is that the ecosystem now has enough substrate — `tracing`, `tracing-subscriber`, `EnvFilter`, `console-subscriber`, OpenTelemetry bridges, schema URLs, and field-sensitivity guidance — that the missing layer is newly specific and newly compounding.

The sharp idea is **not** another subscriber and **not** another exporter.
It is one shared layer that can publish **signal stability truth**, **activation truth**, **bridge-route truth**, **schema posture**, and **sensitivity posture** with compact reviewable artifacts.

That makes **P-0518** a stronger Band A/B support-surface candidate than it looked when the question was still only “can Rust telemetry be wired up?”.


## 2026-03-19 addendum — upgrade support is now more clearly epic-tier when scoped as a downstream contract

**P-0514 Crate Upgrade Pack Kit** looks stronger after the 2026-03-19 refinement because it is no longer just “migration recipes”.
Its sharper promise is a receiver-facing contract for **hazard authority**, **source-lineage truth**, **hazard arbitration**, **workspace/package scope**, **active follow-through state**, and **manual-review boundaries** above release automation and SemVer substrate.


## 2026-03-20 addendum — crate choice looks more epic when the decision can age honestly

**P-0509** is stronger again because its missing layer is no longer just ranking or freezing.
An ecosystem-wide pathfinder becomes more epic when it can publish a small living decision contract with **revisit triggers**, **freeze horizons**, and **decision-watch state** rather than leaving frozen starter sets to rot into copy-pasted folklore.


## 2026-03-20 addendum — workload identity now looks more like a contract/evidence seam than a protocol-substrate bet

**P-0134 spiffe-identity-kit** looks stronger after this refinement because Rust no longer lacks basic SPIFFE/SPIRE substrate.
Its sharper promise is now a receiver-facing contract for **identity source**, **trust-domain scope**, **peer-identity handoff**, and **rotation/failure posture** above protocol/TLS building blocks.


## 2026-03-20 addendum — cfg availability now looks more epic when it distinguishes who can really use the item

The latest pass should push **P-0451 Cfg Availability Ledger Kit** upward in seriousness again.
The reason is not merely that Rust is getting better `doc_cfg` markers.
It is that the ecosystem now has enough adjacent substrate — RFC 3631, the `doc_cfg` stabilization goal, docs.rs rustdoc JSON, docs.rs default-target policy, and Cargo doctest/feature behavior — that the missing layer is newly specific.

The sharp idea is **not** another rustdoc front-end and **not** another generic API diff tool.
It is one shared layer that can publish **docs-visible truth**, **doctest-usable truth**, **downstream-usable truth**, and **default-surface drift truth** with compact reviewable artifacts.

That makes **P-0451** a stronger Band A candidate than it looked when it was still mostly “conditional API matrix would be nice.”

## 2026-03-20 addendum — MSRV now looks more epic when update-path honesty is explicit

The latest pass should push **P-0036 MSRV Workspace Lab** upward in seriousness.
The reason is not merely that MSRV matters more.
It is that Cargo now has enough adjacent substrate — `rust-version`, multiple-workspace-policy guidance, resolver v3, root-only resolver activation, lockfile-v4 behavior, and live issue traffic around mixed workspaces and `metadata` divergence — that the missing layer is newly specific.

The sharp idea is **not** another binary-search finder.
It is one shared layer that can publish **policy-activation truth**, **command-family floor truth**, and **lockfile-authoring truth** with compact reviewable artifacts.

That makes **P-0036** a stronger Band A/B support-surface candidate than it looked when the question was still only “can we infer a minimum compiler?”
