# Design: Semantic Context execution blueprint (2026 Q1)

## Goal
Turn the archive's most important **hidden multiplier** into a sharper **buildable program**.

The missing contribution is not a universal Rust knowledge graph, not another docs scraper, not an assistant-only context blob, and not a semver verdict engine hiding behind the word “platform”.
It is a disciplined companion layer that lets Rust tools share **portable semantic context truth** across semver, docs, fix/lint, CI, IDE, and assistant consumers without pretending those consumers all need the same power.

Read this note when the question is narrower than the broad ladder:

> if a serious Rust team decides to build the archive's key hidden multiplier, what should **Semantic Context** actually ship in theory and practice?

Read with:
- `design/semantic-context-contract-2026Q1.md`
- `design/semantic-context-pilot-program.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/strategic-territory-map-2026Q1.md`
- `proposals/epic-semantic-context-kit.md`

## Why this note is needed now
The archive already knew that **Semantic Context Contract** was strategically important.
What it still lacked was a crisper answer to **what that contribution should actually look like**.

Fresh primary signals sharpen that answer:
- Rust's March 2026 challenges writeup says ecosystem navigation still suffers from **choice paralysis** and **tacit knowledge**, which makes reusable, bounded semantic evidence more valuable rather than less.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says online docs remain the preferred canonical reference even as editor/LLM-mediated learning rises, which means machine consumers need a stronger attachment to canonical sources instead of a weaker one.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo's plumbing goal says `cargo metadata` can include dependency resolution but **excludes feature resolution**, and it decomposes Cargo builds into stages including **resolve features**, **plan a build**, and **stage final artifacts**.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- docs.rs now hosts rustdoc JSON, says it is meant for programmatic inspection of docs and types, warns consumers to check `format_version`, and says coverage only starts from 2025-05-23 with rebuilds still relevant for older releases.
  https://docs.rs/about/rustdoc-json
- The 2025H2 `cargo-semver-checks` goal says accurate integration into `cargo publish` still depends on checking **cross-crate items** and **type information**, and says rustdoc JSON alone is not precise enough for some semver-sensitive facts.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- StableMIR publication work exists specifically to let tools analyze compiled crates and dependencies without direct compiler-internal coupling, and the 2025 GSoC results say `rustc_public` now has independent publication/versioning infrastructure for the tooling ecosystem.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo's 1.93 development-cycle update says schema unification is being considered partly to improve Cargo's JSON output and unblock a faster, more flexible `cargo fix` architecture.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/

Taken together, those signals say the archive should stop describing Semantic Context only as a good substrate idea.
It should describe a real contribution shape.

## Headline answer
If one serious team wants to build the archive's strongest hidden multiplier, the answer should now be:

> Build a **Semantic Context reference layer** that captures exact build subjects, imports ranked semantic lanes honestly, preserves completeness and query budgets explicitly, and emits reusable packs and handoffs for semver, docs, fix/lint, CI, IDE, and assistant consumers.

That answer is deliberately narrower than “build Rust semantic infrastructure”.
It is also deliberately stronger than “cache rustdoc JSON somewhere”.

## What this contribution should be in theory

### Core thesis
A semantic-context system becomes ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what exact subject was captured** — workspace, package set, target/profile/features/cfg/toolchain, local build or release subject;
2. **what resolution/build context bounded that subject** — lockfile posture, feature selection, relevant Cargo/plumbing facts, docs.rs release posture, or compiler-backed augmentation;
3. **which semantic input lanes were used** — local rustdoc JSON, docs.rs rustdoc JSON, Cargo/plumbing outputs, `rmeta`, `rustc_public`, StableMIR, or fallbacks;
4. **how complete and authoritative the merge was** — exact, mixed, partial, stale, fallback-only, or experimental;
5. **which named query families were allowed** — semver/public API, doc lookup, fix/lint, migration, review/CI, assistant/export;
6. **what each downstream consumer is allowed to claim** from the resulting pack.

If a project cannot answer those questions without custom lore, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable semantic context and handoff**.

It should include:
- subject and resolution identity;
- ranked input-lane provenance;
- merge/completeness truth;
- bounded query execution and explanation;
- consumer-specific export and handoff.

It should not become:
- the new global Rust index;
- a replacement for Cargo, rustdoc, docs.rs, StableMIR, or `rustc_public`;
- a semver verdict engine that smuggles its context assumptions out of view;
- or an assistant platform that quietly becomes the source of truth.

