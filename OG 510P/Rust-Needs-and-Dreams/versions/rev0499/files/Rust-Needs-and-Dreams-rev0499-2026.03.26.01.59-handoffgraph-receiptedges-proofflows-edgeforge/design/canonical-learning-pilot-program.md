# Design: Canonical Learning Stack Pilot Program (`cargo learncanon` + `canonical-learning-pack/v0`)

## Goal
Turn the archive’s **Canonical Learning Stack** into a ranked execution plan.

The stack already has:
- **DocProof Kit** for guide/example/doc-check truth,
- **Compile Guidance Kit** for maintainer-authored diagnostic/lint/compile-fail teaching truth,
- and a **canonical-learning consumer pilot** for downstream import discipline.

What is still missing is the stack-level rollout that proves these lanes belong together and can be shipped as one honest ecosystem contribution.

The concrete separation rule now lives in [`design/canonical-learning-lane-map.md`](./canonical-learning-lane-map.md): keep **API-doc/reference + guide/tutorial + executable-example proof + compile-guidance/negative-teaching + docs-host/build posture + structured machine-import + derived consumer overlays + review/handoff imports** distinct.

## Why this now matters
Several current Rust signals now line up unusually well:
- The 2025 State of Rust survey says online documentation remains the preferred canonical reference while some learning traffic appears to be shifting toward LLM tooling and editor/agentic workflows.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust’s 2025 vision work explicitly recommends extending crates toward **better diagnostics and guidance from crates**.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- docs.rs lets crates declare docs-build metadata and documents docs.rs-specific build behavior, cfg/env handling, and CI-facing checks.
  https://docs.rs/about/metadata
  https://docs.rs/about/builds
- docs.rs now hosts rustdoc JSON, which creates a structured documentation import lane for downstream consumers.
  https://docs.rs/about/rustdoc-json
- rustdoc executes documentation examples as tests, and mdBook has a first-class `test` command for Rust code samples in books.
  https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html
  https://rust-lang.github.io/mdBook/cli/test.html
- Rust 1.94 added `#[cfg(doctest)]`, which makes documentation-test-specific surfaces more explicit.
  https://doc.rust-lang.org/beta/releases.html
- `trybuild` already provides a practical compile-fail teaching/testing lane.
  https://docs.rs/trybuild

These ingredients mean the missing problem is no longer basic feasibility.
It is the **stack-level contract** that says what is canonical, what was checked, what is host- or target-specific, what is derived, and what downstream tools may honestly do with it.

## Stack-level design rule
The stack should stay simple:
1. **Maintainers author canon.** `doc-pack/v0` and `guidance-pack/v0` remain the canonical learning surfaces.
2. **Validation stays explicit.** Doctests, mdBook runs, compile-fail checks, and docs-host compatibility checks remain attachable evidence, not invisible implementation details.
3. **Consumers stay derived.** Docs hosts, CI, editors, assistants, atlas views, and release/support consumers import canonical learning truth through declared profiles.
4. **Authority never smuggles itself in.** A consumer that can render or summarize is not automatically allowed to mutate code/docs or infer policy/support/release conclusions.
5. **Partial imports are honest.** Incomplete or target-specific learning coverage is acceptable if the incompleteness stays visible.

## Artifact family

### `learning-lane-catalog/v0`
Declares which canonical-learning lanes are present for this subject.

Should record:
- lane ids present (`api-docs`, `guide-book`, `executable-example`, `compile-guidance`, `docs-host`, `machine-import`, `consumer-overlay`, `review-handoff`)
- which maintainer-authored artifacts own each lane
- which evidence lanes are required versus optional
- which consumers may import each lane directly

Design rule: **the lane catalog is the boundary that stops docs, guidance, execution evidence, host posture, and consumer overlays from collapsing into one blob.**


### 1) `canonical-learning-brief/v0`
Declares the learning subject.

Should record:
- package/workspace/crate/book subject ids
- intended learning lanes present (`api-docs`, `guide-book`, `cli-transcript`, `compile-guidance`, `compile-fail-teaching`)
- feature/target/toolchain/docs-host assumptions
- intended downstream consumers
- success bar for the current pilot slice

### 2) `canonical-learning-sources/v0`
Indexes which canonical learning artifacts exist.

Should record:
- `doc-pack/v0` imports
- `guidance-pack/v0` imports
- docs.rs metadata / docs-host posture imports
- target/feature slice identifiers
- source revision + freshness state

