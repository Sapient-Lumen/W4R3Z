# Design note: Profiled Onramp Stack (Background-aware learning + lane choice + first-project handoff)

## Goal
Define the thin execution bridge that turns **who is approaching Rust, from what background, for which domain** into a **reviewable route** across canonical learning, ecosystem choice, and first-project realization.

This note exists because the archive already has strong notes for:
- choosing Rust and a lane (`design/adoption-decision-stack.md`),
- curating ecosystem lanes (`design/ecosystem-atlas-kit.md`),
- preserving maintainer-authored canonical teaching (`design/canonical-learning-stack.md`), and
- turning a decision into a starter repo plus environment (`design/project-bootstrap-stack.md`).

What is still missing is the explicit bridge between them when the user is not asking only “which crate?” but also:
- “I come from C++ / Python / TypeScript / sync Rust; where do I start?”
- “Which Rust concepts do I need first for this domain?”
- “What should I read, try, and bootstrap in what order?”
- “How do we keep editor/assistant help derived from canonical materials instead of folklore?”

## Read with
- `design/adoption-decision-stack.md`
- `design/ecosystem-atlas-kit.md`
- `design/canonical-learning-stack.md`
- `design/project-bootstrap-stack.md`
- `design/workspace-environment-stack.md`

## Why this seam matters now
- Rust’s March 20, 2026 challenges post says learning Rust depends heavily on background and domain, explicitly recommends tailored learning paths, and says domain-specific materials help newcomers more than one generic tutorial. It also repeats that ecosystem navigation still depends too much on tacit knowledge.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says online docs remain the preferred canonical reference while some learning behavior appears to be shifting toward editor and LLM-mediated workflows. That increases the value of bounded, machine-usable route artifacts instead of ambient tutorial folklore.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust’s 2025 vision work says users still need help navigating crates.io, need advice on a good starter set of crates, and would benefit from better diagnostics and guidance from crates.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- The `cargo script` flagship goal argues that single-file packages reduce friction for educational material, reproducible bug reports, prototypes, and small utilities. That is directly relevant for route checkpoints and first proofs.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-script.html

## Problem statement
Today, Rust newcomers and Rust-adjacent teams often flatten six different concerns together:
1. source background and domain context;
2. concept translation (“what in Rust plays the role of the thing I already know?”);
3. canonical learning materials;
4. ecosystem lane choice;
5. starter/project bootstrap;
6. workspace/environment realization.

That flattening causes recurring failures:
- good canonical docs exist, but they are not routed in the order a specific learner or team needs;
- background-specific confusion gets answered ad hoc in chat, issues, or assistant sessions;
- “starter set” advice and “first project” advice blur together;
- editor/assistant guidance quietly becomes the de facto onramp without showing what was imported from canon;
- domain-specific differences (CLI, service, embedded, safety-critical, async-heavy work) arrive too late.

## Stack claim
A worthy contribution here is a **Profiled Onramp Stack**: a thin control-plane layer that preserves the handoff from **background/domain profile** to **concept translation** to **canonical learning imports** to **lane choice** to **bootstrap/environment handoff**.

It should not replace The Rust Book, rustdoc, mdBook guides, atlas curation, starter repos, editor help, or mentors. It should make those pieces composable and reviewable for a particular learner/team profile.

## Layer boundaries
### 1) Background and domain profile
Owned by the onramp stack.

It answers:
- what background the learner or team is coming from,
- what domain they are trying to enter,
- what constraints matter immediately,
- and what they already know versus still need translated.

This layer should output a bounded profile, not a full curriculum.

### 2) Concept translation
Owned by the onramp stack, but imported from canonical and domain sources.

It answers:
- which prior concepts deserve direct comparison,
- what the closest Rust-native vocabulary is,
- where a familiar analogy is actively misleading,
- and which concepts must be learned before others.

This layer should output translation maps and sequencing hints, not pretend to be the canonical docs themselves.

### 3) Canonical learning imports
Owned by the Canonical Learning Stack.

It answers:
- which maintainer-authored references, guides, examples, and compile-guidance surfaces are canonical,
- which are domain-specific,
- which are illustrative versus supported,
- and what remains conditional on target/runtime/feature choices.

This layer should remain imported and freshness-aware.

### 4) Lane choice and route narrowing
Owned by Adoption Decision + Ecosystem Atlas.

It answers:
- which lane or starter family is appropriate,
- which crate choices are part of that lane,
- which alternatives remain serious,
- and what tradeoffs are being accepted.