### Separation rule
The contribution must preserve at least six distinct truth classes:
- **subject truth** — what code/release/build subject is being discussed;
- **resolution/build-context truth** — how that subject was selected and bounded;
- **input-lane truth** — what evidence lanes were imported;
- **merge/completeness truth** — what unified cleanly, what stayed partial, and what stayed experimental;
- **query truth** — which named question was asked and what reason-coded answer came back;
- **consumer-handoff truth** — what a specific semver/docs/fix/CI/IDE/assistant consumer may import.

This is the biggest theory/practice guardrail in the whole design.
Without it, every consumer turns into a hidden fork of semantic authority.

### Lane hierarchy rule
A worthy v0 should prefer semantic lanes in this order:
1. **local authoritative capture**;
2. **public docs.rs release cache**;
3. **semver/public-API consumer handoff**;
4. **fix/lint/migration consumer handoff**;
5. **compiler-backed augmentation**;
6. **editor / assistant derived slices**.

That order is strategic, not just technical.
It keeps the strongest correctness and review pressure ahead of the most temptation to over-promise.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo semctx capture`
- `cargo semctx explain`
- `cargo semctx query`
- `cargo semctx diff`
- `cargo semctx export --consumer <semver|docs|fix|ci|ide|assistant>`
- `cargo semctx doctor`
- `cargo semctx verify-pack`

The tool should **import** first-party surfaces when available rather than replacing them.

### Public artifact spine
Keep the current family, but make the public review shape more explicit:
- `semctx-subject/v0`
- `resolution-context/v0`
- `semantic-input-catalog/v0`
- `semantic-merge-report/v0`
- `semantic-query-budget/v0`
- `semantic-query-report/v0`
- `semctx-consumer-handoff/v0`
- `semctx-diff-report/v0`
- `semctx-pack/v0`

### Minimum schema disciplines
Every public artifact should keep these fields first-class:
- **subject identity** — workspace/package set/target/profile/features/toolchain or release identity;
- **authority posture** — local authoritative, public cached, compiler-backed, fallback-only, or derived;
- **coverage / completeness** — exact, partial, stale, mixed, unsupported, experimental;
- **version anchors** — rustdoc `format_version`, toolchain version, schema version, compared pack IDs;
- **query budget** — named questions that this pack is allowed to answer;
- **consumer limits** — what the next consumer may and may not claim;
- **raw attachments** — URLs or digests for rustdoc JSON, Cargo outputs, compiler-backed exports, or logs when present;
- **reason-coded ambiguity** — explicit why for every partial or unsupported answer.

### Commands and what they should emit

#### `cargo semctx capture`
Purpose:
- gather one semantic subject;
- import local Cargo/plumbing + rustdoc JSON evidence when available;
- record release-cache posture when using docs.rs;
- emit `semctx-pack/v0`.

Important rule:
- if only a weaker lane is available, emit a **weaker pack** instead of pretending equivalence.

#### `cargo semctx explain`
Purpose:
- tell a human why a semantic answer is authoritative, mixed, stale, partial, or blocked;
- render the same pack at different depths without inventing new facts.

#### `cargo semctx query`
Purpose:
- run only **named query families** that the pack declared;
- emit `semantic-query-report/v0` with reason-coded uncertainty;
- refuse silent widening into arbitrary “ask anything about this crate” behavior.

#### `cargo semctx diff`
Purpose:
- compare two packs while preserving the distinction between:
  - changed subject,
  - changed resolution/build context,
  - changed lane provenance,
  - changed completeness,
  - and changed query answers.

#### `cargo semctx export`
Purpose:
- emit smaller consumer handoffs for semver review, docs lookup, lint/fix, CI review, IDE panes, or assistants without making those slices canonical by themselves.

#### `cargo semctx doctor`
Purpose:
- detect stale docs.rs cache use, missing feature-resolution truth, mismatched rustdoc formats, mixed local-vs-release assumptions, unsupported cross-crate merges, or assistant/export misuse.
- the tool should never hide the fact basis behind prose.

#### `cargo semctx verify-pack`
Purpose:
- validate digests, schema versions, redaction markers, lane declarations, and attachment integrity.

## Ranked feature set

### P0 — required for a worthy v0
- exact subject identity with resolution/build context;
- local authoritative capture lane;
- docs.rs cache import lane with `format_version` and freshness posture;
- explicit merge/completeness report;
- bounded query budgets for **semver/public API** and **docs lookup** first;
- one portable pack plus one portable human-readable brief;
- consumer handoffs that keep semver/docs consumers stronger than IDE/assistant consumers;
- honest `partial`, `stale`, `fallback-only`, and `unsupported` states.

### P1 — strong near-term extensions
- fix/lint/migration consumer handoff;
- richer local-vs-release diffs;
- CI/review export;
- compiler-backed augmentation lanes using `rmeta`, `rustc_public`, or StableMIR where justified;
- pack verification and redaction guidance for private/internal environments.

### P2 — do later or fold elsewhere
- universal search/index products;
- hosted semantic dashboards;
- assistant-optimized omniscient context windows;
- one-shot “answer any Rust code question” APIs;
- trying to settle every compiler-facing analysis substrate question in the same project.

## Pilot lanes that best prove the idea

### 1) Local authoritative semver / public-API lane
Prove:
- exact subject capture;
- exact or bounded feature-resolution posture;
- cross-crate semantic imports with explicit incompleteness;
- reusable handoff into semver/public-API consumers.

This lane matters because the official semver integration work still hits precision and cross-crate blockers.

### 2) docs.rs canonical lookup lane
Prove:
- release-facing semantic lookup with visible cache/freshness posture;
- local-vs-release comparability instead of silent substitution;
- correct `format_version` and rebuild handling.

This lane matters because docs remain canonical and docs.rs is now machine-usable substrate.

### 3) Fix / lint / migration handoff lane
Prove:
- edit-facing tools can import bounded semantic context rather than rebuilding private indexes;
- Cargo-facing structured outputs and future fix architecture can attach to explicit semantic packs;
- migration and review tools stay downstream consumers rather than becoming the context owner.

### 4) Compiler-backed augmentation lane
Prove:
- deeper lanes can coexist with local/docs.rs lanes without flattening authority;
- `rustc_public` / StableMIR style inputs remain explicit imports, not silent upgrades of every answer;
- experimental and authoritative areas can live in the same pack honestly.

### 5) IDE / assistant derived-slice lane
Prove:
- bounded rendered slices can serve fast human workflows;
- provenance, freshness, and unsupported areas survive export;
- the most tempting consumer still stays downstream from canonical evidence.

This lane should come last, not first.
That is the whole point.

## Failure modes to avoid

### 1) The universal-index trap
If the tool starts promising one giant always-current Rust index, it will either lie about freshness or become an empire.

### 2) The verdict-engine trap
If context packs silently become semver verdicts, migration verdicts, or docs recommendations, adjacent seams disappear and users lose reviewability.

### 3) The cache-equals-authority trap
A docs.rs cache is valuable. It is not the same thing as an exact local authoritative capture.

### 4) The compiler-only trap
Compiler-backed lanes are powerful, but leading with them risks a tool that is too hard to adopt and too eager to over-claim.

### 5) The assistant-blob trap
If the public story becomes “feed this giant semantic blob to your agent”, the project stops being Rust infrastructure and becomes a fashionable wrapper.

## Why this is strategically worthy
This blueprint matters because it turns a fuzzy enabling idea into a specific program that can serve many high-pressure consumers without flattening them.

A good Semantic Context project would help Rust in three directions at once:
- **correctness-sensitive consumers** like semver/public API tools get stronger context with explicit partiality;
- **canonical-human-consumer layers** like docs/search/navigation get machine-usable support without surrendering canon;
- **machine-mediated consumers** like fix/lint/CI/IDE/assistant tools get a weaker but reusable import layer instead of each inventing their own shadow workspace model.

That is why the archive should treat Semantic Context as a hidden multiplier and now also as a buildable program.

## Ranking and repo consequence
This note does **not** rewrite the archive's broad ladder.
It does **not** displace **Build-State Evidence** as the strongest one-project answer.
It does **not** displace **Native Edge Contract** as the active specialist frontier.
It does **not** collapse **Public API**, **Migration Truth**, **Canonical Learning**, or **Adoption Navigation** into one substrate story.

What it does do is make one missing execution answer explicit:

**if the archive's hidden multiplier deserves serious implementation work, the right shape is now a thin semantic-context reference layer with exact subject capture, ranked lane imports, bounded query budgets, and explicit consumer handoffs.**
