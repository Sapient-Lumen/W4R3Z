# Design: Semantic-Context Pilot Program (`cargo semctx pilot`, `semctx-pilot-pack/v0`)

## Goal
Turn the **Semantic Context Kit** from a strong substrate idea into a ranked rollout program that proves real reuse quickly:
- capture exact semantic subjects,
- reuse canonical Rust inputs without pretending they are interchangeable,
- ship bounded query packs for concrete consumers,
- and keep assistant/editor workflows attached to canonical evidence instead of hidden tool-local indexes.

The archive already argues that semantic context is strategically important. The missing layer is now more practical:
- which semantic lanes should be piloted first,
- which consumers justify the work immediately,
- where local builds, docs.rs caches, and compiler-backed lanes should stay distinct,
- and how to keep the project from collapsing into another universal “AI context” or bespoke workspace-index effort.

A worthy contribution here is not just `cargo semctx capture`. It is a disciplined pilot plan that proves a few high-value semantic lanes are reusable across materially different consumers before widening the ontology.

Use [`design/semantic-context-lane-map.md`](./semantic-context-lane-map.md) as the authority/freshness lane map for the pilots below. The pilot program decides **which lanes to ship first**; the lane map decides **what each lane is allowed to claim**.

## References (signals)
- The 2025 State of Rust survey says official online docs remain the preferred canonical reference while LLM tooling and agentic/editor workflows are becoming a bigger part of how people learn and navigate Rust.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo’s plumbing goal explicitly says the current machine-facing surface is too thin and that `cargo metadata` does not expose enough, including feature-resolution truth.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- The GSoC 2025 plumbing prototype implemented `resolve-features` and `plan-build`, proving that reusable Cargo phases now exist as concrete building blocks instead of only design wishes.
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- The July 2025 `cargo-semver-checks` update says accurate cross-crate analysis still needs recursive active dependency-feature truth and `rmeta`-based combination, while also noting that docs.rs-hosted rustdoc JSON makes cache reuse more plausible.
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- docs.rs now hosts rustdoc JSON and explicitly tells consumers to check `format_version`, which makes version-aware semantic caching both possible and necessary.
  https://docs.rs/about/rustdoc-json
- StableMIR publication is explicitly about enabling tool developers to analyze compiled crates and dependencies without relying on compiler internals, which gives semantic-context work a plausible deeper lane once the basic pack model is stable.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- Cargo’s 1.93 development-cycle update says schema unification is being considered partly to enable a faster and more flexible `cargo fix` architecture. That is a strong signal that structured, reusable context is becoming a first-class Cargo concern.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/

## Why this needs its own design layer
The Semantic Context Kit already defines the base artifact family: subject, resolution/build context, input catalog, merge report, query report, diff report, and pack.

What it did **not** yet answer clearly enough is:
- which input lanes are mature enough to pilot first,
- which consumers need semantic packs immediately,
- what a minimal cache/freshness discipline looks like,
- how assistant/editor slices should stay derived instead of becoming the canon,
- and what counts as pilot success versus a polite demo.

Without that layer, semantic-context work risks two bad outcomes:
1. **universal-index drift** — the archive starts implying one giant hidden workspace graph can answer everything;
2. **AI-context theater** — tool authors present an opaque assistant payload as if it were the same thing as canonical Rust semantic evidence.

## Design principles
1. **Start with exact subject identity.** Every pilot begins by proving which workspace/package/target/profile/feature/toolchain subject is being described.
2. **Keep authoritative, cached, derived, and experimental lanes visibly distinct.** A pilot may compose them, but it may not erase the boundaries.
3. **Prefer high-value consumers with correctness pressure.** Semver and docs/search consumers are better first pilots than vague “smart coding assistant” demos.
4. **Keep lane provenance visible.** Local rustdoc JSON, docs.rs rustdoc JSON, Cargo outputs, `rmeta`, and StableMIR are not interchangeable evidence.
5. **Bound query families aggressively.** A pilot should answer a few named questions well, not promise a general Rust knowledge graph.
6. **Assistant/editor consumers come later and weaker.** They may consume derived slices, but only after canonical and reviewable lanes exist.
7. **Cache posture is part of the contract.** Freshness, format-version, and local-vs-remote provenance belong in the pilot artifacts.
8. **Graduation requires reuse across different consumers.** A pretty one-tool demo is not enough.

## Artifact family
### 1. `semctx-pilot-brief/v0`
Why this semantic lane is being piloted.

Should record:
- pilot id and summary
- subject family (`local-workspace`, `docsrs-cache`, `compiler-backed`, `edit-handoff`, `assistant-slice`)
- why this lane matters now
- which consumer(s) it is meant to serve
- why the lane is tractable now

### 2. `semctx-lane-profile/v0`
The declared semantic lane contract for a pilot.

Should record:
- authoritative inputs allowed
- fallback inputs allowed
- required subject fields
- cache/freshness rules
- format-version expectations
- known unsupported areas
- redaction/privacy posture when relevant

Design rule: **do not smuggle lane semantics into prose**.
If a pilot depends on them, make them artifacts.

### 3. `semctx-query-budget/v0`
The bounded question set for the pilot.

Should record:
- named query families in scope
- required answer fields
- allowed uncertainty classes
- required reason codes for incompleteness
- query cost / latency expectations when relevant
- explicit out-of-scope queries

Design rule: **a pilot is not a universal query engine**.
It is a bounded semantic service lane.

### 4. `semctx-consumer-handoff/v0`
How a downstream consumer imports the pilot output.

