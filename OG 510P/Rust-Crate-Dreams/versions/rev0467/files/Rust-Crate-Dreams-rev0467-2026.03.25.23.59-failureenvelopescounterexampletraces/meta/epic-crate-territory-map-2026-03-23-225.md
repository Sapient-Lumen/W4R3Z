# Epic crate territory map 225 — preserve extreme variety, but rank the work by ecosystem leverage

The archive is now too broad for a single flat ranking to do honest work.
The better model is a **territory map** with explicit bands.
That lets us keep deep variety without losing prioritization discipline.

## Band A — control-plane epics (highest salience)

These are the most ecosystem-worthy missing crates because they turn repeated, cross-domain pain into portable review artifacts.
They are the crates most likely to improve life for library authors, app teams, infra teams, embedded teams, safety-critical adopters, tooling authors, and future assistants at the same time.

### 1. P-0537 Compile Iteration Feedback Kit
**Why here:** compile time, rebuild opacity, and dev-loop friction remain among Rust's most persistent ecosystem pains, while official Cargo work is actively moving toward build analysis, build-dir reform, and relink-first workflows.

**What it should provide other people:**
- build-basis receipts,
- rebuild-reason reports,
- cache-contention reports,
- live-update outcome / degraded-mode reports,
- ranked action plans,
- portable run bundles for comparing multiple iterations.

### 2. P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit
**Why here:** crates.io surfaces keep improving, but teams still need help deciding **which** crate family to adopt, what trade-offs they are accepting, and how to replay that decision later.

**What it should provide other people:**
- candidate corpus captures,
- inclusion / exclusion receipts,
- starter-set manifests,
- re-entry policies,
- decision timeboxes,
- reviewable “why this won” bundles.

### 3. P-0535 Dependency Lifecycle Transition Kit
**Why here:** supply-chain reality is not just “is this dependency okay today?” It is “how do we replace, pin, fork, phase out, or re-resolve it safely later?”

**What it should provide other people:**
- selection anchors,
- clean-resolve risk reports,
- override-authority receipts,
- source-parity / fork-drift reports,
- off-ramp recipe bundles,
- local-architecture placement records.

### 4. P-0536 Crate Knowledge Pack Kit
**Why here:** the ecosystem increasingly needs cited, pinned, machine-usable crate knowledge that respects version, build, target, and docs.rs limits.

**What it should provide other people:**
- material-basis receipts,
- excerpt lineage,
- citation locators,
- item witnesses,
- build-surface / conditioned-availability notes,
- answerability/refusal matrices,
- compact exports for downstream tools.

### 5. P-0538 Concurrency Contract Kit
**Why here:** async and concurrency complexity remain live pains, and today's crate docs rarely make the critical semantics portable or comparable.

**What it should provide other people:**
- reentrancy scope,
- fairness / progress class,
- cancellation / recovery posture,
- delivery memory,
- audience / claim semantics,
- order / gap visibility,
- closure / join / observer-cursor truth,
- portable support bundles.

### 6. P-0486 Debuggability Support Contract Kit
**Why here:** debugging now has both survey evidence and a dedicated 2026 compiler-team survey behind it. Debug support remains inconsistent across debugger families, operating systems, async code, symbols, and type presentation.

**What it should provide other people:**
- debug-support posture receipts,
- symbol-sidecar manifests,
- backend-observation reports,
- artifact-completeness checks,
- source-material lookup receipts,
- portable debug-support bundles.

### 7. P-0484 Toolchain & Target Support Contract Kit
**Why here:** teams still need a better answer to “what does support for this target / toolchain / profile / host-target route actually mean?”

**What it should provide other people:**
- target support receipts,
- exercised-environment records,
- external-prerequisite declarations,
- host-vs-target execution truth,
- `std` / `no_std` / allocator / linker / sanitizer route boundaries,
- portable support bundles.

### 8. P-0011 Crate Health Contract Kit
**Why here:** stewardship still matters, and richer trust surfaces make over-reading easier rather than harder.

**What it should provide other people:**
- maintenance-window truth,
- maintenance-coverage truth,
- succession maps,
- support-intent receipts,
- routing-drift diffs,
- imported-signal separation from maintainer promises.

### 9. P-0532 Async Runtime Assurance Profile Kit
**Why here:** the “Just Add Async” flagship work makes runtime assumptions, service topology, and capability routes more important, not less.

**What it should provide other people:**
- runtime topology receipts,
- capability matrices,
- surface guards,
- bridge-debt evidence,
- portability ceilings across local / threaded / embedded / serverless lanes.

### 10. P-0431 Public Dependency Boundary Kit
**Why here:** official 2026 supply-chain goals make public/private dependency boundaries more important, but teams still need reviewable migration and boundary evidence rather than only compiler support.

**What it should provide other people:**
- manifest-intent receipts,
- effective-boundary verdicts,
- breakage-risk bundles,
- migration aids for boundary tightening.

## Band B — adoption amplifiers (high salience, but not always first)

