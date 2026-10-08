## Addendum (rev0434)
For questions about **which concrete representative case profiles should sit underneath the shared proving-grounds matrix so serious pilots stop hiding behind one flattering private demo**, read this note right after `design/portfolio-proving-grounds-2026Q1.md`, `design/portfolio-pilot-evaluation-2026Q1.md`, and `meta/ANCHOR_CORPUS_PROTOCOL.md`.

Interpretation rule:
- this note does **not** promote a new seam;
- it does **not** change the broad ladder or the default portfolio order;
- it exists to answer the missing execution question: **once the repo names shared scenarios, what small anchor corpus should it maintain so pilots can bind themselves to comparable representative cases instead of improvised showcase repos?**
- keep **Build-State Evidence** as the strongest one-project answer overall;
- keep the strongest multi-project answer as **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- and require every serious pilot that claims representative coverage to name one or more anchor IDs, what was held constant, what varied, and what those choices still forbid it from claiming.

# Design: Portfolio anchor corpus and representative case profiles (2026 Q1)

## Goal
The archive can now:
- rank strong seams,
- specify what they should ship,
- stage the portfolio,
- triage additions,
- score pilots,
- route consumer slices,
- validate a thin shared envelope,
- maintain specimens,
- run an archive doctor pass,
- and keep a proving-grounds scenario matrix.

What it still lacked was one canonical answer to a narrower but now practical question:

> once a pilot names a scenario card, what *concrete kind of case* should it exercise so readers can compare two pilots on something more repeatable than “a repo like ours”?

This note is the archive's answer to **portfolio anchor corpus**, not frontier promotion.

Read with:
- `design/portfolio-proving-grounds-2026Q1.md`
- `design/portfolio-pilot-evaluation-2026Q1.md`
- `design/portfolio-selection-rubric-2026Q1.md`
- `meta/PROVING_GROUNDS_PROTOCOL.md`
- `meta/ANCHOR_CORPUS_PROTOCOL.md`
- `meta/PILOT_SCORECARD_PROTOCOL.md`

## Why this note is needed now
The repo is now good enough at saying what a worthy seam is that another failure mode matters more: two teams can both claim they exercised the same scenario while quietly choosing radically different repos, scales, operating systems, or workflow shortcuts.

Current Rust signals make an anchor-corpus layer more necessary, not less:

- Rust's March 2026 challenges writeup says Rust's pain is not one uniform beginner problem. Some taxes are universal, but many are domain-shaped and maturity-shaped. That means a pilot needs more than a slogan like “we tested a real project”; it needs a named case profile that says what kind of real project it stood in for.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says the broad challenge picture is fairly stable, docs remain canonical, and many developers increasingly use editors and LLM tooling while still reporting compile/resource/debugging pain. If those pains are stable enough to guide strategy, then the comparison surface for pilots should also become stable enough to compare across revisions.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The January 2026 program-management update says goals now sit under longer-lived roadmaps and application areas meant to focus industry funding. That means a pilot should increasingly be able to say not just “scenario X” but “scenario X exercised through anchor profile Y”, because funders and maintainers care which kind of organization or repo reality the result actually maps to.
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- The rustc-perf improvements goal is explicitly about distributed benchmarking across multiple platforms and configurations, with compare-within-configuration discipline instead of flattening incompatible numbers. That is the right comparison lesson for this archive too: keep anchors concrete enough to compare within a case profile, not so universal that every result becomes fake-commensurate.
  https://rust-lang.github.io/rust-project-goals/2025h2/rustc-perf-improvements.html
- Crater exists because compiler changes are not judged on one anecdotal repo: it builds many crates, runs tests, and compares results between compiler versions. The archive does not need a full Crater empire, but it should learn the same lesson that representative corpus beats charming demo.
  https://github.com/rust-lang/crater
- The March 2026 Build Dir Layout v2 testing call says many tools still rely on unspecified details and explicitly asks people to run tests, release processes, and other workflows against the new layout, because even a crater run “won't cover everything”. That is a direct signal that representative case coverage should be named, not assumed.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- The February 2026 Rust debugging survey says debugging quality varies across debuggers and operating systems and needs multi-environment understanding. That is another argument for anchors that name environmental shape instead of letting one Linux-only, one-debugger success overgeneralize.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Cargo build analysis, libtest JSON, and docs.rs rustdoc JSON all reinforce the same direction: Rust tooling is gaining more machine-usable outputs, but those outputs still come with schema, environment, and format caveats. An anchor corpus is a good place to say which outputs, targets, and comparison conditions matter for a given representative case.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
  https://docs.rs/about/rustdoc-json

Taken together, those signals say the archive needed a **small representative anchor corpus** beneath the scenario matrix.

## Headline answer
A serious portfolio should maintain a **thin anchor corpus** beneath the proving-grounds matrix.
It is not a universal benchmark lab and not a giant zoo of sample repositories.
It exists for a smaller question:

> after a pilot names a scenario card, what concrete representative case profile did it exercise, what conditions did it hold constant, what did it deliberately vary, and what does that still fail to prove?

The anchor corpus should therefore:
1. define a small set of representative anchor cards;
2. bind every anchor card to one or more scenario IDs;
3. state what traits make a case representative for that anchor;
4. state what shortcuts would make a claimed result incomparable or overclaimed;
5. and keep case-profile truth separate from seam ranking, freshness renewal, and seam-local payload semantics.

