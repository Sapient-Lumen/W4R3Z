# Epic crate receiver persona map — 2026-03-24

This note answers a planning question the archive had started circling but had not fully pinned down:

> Who should the leading crates serve first, and what should those people actually receive?

The archive already has salience boards, delivery cards, review packets, and first-release bundles.
What it still needed was a receiver-centered map that keeps crate design grounded in **real organizational roles** instead of generic “users”.

## Main judgment

A worthy epic crate should usually serve at least **three receiver classes** well, not just one:

1. the **builder / maintainer** doing the work,
2. the **reviewer / operator** checking the work,
3. and the **machine / assistant / automation** that needs an importable basis.

If a crate only serves one class, it may still be useful, but it is less likely to count as an ecosystem-shaping epic.

## Receiver classes

### 1. Application maintainer

Needs:
- a smaller choice surface,
- a quick path to “good enough” defaults,
- explicit manual-review triggers,
- and a path out if the choice later ages badly.

Best fit:
- **P-0509 Pathfinder**
- **P-0535 Dependency Lifecycle Transition**
- **P-0536 Crate Knowledge Pack**

What they should receive:
- `decision-brief.md`
- `starter-set.bundle.json`
- `candidate-elimination.receipt.json`
- `manual-review.note.md`
- `offramp-bundle.manifest.json`

### 2. Platform / enablement engineer

Needs:
- a standardized baseline other teams can reuse,
- scenario packs for common workload classes,
- and a way to freeze, replay, or reconsider defaults over time.

Best fit:
- **P-0509 Pathfinder**
- **P-0536 Crate Knowledge Pack**
- **P-0496 Cargo Vendor & Source Parity**
- **P-0484 Toolchain & Target Support**

What they should receive:
- `starter-set.lock`
- `revisit-trigger.policy.json`
- `support-visibility.report.json`
- `source-coverage.report.json`
- `target-support.receipt.json`

### 3. Release / CI engineer

Needs:
- evidence that build and docs surfaces match expectations,
- visibility into hidden path dependencies on layout details,
- and a way to explain why a job broke after a substrate change.

Best fit:
- **P-0472 Docs.rs Build Parity**
- **P-0489 Build-Dir Consumer Transition**
- **P-0496 Cargo Vendor & Source Parity**
- **P-0046 Buildscript UX**

What they should receive:
- `parity-gap.report.json`
- `issue-bundle.manifest.json`
- `source-parity.lock`
- `source-origin.receipt.json`
- `build-explanation.report.json`

### 4. Reviewer / security engineer

Needs:
- one boring review packet,
- imported trust signals with provenance,
- and explicit boundaries on what the packet does not certify.

Best fit:
- **P-0536 Crate Knowledge Pack**
- **P-0496 Cargo Vendor & Source Parity**
- **P-0535 Dependency Lifecycle Transition**
- **P-0125 Cargo SBOM Precursor**

What they should receive:
- `claim-trace.report.json`
- `citation-locator.receipt.json`
- `source-coverage.report.json`
- `selection-anchor.receipt.json`
- `answer-boundary.note.md`

### 5. Debugger / incident responder

Needs:
- session-family coverage truth,
- visibility into symbol and backend reality,
- and a claim ceiling that separates “can attach” from “can inspect async state usefully”.

Best fit:
- **P-0486 Debuggability Support**
- **P-0484 Toolchain & Target Support**
- **P-0058 Native Deps** when symbolization or backend prerequisites matter

What they should receive:
- `session-family.report.json`
- `capability-witness.report.json`
- `claim-ceiling.report.json`
- `external-prerequisite.report.json`

### 6. Offline / regulated adopter

Needs:
- no fake “works everywhere” claims,
- durable evidence bundles,
- clarity about mirrors, vendoring, local transfer, and foreign prerequisites,
- and exportable packets for review outside hosted systems.

Best fit:
- **P-0496 Cargo Vendor & Source Parity**
- **P-0484 Toolchain & Target Support**
- **P-0058 Native Deps**
- **P-0536 Crate Knowledge Pack**

What they should receive:
- `source-coverage.report.json`
- `vendor-parity.report.json`
- `external-prerequisite.report.json`
- `abi-provenance.report.json`
- `assistant-context.pack.json`
- `answer-boundary.note.md`

### 7. Tooling / LLM / automation consumer

Needs:
- pinned citations,
- stable-enough machine surfaces,
- explicit format/version windows,
- and refusal boundaries when a question exceeds the available evidence.

Best fit:
- **P-0536 Crate Knowledge Pack**
- **P-0509 Pathfinder**
- **P-0472 Docs.rs Build Parity**

What they should receive:
- `assistant-context.pack.json`
- `claim-trace.report.json`
- `query-support.matrix.json`
- `starter-set.bundle.json`
- `build-surface.receipt.json`

## Crosswalk for the top current epics

### P-0509 — Pathfinder
Primary receivers:
- application maintainer,
- platform engineer,
- reviewer.

Core value:
- help another person choose and revisit a starter set without flattening all scenarios into one best-crate answer.

### P-0536 — Crate Knowledge Pack
Primary receivers:
- reviewer,
- tool/LLM consumer,
- platform engineer.

Core value:
- make current crate knowledge pinned, cited, machine-usable, and bounded.

### P-0486 — Debuggability Support
Primary receivers:
- debugger / incident responder,
- application maintainer,
- reviewer.

Core value:
- tell another person what debugging support actually exists for this session family and what still requires manual investigation.

### P-0496 — Cargo Vendor & Source Parity
Primary receivers:
- release / CI engineer,
- offline / regulated adopter,
- reviewer.

Core value:
- tell another person where the dependency graph actually came from and whether “offline / mirrored / vendored” claims are honest.

## Receiver rule

Before promoting any proposal, the archive should now ask:

1. which receiver classes does it serve?
2. what exact packets do they receive?
3. can at least one human receiver and one machine receiver use the result?
4. what review task becomes boring because the crate exists?

If those questions do not yet have tight answers, the proposal probably still needs more planning.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://rust-lang.github.io/rust-project-goals/2025h1/rust-vision-doc.html
- https://rust-lang.github.io/rust-project-goals/2024h2/notes.html
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
