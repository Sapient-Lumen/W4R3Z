# Epic-contribution v0 kernel briefs (2026 Q1)

## Why this note exists
The archive now has:
- broad ranking and portfolio notes,
- macro-program grouping,
- reference architectures,
- launch charters,
- stage gates,
- review packets,
- specimen packets,
- live dossiers,
- and live current-decision packets.

What it still lacked was a **first-build layer**.
The repo could say:
- which candidates are strongest,
- what verdict they deserve now,
- and what big shape they should eventually take,

but it still could not say, in one bounded artifact family, **what a real v0 would contain if a small team tried to build it next week**.
That creates four avoidable failures:
- good candidates stay abstract because their next honest repo shape is missing;
- `advance` and `deepen` verdicts drift back into rhetoric instead of producing first shipsets;
- future assistants re-invent folder trees, command surfaces, and proof assets from scratch; and
- `hold` candidates silently get kernelized anyway, creating renewal debt before the archive has earned the right to widen them.

A **v0 kernel brief** is the missing bridge.
It is narrower than a reference architecture, more build-shaped than a packet, and more operational than a charter.

## What a v0 kernel brief is
A v0 kernel brief should answer:
- what exact bounded thing gets built first;
- what repository shape it wants;
- what commands, schemas, or document surfaces it exposes;
- what upstream seams it imports instead of replacing;
- what proof assets it emits;
- what proving grounds make it believable;
- what upkeep it immediately incurs;
- and what larger empire it explicitly refuses.

A kernel brief is therefore not:
- a grand product roadmap,
- a universal platform plan,
- or a hidden request to upstream everything into Cargo or rustc.

Think of it as the archive's **first honest shipset note**.

## Why this is the right next layer now
Fresh Rust signals still reward bounded first builds over sweeping frameworks:
- Cargo build analysis is still a prototype to record build metadata and expose unstable `cargo report` subcommands for rebuild reasons and timings.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Cargo's build-dir-layout work is explicitly trying to reduce lock contention, make cache units more manageable, and support cross-workspace cache reuse, while the current testing call says many tools still rely on unspecified internals because features are missing.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo still treats third-party tooling as a real, stable seam through `cargo metadata`, `--message-format=json`, and custom subcommands.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo's plumbing-commands goal still frames command separation as a third-party experiment around locate/read/resolve/plan/execute phases, not a promise that Cargo itself will ship every desired seam immediately.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- The 2025 State of Rust survey still keeps resource usage and debugging in the productivity-pain band.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The debugging survey still sets the bar at multi-debugger, multi-OS, visualizers, async debugging, and Rust expression evaluation, which implies a fixture/replay/acceptance corpus more than a single blessed debugger.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- crates.io's 2026 development update, the January 2026 Foundation/project-director update, and the Alpha-Omega security update all point toward concrete security/provenance/capability-analysis work: Trusted Publishing expansion, prototype Capslock-style capability analysis, vulnerability surfacing, and anomaly detection.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://blog.rust-lang.org/inside-rust/2026/02/09/project-director-update/
  https://rustfoundation.org/media/strengthening-rust-security-with-alpha-omega-a-progress-update/
- The March 2026 Cargo advisory keeps alternate-registry and local-operator reality sharply visible.
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- The safety-critical writeup still argues for target-readiness checklists, dependency-lifecycle playbooks, safety-case-friendly async requirements, and shared ownership rather than one magic certification crate.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The 2026 goals process still says goals are contracts with champions, and the maintenance writeup plus Foundation strategy keep sustainable maintenance and owner realism central.
  https://rust-lang.github.io/rust-project-goals/2026/
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
  https://rustfoundation.org/strategic-plan/

Taken together, those signals say the next worthy repo layer is **first-build kernelization for the candidates that have earned it**, not another reranking memo.

## What belongs in the first kernel corpus
The first corpus should cover only top-band candidates whose present verdict can honestly support a first build shape.
That means:
1. **Build-State Evidence** — yes, now
2. **Feedback / Debug Acceptance Commons** — yes, but deepen-shaped
3. **Package Intake + Release Boundary Review** — yes, now
4. **Safety-Critical + Institutional Readiness Commons** — yes, but commons-shaped
5. **Navigation / Defaults / Claims Commons** — **not yet**

Why exclude navigation/defaults for now:
- the current verdict is still `hold`;
- the main blocker is renewal capacity, not imagination;
- kernelizing it now would create freshness debt before the repo proves review cadence.

This is a feature, not a bug.
A worthy repo should know when **not** to instantiate a first build.

## Required fields for a v0 kernel brief
Every kernel brief should keep these sections visible:
1. **identity** — candidate, macro-program, current verdict context;
2. **why this kernel and not a bigger build** — what exact bounded first shipset is justified;
3. **repo shape** — top-level packages, docs, fixtures, schemas, or corpora;
4. **user surfaces** — commands, generated artifacts, cards, or packs;
5. **import seams** — what current upstream/public interfaces it depends on;
6. **proof assets** — what evidence the build emits;
7. **proving grounds** — where the kernel should be tried first;
8. **operator / maintainer burden** — who carries it and what drifts;
9. **refused expansions** — what empire is still out of bounds;
10. **exit criteria** — what would justify a stronger next-stage shape.

## The first kernel family
### 1) Build-State Evidence → `build-state-pack/v0`
This should be the clearest first kernel.
It wants a small companion repo with:
- one machine-readable session pack,
- one diff surface,
- one doctor surface,
- adapters to stable Cargo seams,
- and explicit optional adapters for unstable `cargo report *` surfaces.

### 2) Feedback / Debug Acceptance Commons → `debug-acceptance-matrix/v0`
This should not start as a debugger fork.
It wants:
- fixture sets,
- tuple cards,
- replay recipes,
- session-pack exports,
- and clear unsupported-state receipts.

### 3) Package Intake + Release Boundary Review → `intake-review-kit/v0`
This should not start as a registry-wide trust oracle.
It wants:
- local review receipts,
- route profiles,
- quarantine / waiver / escalation flows,
- optional capability-analysis imports,
- and replay drills against recent incident classes.

### 4) Safety-Critical + Institutional Readiness Commons → `readiness-cards/v0`
This should not start as certification theater.
It wants:
- target-readiness cards,
- dependency-lifecycle playbooks,
- FFI/interop evidence recipes,
- async-runtime requirement sketches,
- and validation/linting for the cards themselves.

## What these first briefs should teach
- not every worthy contribution begins as a crate;
- not every top-band candidate deserves kernelization now;
- strong first builds import existing seams instead of pretending to replace them;
- the first value should come from **improving a real local decision**; and
- a first repo shape is part of the archive's judgment, not an implementation detail to postpone forever.

## Anti-goals
This layer should refuse:
- treating every packet as permission to launch a new tool;
- turning every first build into a Cargo merge request;
- building hosted services where local proofs would do;
- hiding maintenance burden behind “MVP” language;
- or silently kernelizing `hold` candidates.

## Default interpretation for future revisions
Until the portfolio changes materially:
- this is a **first-build deepening** move, not a frontier promotion;
- the broad ladder is unchanged;
- live packets still govern verdict posture;
- v0 kernel briefs now govern the first honest repo shape for candidates that earned it; and
- future practical-build revisions should deepen the nearest kernel brief before inventing another abstract “what should v0 look like?” note.