This layer should output a bounded route decision, not a magical “best Rust stack” verdict.

### 5) Bootstrap and environment handoff
Owned by Project Bootstrap + Workspace Environment.

It answers:
- what the first project realization should be,
- what the first runnable proof should be,
- what toolchain/editor/native prerequisites matter,
- and what remains manual or unresolved.

This layer should remain a handoff, not replace the learning route that preceded it.

## Artifact family
This stack only needs a small artifact family:
- `onramp-profile/v0` — source background, domain, constraints, and declared prior knowledge
- `concept-translation-map/v0` — direct comparisons, anti-analogies, sequencing notes, and risk points
- `learning-route/v0` — ordered canonical learning imports, atlas/adoption waypoints, and route rationale
- `onramp-checkpoint/v0` — small proofs, exercises, bug-repro tasks, or bootstrap checkpoints that verify progress honestly
- `onramp-handoff/v0` — references to learning, adoption, bootstrap, and environment artifacts plus freshness/owner info
- `onramp-pack/v0` — compact bundle tying the pieces together

Design rule: these are **composition artifacts**, not a universal tutoring substrate.

## What a worthy contribution would look like in practice
### Thin UX surface
A credible contribution would look like:
- `cargo onramp plan`
- `cargo onramp render`
- `cargo onramp check`
- `cargo onramp handoff`
- `cargo onramp pack`

or an equivalent companion tool that stays visibly above docs, atlas, and bootstrap layers rather than pretending to replace them.

### Inputs
It should accept:
- a background profile (for example C/C++, Python/TypeScript, existing Rust but sync-only, embedded/safety-critical constraints),
- a target domain,
- canonical learning sources,
- a chosen atlas/adoption lane when available,
- and optional org-local overlays.

### Outputs
It should produce:
- a reviewable route through canonical materials,
- a small concept-translation map,
- checkpoints that can be proved with examples or tiny starter artifacts,
- an explicit handoff into project bootstrap and workspace environment,
- and machine-usable bounded context for docs hosts, editors, or assistants.

### Positive properties
The contribution is worthy when it:
1. routes people to canonical materials instead of silently replacing them;
2. makes background-specific confusion explicit instead of ad hoc;
3. keeps domain-specific learning paths visible;
4. carries lane choice and starter choice as separate truths;
5. gives assistants/editors a bounded derived surface rather than letting them improvise the whole onramp;
6. stays thin enough to wrap existing docs, books, starter repos, and example workflows.

## Ranked first execution lanes
### 1. High-level-language developer → CLI / internal tool
Best first lane because it exercises concept translation, canonical docs, starter-set choice, and first-project realization without forcing async or native-platform complexity immediately.

### 2. C/C++ developer → service / systems component
High leverage because the March 2026 challenges post explicitly says some learners need direct reference/pointer comparisons and because Rust adoption often enters through existing systems teams.

### 3. Sync-Rust team → async/service route
A strategically important second-wave route because async still feels like a separate programming model for many users, and ecosystem/runtime lock-in must be made explicit rather than left as tacit knowledge.

### 4. Embedded / `no_std` learner route
Important because the challenges work says constraints amplify learning and debugging pain here, but should follow after the archive proves the model on more tractable ground.

### 5. Safety-critical conservative route
Important because domain-specific trust, support, and certification constraints change the route materially, but should follow once the route machinery itself is proven.

## Non-goals
- one universal Rust curriculum;
- a hidden recommendation engine that chooses crates without showing why;
- replacing The Rust Book or maintainer-authored docs;
- a magical chat tutor that becomes the new canon;
- flattening learning route, lane choice, starter repo, and environment setup into one blob.

## Failure modes to resist
- **Curriculum absolutism:** acting as if all learners should follow one canonical path.
- **Assistant canonization:** letting derived editor/assistant narratives replace canonical docs and route artifacts.
- **Template confusion:** using starter repos as the primary teaching surface instead of as one later checkpoint.
- **Background erasure:** pretending a C++ engineer, a TypeScript engineer, and an embedded newcomer need the same first route.
- **Lane drift:** hiding meaningful ecosystem choices behind one supposedly neutral route.

## Practical archive consequence
This seam should now sit beside Canonical Learning and Project Bootstrap as the missing **profile-aware entry layer** for real Rust adoption.

In other words: the next worthy contribution is probably **not another tutorial site** and not another hidden starter template. It is a thin, reviewable `cargo onramp` / `onramp-pack/v0` layer that turns background, domain, and canonical materials into a trustworthy first route without lying about where the route came from.
