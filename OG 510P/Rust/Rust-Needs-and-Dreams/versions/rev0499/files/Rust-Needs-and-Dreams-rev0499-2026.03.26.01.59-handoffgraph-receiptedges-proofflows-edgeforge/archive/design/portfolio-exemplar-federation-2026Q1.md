# Design: Portfolio Exemplar Federation (2026 Q1)

## Goal
The archive already has:
- a proving-grounds matrix;
- an anchor corpus;
- pilot scorecards;
- a shared artifact spine;
- and stronger stage-order / proof-burden / compounding discipline.

What it still lacked was one practical answer to a narrower but now highly consequential question:

> once the repo has scenario cards, anchor profiles, and a shared artifact family, what *actual maintained proving terrain* should future pilots, receipts, and comparison work run on so they stop freehanding their own favorite demo repos?

This note is the archive's answer to **exemplar federation**, not frontier promotion.

Read with:
- `design/portfolio-proving-grounds-2026Q1.md`
- `design/portfolio-anchor-corpus-2026Q1.md`
- `design/shared-spine-execution-blueprint-2026Q1.md`
- `design/portfolio-pilot-evaluation-2026Q1.md`
- `meta/EXEMPLAR_FEDERATION_PROTOCOL.md`
- `proofgrounds/portfolio-exemplar-federation-v0/exemplars.json`

## Why this note is needed now
The repo is now good at naming priorities and proof burdens.
That creates a new failure mode: future pilots can still win by choosing flattering repos, hand-wavy fixtures, or one-shot private demos whose shape no later team can reproduce.

Current Rust signals make an exemplar-federation layer more necessary, not less:

- Rust's March 2026 challenges writeup keeps saying the pain is both **broad** and **domain-shaped**: compile/resource taxes are universal, but async, package choice, embedded, safety-critical, and GUI workflows all carry different practical realities. That means one “real project” is not enough as proof terrain.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says resource usage remains a major productivity limiter, debugging is still a notable pain point, docs remain canonical, and editor/LLM mediation is rising. That means future pilots need renewable, reviewable proving worlds rather than attractive screenshots or chat summaries.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The March 2026 Cargo build-dir testing call explicitly says a crater run “won't cover everything” and asks people to run their own tests, release processes, and workflows against the new layout. That is almost a direct statement that the ecosystem needs better maintained proving terrain than one giant batch run or one anecdotal repo.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Crater itself exists because compiler regressions are not judged on one story: it builds and tests many crates and compares results between compiler versions. The archive should learn the corpus lesson without pretending it needs a compiler-team-scale empire.
  https://github.com/rust-lang/crater
- The rustc-perf improvements goal is pushing toward distributed benchmarking across multiple machines and configurations and explicitly says comparisons should happen **within a configuration, not across incompatible ones**. That is exactly the comparison discipline the archive needs for broader ecosystem pilots too.
  https://rust-lang.github.io/rust-project-goals/2025h2/rustc-perf-improvements.html
- The Rust debugging survey says support varies across multiple debuggers and operating systems, and that “truly stellar” support requires cross-debugger and cross-OS coverage. That makes single-host/single-tool demonstrations especially misleading for feedback-loop work.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- docs.rs changed its default build targets in October 2025, which is a reminder that docs-derived or consumer-routed claims can drift when target assumptions move. Exemplar terrain therefore needs explicit target posture, not just “the docs built once”.
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- The Rust Foundation's 2026–2028 strategy explicitly names stable infrastructure and sustainable maintenance. A small exemplar federation is exactly that kind of infrastructure: a maintained proving substrate that many stronger tools can reuse.
  https://rustfoundation.org/strategic-plan/

Taken together, those signals say the archive should now maintain not only scenario cards and anchor profiles, but also a **living exemplar federation**.

## Headline answer
A worthy repo increment here is:

> Build and maintain a **Portfolio Exemplar Federation**: a small renewable set of exemplar workspaces and replay bundles, each bound to scenario cards and anchor profiles, with explicit privacy posture, comparison invariants, required artifact families, and public-versus-private twin strategy.

This is **not** a universal sample-repo zoo.
It is also **not** just one benchmark pack, one canonical demo workspace, or one hosted proving service.

It is a thinner answer:
- a few named exemplar cards;
- each exemplar bound to scenario + anchor ids;
- a clear statement of what is public, what may need private shadow runs, and what stays comparable across both;
- and a shared replay expectation for the artifact spine.

## What this layer should do
Use the exemplar-federation layer when the repo needs to answer:
- what actual maintained proving terrain should future pilots reuse;
- when a public demo is enough versus when a private shadow twin is required;
- what comparison invariants a future pack or brief must preserve;
- and how a pilot can leave behind renewable proof instead of a beautiful but non-repeatable story.

Do **not** use it to claim:
- that every seam must publish a public reference repo;
- that one exemplar proves ecosystem-default readiness;
- that an exemplar federation replaces scenario cards, anchors, or seam-local fixtures;
- or that public exemplar success is the same thing as production validation in all domains.

