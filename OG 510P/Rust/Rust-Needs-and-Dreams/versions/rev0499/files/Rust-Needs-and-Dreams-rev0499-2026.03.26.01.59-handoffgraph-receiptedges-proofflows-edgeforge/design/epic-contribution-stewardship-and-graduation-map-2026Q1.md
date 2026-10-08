# Design: Epic contribution stewardship and graduation map (2026Q1)

## Goal
The archive already has:
- the broad worthy-contribution ladder;
- current packet posture;
- buildout order;
- decision-rights burden;
- boundary fit;
- incubation vehicles; and
- a shared operating-surface grammar.

What it still lacked was one explicit answer to a different practical question:

> once a worthy Rust contribution has the right seam, the right first vehicle, and the right operator grammar, **where should it live as it matures, what should remain outside core, what should become optional toolchain or service truth, and what should only become real through long-horizon stewardship?**

This note is the archive's answer to that question.
It does **not** rerank the broad ladder.
It does **not** promote a new frontier.
It does **not** replace the incubation map, decision-rights map, or operating-surface note.
It exists so the repo can say something more useful than “start as a companion” and more disciplined than “merge it into Cargo”.

Read with:
- `design/epic-contribution-operating-surface-2026Q1.md`
- `design/epic-contribution-worthy-repo-buildout-2026Q1.md`
- `design/epic-contribution-live-ecosystem-refresh-2026Q1.md`
- `design/epic-contribution-incubation-map-2026Q1.md`
- `design/epic-contribution-boundary-map-2026Q1.md`
- `design/epic-contribution-decision-rights-map-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- `design/compatibility-claims-execution-blueprint-2026Q1.md`
- `design/tooling-contract-execution-blueprint-2026Q1.md`
- `meta/STEWARDSHIP_AND_GRADUATION_PROTOCOL.md`
- `meta/OPERATING_SURFACE_PROTOCOL.md`
- `meta/WORTHY_REPO_BUILDOUT_PROTOCOL.md`
- `meta/LIVE_ECOSYSTEM_REFRESH_PROTOCOL.md`
- `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`
- `meta/AMNESIA_RESISTORS.md`

## Why this layer is merited now
The latest official and primary Rust signals make a pattern harder to ignore:
- Cargo build analysis is being prototyped *inside Cargo* as recorded metadata plus unstable `cargo report` subcommands, which means some raw evidence belongs upstream even when richer review products still belong outside.
- Cargo's external-tools chapter still treats custom subcommands, `cargo metadata`, and structured output as the intended extension path for a large class of ecosystem tooling.
- `cargo clippy` is still the clearest middle shape: an external command distributed with the toolchain as an optional component, not a promise that every useful thing belongs in Cargo core.
- `cargo-semver-checks` is now explicitly working on blockers for merging into Cargo, which is a strong reminder that some companions may earn *partial* or *substantial* upstreaming, but only after paying a heavy proof burden.
- crates.io security and trusted-publishing work keeps getting more concrete, but that truth remains service-side truth, not a complete intake-review product by itself.
- docs.rs rustdoc JSON is service-hosted machine truth whose freshness and format caveats stay attached to the service.
- the FLS/specification work is now a live example of a high-assurance artifact moving from private stewardship into Rust Project stewardship, while remaining a long-horizon maintenance obligation rather than a one-off publish event.
- safety-critical and interop work is increasingly explicit about consortium- and institution-shaped stewardship, not one-crate heroics.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/commands/cargo-clippy.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/inside-rust/2026/03/25/project-director-update/
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2025/03/26/adopting-the-fls/
- https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://rustfoundation.org/strategic-plan/

## Headline answer
The worthy repo should now treat each strong contribution as needing **two explicit residency claims**:
1. **where the first serious product should live**; and
2. **what graduation path should be allowed later without collapsing everything into upstream core**.

The archive should therefore stop asking only “core or external?” and start asking:
- what raw facts or contracts belong upstream;
- what high-level review or diagnosis belongs in a companion layer;
- what truth is inherently service-side;
- what broad-reach tooling deserves optional toolchain distribution;
- what artifacts should remain editorial commons rather than productized commands; and
- what seams are only real as consortium/program stewardship.

## The six residency classes
These classes are ordered from lowest to highest compatibility/stewardship burden.
A worthy contribution may span more than one class, but the split must be explicit.

### 1. Companion-first local product
This is the default for review, diagnosis, export, comparison, and policy overlays.

Use when:
- one team can get immediate value locally or in CI;
- the product imports several upstream/service facts and adds higher-level judgment;
- the product still needs rapid iteration on schema, UX, and refusal posture; or
- route-specific or negative-state truth would be flattened by premature upstreaming.

What belongs here:
- review commands;
- doctor and diff flows;
- attachable export bundles;
- boundary receipts;
- opinionated analysis over upstream facts.

Wrong graduation move:
- merging the whole product into Cargo or rustc because the first prototype is useful.

### 2. Companion with narrow upstream substrate asks
This is the right shape when the product should stay outside core but upstream should expose cleaner raw facts.

Use when:
- the companion is clearly the product surface;
- one or two upstream hooks would remove scraping, fragile inference, or hidden heuristics;
- compatibility burden belongs in a small fact surface, not in the higher-level workflow.

What belongs upstream in this class:
- stable identifiers;
- structured messages;
- machine-readable reports;
- bounded metadata carriage;
- import surfaces that let companions remain honest.

Wrong graduation move:
- treating narrow import hooks as a mandate to upstream the full UX, policy language, or review flow.

### 3. Optional toolchain-distributed component
This is the Clippy-like class.
It is the right answer when reach matters, but the product still is not Cargo core.

Use when:
- broad discoverability and distribution matter;
- the component should track toolchain compatibility closely;
- the workflow is broadly reusable enough to justify toolchain shipping;
- but the contribution still has a distinct command, cadence, or domain identity.

What belongs here:
- cross-cutting checkers with strong proof burden;
- high-reach commands that remain logically external to Cargo core;
- tools whose value grows mainly from presence, not from central policy control.

Wrong graduation move:
- assuming every important companion should become an optional component.

### 4. Service-side truth surface
This class covers facts whose authority comes from operating the service.

Use when:
- the source of truth is a registry, docs host, or other live service;
- freshness, policy, or route ownership belongs to that operator;
- consumers should import the truth rather than re-host it as if it were universal canon.

What belongs here:
- crates.io vulnerability surfacing and publishing mode facts;
- docs.rs rustdoc JSON hosting and service metadata;
- service-origin status, route, and freshness markers.

Wrong graduation move:
- confusing service truth with complete ecosystem judgment.
A service can expose facts without owning the whole review boundary.

### 5. Rust Project canonical document or upstream substrate
This class is for language/toolchain/reference contracts that must be maintained where their compatibility promises live.

Use when:
- the artifact describes or constrains Rust itself;
- downstream tools need a shared canonical reference;
- the thing becomes misleading if it remains “just one implementation's interpretation”.

What belongs here:
- specification/reference stewardship;
- stable compiler/Cargo/library-facing contracts;
- first-party protocol or machine-output surfaces whose absence forces ecosystem hacks.

Wrong graduation move:
- keeping long-lived canonical substrate work permanently in a companion repo once its value depends on being authoritative.

### 6. Foundation / consortium / institutional commons
This class is for work whose main challenge is sustained multi-party stewardship.

Use when:
- trust depends on cross-organization maintenance;
- renewal cost is large and ongoing;
- checklists, readiness profiles, qualification posture, or interop programs must stay live;
- or industry/public-good coordination matters more than shipping one binary.

What belongs here:
- safety-critical readiness commons;
- interop roadmaps and durable acceptance corpora;
- other institution-shaped stewardship programs.

Wrong graduation move:
- pretending a startup product, a single crate, or a badge is enough to replace a stewardship commons.

## The graduation rule
The default graduation sequence for worthy Rust contributions should be:

1. **prove value in a companion**;
2. **identify the narrow raw-fact hooks that belong upstream**;
3. **separate service truth from review/product logic**;
4. **promote only the compatibility-bearing substrate**;
5. **use optional toolchain distribution sparingly, for high-proof high-reach cases**; and
6. **move long-horizon readiness/spec/interoperability work into durable stewardship homes instead of keeping them as forever-prototypes**.

This is intentionally not a one-way escalator into Cargo core.
The most common correct outcome is a **split home**:
- upstream or service-side for raw facts and canonical contracts;
- companion/tooling layer for review, explanation, and policy overlays;
- consortium/editorial/program layer for renewal-heavy commons.

## Graduation-adjusted view of the current leaders
This is **not** a broad-importance rerank.
It is a “where should this mature?” map.

### 1. Build-State Evidence
**Best path:** class 1 → class 2, with limited class-5 imports.

Why:
- the real product is reviewable evidence, diff, and doctor surfaces;
- Cargo is already the right place for some raw recorded facts and unstable `cargo report` experiments;
- but the evidence product should stay companion-first while imports stabilize.

What to build in practice:
- companion pack/diff/doctor/export commands;
- explicit import lineage from Cargo surfaces;
- fallback posture when upstream facts are absent or experimental.

What may graduate upstream:
- better recorded metadata;
- stable identifiers or report fields;
- narrowly-scoped machine outputs.

What should not graduate wholesale:
- the whole review surface, judgment layer, or hosted analysis story.

### 2. Package Intake + Release Boundary Review
**Best path:** class 1 + class 4, with selected class-2 hooks.

Why:
- the review product is local/operator-facing and should stay companion-first;
- crates.io and similar services own some route truth and publish/security facts;
- intake judgment still belongs above raw service facts.

What to build in practice:
- local review/admit/quarantine/waive/recheck receipts;
- imported crates.io security/publishing facts with provenance preserved;
- route-specific policy overlays;
- alternate-registry / mirror / offline posture kept visible.

What may graduate upstream or service-side:
- better service truth fields;
- narrow package/provenance carriage;
- better route metadata.

What should not graduate wholesale:
- a universal “safe crate” portal or service-owned total trust score.

### 3. Feedback / Debug Acceptance Commons
**Best path:** class 1 + class 6, with selected class-2 and class-3 moves.

Why:
- local/session exporters and replay tools should stay companion-first;
- cross-debugger/OS/runtime acceptance is consortium-shaped;
- a few pieces may later deserve toolchain-distributed reach or better upstream hooks.

What to build in practice:
- companion session/replay/export tools;
- shared acceptance matrix and corpus under durable stewardship;
- explicit unsupported/regressed tuple receipts.

Possible higher-reach moves:
- optional distribution for especially mature exporters or checkers;
- narrow upstream improvements to debug-info or structured acceptance artifacts.

What should not happen:
- declaring the problem solved through one IDE plugin or one debugger vendor's surface.

### 4. Safety-Critical + Institutional Readiness Commons
**Best path:** class 5 + class 6.

Why:
- canonical specification and language-adjacent contracts belong under Rust Project stewardship;
- readiness corpora, interop guidance, lifecycle playbooks, and qualification-oriented overlays are consortium/program work.

What to build in practice:
- readiness cards and renewal rules in a commons layer;
- explicit references to canonical Rust-spec work where authority matters;
- coalition-owned evidence and freshness discipline.

What should not happen:
- treating this as one crate, one compliance badge, or one vendor-controlled checklist.

### 5. Compatibility Claims
**Best path:** class 1 → class 2 → occasional class 3.

Why:
- claim generation and review are companion-shaped;
- upstream should expose raw facts, not own every ecosystem claim;
- some especially high-value checks may later merit toolchain distribution.

What to build in practice:
- claim packs and renewal receipts outside core;
- imports from rustdoc JSON, libtest JSON, support envelopes, and release-boundary facts;
- bounded, renewable negative-state claims.

What may graduate:
- narrow fact surfaces;
- high-proof compatibility checks with broad utility.

What should not graduate wholesale:
- a single global compatibility dashboard or Cargo-owned policy empire.

### 6. Tooling Contract / Semantic Context
**Best path:** class 2 + class 5.

Why:
- the real value here is raw discoverability/import substrate and stable machine-facing contracts;
- higher-level tooling products should import it rather than trying to replace it.

What to build in practice:
- clearer machine-facing outputs and contracts;
- versioned import surfaces;
- companion exemplars and adapters that prove usefulness without masquerading as the whole product answer.

What should not happen:
- recasting the substrate layer as a universal end-user platform.

### 7. Adoption Navigation + Ecosystem Atlas
**Best path:** class 1 + class 6, with narrow metadata asks.

Why:
- the product is editorial/defaults/renewal work;
- it benefits from stronger metadata and import surfaces but should remain visibly weaker than canonical upstream docs on upstream-specific facts;
- renewal burden and neutrality concerns make durable commons stewardship more realistic than cargo-core placement.

What should not happen:
- upstreaming it as an official universal chooser or score-first product portal.

## What the worthy contribution should look like in theory and practice
A contribution becomes much stronger when its design note can answer **all five** of these at once:
1. **product residence now** — where the first real value lives;
2. **raw-fact residence** — where authoritative facts originate;
3. **graduation candidate** — what, if anything, might move closer to upstream, service truth, or toolchain distribution later;
4. **stewardship home** — who must keep it trustworthy after launch; and
5. **refused graduation** — what tempting move would make it look more official while making it less honest.

Future repo work should therefore favor notes and kernels that explicitly name:
- split-home designs;
- authority versus analysis;
- optional distribution versus core merger;
- service truth versus operator review;
- and durable stewardship versus forever-prototype drift.

## The strongest practical recommendation
The archive should now default to this portfolio posture:
- **Build-State Evidence** as the clearest companion-first product with narrow upstream-fact asks;
- **Package Intake + Release Boundary Review** as the clearest companion + service-truth split-home build;
- **Feedback / Debug Acceptance Commons** as the clearest companion + consortium split-home build;
- **Safety-Critical + Institutional Readiness** as the clearest canonical-substrate + consortium split-home build;
- **Compatibility Claims** as the clearest companion-first renewable-claims build with selective future distribution; and
- **Tooling Contract / Semantic Context** as the clearest substrate-first import layer rather than a standalone empire.

That is the practical answer to “what should a worthy contribution look like in theory and in practice?” once the archive already knows the rank and the first buildout order.
The best ones should not just be exciting, useful, or buildable.
They should also have an **honest home** and an **honest graduation path**.
