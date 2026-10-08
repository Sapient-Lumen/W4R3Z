# Rust ecosystem gap map — 2026-03-22

This file is the broad territory map for the current archive.
It is intentionally **not** a dump of every tempting idea.
It is a ranked synthesis of where epic-yet-worthy crate contributions still look most justified after reading the latest archive and re-checking fresh upstream signals.

## Main judgment

The strongest missing crates are usually **support contracts** that sit above already-real substrate:

- they make a messy truth reviewable,
- they hand other people a stable artifact,
- they prevent overclaiming,
- and they reduce tacit knowledge.

The archive should therefore keep preferring crates that answer
**“what does another engineer get, trust, review, diff, and reuse?”**
over crates that merely automate one local trick.

## Tier A — structural, ecosystem-wide, and still painfully under-packaged

### 1. P-0484 Toolchain & Target Support Contract Kit
Why it stays first:
- Rust’s own challenge work still calls out cross-compilation friction and embedded ecosystem maturity issues.
- Safety-critical guidance explicitly asks for target-focused readiness checklists.
- docs.rs, rustup, Cargo config, and CI still describe support truth in fragments.

What an epic crate here provides other people:
- one support-class vocabulary,
- one target-readiness checklist,
- one override-lineage receipt,
- one honest exercise-scope map,
- one host-vs-target topology artifact.

### 2. P-0011 Crate Health Contract Kit
Why it rose:
- the 2025 survey reports persistent concern around developer/maintainer support;
- the Foundation strategy now makes sustainable maintenance a named pillar;
- crates.io continues to add trust/security signals, but support posture is still diffuse.

What an epic crate here provides other people:
- one stewardship posture,
- one maintenance-window answer,
- one succession/backstop map,
- one response-channel receipt,
- one imported-signal-vs-declared-signal split.

### 3. P-0535 Dependency Lifecycle Transition Kit
Why it stays near the top:
- safety-critical guidance explicitly says teams adopt crates early, then constrain, replace, or internalize them as criticality rises;
- embedded and regulated users still need reusable transition patterns rather than bespoke folklore.

What an epic crate here provides other people:
- one criticality-lane map,
- one abstraction-seam ledger,
- one transition posture,
- one off-ramp recipe,
- one lifecycle drift report.

### 4. P-0120 Unsafe Contract Auditor Kit
Why it stays central:
- 2026 flagship safety-critical work explicitly includes normative unsafe documentation;
- unsafe obligations increasingly need source-of-truth and witness-boundary honesty, not just comments and Miri runs.

What an epic crate here provides other people:
- one obligation inventory,
- one authority-source map,
- one witness-fidelity report,
- one interpreter-boundary receipt,
- one portable audit bundle.

## Tier B — productivity pain that still taxes almost everybody

### 5. P-0486 Debuggability Support Contract Kit
Why it rose:
- the 2025 survey still lists debugging among notable productivity pain points;
- the 2026 debugging survey makes the gaps explicit: debugger-family support, visualizers, async debugging, and Rust-expression evaluation.

What an epic crate here provides other people:
- one support-posture verdict,
- one symbol-sidecar manifest,
- one backend-coverage report,
- one source-lookup impact report,
- one diffable release handoff.

### 6. P-0490 Cargo Lock Contention Witness Kit
Why it remains high:
- build-dir/layout work is making contention more concrete, not less;
- teams still need a portable answer for who blocked whom, under which root and command lane.

What an epic crate here provides other people:
- one root-authority receipt,
- one actor command-lane receipt,
- one observed wait-window report,
- one blocker-identity exactness class,
- one mitigation-cost explanation.

### 7. P-0469 Cargo Rebuild Explanation Kit
Why it remains high:
- the compiler-performance survey shows incremental rebuilds and “why is this slow?” remain central pain;
- the March 2026 challenges write-up treats compile performance as the universal productivity tax.

What an epic crate here provides other people:
- one baseline-authority answer,
- one comparison-compatibility check,
- one reverse-impact report,
- one exactness class,
- one reviewable rebuild bundle.

### 8. P-0435 Cargo Script Workbench Kit
Why it stays relevant:
- single-file packages are becoming more real upstream;
- the missing value is still not another launcher but support truth around frontmatter, discovery, cache residency, and export.

