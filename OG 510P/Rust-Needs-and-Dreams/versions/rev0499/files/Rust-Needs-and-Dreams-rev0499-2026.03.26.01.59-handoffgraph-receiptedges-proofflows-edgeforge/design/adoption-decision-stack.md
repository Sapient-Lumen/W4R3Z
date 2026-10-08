
## 2026 bundle note
This stack is now best read together with [`design/adoption-navigation-bundle.md`](./adoption-navigation-bundle.md).
The stack still defines the composition logic for project-scoped recommendations, but the archive now treats the next repo-shaping move as the larger **Adoption Navigation Bundle** above Atlas + Canonical Learning + Trust / Maintenance / Semantic Context imports.

New default rule:
- use this file to describe how recommendation layers compose;
- use the bundle file to describe the portable artifact family, MVP, and non-goals;
- keep **question, candidate lanes, canonical references, imported evidence, local-fit checks, and bounded brief** distinct.

# Design note: Adoption Decision Stack (Ecosystem Atlas + Interop Commons + Trust Decision + Maintenance Reality + Canonical Learning + Semantic Context)

## Goal
Define the **division of labor and consumer flow** for answering concrete Rust ecosystem questions like:
- what stack should we adopt for this project,
- which lane is the conservative default versus the higher-leverage alternative,
- what trust, maintenance, and support caveats actually matter,
- what canonical docs/examples should onboard the team,
- and what migration or semantic-fit risks show up once the choice meets a real codebase.

This is **not** a new top-level truth engine.
It is a stack note explaining how the archive’s existing substrate pieces should compose so Rust can produce **bounded, freshness-aware adoption briefs** for humans and assistants instead of leaving stack selection to prestige, stale blog posts, or ungrounded LLM folklore.

Read this with:
- [`design/ecosystem-atlas-kit.md`](./ecosystem-atlas-kit.md)
- [`design/interop-commons-kit.md`](./interop-commons-kit.md)
- [`design/trust-decision-stack.md`](./trust-decision-stack.md)
- [`design/maintenance-reality-stack.md`](./maintenance-reality-stack.md)
- [`design/canonical-learning-stack.md`](./canonical-learning-stack.md)
- [`design/semantic-context-kit.md`](./semantic-context-kit.md)
- [`design/edit-workflow-kit.md`](./edit-workflow-kit.md)

## Why this note is needed now
Rust’s current signals no longer say only “there are many crates.”
They say the missing problem is **project-scoped selection and adoption judgment**:
- Rust’s 2025 vision work explicitly recommends helping users get oriented in the crates.io ecosystem, says there is no clear place to get advice on a good “starter set” of crates, and argues that better interop is part of the answer.
- The 2025 State of Rust survey says online docs remain the preferred canonical reference, community-learning signals may be shifting toward LLM tooling, and editors with agentic support are rising.
- crates.io now exposes materially better decision inputs such as the Security tab, Trusted Publishing-only mode, SLOC, and `pubtime`.
- docs.rs target defaults have already shifted to reflect platform reality, which is a reminder that support claims drift and should be imported with freshness rather than copied into static recommendation prose.
- The Rust Foundation’s current strategy pairs responsible growth in adoption with sustainable maintainer support and stable secure infrastructure.
- Cargo’s own development notes keep stressing that Cargo cannot be everything to everyone and that plugins matter, which is a strong signal that a thin companion layer is the right execution posture.
- The ecosystem already has de facto and semi-curated discovery aids such as Blessed.rs and lib.rs, which is useful evidence that the problem is real — but they do not produce project-scoped, freshness-aware, reviewable adoption artifacts.

Together these signals justify treating **adoption briefs** as a real missing artifact family above existing kits.

## Stack layers

### 1) Navigation and lane truth: Atlas + Interop Commons
This layer owns the candidate answer space:
- which domains and lanes exist,
- which slots matter,
- which crate families fill them,
- which shared seams or adapters make them compose,
- and which curator/freshness assumptions apply.

Questions this layer answers:
- “What are the respectable lanes for this kind of project?”
- “What slots and interop seams matter?”
- “What is the conservative default versus the more opinionated alternative?”

Design rule: **adoption briefs must import lane truth instead of inventing fresh stack folklore.**

### 2) Trust and governance truth: Trust Decision Stack
This layer owns supply-chain, provenance, advisory, lifecycle, and policy-relevant evidence:
- trust signals,
- inventory and signature attachments,
- lifecycle intent,
- and explicit policy decisions or `INCONCLUSIVE` states where they exist.

Questions this layer answers:
- “Are there trust or policy caveats that materially affect adoption?”
- “Is this recommendation acceptable only for some org profiles?”
- “Which claims are evidence versus decisions?”

Design rule: **adoption briefs may summarize trust posture, but must not masquerade as the policy engine.**

### 3) Sustainability truth: Maintenance Reality Stack
This layer owns declared lifecycle intent plus live stewardship evidence:
- support windows,
- successor relationships,
- queue pressure,
- explicit help requests,
- mentoring capacity,
- and operational visibility posture.

