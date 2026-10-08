# Design: Canonical Learning lane map

## Goal
Sharpen the archive’s existing **Canonical Learning Stack** so future revisions stop flattening learning into one vague “docs quality” or “smart docs” verdict.

The core move is simple:
- keep **maintainer-authored reference docs** separate from **long-form guides and curricula**;
- keep **positive executable examples** separate from **negative compile-guidance teaching**;
- keep **docs-host/build assumptions** separate from both authored surfaces;
- keep **structured machine-import lanes** separate from rendered or summarized views; and
- keep **consumer overlays** thinner than the canonical learning artifacts they import.

Read this with:
- [`design/canonical-learning-stack.md`](./canonical-learning-stack.md)
- [`design/canonical-learning-pilot-program.md`](./canonical-learning-pilot-program.md)
- [`design/canonical-learning-consumer-pilot-program.md`](./canonical-learning-consumer-pilot-program.md)
- [`design/docproof-kit.md`](./docproof-kit.md)
- [`design/compile-guidance-kit.md`](./compile-guidance-kit.md)
- [`proposals/epic-canonical-learning-stack.md`](../proposals/epic-canonical-learning-stack.md)

## Why this needs an explicit lane map now
Rust’s current signals are no longer saying only “docs matter”.
They are saying canonical learning now spans **distinct authoring, validation, host, machine-import, and consumer lanes**:
- the 2025 State of Rust survey says online docs remain the preferred canonical reference while some learning traffic is shifting toward LLM/editor workflows;
- the same survey says many users still find compiler error-code explanations useful, which is a strong sign that compile-time teaching belongs in the canonical-learning conversation rather than sitting outside it;
- Rust’s 2025 vision work explicitly recommends extending crates toward **better diagnostics and guidance from crates**;
- docs.rs already documents docs-host-specific build metadata, cfg/env behavior, and CI-facing checks, which means hosted-doc posture is not reducible to authored prose;
- docs.rs now hosts rustdoc JSON, which makes structured machine import a first-class lane rather than a scraping afterthought;
- rustdoc documentation tests plus `#[cfg(doctest)]` make executable example lanes more explicit;
- mdBook keeps book-shaped example validation explicit; and
- `trybuild`, structured rustc JSON diagnostics, diagnostic attributes, and `cargo fix` show that negative-teaching, machine-readable diagnostics, and suggestion consumers are all real present-tense lanes.

References:
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
- https://docs.rs/about/rustdoc-json
- https://doc.rust-lang.org/rustdoc/documentation-tests.html
- https://doc.rust-lang.org/beta/releases.html
- https://rust-lang.github.io/mdBook/cli/test.html
- https://docs.rs/trybuild
- https://doc.rust-lang.org/reference/attributes/diagnostics.html
- https://doc.rust-lang.org/beta/rustc/json.html
- https://doc.rust-lang.org/cargo/commands/cargo-build.html
- https://doc.rust-lang.org/cargo/commands/cargo-fix.html

## The lane map

### 1) API-doc / reference lane
This lane is primarily owned by **DocProof Kit**.
It answers:
- what rustdoc-facing reference surfaces exist;
- what API items, examples, and support markers are maintainer-authored;
- which docs targets / features the maintainer intends as reference surfaces.

Examples:
- `doc-pack/v0`
- `guide-profile/v0` sections marked `api-docs`
- rustdoc item / example catalogs imported as canonical source pointers

Design rule: **reference docs are not the same thing as guides, transcripts, or editor summaries.**

### 2) Guide / tutorial / curriculum lane
This lane is also primarily owned by **DocProof Kit**.
It answers:
- which long-form books, tutorials, walkthroughs, recipes, or transcripts are canonical;
- what chapter structure and ordering matter;
- which parts are explanatory versus normative.

Examples:
- `guide-profile/v0`
- `example-catalog/v0` sections marked `guide-book` or `tutorial`
- `doc-pack/v0` sections for chapters, walkthroughs, and transcripts

Design rule: **guide structure must stay separate from API-reference structure.**

### 3) Executable-example / positive-proof lane
This lane records which examples were actually run successfully.
It answers:
- which rustdoc examples were tested;
- which mdBook examples were tested;
- what target/feature/toolchain/docs-host scope the run covered;
- which omissions remain.

Examples:
- rustdoc doctest outputs imported into `doc-check-report/v0`
- mdBook `test` outputs imported into `doc-check-report/v0`
- `canonical-learning-check-report/v0` sections for positive example evidence

Design rule: **“example exists” is not the same thing as “example was executed under this slice.”**