## The federation model

### 1) Exemplar card
An exemplar card names one maintained proving world.
It should include:
- exemplar id and class;
- scenario bindings;
- anchor bindings;
- workspace posture and operational purpose;
- privacy posture;
- replay cadence / renewal rhythm;
- required shared artifact family;
- comparison invariants;
- allowed variation;
- public/private twin strategy;
- and explicit non-claims.

### 2) Public exemplar vs private twin
The archive should now say this explicitly:
some worthy proving worlds should be public, while others should exist as **shadow twins**.

Examples:
- a public inner-loop workspace can prove build-state and shared-spine value in the open;
- a restricted intake or safety-governed lane may need a **private twin** to exercise real policies, but should still publish the anchor/scenario class, replay contract, and weaker public artifact family.

This preserves honesty without forcing every operational reality into an open repo.

### 3) Replay bundle
Every exemplar should imply a small replay bundle:
- subject declaration;
- setup notes or capture preconditions;
- required pack / brief / lineage roles;
- and the minimum command family or workflow lane to rerun.

The exemplar federation is not complete until a later team could plausibly regenerate at least the same artifact family and compare with the prior run.

### 4) Comparison invariants
Each exemplar must say what stays fixed.
Typical invariants:
- workspace shape;
- dominant target or tuple family;
- release vs inner-loop posture;
- route/policy posture;
- debugger family or tool tuple when applicable;
- and what artifact roles are required.

This is the archive's protection against cargo-cult “real world” claims.

### 5) Renewal posture
Exemplar cards should carry a renewal rhythm.
Some worlds are worth rerunning quarterly; others only when upstream substrate or target posture changes.

The federation must therefore stay small enough to renew.
Better five living exemplars than thirty undead demos.

## The first thin federation
The archive's first exemplar federation should cover five proving worlds:

### A) Public inner-loop workspace exemplar
Purpose:
- reusable proving terrain for Build-State Evidence, shared spine, and local explainability.

Should prove:
- replayable build/rebuild/session artifacts;
- pack vs brief vs lineage separation;
- inner-loop comparison discipline.

Should not claim:
- release-boundary truth;
- locked-down intake posture;
- coalition-grade debugger acceptance.

### B) Public release-boundary library exemplar
Purpose:
- proving terrain for Migration/Public API, docs-derived routing, and compatibility claims.

Should prove:
- public-boundary artifact families;
- diff/verify flows;
- target-aware docs drift handling.

### C) Restricted-intake shadow exemplar
Purpose:
- proving terrain for Package Intake Gateway and route/payload review.

Should prove:
- route identity, staging posture, and review receipts.

Public rule:
- publish the card, invariants, and weaker public artifact family even if the full workspace or raw capture cannot be public.

### D) Public native-edge/polyglot exemplar
Purpose:
- proving terrain for Native Edge / interop / foreign-build boundary truths.

Should prove:
- provider/link/binding handoff discipline;
- host-vs-target posture;
- boundary-specific attachments.

### E) Cross-target docs and consumer-routing exemplar
Purpose:
- proving terrain for docs.rs target drift, semantic context, adoption navigation, and assistant-safe handoff.

Should prove:
- target-aware docs imports;
- weaker consumer brief generation;
- cross-target drift visibility.

## What a worthy contribution would look like in practice
A serious first build here would include:
- `design/portfolio-exemplar-federation-2026Q1.md`
- `meta/EXEMPLAR_FEDERATION_PROTOCOL.md`
- `proofgrounds/portfolio-exemplar-federation-v0/README.md`
- `proofgrounds/portfolio-exemplar-federation-v0/exemplars.json`
- `tools/check_exemplar_federation.py`

The repo should then start treating exemplar cards as first-class maintained assets, just like scenario cards, anchors, hypotheses, and source-atlas cards.

## Why this is strategically worthy
This layer is not the broadest first product.
It is a **truth-preserving enabler** for later products and programs.

Without it:
- pilots overfit to flattering demos;
- public artifact families drift away from real workflows;
- private-world proofs remain unshareable folklore;
- and future LLM/archive work starts hallucinating proof terrain from prose.

With it:
- Build-State Evidence gets durable proving worlds;
- Feedback Loop / Debuggability Acceptance gets a path to cross-tuple replay instead of one-off screenshots;
- Package Intake Gateway gets a public/private shadow strategy instead of all-or-nothing openness;
- Semantic Context and Adoption Navigation get target-aware docs worlds;
- and the shared spine gains real artifact packs to lint, diff, and renew.

## Recommended archive move
Treat this as a **deepening + repo-construction** pass.
Do **not** change the broad ladder.
Do **not** promote a new frontier.

Instead:
- keep **Build-State Evidence** as the strongest broad first build;
- keep **Feedback Loop / Debuggability Acceptance** as the clearest second serious build;
- keep the shared spine as stage-0 contract glue;
- and add one explicit answer for **what maintained proving terrain the portfolio should actually keep alive so future packs, briefs, and pilots can be renewed on shared worlds rather than demo folklore**.