## What this note is for
Use the anchor-corpus layer when the archive needs to answer:
- which concrete case profiles should sit under scenario cards;
- what a pilot must hold constant to compare itself honestly against other pilots;
- when a pilot exercised the right scenario class but still used too-narrow case conditions;
- and what “tested on a representative repo” should actually mean.

Do **not** use it to claim:
- that the archive must maintain a huge fleet of public sample repos now;
- that one anchor card proves real-world default readiness;
- that anchors replace scenario cards;
- or that anchor coverage is the same thing as fresh ecosystem evidence.

## The anchor-corpus model

### 1) Anchor card
An anchor card is a named representative case profile.
It should say:
- what scenario IDs it binds to;
- what shape of workspace or package it stands in for;
- what traits must be present for the anchor to count;
- what traits must stay constant when comparing pilots;
- what traits are allowed to vary;
- what minimum artifacts a pilot should leave behind there;
- and what the anchor still does **not** prove.

### 2) Anchor corpus
The corpus is the maintained set of anchor cards.
It should stay small enough that maintainers can remember it and tools can validate it.
The first corpus should prefer **representative profiles** over big public fixtures.

### 3) Anchor binding
A serious pilot should name one or more anchor IDs.
If it claims a scenario but no fitting anchor exists yet, it should say so and leave behind a request to widen the corpus.

### 4) Comparison discipline
Anchor cards should include:
- what to hold constant;
- what is allowed to vary;
- what evidence families matter most;
- and what conclusions remain forbidden.

This keeps pilots comparable without flattening them into one synthetic benchmark score.

## The first anchor corpus
The archive's first anchor corpus should cover the existing scenario matrix with five representative case profiles:

### A) Medium multi-crate inner-loop workspace
Purpose:
- stand in for the normal “Rust workspace under developer and CI pressure” case,
- with enough shape to stress build receipts, cache reuse, lock contention, and repeated inner-loop decisions.

Bind to:
- `inner_loop_workspace_pressure`

Good for:
- **Build-State Evidence**,
- **Semantic Context** consumers tied to editing or rebuild explanation,
- build-analysis and cargo-report-style evidence.

### B) Small publishable library family at release boundary
Purpose:
- stand in for public API, migration, semver, docs, and support claims where publishability and public surface matter.

Bind to:
- `public_library_release_boundary`

Good for:
- **Migration/Public API**,
- **Semantic Context**,
- docs- and public-boundary-derived comparisons.

### C) Restricted consumer with explicit intake controls
Purpose:
- stand in for “before we use this package, we need route, payload, staging, and policy review truth”.

Bind to:
- `locked_down_intake_policy_lane`

Good for:
- **Package Intake Gateway**,
- package admission,
- release/security/compliance operator handoffs.

### D) Polyglot Rust↔native component boundary
Purpose:
- stand in for build-script, linker, ABI, provider, foreign-build, and host-vs-target complexity without pretending all interop cases are the same.

Bind to:
- `native_edge_polyglot_boundary`

Good for:
- **Native Edge Contract**,
- cross-language interop roadmaps,
- sys/build/bindings/provider adjacent ideas.

### E) Docs-derived cross-target consumer support case
Purpose:
- stand in for “we are making claims from docs, rustdoc JSON, or routed consumer views and target drift matters”.

Bind to:
- `cross_target_docs_consumer_drift`

Good for:
- **Semantic Context**,
- **Adoption Navigation**,
- routed-brief consumers that must stay visibly weaker than canon.

## Required anchor-card fields
The repo-level minimum lives in `meta/ANCHOR_CORPUS_PROTOCOL.md`, but the short version is:
- `anchor_id`
- `title`
- `anchor_class`
- `scenario_bindings`
- `representative_shape`
- `required_traits`
- `hold_constant`
- `allowed_variation`
- `minimum_artifacts`
- `primary_evidence_focus`
- `must_not_claim`
- `notes`

These fields make the corpus concrete without turning it into a synthetic benchmark spec.

## What makes this a worthy repo increment
This note does not invent a new strategic winner.
It makes the existing proving-grounds layer more usable.

That is valuable because the archive's strongest answers increasingly depend on **reviewable artifacts and bounded claims**, but scenario cards alone are still too abstract to stop flattering demo choice.
An anchor corpus gives the proving grounds more bite:
- **Build-State Evidence** pilots can bind to a named workspace-pressure anchor instead of “a project like ours”;
- **Migration/Public API** pilots can bind to a publishable library-family anchor instead of “some crate”;
- **Package Intake Gateway** pilots can bind to a restricted-intake anchor instead of “an enterprise setting” in the abstract;
- **Native Edge** pilots can bind to a polyglot boundary anchor instead of “interop” in general;
- **Semantic Context** and **Adoption Navigation** pilots can bind to a docs/consumer-drift anchor instead of “developer guidance” in the abstract.

So the anchor corpus does not compete with the proving grounds. It makes the proving grounds more reproducible.

## Default anti-goals
Do not let this become:
- a giant public benchmark zoo;
- a promise that every anchor has a curated reference repo immediately;
- a hidden reranking mechanism that changes the ladder without saying so;
- or a fake-complete standard that blocks useful pilots until a perfect corpus exists.

The archive wants a **small representative anchor corpus**, not a cargo-cult copy of Crater or rustc-perf.

## Practical default
Until stronger evidence arrives, the default anchor-corpus answer is:
- keep the broad ladder intact;
- treat this layer as **deepening + hygiene**, not promotion;
- require new serious pilots that claim representativeness to name one or more anchor IDs explicitly;
- require them to state what was held constant and what varied;
- and prefer a thinner honest anchor corpus over a larger fake-complete evaluation empire.
