# Design: Adoption Decision pilot program

## Goal
Prove that Rust can answer **real project-scoped stack questions** with a thin, reviewable artifact family rather than relying on prestige, tacit ecosystem knowledge, or opaque recommendation engines.

This pilot is about making adoption recommendations:
- concrete,
- freshness-aware,
- explainable,
- alternative-rich,
- and grounded in imported evidence.

It is **not** about ranking all crates globally.

Read with:
- [`design/adoption-decision-stack.md`](./adoption-decision-stack.md)
- [`design/ecosystem-atlas-kit.md`](./ecosystem-atlas-kit.md)
- [`design/interop-commons-kit.md`](./interop-commons-kit.md)
- [`design/trust-decision-stack.md`](./trust-decision-stack.md)
- [`design/maintenance-reality-stack.md`](./maintenance-reality-stack.md)
- [`design/canonical-learning-stack.md`](./canonical-learning-stack.md)
- [`design/semantic-context-kit.md`](./semantic-context-kit.md)

## Why pilot this now
The current Rust story is not “there is no guidance.”
It is “guidance exists, but it is fragmented across neutral registries, unofficial curation, docs, issue threads, local team lore, and increasingly assistant answers.”

That is exactly the kind of problem that benefits from a **thin review layer** instead of a universal platform:
- the Rust vision work now explicitly says users need help getting oriented in the crates.io ecosystem;
- the 2025 survey says docs remain canonical while LLM/editor tooling is rising;
- crates.io has richer trust and freshness signals than it used to;
- Blessed.rs and similar efforts show the problem is worth curating, but they do not answer “what should *this* team adopt *here*?”;
- Cargo is continuing to favor plugin-space expansion instead of becoming a universal product for every downstream workflow.

That combination means the archive should prove the adoption layer through a ranked pilot program before broadening it.

## Candidate artifact family to exercise
The pilot should treat the following artifacts as the minimum viable family:
- `adoption-question/v0`
- `candidate-lane-set/v0`
- `adoption-brief/v0`
- `adoption-alternative-set/v0`
- `adoption-check-report/v0`
- `adoption-diff-report/v0`
- `adoption-pack/v0`

Pilot rule: **every rendered recommendation must keep imported evidence categories visibly separate.**

## Ranked pilot lanes

### 1) Greenfield CLI / internal-tool brief
**Why first**
- Lowest coordination cost.
- Clear tradeoffs across parser, terminal, config, logging, testing, packaging, and support lanes.
- Strong enough to show the value of imported trust/docs/maintenance signals without needing distributed-systems complexity.

**Success bar**
A brief can recommend a sensible CLI lane, name at least one serious alternative, point to canonical docs/examples, and explain why the choice is suitable without pretending the decision is universal.

### 2) HTTP/service brief
**Why second**
- High-demand lane for real Rust teams.
- Forces the adoption stack to import runtime settings, middleware/interoperability seams, observability, background work, and support posture.
- Flushes out whether Atlas + Commons are mature enough to support service recommendations without hand-wavy prose.

**Success bar**
A brief can recommend a service lane and preserve where the answer came from: lane truth, trust/maintenance posture, canonical docs, and any local-fit caveats.

### 3) Safety-oriented / regulated internal platform brief
**Why third**
- Stress-tests the system against settings where popularity should not dominate.
- Forces maintenance, support claims, trust posture, and evidence imports to be first-class.

**Success bar**
A brief can justify a more conservative lane without hiding the alternatives or pretending policy decisions came from Atlas alone.

### 4) Existing workspace / migration-sensitive recommendation
**Why fourth**
- Proves the stack can stay grounded when the user already has code.
- Imports Semantic Context and Edit Workflow without becoming an auto-migration tool.

**Success bar**
A brief can state what the recommended lane would imply for the existing workspace and what remains uncertain.

### 5) Assistant-rendered brief consumer
**Why fifth**
- The ecosystem pressure is increasingly human + machine, not one or the other.
- The 2025 survey explicitly points toward LLM/editor tooling as part of the learning/navigation story.
- This lane proves the archive can serve assistants **without** making them canonical.

**Success bar**
A bounded assistant context derived from the same adoption pack preserves caveats, alternatives, freshness, and uncertainty.

## Pilots to defer
- a global crate recommender or ranking engine;
- hidden telemetry-driven popularity models;
- direct code generation from adoption briefs;
- social “best stack” dashboards;
- one-shot mega-briefs that try to cover all Rust domains at once.

## Immediate archive consequences
- Treat [`design/adoption-decision-stack.md`](./adoption-decision-stack.md) as a real frontier note, but keep it explicitly **consumer-thin**.
- Future archive work on Atlas, Trust, Maintenance, Canonical Learning, and Semantic Context should ask whether it improves the quality of eventual adoption briefs.
- Do **not** widen this pilot until at least one lane proves that imported truths stay visibly separate in the final rendered brief.

## Why this would be a worthy contribution
Rust already has many of the ingredients needed for better ecosystem decisions.
The missing contribution is the thing that turns them into a **reviewable answer for a concrete project**.

That sounds smaller than a compiler feature or a new framework.
But it could materially improve:
- team onboarding,
- stack selection speed,
- recommendation freshness,
- assistant quality,
- and institutional memory around why a team chose one lane and not another.
