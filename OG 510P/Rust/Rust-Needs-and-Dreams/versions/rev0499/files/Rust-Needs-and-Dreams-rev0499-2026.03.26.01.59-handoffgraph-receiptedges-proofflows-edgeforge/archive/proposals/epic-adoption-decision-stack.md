# Epic proposal: Adoption Decision Stack

## Thesis
One of the most worthy contributions Rust could make now is a **thin, reviewable adoption-decision layer**.

Not another "best crates" page.
Not a hidden score.
Not an AI chooser pretending to be authority.

A real artifact system for answering, in a reviewable way:
- what project question is being asked,
- which atlas lanes and interop seams were considered,
- which trust, maintenance, docs, and support signals were imported,
- which local repository or migration facts changed the answer,
- what recommendation is being made,
- what serious alternatives remain viable,
- what freshness budget applies,
- and what changed when the recommendation drifted.

That would give Rust a way to turn ecosystem navigation into **project-scoped decisions** without collapsing the ecosystem into one globally blessed stack.

## Why now
The signals are unusually aligned:
- Rust’s 2025 vision work now explicitly recommends helping users navigate the crates.io ecosystem, says there is no clear place to get advice on a good “starter set” of crates, and points to smoother interop as part of the answer.
- The 2025 State of Rust survey says online docs remain the canonical reference, LLM/editor tooling is increasingly part of how people learn, maintainer support is a visible concern, and hiring/codebase growth continues.
- crates.io now exposes a Security tab, Trusted Publishing-only mode, SLOC metrics, and `pubtime`. That means recommendation inputs are richer than they used to be.
- docs.rs changed its default targets in October 2025 to reflect platform reality. That is a strong reminder that support claims drift and need freshness-aware imports rather than frozen prose.
- Cargo’s own development notes keep emphasizing that Cargo cannot be everything to everyone and that plugins matter, which argues for a companion decision layer instead of trying to stuff recommendation logic into Cargo itself.
- The Rust Foundation’s 2026–2028 strategy explicitly pairs **responsible growth in adoption** with **sustainable support for maintainers** and **stable, secure infrastructure**. That is exactly the policy environment where adoption guidance should import maintenance and trust reality instead of chasing popularity.
- The ecosystem already relies on unofficial and semi-curated navigation aids like Blessed.rs and lib.rs. That is evidence that the demand is durable — but those resources still do not produce project-scoped, renewable, reviewable adoption briefs.

Sources:
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- https://rustfoundation.org/media/annual-report-strategy-2025/
- https://blessed.rs/crates

## What should be built
A first credible version should ship:
1. canonical schemas for:
   - `adoption-question/v0`
   - `candidate-lane-set/v0`
   - `adoption-brief/v0`
   - `adoption-alternative-set/v0`
   - `adoption-check-report/v0`
   - `adoption-diff-report/v0`
   - `adoption-pack/v0`
2. import adapters for:
   - Atlas lanes / slot maps / freshness budgets,
   - Interop Commons seams and readiness reports,
   - Trust Decision / Policy / Lifecycle / publisher-source identity inputs,
   - Canonical Learning and Support Envelope artifacts,
   - Semantic Context imports for local repository, migration, or platform-fit evidence;
3. renderer outputs for:
   - human decision briefs,
   - compact team review memos,
   - migration-sensitive “why not the alternatives” summaries,
   - bounded assistant contexts derived from the same canonical pack;
4. drift support for:
   - freshness expiry,
   - changed trust or maintenance posture,
   - changed docs/support posture,
   - changed interop seams,
   - changed local-fit assumptions;
5. explicit review roles so recommendations can be signed off, challenged, or renewed without pretending they are objective law;
6. a ranked pilot program proving the layer can make good decisions without turning into one more prestige engine.

## Suggested CLI shape
A plausible companion-tool shape would be:
- `cargo adopt question`
- `cargo adopt brief`
- `cargo adopt check`
- `cargo adopt diff`
- `cargo adopt render`
- `cargo adopt pack`

The command surface matters less than the artifact boundary. The important point is that the adoption decision stays **thin** and **import-driven**.

## Initial pilots
Start with a ranked pilot program instead of trying to answer every Rust stack question at once:
1. **Greenfield CLI/internal-tool brief**
   - prove the system can answer a bounded question where tradeoffs are visible and migration cost is near zero;
2. **HTTP/service brief**
   - prove it can import runtime / HTTP / middleware / observability / background-work seams instead of hand-waving;
3. **Safety-oriented or regulated brief**
   - prove it can weight maintenance, support, and trust posture more heavily than popularity;
4. **Migration-sensitive existing-workspace brief**
   - prove it can import local semantic-fit evidence and explain why a theoretically good stack is not worth the change here;
5. **Assistant-consumer brief**
   - prove the same canonical pack can render bounded machine guidance without changing the underlying recommendation truth.

Cross-cutting pilot requirements:
- one pilot must import a **missing commons** note instead of pretending the stack already composes cleanly;
- one pilot must expire and be re-checked so freshness failure becomes part of the design rather than an afterthought;
- one pilot must produce a serious alternative set, not just a single winner.

## Milestones
### Milestone 1: Canonical artifacts + import boundaries
- publish schemas and examples;
- keep question, imports, recommendation, alternatives, and freshness/check state distinct;
- prove that project-local context can be imported without mutating atlas truth.

### Milestone 2: Reviewable human briefs
- render concise adoption briefs with reason-coded rationale;
- attach serious alternatives and explicit unanswered questions;
- require human-readable check reports before renewal.

### Milestone 3: Drift and renewal
- diff what changed between recommendation moments;
- surface stale inputs and invalidated assumptions;
- make re-checks cheap enough that teams will actually use them.

### Milestone 4: Assistant and org overlays
- derive bounded assistant contexts from the same canonical pack;
- support org-specific overlays and policy imports without forking atlas lanes into private folklore.

## Success metrics
- Teams can answer “what stack should we adopt here?” without rebuilding an ad hoc spreadsheet or Slack ritual.
- Alternatives remain visible instead of disappearing behind prestige defaults.
- Trust, maintenance, docs, and local-fit caveats survive into the final brief.
- Recommendation drift becomes auditable instead of anecdotal.
- Assistant guidance becomes more bounded and less stale.
- Atlas curation remains plural while project decisions become more concrete.

## Archive fit
This proposal sits directly above existing archive work:
- **Ecosystem Atlas** owns domains, lanes, slot maps, curator provenance, and freshness budgets.
- **Interop Commons** owns neutral shared seams and readiness reports.
- **Trust Decision** owns imported trust / policy / lifecycle / admission evidence.
- **Maintenance Reality** owns stewardship and succession posture.
- **Canonical Learning** owns the docs/examples/guidance surfaces users should actually read.
- **Semantic Context** owns local repository and migration-sensitive grounding.

What none of those owns is the final **project-scoped adoption answer**.

That is why this could be an epic contribution. It would turn “what should we use here, now?” from a recurring social ritual into a reviewable artifact family that composes with Rust’s growing ecosystem evidence instead of replacing it.
