## 2026Q1 frontier note
This proposal should now be read together with `design/adoption-navigation-contract-2026Q1.md`.

The promotion decision in rev0409 is that Rust's missing contribution is not just a better curation site.
It is a portable **project-scoped recommendation contract** that can export a question record, candidate lanes, canonical references, imported evidence, local-fit checks, bounded briefs, and diffable renewal points.

# Epic Proposal: Adoption Navigation Bundle (`cargo adopt` + `adoption-navigation-pack/v0`)

## One-sentence pitch
Make Rust stack selection boring by standardizing a portable **question → candidate lanes → canonical references → imported evidence → local-fit check → bounded brief** bundle instead of leaving ecosystem guidance scattered across search results, prestige signals, stale internal docs, and assistant memory.

## Deliverables
- `cargo adopt` reference tool
- schemas:
  - `adoption-question/v0`
  - `candidate-lane-set/v0`
  - `canonical-reference-set/v0`
  - `adoption-evidence-report/v0`
  - `local-fit-check/v0`
  - `adoption-brief/v0`
  - `adoption-alternative-set/v0`
  - `adoption-handoff/v0`
  - `adoption-diff-report/v0`
  - `adoption-navigation-pack/v0`
- adapters/importers for:
  - `atlas-domain/v0`, `stack-lane/v0`, `stack-slot-map/v0`, `atlas-pack/v0`
  - `canonical-learning-pack/v0`
  - trust / lifecycle / maintenance / support imports
  - docs.rs / canonical-doc pointers
  - semantic-context and local trial inputs
- docs:
  - greenfield CLI lane recipe
  - service/backend lane recipe
  - safety-oriented internal-tool lane recipe
  - local-fit evaluation recipe
  - assistant / platform-team bounded-handoff recipe

## Why now (signals)
- Rust’s March 20, 2026 challenges post names ecosystem navigation, choice paralysis, tacit knowledge, and uneven domain maturity as explicit adoption blockers.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says online docs remain canonical while learning and editor behavior continue shifting toward machine-mediated workflows.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust’s December 2025 vision work says users need help getting oriented in crates.io and recommends better supportive interfaces and guidance from crates.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- docs.rs target-default changes in October 2025 show that platform-support defaults drift and should be imported explicitly rather than baked forever into recommendation prose.
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- crates.io’s January 2026 update added Trusted Publishing controls, SLOC, and `pubtime`, creating stronger machine-usable recommendation inputs.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- the Rust Foundation’s 2026–2028 strategy couples stable infrastructure, sustainable maintenance, and adoption growth, which is exactly where recommendation infrastructure now belongs.
  https://rustfoundation.org/strategic-plan/
- Rust’s January 2026 maintenance writeup says maintenance is continuous and socially real, which means any serious recommendation layer must import stewardship posture rather than ignore it.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/

## Non-goals
- replacing crates.io, docs.rs, or maintainer-authored docs;
- shipping a universal “best crates” answer;
- inventing a single numeric recommendation score;
- using assistants as the source of truth;
- silently replacing trust, maintenance, compatibility, or policy systems with one meta-layer.

## Strategic value
This deserves promotion because it gives the archive a missing **decision-record composition point**.
With it:
- Atlas-style lane curation can become project-scoped decisions instead of ambient lore;
- canonical references can travel with recommendations instead of being rewritten from memory;
- trust and maintenance inputs can shape recommendations without collapsing into one score;
- local-fit checks can remain explicit rather than being smuggled into prose after the fact;
- assistants and platform teams can reuse bounded recommendation truth without becoming hidden authorities.

The prize is not a smarter recommendation engine.
The prize is a durable record of **what was being decided, which lanes were considered, what evidence mattered, what local trial work was done, and what the final brief is actually allowed to claim**.

## Proposed shape
Ship a narrowly scoped bundle layer:
1. import Atlas domain/lane/slot artifacts as the candidate answer space;
2. import canonical-learning artifacts as the maintainer-authored reference surface;
3. import trust / maintenance / lifecycle / docs posture as explicit evidence lanes;
4. record local-fit checks against real workspaces or bounded prototypes;
5. emit a brief that keeps the default lane, serious alternatives, freshness, and unanswered questions explicit;
6. emit bounded handoffs for human review, internal platforms, CI policy, and assistants.

## Critical design bet
The critical bet is that **Rust needs project-scoped recommendation bundles more than it needs one universal curation authority**.
That means:
- multiple respectable lanes remain first-class;
- canonical references remain maintainer-authored;
- evidence remains imported and freshness-visible;
- local fit remains a real lane, not an afterthought;
- bounded consumer handoffs remain derived rather than canonical.

Without that boundary, the contribution either stays too weak to matter or bloats into a hidden governance engine.

## Milestones
1. **v0 question + lane-set lane**
   - `adoption-question/v0`
   - `candidate-lane-set/v0`
2. **v0.2 canonical-reference lane**
   - `canonical-reference-set/v0`
   - import canonical-learning sources
3. **v0.3 evidence lane**
   - `adoption-evidence-report/v0`
   - trust / maintenance / docs freshness imports
4. **v0.4 local-fit lane**
   - `local-fit-check/v0`
   - bounded workspace/prototype trials
5. **v1 brief + handoff lane**
   - `adoption-brief/v0`
   - `adoption-alternative-set/v0`
   - `adoption-navigation-pack/v0`
   - `adoption-handoff/v0`

## Execution order
Use [`design/adoption-navigation-bundle.md`](../design/adoption-navigation-bundle.md) as the bundle definition.
Then roll out beneath it in this order:
1. [`design/ecosystem-atlas-kit.md`](../design/ecosystem-atlas-kit.md)
2. [`design/adoption-decision-stack.md`](../design/adoption-decision-stack.md)
3. [`design/canonical-learning-stack.md`](../design/canonical-learning-stack.md)
4. trust / maintenance / compatibility / support imports
5. semantic-context local-fit and bounded assistant/platform handoffs

## Success metrics
- teams can answer “what should we adopt here?” without inventing a new spreadsheet or Slack ritual;
- candidate lanes and serious alternatives stay visible;
- canonical references survive into the recommendation instead of being replaced by vibes;
- freshness and drift are auditable;
- assistants become more bounded and less stale;
- the ecosystem gets one explainable recommendation seam instead of more prestige-driven lore.