Questions this layer answers:
- “Is this lane sustainable enough for our time horizon?”
- “Are we choosing a stack whose maintenance story is mostly social memory?”
- “Should a brief weight current operational strain or succession risk?”

Design rule: **do not collapse popularity into sustainability.**

### 4) Canonical explanation truth: Canonical Learning Stack
This layer owns what should count as the canonical explanatory surface:
- checked docs,
- guide/example inventories,
- compile-time guidance,
- compile-fail teaching artifacts,
- and support-level distinctions.

Questions this layer answers:
- “What should a team read first after choosing this lane?”
- “Which examples are canonical versus illustrative?”
- “What guidance artifacts can an assistant quote or summarize safely?”

Design rule: **adoption briefs should point to canonical learning surfaces instead of replacing them with hand-written advice.**

### 5) Local-fit truth: Semantic Context + Edit Workflow
This layer owns what happens when a recommendation meets a real workspace:
- local semantic context,
- feature/resolution/build assumptions,
- candidate migration edits,
- compatibility or API drift findings,
- and bounded workspace-specific context.

Questions this layer answers:
- “Does the recommended lane actually fit this codebase?”
- “What migration burden or semantic mismatch is already visible?”
- “What would adoption change in this repository?”

Design rule: **a good ecosystem recommendation is still only a hypothesis until it meets local code truth.**

### 6) Derived consumer layer: adoption briefs
The missing consumer artifact is a **thin, reviewable recommendation brief** that imports the layers above without flattening them.

Candidate artifact family:
- `adoption-question/v0` — project scope, constraints, time horizon, risk posture, and explicit non-goals.
- `candidate-lane-set/v0` — imported atlas lanes, commons seams, and the initial shortlist.
- `adoption-brief/v0` — recommended lane(s), reason-coded rationale, freshness status, major caveats, and unanswered questions.
- `adoption-alternative-set/v0` — serious alternatives, why they are not default here, and switch/migration cost.
- `adoption-check-report/v0` — what trust/maintenance/docs/context checks were re-run, what drifted, and what remained unavailable.
- `adoption-diff-report/v0` — what changed between two recommendation moments.
- `adoption-pack/v0` — bundle of the question, imported evidence pointers, brief, alternatives, and check report.

Design rule: **the brief stays thinner than its imported evidence.**

## What a worthy contribution should look like in practice
A serious contribution here is **not** another blessed-crates page, opaque recommender model, crate score, or AI wrapper that free-associates about the ecosystem.

It is a thin consumer layer that can answer a concrete question like:
> “We are building an internal CLI with long support horizons and conservative supply-chain posture; which Rust lane should we adopt, what are the main alternatives, and what caveats should we budget for?”

…and then produce a reviewable answer that:
- imports Atlas lanes instead of inventing them,
- cites trust/maintenance/support/docs/context inputs separately,
- keeps freshness visible,
- exposes alternatives and non-claims,
- and can be rendered for a human reviewer and a bounded assistant consumer from the same pack.

## Ranked first execution lanes
1. **Greenfield CLI/internal-tool lane**
   - Smallest lane where stack choice still matters and documentation/trust/maintenance signals are legible.
2. **HTTP/service lane**
   - High-demand lane with real runtime, interop, and support tradeoffs.
3. **Safety-oriented or regulated internal-platform lane**
   - Forces maintenance/trust/support evidence to matter more than popularity.
4. **Migration-sensitive existing-workspace lane**
   - Proves semantic-context and edit-workflow imports can keep recommendations grounded.
5. **Bounded assistant-consumer lane**
   - Same adoption pack should produce a concise assistant context without changing the underlying recommendation truth.

## Non-goals
- one universal Rust “best stack” answer;
- replacing Atlas, Trust Signals, Policy, Lifecycle, DocProof, or Semantic Context with a mega-schema;
- automated code generation or auto-migration from a brief;
- hidden scoring models that cannot be reviewed;
- assistant-first artifacts that have no human-review path.

## Archive implications
- The archive should now treat **Atlas + Commons + Trust Decision + Maintenance Reality + Canonical Learning + Semantic Context** as a coupled **Adoption Decision Stack** for project-scoped selection work.
- Future revisions should prefer **thin adoption briefs, visible imports, freshness budgets, alternative sets, and local-fit checks** over more “top crates” prose, prestige-led recommendation lists, or ungrounded assistant guidance.
- This should remain a **stack note plus pilot program** until the archive proves that the derived brief layer is genuinely thinner than the imported evidence.

## References (signals)
- What do people love about Rust?
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey results:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- crates.io development update (Jan 2026):
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- docs.rs changed default targets:
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- Cargo development cycle 1.94:
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Rust Foundation strategy / annual report note:
  https://rustfoundation.org/media/annual-report-strategy-2025/
- Blessed.rs recommended crate directory:
  https://blessed.rs/crates
