# Epic Proposal: Reviewable Lane Defaults (`cargo lane` + `lane-default-pack/v0`)

## One-sentence pitch
Give Rust a portable way to publish **reusable scoped defaults** for recurring project classes — with alternatives, freshness, and bounded handoffs — so the ecosystem can be more helpful than “it depends” without quietly turning one lane into an ecosystem-wide permanent blessing.

## Deliverables
- `cargo lane` reference tool
- schemas:
  - `lane-default-scope/v0`
  - `lane-default-card/v0`
  - `lane-slot-defaults/v0`
  - `lane-default-evidence/v0`
  - `lane-default-freshness/v0`
  - `lane-default-handoff/v0`
  - `lane-default-pack/v0`
  - optional `lane-default-diff/v0`
  - optional `lane-default-override-report/v0`
- adapters/importers for:
  - `atlas-domain/v0`, `stack-lane/v0`, `stack-slot-map/v0`, `atlas-pack/v0`
  - `adoption-navigation-pack/v0`
  - `canonical-learning-pack/v0`
  - trust / maintenance / compatibility / support imports
  - local institutional overlay inputs
- docs:
  - conservative internal CLI default recipe
  - conservative service default recipe
  - existing-monorepo component recipe
  - script / repro lightweight default recipe
  - human / bootstrap / onramp / assistant bounded-handoff recipe

## Why now (signals)
- Rust’s March 20, 2026 challenges post says ecosystem navigation still depends too much on **choice paralysis**, **tacit knowledge**, and uneven domain maturity.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- Rust’s December 2025 vision work says users still need help getting oriented in crates.io and finding a good “starter set” of crates, while recognizing the political risk of blessing crates too broadly.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- The 2025 State of Rust survey says online docs remain canonical while editor and LLM-mediated workflows continue to rise, which increases the cost of fuzzy recommendation authority.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- crates.io’s January 2026 update added `pubtime`, SLOC, and source links to docs.rs, so refresh and review inputs are materially better than they used to be.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo’s February 2026 development-cycle note says Cargo cannot be everything to everyone and that plugins matter, which argues for a companion layer instead of forcing cargo core to become the full recommendation engine.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The Rust Foundation’s 2026–2028 strategy couples stable infrastructure, sustainable maintenance, and adoption growth, which is exactly where scoped defaults now belong.
  https://rustfoundation.org/strategic-plan/

## Non-goals
- replacing crates.io, docs.rs, or maintainer-authored canon;
- shipping a global “best crates” leaderboard;
- hiding a permanent recommendation score behind one command;
- using assistants as the source of truth;
- turning one starter template into the answer for an entire project class;
- pretending local organizational overlays are the same thing as public reusable defaults.

## Strategic value
This epic fills a missing middle layer in the archive’s current control plane.
Without it, Rust guidance tends to oscillate between:
- **candidate-space only** curation,
- **project-specific** adoption briefs,
- and accidental blessing when one answer gets repeated often enough.

With it:
- Atlas candidate space can stay broad;
- Adoption Navigation can stay project-specific when needed;
- Canonical Learning can travel into defaults without being rewritten from memory;
- Profiled Onramp and Project Bootstrap can import defaults instead of inventing them ad hoc;
- local institutional overlays can stay explicitly local;
- assistants can consume a bounded public default without being asked to become the ecosystem authority.

The prize is not a better score.
The prize is a durable answer to:
**“for this recurring project class, what reusable default lane are we prepared to recommend right now, and under what assumptions?”**

## Proposed shape
Ship a narrow companion layer that:
1. imports Atlas candidate space and slot maps;
2. records the project-class scope, runtime family, support/risk posture, team-maturity assumptions, and override threshold;
3. publishes one reusable default lane with serious alternatives still visible;
4. links canonical references and imported evidence rather than restating them from memory;
5. records freshness budgets and invalidation triggers;
6. emits bounded handoffs for onramp, bootstrap, local overlays, and assistants.

## Critical design bet
The critical bet is that **Rust needs reusable scoped defaults more than it needs stronger global blessing**.
That means:
- defaults are always scoped;
- alternatives remain first-class;
- canon remains maintainer-authored;
- evidence remains imported and freshness-visible;
- escalation to a project-specific brief remains normal;
- local institutional overlays remain explicitly distinct from public defaults.

Without that boundary, the contribution either stays too weak to matter or mutates into a hidden governance engine.

## Milestones
1. **v0 scope and card lane**
   - `lane-default-scope/v0`
   - `lane-default-card/v0`
2. **v0.2 slot and evidence lane**
   - `lane-slot-defaults/v0`
   - `lane-default-evidence/v0`
3. **v0.3 freshness and diff lane**
   - `lane-default-freshness/v0`
   - `lane-default-diff/v0`
4. **v0.4 handoff lane**
   - `lane-default-handoff/v0`
   - imports for Onramp / Bootstrap / local overlay consumers
5. **v1 default-pack lane**
   - `lane-default-pack/v0`
   - bounded assistant and human-review renderers
   - override-report support for project-specific divergence

## Execution order
Use [`design/reviewable-lane-defaults.md`](../design/reviewable-lane-defaults.md) as the design definition and [`design/reviewable-lane-defaults-pilot-program.md`](../design/reviewable-lane-defaults-pilot-program.md) as the rollout sequence.
Then implement beneath it in this order:
1. [`design/ecosystem-atlas-kit.md`](../design/ecosystem-atlas-kit.md)
2. [`design/adoption-navigation-bundle.md`](../design/adoption-navigation-bundle.md)
3. [`design/canonical-learning-stack.md`](../design/canonical-learning-stack.md)
4. trust / maintenance / compatibility / support imports
5. [`design/profiled-onramp-stack.md`](../design/profiled-onramp-stack.md)
6. [`design/project-bootstrap-stack.md`](../design/project-bootstrap-stack.md)
7. [`design/institutional-overlay-stack.md`](../design/institutional-overlay-stack.md)

## Success metrics
- recurring project classes stop recomputing guidance from scratch every time;
- defaults remain scoped and freshness-aware instead of drifting into lore;
- serious alternatives stay visible;
- starter paths and onramps become more consistent without becoming universal;
- assistants and internal platform docs become less stale because they can import bounded defaults;
- the ecosystem gains a recommendation layer that is helpful **and** politically honest.
