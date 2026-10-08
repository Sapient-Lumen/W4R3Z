# Design: Canonical Learning Consumer Pilot Program (`learning-consumer-pack/v0`)

## Goal
Define the first **shared consumer-execution layer** above the archive’s **Canonical Learning Stack**.

The stack already has two maintainer-authored canonical surfaces:
- [`doc-pack/v0`](./docproof-kit.md) from **DocProof Kit**;
- [`guidance-pack/v0`](./compile-guidance-kit.md) from **Compile Guidance Kit**.

What is still missing is a disciplined way for downstream consumers to import those artifacts without quietly becoming the new source of truth.
This pilot program exists to prove that **CI, docs hosts, editors, assistants, atlas views, and release/support consumers** can all consume canonical learning artifacts while staying visibly derived.

The stack-level execution order now lives in [`design/canonical-learning-pilot-program.md`](./canonical-learning-pilot-program.md): canonical authoring and validation first, bounded consumer imports second. The lane rule itself now lives in [`design/canonical-learning-lane-map.md`](./canonical-learning-lane-map.md): consumers import **specific learning lanes** rather than a fake universal docs blob.

## Why this now matters
Current Rust signals line up unusually well:
- The 2025 State of Rust survey says online docs remain the preferred canonical reference while editor/agentic use is rising.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust’s recent vision work explicitly recommends better diagnostics and guidance from crates plus deeper compilation-workflow extensibility.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- docs.rs already hosts rustdoc JSON, which is an explicit structured docs input for downstream tooling.
  https://docs.rs/about/rustdoc-json
- `rustc` already emits structured JSON diagnostics with spans, child messages, and suggestions, while Cargo can surface JSON diagnostics and `cargo fix` can apply compiler suggestions.
  https://doc.rust-lang.org/beta/rustc/json.html
  https://doc.rust-lang.org/cargo/commands/cargo-build.html
  https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- Stable diagnostic attributes give crate authors more intentional diagnostic surface area to publish.
  https://doc.rust-lang.org/reference/attributes/diagnostics.html

Those pieces mean the ecosystem no longer only lacks raw machine-readable data.
It lacks a **humble import contract** that says what is canonical, what is derived, what can be rendered or suggested, and what must never be silently promoted to canon.

## Why this needs its own design layer
Without a consumer layer, the archive’s current canonical-learning story still has a hidden gap:
1. maintainers can publish good docs and compile guidance;
2. downstream tools can scrape or import them;
3. but there is no shared rule for how a consumer should declare derivation, freshness, edits, omissions, or uncertainty.

That gap is exactly where ecosystems drift into:
- assistant-shaped pseudo-canon,
- editor-only hidden guidance state,
- CI gates that overclaim support from partial evidence,
- or docs overlays that silently normalize away maintainer intent.

The right next move is **not** a universal docs portal or one giant “AI context” blob.
It is a ranked consumer pilot that proves import discipline.

## Design principles

### Import rule by lane
Consumers should say which lanes they imported directly: API-doc/reference, guide/tutorial, executable-example proof, compile-guidance/negative-teaching, docs-host/build posture, or structured machine-import lanes. They should then publish derived overlays and authority boundaries separately.

1. **Canonical first.** `doc-pack` and `guidance-pack` remain the maintainer-authored truth.
2. **Consumers must declare derivation.** Rendered overlays, suggestions, summaries, and policy views must be marked derived.
3. **Import profiles beat ambient scraping.** A consumer should publish what it imported, what it ignored, what it normalized, and why.
4. **Mutation authority must stay explicit.** Reading canonical learning artifacts is not the same as having the right to rewrite code, docs, or policy.
5. **Different consumers need different truths.** CI, docs hosts, editors, assistants, atlas views, and support/release tooling should not be flattened into one generic consumer.
6. **Partial imports are acceptable when declared.** Incomplete support is better than fake completeness.
7. **Success requires a real downstream use.** Exporting more JSON alone does not count.

## Artifact family

### 1) `learning-consumer-profile/v0`
Declares one downstream consumer lane.

Should record:
- consumer id and class (`docs-host`, `ci`, `editor`, `assistant`, `atlas`, `release-review`, `support-review`)
- imported canonical artifacts (`doc-pack`, `guidance-pack`, or both)
- required fields and optional fields
- freshness / cache posture
- whether the consumer is human-facing, tool-facing, or mixed
- whether it can only render, can annotate, can suggest edits, or can gate

### 2) `learning-import-report/v0`
Records what a consumer actually imported.

Should record:
- source artifact identities and versions
- feature/target/toolchain scope when relevant
- omitted sections
- normalization rules used
- parse or compatibility issues
- freshness timestamp / staleness status
- whether the import was full, partial, fallback, or failed

### 3) `learning-overlay-report/v0`
Describes any derived rendering layered above canonical inputs.

Should record:
- overlay id and consumer id
- which canonical artifacts it derives from
- added summaries, grouping, filters, or cross-links
- whether any wording was synthesized
- whether edits/suggestions were proposed
- links back to canonical source items
- explicit “derived, not canonical” marker

