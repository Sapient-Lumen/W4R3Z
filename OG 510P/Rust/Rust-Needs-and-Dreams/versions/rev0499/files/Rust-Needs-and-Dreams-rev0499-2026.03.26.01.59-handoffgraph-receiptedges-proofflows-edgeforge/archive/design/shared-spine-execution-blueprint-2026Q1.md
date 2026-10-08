# Design: Shared spine execution blueprint (2026Q1)

## Goal
The archive already has:
- ranking and comparative scorecards for the strongest worthy Rust ecosystem contributions;
- a delivery matrix, incubation map, proof-burden map, bet-sizing map, and compounding map;
- a sequencing note that says **shared spine first**;
- and a portfolio-artifact conventions note that explains the thin common grammar in principle.

What it still lacked was the next practical answer:

> if the **shared spine** is real enough to come before the archive's strongest evidence, bridge, and widener layers, then **what should that contribution actually be** in theory and practice before it collapses into one vague style guide, one mega-schema dream, or one assistant-memory blob?

This note is the archive's answer to that question.
It does **not** rerank the broad ladder.
It does **not** promote a new frontier.
It turns Stage 0 from “good portfolio hygiene” into a concrete worthy contribution shape.

Read with:
- `design/portfolio-artifact-conventions-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/epic-contribution-compounding-map-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/semantic-context-execution-blueprint-2026Q1.md`
- `design/tooling-contract-execution-blueprint-2026Q1.md`
- `design/compatibility-claims-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `meta/REVISION_OPERATING_PROTOCOL.md`
- `meta/AMNESIA_RESISTORS.md`

## Why this note is needed now
The official Rust picture is no longer just saying “these things hurt.”
It is also saying that several of the archive's strongest bets now have enough machine-usable motion that **shared lineage and compatibility discipline** can be built as a real layer instead of remaining a repo slogan.

The March 2026 challenges writeup still clusters pain around recurring practical taxes, not only language novelty. That favors a stage-0 contribution that reduces tacit knowledge and silent tool mismatch across later layers. The same post now also matters for a second reason: its author's note says the original version was retracted after readers felt the LLM voice bled through. Even though the team stood by the content, that is unusually direct project-level evidence that generated summaries should not silently become canonical truth. A shared spine should therefore make assistant slices weaker than canonical packs by design.
https://blog.rust-lang.org/2026/03/20/rust-challenges/

The 2025 State of Rust survey says resource usage remains a major problem while docs remain canonical and editor/LLM mediation continues to rise. That means future Rust guidance will increasingly be consumed through machine-mediated surfaces, which raises the value of canonical packs, bounded briefs, and explicit lossiness instead of summary-first folklore.
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

The Cargo plumbing goal says Cargo's existing machine-facing commands are still too porcelain-oriented, that `cargo metadata` can include dependency resolution but excludes feature resolution, and that Cargo's work naturally decomposes into locate/read/resolve/plan/execute/stage phases. That is strong evidence that later ecosystem layers need a common outer contract for subject, scope, imports, and handoff, because there is no single upstream “everything pack” they can just reuse yet.
https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html

Cargo build-analysis is explicitly prototyping recorded build metadata across invocations, `cargo report` subcommands for rebuild reasons and timing data, local-only storage, and schema evolution without a stable commitment yet. That is almost a model case for why the archive needs a shared stage-0 kit: important inputs are becoming machine-usable, but they are still versioned, partial, and moving.
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html

The Cargo 1.94 and 1.93 development-cycle notes reinforce the same point from two angles. 1.94 says Cargo cannot be everything to everyone because of the compatibility guarantees it must uphold and highlights plugin value, while also pushing structured logging and `cargo report rebuild` / `cargo report sessions`. 1.93 shows Cargo continuing to treat build-dir layout, custom artifacts, and JSON/schema questions as active implementation terrain. A stage-0 shared spine should therefore be a **companion protocol + validator + fixture kit**, not another “Cargo replacement”.
https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/

The March 2026 build-dir-layout testing call says the layout is internal-only but many projects rely on unspecified details because Cargo lacks missing features. That is exactly the situation where a thin outer review contract helps: later tools should record which internal assumptions or polyfills they depended on instead of laundering them into timeless facts.
https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/

The docs.rs rustdoc JSON page, the libtest JSON goal, and StableMIR / `rustc_public` progress all say more Rust substrate is becoming available in machine-usable form, but with format-version, availability, and maturity caveats that need to travel with the data. That is an argument for shared compatibility gates and lineage receipts, not for flattening everything into one opaque cached blob.
https://docs.rs/about/rustdoc-json
https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
https://blog.rust-lang.org/2025/08/05/july-project-goals-update/

The March 2026 Cargo security advisory and the updated malicious-crate notification policy reinforce a similar lesson on the operational side: package ingress, extraction, and notification posture need explicit route and evidence boundaries. A shared spine is what lets package-intake work stay connected to broader evidence and compatibility layers without becoming another isolated security portal.
https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/

The Foundation's 2026–2028 strategy and the Innovation Lab together matter for owner shape: neutral institutional support is now real for important infrastructure, but it is still selective and should not be the default answer. The shared spine should begin as a small companion protocol and fixture project with upstream liaisons; it only graduates into keystone institutional support if multiple later layers truly depend on it.
https://rustfoundation.org/strategic-plan/
https://rustfoundation.org/rust-innovation-lab/

Taken together, those signals say the archive should stop treating **shared spine** as mere advice and start treating it as a concrete stage-0 contribution.

## Headline answer
If one serious team wants to build the archive's most useful stage-0 layer, the answer should now be:

> Build a **Shared Spine Contract Kit**: a thin common envelope, lineage-receipt protocol, compatibility-gate format, validator/linter, fixture corpus, and bounded brief/assistant handoff rules that multiple stronger Rust ecosystem contributions can reuse without collapsing into one product or one canonical mega-schema.

This is deliberately narrower than “build the Rust ecosystem control plane”.
It is also deliberately stronger than “write down some conventions in a markdown file”.

## What this contribution should be in theory

### Core thesis
A shared spine becomes a worthy ecosystem contribution when it can answer all of these questions for **multiple later seams** without becoming their payload owner:
1. **what exact subject is under review**;
2. **what scope and capture context bounded that subject**;
3. **what imports were consumed and under what authority/freshness posture**;
4. **what derived claims were added and how strong they are**;
5. **what partial, stale, unsupported, or lossy states remain**;
6. **what downstream consumer may import or summarize the result**.

If a later tool cannot answer those questions without repo lore, terminal archaeology, or assistant memory, then the stage-0 layer is not real yet.

### Boundary rule
The contribution should stop at **shared outer contract and lineage**, not own every seam's inner semantics.

It should include:
- a common envelope and truth-class vocabulary;
- named artifact roles such as canonical pack, brief, diff, verify receipt, lineage receipt, and assistant slice;
- compatibility and schema/toolchain gating;
- fixture and adapter validation;
- and explicit consumer-lossiness rules.

It should not become:
- a global Rust package index;
- a new hosted evidence registry;
- a universal build database;
- a recommendation site;
- a replacement for Cargo, docs.rs, rustdoc, StableMIR, or RustSec;
- or an LLM memory system that silently rewrites canon.

### The six truth classes this layer must preserve
A worthy v0 must keep these distinct across every seam that adopts it:
- **subject truth** — the exact workspace, package, release, route, run, or tuple under review;
- **capture truth** — the time, toolchain, feature set, platform, or route context that bounded the capture;
- **import truth** — first-party or raw evidence lanes and their version/freshness posture;
- **derived truth** — diagnosis, interpretation, or normalization built on those imports;
- **partiality truth** — what stayed stale, fallback-only, unsupported, mixed, or inconclusive;
- **handoff truth** — what the next CI/doc/review/assistant consumer is allowed to claim.

This is the main anti-folklore rule for both tools and the archive itself.

### Canon rule
The shared spine should formalize a family order, not just a file format:
1. **canonical pack** — strongest reviewable artifact;
2. **brief / handoff** — weaker consumer slice that points back to the pack;
3. **diff artifact** — comparison artifact that records changed authority and changed subject separately;
4. **verify receipt** — bounded stronger check tied to a specific proof lane;
5. **lineage receipt** — execution/import trail for how the above were produced;
6. **assistant slice** — explicitly derived, non-canonical summary object that may be rendered for LLMs or editors but may not overwrite the pack.

The theory consequence is simple:
no summary, dashboard, or assistant rendering should ever be stronger than the canonical pack it came from.

### Compatibility rule
The shared spine should make compatibility problems first-class.
Every artifact in the family should record:
- schema family + schema version;
- producing tool + version;
- imported source versions or format anchors when available;
- declared consumer budget;
- and whether parsing/compatibility succeeded exactly, partially, via fallback, or not at all.

That rule is merited now because Cargo report surfaces, rustdoc JSON, and compiler-facing public APIs are all active but still evolving.

### Refusal rule
A serious stage-0 layer must prefer explicit weaker states over silent success.
It must be able to say:
- unsupported;
- stale;
- fallback-only;
- mixed-authority;
- inconclusive;
- manual-review-required.

The archive should now treat those as strengths, not UX failures.

## What this contribution should be in practice

### Reference tool shape
A worthy v0 should probably look like a small companion toolkit rather than a hosted service:
- `spine lint-pack`
- `spine explain-pack`
- `spine diff-packs`
- `spine verify-compat`
- `spine emit-brief`
- `spine trace-lineage`
- `spine fixture-check`
- `spine adapter-audit`

This tool should not own the domain payload generation itself.
It should validate and normalize the **shared outer contract** around packs produced by build-state, semantic-context, package-intake, compatibility, and acceptance/debugging layers.

### Public artifact family
Keep seam payloads separate, but make the outer family explicit:
- `shared-envelope/v0`
- `lineage-receipt/v0`
- `consumer-brief/v0`
- `comparison-brief/v0`
- `compatibility-gate/v0`
- `assistant-slice/v0`
- `fixture-pack/v0`
- `adapter-report/v0`

A build-state pack or semctx pack may embed `shared-envelope/v0` and then carry its own inner payload.
The shared spine should standardize the envelope, lineage, lossiness, and gating parts.

### Minimum required envelope fields
Every participating canonical pack should expose at least:
- `schema_family`
- `schema_version`
- `pack_kind`
- `subject`
- `scope`
- `capture_epoch`
- `producer`
- `authority`
- `freshness`
- `partiality`
- `imports`
- `attachments`
- `lineage`
- `handoff_budget`
- `consumer_limits`

The point is not these exact names.
The point is that every participating seam should have obvious places for the same honesty questions.

### Adapter lanes the v0 should support first
Do **not** try to wire up every archive seam at once.
The worthy v0 should support four adapters first:

#### 1) Build-State adapter
Inputs:
- Cargo build-analysis / `cargo report` outputs where available;
- build-dir or timing attachments;
- explicit local build subject.

Why first:
- broadest pain;
- clearest first unlock;
- easiest proving ground for canonical pack vs brief vs lineage separation.

#### 2) Semantic Context adapter
Inputs:
- local rustdoc JSON;
- docs.rs rustdoc JSON;
- compiler-backed augmentation when available.

Why second:
- strongest hidden multiplier;
- best proving ground for compatibility-gate and mixed-authority states.

#### 3) Package Intake adapter
Inputs:
- registry/route data;
- extraction or policy receipts;
- advisory or notification posture;
- alternate-registry / mirror context where available.

Why third:
- strong operational bridge;
- best proving ground for fail-closed and manual-review-required states.

#### 4) Acceptance / Feedback adapter
Inputs:
- debugger tuple or test/acceptance tuple receipts;
- libtest JSON or related machine-readable outputs when relevant.

Why fourth:
- keeps the shared spine from becoming only build/package infrastructure;
- proves the family can carry acceptance-corpus work too.

### Ranked feature set

#### P0 — required for a worthy v0
- common envelope for canonical packs;
- lineage receipt that keeps imports and derivations separate;
- bounded brief format with explicit lossiness;
- assistant-slice format that is always non-canonical;
- compatibility gate for schema/toolchain/format mismatches;
- fixture corpus spanning at least build-state, semantic-context, and package-intake;
- validator/linter that rejects missing honesty fields;
- explicit `partial`, `stale`, `fallback-only`, `mixed-authority`, and `manual-review-required` outcomes.

#### P1 — strong near-term extensions
- diff artifacts shared across at least three seams;
- adapter audit reports for common failure patterns;
- redaction guidance for private/internal packs;
- review-pane rendering helpers for PRs and CI;
- provenance digests or attachment checks;
- stronger policy around brief freshness and renewal windows.

#### P2 — do later or refuse
- central hosted registry;
- giant unified inner-payload schema;
- assistant-native “omniscient context” APIs;
- universal package scoring;
- replacing seam-specific tools with the spine itself.

## Proving grounds
A worthy shared-spine build should not graduate on elegance alone.
It should survive at least these proving grounds:

### 1) Cross-seam fixture proof
Demonstrate one shared-envelope family across:
- one build-state pack,
- one semantic-context pack,
- one package-intake pack,
- and one acceptance/debugging or test-result pack.

### 2) Mixed-authority proof
Show a semantic-context case where local capture, docs.rs cache, and version mismatch produce explicit mixed or partial states rather than false certainty.

### 3) Fail-closed proof
Show a package-intake or extraction scenario where missing route or compatibility evidence produces `manual-review-required` or equivalent instead of a “green” brief.

### 4) Assistant-discipline proof
Show one assistant slice derived from a canonical pack where the slice is visibly weaker, references the parent pack, and is rejected if the lineage pointer is missing.

### 5) Non-human consumer proof
Show at least one CI/review consumer and one non-LLM tool consumer ingesting the same family without reverse-engineering prose.

## Owner and stewardship shape
The archive should now treat this contribution as:
- **first vehicle:** bootstrap companion protocol + validator + fixture repo;
- **staffing shape:** small technical team with strong schema/adapter discipline and named upstream liaisons;
- **upstream relation:** companion-first, importing Cargo/docs.rs/compiler outputs rather than trying to upstream every rule immediately;
- **later vehicle if it matters enough:** neutral commons or institution-backed infrastructure only after multiple high-value seams truly depend on it.

Wrong starting vehicles to refuse:
- big hosted platform;
- “let the LLM remember the repo” meta-layer;
- giant standardization process before there are proving-ground fixtures;
- or a Cargo-upstream land-grab that ignores Cargo's compatibility posture.

The Rust Innovation Lab and Foundation support shapes matter as eventual options, but only after the shared spine proves that it is real infrastructure for multiple later layers.

## What this contribution is *not*
It is **not** the broad first public build.
That still belongs to **Build-State Evidence**.

It is **not** a new top-band ranking answer.

It is **not** a new frontier.

It is the strongest concrete answer to the question:

> if the archive says **shared spine first**, what should that actually become before later bets depend on it?

The answer is:
- thin common envelope,
- lineage receipts,
- compatibility gates,
- briefs and assistant slices that are explicitly weaker than canonical packs,
- and fixture-driven validation across the archive's core contributing seams.

## Repo consequence
Treat this note as **deepening + hygiene**, not promotion.

Future revisions that claim to improve the archive's stage-0 layer should now say explicitly:
- what is shared versus seam-specific;
- which artifact role changed;
- which compatibility or version gate changed;
- whether assistant slices became safer or more dangerous;
- what proving ground now passes that did not pass before;
- and what wrong shape was explicitly refused.

If a future revision cannot answer those questions, it is probably smearing the shared spine back into prose.
