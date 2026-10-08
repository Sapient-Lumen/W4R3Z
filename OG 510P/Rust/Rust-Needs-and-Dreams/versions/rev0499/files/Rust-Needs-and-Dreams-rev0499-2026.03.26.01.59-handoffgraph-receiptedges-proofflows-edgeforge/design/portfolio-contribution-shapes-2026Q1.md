# Design: Portfolio contribution shapes and intervention archetypes (2026 Q1)

## Goal
The archive can now rank seams, specify execution blueprints, stage the portfolio, triage candidates, score pilots, bind them to proving grounds and anchors, route downstream consumers, maintain specimens, run conformance checks, keep a hypothesis ledger, and maintain a source atlas.

What it still lacked was one canonical answer to a narrower but increasingly important question:

> once we think a Rust contribution is worthy, what **shape** should it actually take in theory and practice — protocol, collector, reference layer, report command, service, corpus, checker, bridge, pilot program, or stewarded program?

This note is the archive's answer to a **contribution-shape atlas**, not frontier promotion.

Read with:
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/portfolio-selection-rubric-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/portfolio-artifact-conventions-2026Q1.md`
- `meta/CONTRIBUTION_SHAPE_PROTOCOL.md`
- `meta/CANDIDATE_TRIAGE_PROTOCOL.md`

## Why this note is needed now
The repo already knows a lot about **which seams matter**. What it still risked getting wrong was **what form a serious answer should take**.

Current Rust signals make that problem more visible, not less:
- The March 20, 2026 challenges writeup says the hardest recurring problems are not only language-level; they include compilation performance, tacit knowledge, and domain-shaped ecosystem friction. That means the best contributions will not all be language features or new crates.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says the broad challenge picture is fairly stable and docs remain canonical even as editor/LLM-mediated learning rises. That favors contributions that improve evidence, routing, and explanation surfaces — not only new framework code.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The February 11, 2026 program-management update says the project now organizes goals under **roadmaps** and **application areas** to focus industry funding. That is a direct reminder that some worthy contributions are not one tool at all, but a multi-asset program shape.
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- Cargo build analysis is explicitly a **collector + report-command** shape: it records metadata across invocations and introduces `cargo report` surfaces while keeping schemas unstable during prototyping.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The Cargo 1.94 cycle shows the same shape in practice: `cargo report rebuild`, `cargo report sessions`, manpages, and structured logging are all about explain/report surfaces rather than a hosted service or a universal cache empire.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- StableMIR is explicitly a **semver-governed compiler-facing API / reference-layer** shape meant to let tool developers build reliably without compiler internals.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- The libtest JSON goal is explicitly about **programmatic output** and shifting some reporting responsibility toward Cargo and runners, which is a report-surface and contract-shape decision, not “just another crate.”
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- crates.io's January 2026 update says the new frontend generates type-safe client code from an OpenAPI description. That is a service/API shape choice that differs materially from a local command, a protocol, or a corpus.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

Taken together, those signals say the archive needed one explicit answer for **what kind of contribution a given worthy seam should become**.

## Headline answer
A serious archive should maintain a **small shared atlas of contribution shapes**.

A contribution-shape card is not a ranking and not a seam.
It is a maintained answer to questions like:
- where does the truth live,
- how many producers and consumers need to agree,
- whether local explainability matters more than hosting,
- whether the first step is a corpus/checker pair rather than a service,
- and whether the work is really a program to be stewarded rather than a single tool to be shipped.

The atlas should help the repo answer three practical questions:
1. **What form should this contribution take first?**
2. **What artifacts should exist before it claims success?**
3. **What common category mistake should we avoid?**

## What this note is for
Use the contribution-shape layer when the archive needs to decide whether a worthy contribution should begin as a protocol/contract, a fact collector, a reference/query layer, a local report command, a hosted service surface, a curated corpus, a validator, an interop bridge, a bounded pilot program, or a longer-lived stewarded program.

Do **not** use it to claim that shape alone proves value, that every seam needs one shape only, that a checker can prove a product strategy is correct, or that a worthy idea becomes better just by sounding more infrastructure-like.

## The shape model
A good shape card should stay thin and practical. It should name:
- what kind of work this is;
- where authoritative truth tends to live;
- what artifacts must exist before the shape is real;
- which kinds of seams benefit most from it;
- what it is commonly mistaken for;
- and what failure mode to watch for.

The shape atlas should therefore keep these distinct:
- **protocol / contract** — many parties need a common boundary or semantics;
- **evidence collector** — capture and preserve observable facts from builds, tests, intake, or runs;
- **reference layer** — import bounded truths and answer narrow queries or diffs without owning all upstream semantics;
- **report command** — explain or summarize local machine state close to the workflow;
- **service surface** — hosted API / UI / registry / docs behavior where shared hosting matters;
- **corpus / atlas** — curated cards, defaults, anchors, hypotheses, or sources used to stabilize comparison and memory;
- **checker / validator** — enforce a small honesty or conformance boundary;
- **bridge / adapter** — connect foreign or native boundaries without pretending to replace both sides;
- **pilot program** — bounded proving lane with explicit scenarios, anchors, and verdicts;
- **stewarded program** — multi-asset, funding-aware, long-lived work that cannot honestly be sold as one crate.

## The first shared atlas
The archive's first contribution-shape atlas should cover at least these eight classes:
- `protocol_contract`
- `evidence_collector`
- `reference_layer`
- `report_command`
- `service_surface`
- `corpus_atlas`
- `checker_validator`
- `bridge_adapter`
- `pilot_program`
- `stewarded_program`

That atlas should not pretend these are interchangeable.
A report command is not a service.
A reference layer is not a collector.
A bridge is not a whole platform.
A corpus plus checker is not a substitute for upstream contracts.
A stewarded program is not “just ship a crate and see what happens.”

## Why a shape atlas is better than just “more strategy prose”
The archive already had many good ideas. What it lacked was a durable way to remember **what kind of thing each good idea should become first**.

Without a shape atlas, future revisions are more likely to:
- build a service before proving a local report layer;
- build a dashboard before a collector or reference layer exists;
- demand a protocol when a corpus/checker pair would be enough;
- or confuse a fundable roadmap/program with a one-binary deliverable.

The shape atlas is a smaller answer than a full product-methodology system and a more durable answer than case-by-case instinct.

## Default shape guidance for the archive's top seams
Until stronger evidence arrives, the archive should treat its current leading seams this way:
- **Build-State Evidence** should primarily look like an **evidence collector + report command + reference layer**, not a remote cache empire or replacement build system.
- **Semantic Context** should primarily look like a **reference layer** with bounded imports and routed views, not a universal knowledge graph or assistant-only blob.
- **Package Intake Gateway** should primarily look like an **evidence collector + reference layer + checker/receipt lane**, and only later, if needed, a stronger service integration.
- **Migration/Public API** should primarily look like a **reference layer + report/diff surface**, not just a semver score.
- **Adoption Navigation** should primarily look like a **reference layer + corpus/atlas + routed brief system**, not a generic crate-score website.
- **Native Edge** should primarily look like a **bridge/adapter + reference layer**, not a grand one-runtime-to-rule-them-all platform.

## What should be machine-checkable
A shared checker for the shape atlas should stay thin. It may enforce top-level schema family and revision, unique shape IDs, required class coverage, non-empty field presence, and existence of linked canon assets.

It should **not** try to prove that a chosen shape is optimal, that a seam is correctly ranked, or that a program will succeed.

## What should happen after the shape atlas changes
When the atlas changes materially, the repo should prefer a visible packet:
- update the design note or protocol if the model changed;
- update the corpus cards that actually encode the shapes;
- update the checker if the minimum rules changed;
- and update doctor/hygiene wiring if the atlas has become part of required repo health.

## Default interpretation for future revisions
Until stronger evidence arrives:
- the contribution-shape atlas is a **deepening + hygiene** layer, not a promotion;
- it strengthens the archive's ability to decide what form a worthy contribution should take before overdesigning it;
- it should stay small, reusable, and strongly anti-category-error;
- and it should resist a common failure mode: picking a seductive delivery shape first and only later discovering that the seam needed a different artifact family all along.