### 4) `learning-authority-boundary/v0`
States what the consumer is and is not allowed to treat as authoritative.

Should record:
- canonical fields it may cite directly
- fields it may summarize but not rewrite
- fields it may derive heuristically
- mutation rights (`none`, `propose-only`, `manual-apply-only`, `gated-apply`)
- support/policy/release conclusions it may not infer without additional inputs

Design rule: **do not let importers smuggle policy, support, or code-mutation authority into a learning consumer by accident**.

### 5) `learning-consumer-scorecard/v0`
Grades whether a consumer lane is honest enough to widen.

Should ask:
- did the consumer preserve canonical-vs-derived boundaries?
- did it publish a real import report instead of silently scraping?
- did it remain useful under partial imports?
- did it avoid turning summaries or suggestions into pseudo-canon?
- did it improve a real workflow?
- should the lane graduate, stay experimental, split, or stop?

### 6) `learning-consumer-pack/v0`
Review bundle containing:
- consumer profile
- import report
- overlay report(s)
- authority boundary
- scorecard
- pointers to source `doc-pack` / `guidance-pack`

## Ranked first pilots

### 1) Docs-host / rendered-doc lane
**Why first**
- Docs are still the canonical reference in current Rust survey data.
- docs.rs already hosts structured rustdoc JSON.
- This lane proves that a host can import canonical learning truth while keeping rendered grouping/search/links derived.

**What to prove**
- docs host imports `doc-pack` and optional `guidance-pack` pointers honestly;
- rendered overlays link back to canonical examples and guidance ids;
- host-level annotations never silently replace maintainer-authored support or learning claims.

### 2) CI / release-review lane
**Why second**
- CI is where many teams will first operationalize canonical learning truth.
- It is also where overclaiming is easiest if a partial docs/test/guidance run turns into a fake badge.

**What to prove**
- CI can consume doc/guidance artifacts, run checks, and publish import + scorecard outputs;
- review output remains explicit about what was checked and what was not;
- support/release conclusions remain imported from their own stacks rather than guessed from learning artifacts alone.

### 3) Editor overlay lane
**Why third**
- Editors are an obvious consumer, but they are also where hidden indexes and silent rewrites most easily become pseudo-canon.
- This lane proves overlay discipline before assistant-facing flows widen.

**What to prove**
- editor surfaces can show stable guidance ids, examples, and docs links from canonical sources;
- fixes or quick actions remain suggestions linked to canonical guidance or compiler diagnostics;
- local caches and partial imports are declared, not hidden.

### 4) Assistant slice lane
**Why fourth**
- The survey and current usage patterns make this strategically necessary.
- But it should not be first, because assistants are the highest-pressure place for accidentally replacing canon.

**What to prove**
- an assistant can consume a bounded learning slice with explicit freshness and derivation markers;
- summaries and code suggestions remain linked back to canonical artifacts;
- assistant outputs publish an authority boundary that forbids silently inventing support/policy or mutating without a separate governed lane.

### 5) Atlas / support / release import lane
**Why fifth**
- These are important downstream consumers, but they should widen only after docs-host, CI, editor, and assistant lanes prove the import contract.
- This lane proves the archive’s cross-stack story stays modular.

**What to prove**
- Atlas can use canonical learning inputs for guidance overlays without becoming canon;
- Support Envelope / Release Pipeline consumers can import doc/guidance facts only where their own evidence policies allow;
- derived review views remain explicitly downstream and bounded.

## What should wait
Do **not** start with:
- a universal assistant context format,
- a global docs ranking engine,
- automatic mutation of docs/code from imported learning artifacts,
- or support/policy/release verdicts inferred only from learning packs.

Those are downstream views.
The first job is to prove import discipline and authority boundaries.

## Success bar
A canonical-learning consumer pilot is successful when it can show all of the following:
1. a real maintainer-authored canonical source (`doc-pack`, `guidance-pack`, or both);
2. a declared consumer profile;
3. an import report that makes omissions and freshness visible;
4. an overlay report or rendered output that stays visibly derived;
5. an explicit authority boundary;
6. one real workflow improvement for docs hosting, CI, editing, assistants, atlas, or review;
7. no silent promotion of derived outputs into canonical truth.

## Why this would count as a worthy contribution
Rust is unusually strong at producing structured outputs and unusually weak at preserving **authority boundaries** once those outputs spread through tools.
A good canonical-learning consumer pilot would not just make docs or diagnostics more machine-readable.
It would make them **machine-usable without surrendering canon**.

That is an ecosystem contribution because it improves several high-value lanes at once:
- better docs hosting,
- better CI review,
- safer editor overlays,
- more honest assistant behavior,
- and cleaner imports into atlas, support, and release tooling.

It is also one of the clearest places where “ideal Rust” and “practical Rust” meet: supportive, structured, tool-friendly — but still explicit about who gets to define truth.