What an epic crate here provides other people:
- one frontmatter-authority receipt,
- one discovery-scope receipt,
- one invocation-interpretation receipt,
- one cache-residency receipt,
- one export-lineage plan.

## Tier C — ecosystem navigation, machine-readable learning, and “supportive crate interfaces”

### 9. P-0536 Crate Knowledge Pack Kit
Why this new lane belongs:
- the survey says docs remain canonical;
- the same survey suggests some learning activity is shifting toward LLM tooling;
- raw rustdoc/docs.rs substrate already exists, but there is still no maintainer-approved, provenance-aware crate knowledge handoff.

What an epic crate here provides other people:
- one canonical API/docs/example pack,
- one official-vs-inferred provenance split,
- one visibility map for feature/target gating,
- one query slice for support/search/assistant use,
- one diffable knowledge bundle.

### 10. P-0476 Rustdoc Coverage Review Bundle Kit
Why it remains important:
- docs debt is still hard to review with percentages alone;
- public-item importance and example debt still need API-aware review artifacts.

### 11. P-0472 Docs.rs Build Parity & Evidence Kit
Why it stays distinct:
- hosted docs behavior, target defaults, and sandbox limits still drift in ways ordinary maintainers miss;
- parity evidence remains different from canonical docs knowledge.

### 12. P-0518 Crate Observability Surface Pack Kit
Why it deserves attention:
- crates increasingly need “supportive interfaces”, not just raw emitted signals;
- adopters still lack a stable answer to what a crate emits, where it goes, what it costs, and what is safe to rely on.

## Tier D — strategically important domain and assurance lanes

These remain highly worthy, but they are less “universal missing middle” and more “critical frontier for specific domains”:

- **P-0532 Async Runtime Assurance Profile Kit**
- **P-0431 Public Dependency Boundary Kit**
- **P-0433 MC/DC Coverage Workbench Kit**
- **P-0459 Clippy Safety Profile & Waiver Kit**
- **P-0460 Unsafe Field Invariant Ledger Kit**
- **P-0121 FFI Boundary & Bindings Conformance Kit**

These are still epic lanes.
They simply lose a little salience in a broad portfolio rerank because the archive has already been productizing them aggressively.

## Where the archive should synthesize or eliminate instead of proliferating

### Do not add another “docs thing” unless it clearly escapes this cluster
- P-0051 rustdoc JSON normalization
- P-0455 doctest extraction/support
- P-0472 docs.rs parity evidence
- P-0476 docs coverage review
- P-0536 crate knowledge pack

### Do not add another generic “Cargo is slow” idea unless it clearly escapes this cluster
- P-0490 lock contention
- P-0469 rebuild explanation
- P-0484 toolchain/target support
- P-0435 cargo script workbench

### Do not add another generic “crate trust / health / support” idea unless it clearly escapes this cluster
- P-0011 crate health
- P-0535 dependency lifecycle transition
- P-0431 public dependency boundary

### Do not add another “safe async helper” unless it clearly escapes this cluster
- P-0532 async runtime assurance
- the existing async language/library roadmap upstream

## What should count as a worthy or epic crate contribution after this pass

A proposal should usually satisfy most of these:

1. **Receiver-facing** — another engineer gets a stable artifact or contract.
2. **Cross-context useful** — it helps CI, release review, support, docs, or policy, not just one workstation.
3. **Honesty-preserving** — it prevents overclaiming by keeping distinct truths separate.
4. **Diffable** — it creates release-to-release or branch-to-branch review value.
5. **Substrate-leveraging** — it stands on real upstream facts rather than fantasy.
6. **Portfolio-aware** — it sharpens or joins existing lanes instead of cloning them.
7. **Sustainable** — a small team could realistically maintain it.

## Freshness anchors

- 2025 State of Rust survey — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust challenges / vision follow-up — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- Rust compiler performance survey 2025 results — https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Rust debugging survey 2026 — https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Rust in 2026 flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- What does it take to ship Rust in safety-critical? — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- crates.io development update — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Rust Foundation strategic plan 2026–2028 — https://rustfoundation.org/strategic-plan/
- docs.rs rustdoc JSON — https://docs.rs/about/rustdoc-json
- docs.rs builds — https://docs.rs/about/builds