### 3) `canonical-learning-check-report/v0`
Summarizes what validation actually ran.

Should record:
- rustdoc doctest results
- mdBook test results
- compile-fail / guidance example results
- docs.rs-compat or host-specific check results when available
- omitted lanes and reasons
- target/feature/toolchain coverage

### 4) `canonical-learning-consumer-handoff/v0`
Connects the stack to downstream consumer lanes.

Should record:
- consumer profile ids
- imported sources and omissions
- whether the consumer may render, annotate, suggest, gate, or only summarize
- freshness posture
- explicit derived/not-canonical markers

### 5) `canonical-learning-pack/v0`
Review bundle containing:
- lane catalog
- brief
- source index
- check report
- consumer handoffs
- pointers to underlying `doc-pack/v0` and `guidance-pack/v0`

## Ranked rollout

The rollout should obey the lane map: canonical authoring lanes first, validation lanes second, consumer overlays third, and review/handoff imports last.


### 1) API docs + docs.rs lane
**Why first**
- It is closest to what Rust users already treat as canonical.
- docs.rs metadata, docs.rs build behavior, and rustdoc doctests already exist.

**What to prove**
- package docs can publish a bounded `doc-pack/v0` plus docs-host assumptions;
- docs.rs-specific build or target assumptions remain explicit;
- the resulting pack is good enough for host import without pretending hosted rendering is the canon.

### 2) Guide-book lane
**Why second**
- mdBook already gives Rust a serious long-form guide substrate.
- This proves that canonical learning is larger than API docs.

**What to prove**
- guide chapters and example catalogs can travel together;
- `mdbook test` results can attach to the same learning subject;
- guide-specific omissions and non-Rust blocks remain visible.

### 3) Compile-guidance lane
**Why third**
- This is where Rust’s “better diagnostics and guidance from crates” vision becomes concrete.
- It proves canonical learning includes compiler-time teaching, not just hosted prose.

**What to prove**
- compile guidance can publish stable ids, catalogs, and example links;
- compile-fail lanes can attach evidence without becoming brittle pseudo-canon;
- learning packs can link docs and diagnostics instead of leaving them as parallel worlds.

### 4) Shared consumer-import lane
**Why fourth**
- Once canonical sources exist, consumers need a bounded import rule.
- The archive already has a dedicated consumer pilot for this step.

**What to prove**
- docs hosts, CI, editors, and assistants can import canonical learning artifacts without replacing them;
- derived overlays stay marked derived;
- mutation authority and policy/support/release overclaims remain forbidden unless separately imported.

### 5) Support / atlas / release-review lane
**Why fifth**
- These are high-value downstream consumers, but they should widen only after canonical authoring and bounded import behavior exist.

**What to prove**
- atlas/release/support consumers can reuse canonical learning truth without rebuilding it from prose scraping;
- incompleteness remains visible;
- learning truth is reused as an input, not mistaken for a final product or support verdict.

## What should wait
Do **not** start with:
- a universal docs portal,
- a giant AI-context blob,
- automatic code/doc rewriting from learning imports,
- or a documentation score/ranking engine.

Those are downstream views.
The first job is to prove a stable canonical-learning subject with explicit checks and bounded consumer handoffs.

## Success bar
A canonical-learning stack pilot succeeds when it can show all of the following:
1. one real maintainer-authored canonical learning subject;
2. explicit source indexing across docs and/or compile guidance;
3. real validation evidence rather than hand-wavy “docs were reviewed” claims;
4. at least one downstream consumer handoff that stays visibly derived;
5. explicit authority boundaries for mutation and for higher-stakes conclusions;
6. one workflow improvement for docs hosting, guide maintenance, compile guidance, CI review, editor overlays, or assistants.

## Why this would count as a worthy contribution
Rust already has good learning ingredients.
What it still lacks is the **composition point** that lets humans, CI, docs hosts, editors, assistants, atlas systems, and release/support reviewers talk about the *same learning subject* without silently changing what is canonical.

That is an ecosystem contribution because it improves several strategic lanes at once:
- maintainer-authored docs stay central,
- compile guidance becomes first-class teaching surface,
- host/build assumptions stop hiding in incidental config,
- derived machine consumers become more honest,
- and downstream review can import one bounded learning pack instead of scraping blogs, READMEs, stderr, and memory.