Should record:
- consumer class (`semver`, `docs`, `fix-lint`, `editor`, `assistant`, `review-ci`)
- which artifacts are consumed directly
- which artifacts are rendered into a weaker derived view
- what additional local assumptions the consumer makes
- what the consumer must not claim on top of the pack

Design rule: **consumer power should be explicit**.
Derived assistant/editor views are weaker than canonical captured context.

### 5. `semctx-pilot-scorecard/v0`
Decides whether the pilot is worth widening.

Should ask:
- did the pilot preserve subject and provenance truth honestly?
- did at least one real downstream consumer use it?
- did the pilot keep authoritative and fallback lanes visibly distinct?
- did it avoid becoming a hidden universal index?
- did it make incompleteness/freshness visible instead of hiding it?
- does widening the pilot still look justified?

### 6. `semctx-pilot-pack/v0`
Bundle for review and reuse:
- pilot brief
- lane profile
- query budget
- consumer handoff
- semantic artifacts from the base kit
- current scorecard
- references and rendered summaries

## Ranked first pilots

### 1) Local workspace + semver consumer lane
**Why first**
- Cross-crate semver work is already blocked on better feature-resolution truth and reliable cross-crate combination.
- This lane has strong correctness pressure and a clear consumer.
- It proves the most important semantic-context claim first: exact subject identity plus explicit build/resolution provenance.

**Core artifacts**
- `semctx-subject/v0`
- `resolution-context/v0`
- `semantic-input-catalog/v0` for Cargo/plumbing + local rustdoc JSON
- `semantic-merge-report/v0`
- `semantic-query-report/v0` for bounded semver-facing questions

**Primary consumers**
- semver / public-api analysis
- release-admission review
- downstream compatibility review

### 2) docs.rs cache + canonical-doc lookup lane
**Why second**
- docs remain canonical, and docs.rs-hosted rustdoc JSON is now real infrastructure.
- This lane proves the archive can reuse remote canonical-ish inputs without pretending they are the same as local builds.
- It turns “docs are canonical” into a machine-usable but still reviewable workflow.

**Core artifacts**
- `semctx-lane-profile` with docs.rs freshness and `format_version` rules
- `semantic-input-catalog/v0` with docs.rs vs local provenance
- `semantic-query-report/v0` for item lookup / documentation-context queries
- `semctx-diff-report/v0` for local-vs-docsrs comparability

**Primary consumers**
- docs/search frontends
- atlas/navigation layers
- reviewer-facing lookup tools

### 3) fix/lint context handoff lane
**Why third**
- Cargo and lint/fix workflows increasingly need structured machine-facing context.
- This lane proves that edit/lint consumers can import bounded semantic context rather than rebuilding private workspace indexes.
- It is the natural bridge from Semantic Context to Edit Workflow without collapsing the two.

**Core artifacts**
- `semctx-query-budget/v0` for fix/lint context families
- `semctx-consumer-handoff/v0` to `cargo editflow` or other fix/lint consumers
- `semantic-query-report/v0` with explicit unsupported markers

**Primary consumers**
- lint/fix tools
- migration tools
- CI/review automation

### 4) Editor / assistant context-slice lane
**Why fourth**
- Official survey data says these workflows are rising, but canonical docs remain primary.
- This is exactly why they should arrive after stronger reviewable lanes exist.
- The value is not “ship the assistant”. It is to prove bounded derived slices can exist without replacing the canonical pack.

**Core artifacts**
- `semctx-consumer-handoff/v0` with weaker-authority derived-view semantics
- explicit render/export profile for bounded slices
- scorecard checks that derived views do not erase provenance, freshness, or unsupported areas

**Primary consumers**
- editor overlays
- assistant tools
- question-answering / navigation helpers

### 5) Compiler-backed augmentation lane (`rmeta` / StableMIR / `rustc_public`)
**Why fifth**
- This is the most powerful lane, but also the easiest to over-promise.
- It should arrive only after the pack model, consumer handoffs, and cache posture already work.
- The likely result for some time will be mixed authoritative/experimental truth, which the pilot should be allowed to report honestly.

**Core artifacts**
- `semantic-input-catalog/v0` with experimental/compiler-backed lane identity
- `semantic-merge-report/v0` preserving authoritative vs experimental areas
- scorecard with explicit watch/wait and split-lane outcomes

**Primary consumers**
- advanced analysis tools
- deeper IDE tooling
- MIR / compiler-aware ecosystem tools

## Graduation criteria
A semantic-context pilot should graduate only when it has:
1. an explicit pilot brief;
2. a lane profile that keeps authoritative and fallback inputs distinct;
3. a bounded query budget with named out-of-scope questions;
4. a real consumer-handoff artifact;
5. at least one real downstream consumer;
6. a scorecard showing the pilot stayed reviewable and did not collapse into a hidden index or “AI context” blob.

## Anti-goals
- one giant Rust knowledge graph with unclear freshness;
- collapsing local builds, docs.rs caches, and compiler-backed exports into one undifferentiated lane;
- treating assistant/editor payloads as canonical semantic artifacts;
- widening the query catalog faster than subject/provenance discipline can support;
- pretending every semantic question is equally ready today.

## Why this is an ecosystem contribution
Rust now has the raw ingredients for better tool-facing semantic context, but they are arriving through multiple channels at once: Cargo plumbing, docs.rs rustdoc JSON, semver work, compiler-backed analysis lanes, and editor/assistant demand.

A good Semantic-Context Pilot Program would make those channels compose **honestly**.
It would help Rust serve both human and machine consumers without letting either drift away from canonical truth.