### 4) Compile-guidance / negative-teaching lane
This lane is primarily owned by **Compile Guidance Kit**.
It answers:
- what compile-time diagnostics, lint messages, `must_use` guidance, and compile-fail teaching surfaces are intentionally authored;
- which examples are expected to fail;
- which error shapes or stable ids downstream consumers may rely on.

Examples:
- `guidance-pack/v0`
- `diagnostic-catalog/v0`
- `lint-catalog/v0`
- compile-fail doctest and `trybuild` evidence imported into `guidance-check-report/v0`

Design rule: **negative-teaching lanes must not be collapsed into positive example proof or generic docs prose.**

### 5) Docs-host / build-environment lane
This lane captures hosted-doc assumptions and compatibility.
It answers:
- which docs.rs metadata or docs-host-specific cfg/env behavior mattered;
- which targets or features shaped the host build;
- what was checked locally or in CI to approximate hosted behavior.

Examples:
- docs.rs metadata imports inside `canonical-learning-sources/v0`
- docs-host posture blocks in `canonical-learning-brief/v0`
- docs-host result sections inside `canonical-learning-check-report/v0`

Design rule: **host/build posture must stay separate from canonical learning text.**

### 6) Structured machine-import lane
This lane captures structured artifacts meant for tools.
It answers:
- which rustdoc JSON or structured diagnostics were published;
- which schema/version/freshness assumptions matter;
- which parts are canonical machine imports versus derived indexes.

Examples:
- rustdoc JSON pointers in `canonical-learning-sources/v0`
- structured rustc diagnostic imports in `guidance-pack/v0` or consumer import reports
- `learning-lane-catalog/v0`

Design rule: **machine-readable source material is not the same thing as rendered UX or assistant summaries.**

### 7) Consumer-overlay lane
This lane is owned by the **canonical-learning consumer pilot**.
It answers:
- what docs hosts, CI, editors, assistants, atlas views, or release/support tools imported;
- what they rendered, grouped, filtered, summarized, or suggested;
- what remained derived instead of canonical.

Examples:
- `learning-consumer-profile/v0`
- `learning-import-report/v0`
- `learning-overlay-report/v0`
- `learning-authority-boundary/v0`

Design rule: **consumers may render or summarize canonical learning truth, but they must not silently replace it.**

### 8) Review / handoff lane
This lane is where canonical learning becomes strategically reusable.
It answers:
- what release-review, support-review, atlas, policy, or assistant contexts are allowed to conclude from learning artifacts;
- which omissions or caveats must travel with the handoff;
- which downstream conclusions require more evidence from other stacks.

Examples:
- `canonical-learning-consumer-handoff/v0`
- bounded learning sections inside atlas/support/release review packs
- `canonical-learning-pack/v0`

Design rule: **learning evidence can inform support/release/adoption work, but it must not become a hidden support or policy verdict.**

## False equivalences this lane map is meant to stop
1. **API docs ↔ guides**
   - reference coverage is not the same thing as teaching flow.
2. **positive examples ↔ negative-teaching diagnostics**
   - successful snippets and expected-failure cases are different kinds of evidence.
3. **authored canon ↔ docs-host behavior**
   - docs.rs metadata/build posture is not the same thing as the prose itself.
4. **structured imports ↔ derived overlays**
   - rustdoc JSON or structured diagnostics are not identical to search indexes, editor caches, or assistant slices.
5. **render/summarize authority ↔ mutate/gate authority**
   - an editor or assistant that imports learning truth is not automatically allowed to rewrite code, rewrite docs, or infer support policy.
6. **learning evidence ↔ release/support verdict**
   - checked docs and guidance still do not prove compatibility, support, or maintenance posture by themselves.

## What should change elsewhere in the archive
- **Canonical Learning Stack** should cite this lane map as the rule for what must stay separate.
- **DocProof Kit** should remain the owner of API-doc, guide, transcript, and positive-example validation truth.
- **Compile Guidance Kit** should remain the owner of diagnostic/lint/compile-fail teaching truth.
- **Canonical-learning consumer pilot** should remain the owner of derived overlay, import, and authority-boundary truth.
- **Semantic Context**, **Edit Workflow**, **Atlas**, **Support Envelope**, and **release-review consumers** should import bounded learning views rather than each carrying a hidden model of what “canonical learning” means.

## Worthy contribution, sharpened
The worthy contribution here is **not** another docs portal, assistant-memory blob, universal docs schema, or one-number documentation score.
It is a thin `cargo learncanon` / `canonical-learning-pack/v0` layer whose lane catalog, canonical source index, check reports, import reports, authority boundaries, and bounded consumer handoffs let Rust teams compare learning claims honestly across API docs, guides, runnable examples, compile guidance, docs-host posture, structured machine imports, and derived consumer overlays without semantic collapse.