These crates help users adopt difficult language / tooling / safety capabilities with honest boundaries.
They become especially important when a new Rust capability is emerging but not yet comfortably operational for ordinary teams.

### Strong adoption-amplifier lanes
- **P-0427 Rust Specification Witness Kit** — clause-linked executable examples and drift witnesses above FLS / reference work.
- **P-0433 MC/DC Coverage Workbench Kit** — safety-critical coverage evidence above Rust coverage tooling.
- **P-0440 Projection & Reborrow Semantics Kit** — projection authority, borrow-mode coverage, and witness-backed semantics.
- **P-0447 In-Place Initialization Adoption Kit** — constructor-lane comparison, address-commit receipts, and cleanup evidence.
- **P-0125 Cargo SBOM Precursor Workbench Kit** — reviewable SBOM groundwork while official substrate matures.
- **P-0175 Trusted Publishing Tooling Kit** — workflow-route receipts, registry-state imports, and authorization-drift evidence.
- **P-0036 MSRV Workspace Lab** — effective workspace-floor and command-family-floor truth.
- **P-0455 Doctest Extraction & Support Contract Kit** — extraction basis, rewrite lineage, and execution-mode honesty.
- **P-0528 Cargo Feature Surface Contract Kit** — public feature surface and activation-profile truth.
- **P-0120 Unsafe Contract Auditor Kit** — authority imports, obligation drift, and witness comparison above unsafe code review.

### What adoption amplifiers should provide
- capability matrices,
- witness reports,
- migration / adoption checklists,
- lane-boundary notes,
- scenario fixtures showing close-but-not-equal cases,
- doctor checks rejecting fake support claims.

## Band C — sector labs and interop workbenches (broad variety, targeted leverage)

This archive already has serious breadth here: healthcare, robotics, industrial, automotive, identity, geospatial, media, scientific data, privacy, attestation, accessibility, and more.
That breadth should stay.
But these proposals should normally be promoted only when they are clearly more than wrappers.

### A sector/workbench crate should usually provide
- conformance corpora,
- profile / dialect matrices,
- golden fixtures,
- interop evidence receipts,
- replayable test harnesses,
- conversion-loss or portability reports.

### Promotion rule for this band
Promote a sector lab upward only when it:
1. serves a recognized standard or hard interoperability seam,
2. exports evidence artifacts other teams can audit,
3. is useful across multiple organizations or products,
4. avoids collapsing dialect, profile, capability, and policy into one fake “supports X” story.

## Band D — moonshots / outside-the-box pack-family bets

These are the ideas that could become epic later if they prove a reusable seam.
They should be incubated as pack families or operator substrates before being promoted as top-frontier crates.

### Current promising moonshot patterns
- crate-surface pack families (`crate-authority-surface-pack-kit`, `crate-runtime-handoff-pack-kit`, `crate-upgrade-pack-kit`, etc.),
- `evidence-bundle-core-kit`,
- `assurance-case-workbench-kit`,
- `capability-sandbox-kit`,
- cross-crate pack / bundle substrate that lets many crates publish reusable support contracts.

### What a moonshot should prove before promotion
- a real import seam between crates or tools,
- a minimal portable artifact format,
- at least two or three distinct use cases,
- a convincing exit from “this is a concept doc” into “other people would adopt this substrate”.

## What counts as a worthy or epic crate contribution now

A crate is usually worthy of promotion when it does most of the following:

1. cuts a recurring decision or support cost felt by many teams,
2. exports **receipts, reports, manifests, or bundles** another team can inspect later,
3. keeps adjacent truths separate instead of flattening them into one marketing word,
4. composes with Rust / Cargo / docs.rs / crates.io / CI / rustup instead of trying to replace them,
5. remains useful even if an upstream language or compiler feature lands later,
6. gives downstream users one materially sharper answer than README spelunking does today,
7. has a realistic maintenance and governance story.

## What to demote, merge, or eliminate

Default demotion candidates are:
- protocol/client/parser wrappers without conformance or evidence artifacts,
- generic “crate ranking” or trust-score dashboards,
- generic AI shells without material-basis and citation receipts,
- thin runtime or adapter wrappers that flatten semantics,
- work that waits on a future language feature without offering present-day value.

When in doubt, prefer **deepen / merge / eliminate** over **append**.

## Operational shape every serious proposal should aim for

A serious proposal should describe:
- the artifact family (`*.receipt.json`, `*.report.json`, `*.manifest.json`),
- the doctor / triage commands,
- the scenario fixtures,
- the human review flow,
- the machine-consumable export surface,
- the maintenance / deprecation / off-ramp story.

## Sources consulted
- Rust challenges — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust in 2026 / flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo build analysis — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Cargo build-dir layout — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Relink-don't-rebuild — https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- crates.io development update — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io malicious crate update — https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- docs.rs builds — https://docs.rs/about/builds
- docs.rs metadata — https://docs.rs/about/metadata
- docs.rs rustdoc JSON — https://docs.rs/about/rustdoc-json
- Rust debugging survey 2026 — https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- safety-critical Rust write-up — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
