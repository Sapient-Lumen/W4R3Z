# Epic-contribution kernel interface contracts (2026 Q1)

## Why this note exists
The archive now has:
- broad ranking and macro-program notes,
- reference architectures,
- launch charters,
- stage gates,
- review packets,
- dossiers and live decision packets,
- v0 kernel briefs,
- and slice-0 milestone plans.

What it still lacked was the next practical answer after slice planning:
**what exact command, file, schema, and receipt surfaces should a first implementation expose so two teams could build the same kernel without telepathy?**

That missing layer creates four avoidable failures:
- a kernel brief stays conceptually sharp but implementation still drifts because command names, emitted artifacts, and negative states are implicit;
- slice plans quietly widen because they never freeze the first contract surface;
- later assistants re-invent package names, schema families, or CLI verbs from memory; and
- experimental imports get treated like stable contracts because the interface boundary was never written down.

A **kernel interface contract** is the missing bridge.
It is narrower than a kernel brief, more durable than a slice note, and more machine-facing than a packet.

## What a kernel interface contract is
A kernel interface contract should answer:
- what the first public surfaces are;
- what commands or document operations exist;
- what artifact families are emitted;
- what stable imports are allowed;
- what optional experimental imports are labeled as such;
- what versioning posture applies;
- what negative states or unsupported-state receipts must stay visible;
- and what contract widening is still refused.

A kernel interface contract is **not**:
- a promise that Cargo or the Rust project will upstream the surface;
- a hidden API-freeze for every possible consumer;
- or a hosted-service roadmap in disguise.

Think of it as the archive's **first interoperable machine-facing spine** for a top-band kernel.

## Why this is the right next layer now
Fresh Rust signals still reward explicit machine-facing seams and careful negative-state handling:
- Cargo's external-tools chapter still points tool authors to `cargo metadata`, `--message-format=json`, and custom subcommands rather than undocumented scraping.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- That same chapter warns that `--message-format=json` only governs Cargo and rustc output, and commands may emit additional non-JSON output afterward. That means first contracts need explicit end-of-stream and partial-output posture rather than “just parse stdout”.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo build analysis is still prototyping recorded build metadata and unstable `cargo report` subcommands, explicitly avoiding user-facing stability guarantees during the prototype phase. That makes stable/experimental separation inside the contract layer mandatory.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The build-dir-layout goal and March 2026 testing call still say many tools rely on unspecified layout details and ask users to validate real workflows. That makes path/layout caveats part of the interface contract, not an implementation footnote.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo's plumbing goal still frames phase-oriented command seams as third-party experimentation, which argues for companion-first contracts rather than premature upstream entitlement.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo's unstable SBOM pre-cursor feature already emits JSON files with a defined naming pattern. Even if unstable, it is evidence that artifact-family thinking is now real and importable.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- The 2026 debugging survey still frames the missing work as tuple-specific capability truth — debugger × OS × async × visualizer × expression evaluation — which wants session-pack and tuple-card contracts more than a new debugger ranking.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- crates.io's January 2026 update and the March 2026 Cargo advisory both reinforce route-specific intake work: Trusted Publishing and provenance/security improvements are real, but alternate-registry and route posture still need explicit local review artifacts.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- The safety-critical writeup still points toward checklists, playbooks, evidence links, and shared ownership — which means readiness-card contracts should prioritize owner/freshness/evidence fields and diffability over flashy UX.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

Taken together, those signals say the next worthy repo layer is **contract surfaces for already-earned kernels**, not another ranking rewrite.

## What belongs in the first contract corpus
The first corpus should cover only kernels that already have:
- a live packet,
- a kernel brief,
- and a slice-0 plan.

That means:
1. **Build-State Evidence** → yes
2. **Feedback / Debug Acceptance Commons** → yes
3. **Package Intake + Release Boundary Review** → yes
4. **Safety-Critical + Institutional Readiness Commons** → yes
5. **Navigation / Defaults / Claims Commons** → **still no**

Why navigation/defaults is still absent:
- it is still `hold`;
- its blocker is renewal/stewardship burden, not missing machine-facing protocol work;
- contract-writing it now would create fake implementation certainty before the editorial renewal problem is solved.

## Required fields for a kernel interface contract
Every contract note should keep these sections visible:
1. **identity** — candidate, governing kernel, governing slice;
2. **contract scope** — what exact surface is being fixed now;
3. **public surfaces** — commands, files, cards, or rendered outputs;
4. **required inputs** — what the operator must provide;
5. **emitted artifact families** — schema families, receipts, notes, or packs;
6. **stable imports** — documented imports that may be relied on;
7. **optional experimental imports** — allowed but caveated imports;
8. **versioning and compatibility posture** — how the first contract evolves;
9. **negative states / receipts** — what unsupported, partial, or ambiguous states must be preserved;
10. **proving-ground invocation** — one real way the contract should be exercised;
11. **refused expansions** — what bigger protocol shape is still out of bounds;
12. **exit criteria** — what would justify widening or stabilizing the contract.

## The first contract family
### 1) Build-State Pack → `build-state-pack/contract0`
This should define:
- `capture`, `diff`, and `doctor` command surfaces;
- the first session-pack / diff / doctor-note artifact families;
- stable use of Cargo metadata + JSON messages;
- optional unstable imports for `cargo report *`, build-dir-layout-v2, or SBOM pre-cursors with caveat labels;
- and explicit partial-output / mixed-output receipts.

### 2) Debug Acceptance Matrix → `debug-acceptance-matrix/contract0`
This should define:
- `collect`, `tuple-card`, `replay`, and `matrix` surfaces;
- session-pack, tuple-card, and replay-result artifact families;
- debugger/runtime/version tuple identity requirements;
- and unsupported-state receipts for visualizer, async, stepping, or expression-evaluation gaps.

### 3) Package Intake Review Kit → `package-intake-review-kit/contract0`
This should define:
- `review`, `waive`, `quarantine`, and `drill` surfaces;
- route-profile, intake-receipt, waiver, quarantine, and drill-report families;
- stable local project/workflow inputs;
- optional provenance, capability-analysis, SBOM, or advisory imports;
- and explicit handling for alternate-registry uncertainty.

### 4) Safety-Critical Readiness Cards → `safety-critical-readiness-cards/contract0`
This should define:
- `lint`, `pack`, and `diff` surfaces;
- readiness-card, readiness-pack, and stale-card receipt families;
- owner/freshness/evidence/"does not prove" minimums;
- and refusal of certification theater, badge issuance, or universal-readiness claims.

## What these first contracts should teach
- a worthy top-band contribution should usually expose a **small explicit contract surface** before it chases adoption breadth;
- experimental imports must stay visibly experimental;
- negative states are part of the contract, not a bug to hide later;
- command names and artifact families matter because they determine whether a kernel is actually reusable; and
- refusing to contractize a `hold` candidate is part of the archive's quality bar.

## Anti-goals
This layer should refuse:
- treating a contract note as proof that a surface is upstream-worthy;
- pretending unstable Cargo prototype data is already a stable interface;
- turning every contract into a long-term network protocol or hosted API;
- flattening CLI, schema, rendered note, and receipt surfaces into one fake “API”; or
- writing contracts for candidates that are still blocked on stewardship rather than product shape.

## Default interpretation for future revisions
Until the portfolio changes materially:
- this is a **contract-surface deepening** move, not a frontier promotion;
- the broad ladder is unchanged;
- live packets still govern verdict posture;
- kernel briefs still govern repo shape;
- slice notes still govern first milestones;
- and kernel interface contracts now govern the **first explicit command/file/schema surface** for kernels that have already earned implementation.
