## Addendum (rev0427)
For questions about **how the archive should prove that a staged contribution or pilot actually worked instead of just demoing well**, read this note right after `design/portfolio-selection-rubric-2026Q1.md` and `design/portfolio-execution-sequencing-2026Q1.md`.

Interpretation rule:
- this note does **not** promote a new seam;
- it does **not** change the broad ladder or the default build sequence;
- it exists to answer the missing execution question: **what evidence should make a serious pilot graduate, stall, deepen, fold, delay, or die?**
- keep **Build-State Evidence** as the strongest one-project answer overall;
- keep the strongest multi-project answer as **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- and require every serious pilot to prove **lane value**, **artifact honesty**, **downstream decision value**, and **stewardability** rather than just shipping a slick interface.

# Design: Portfolio pilot evaluation and exit criteria (2026 Q1)

## Goal
The archive can now:
- rank strong seams,
- describe what they should ship,
- define a thin shared grammar,
- stage the portfolio,
- and triage new candidates.

What it still lacked was one canonical answer to a harder practical question:

> once a serious team starts building one of these seams, how should the repo judge whether the pilot actually proved itself, graduated, stalled, should be folded into another seam, or should be killed?

This note is the archive's answer to **pilot proof**, not frontier promotion.

Read with:
- `design/portfolio-selection-rubric-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/portfolio-artifact-conventions-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `meta/PILOT_SCORECARD_PROTOCOL.md`

## Why this note is needed now
The repo has become good at deciding what seems worthy.
That creates a new failure mode: the archive can now admit pilots that look persuasive in screenshots, talks, or local demos without forcing them to prove that they reduced a real tax or emitted trustworthy reusable artifacts.

Current official Rust signals make that failure mode more dangerous, not less:

- Rust's March 2026 challenges writeup says the major problems are recurring and practical: compile/resource pain, choice paralysis / tacit knowledge, async complexity, and domain-specific maturity gaps. That argues for evaluating pilots on whether they reduce a real lane tax, not whether they merely look clever.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says the broad challenge pattern is stable, docs remain canonical, and editor/LLM-mediated learning is rising. That argues for pilots that emit reviewable machine-usable artifacts and improve canonical handoffs rather than producing one more UI or assistant wrapper.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2026 goals overview says goals are a contract and that new goals may be added only when the needed resources are already known. The owner guidance says owners must report regularly, that milestones matter, and that design axioms are part of building trust. That argues for pilots with explicit scorecards, stage exits, and steward expectations.
  https://rust-lang.github.io/rust-project-goals/2026/
  https://rust-lang.github.io/rust-project-goals/about/owners.html
- Cargo's build-analysis goal is explicitly about recording build metadata across invocations and surfacing rebuild reasons and timings in machine-usable form. The revived libtest JSON goal says people had come to rely on programmatic output. That argues for pilots being judged partly by the quality of their emitted evidence, not only by UX.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- docs.rs rustdoc JSON, the `cargo-semver-checks` blocker work, and witness-based checking all reinforce that serious ecosystem tools advance by importing bounded truth and proving claims with stronger evidence when needed. That argues for pilots that can show not just output volume, but **proof quality** and **false-positive / false-negative posture**.
  https://docs.rs/about/rustdoc-json
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- The January 2026 maintenance writeup says maintainership has a multiplicative effect, and the Rust Foundation strategy pairs stable infrastructure, sustainable maintenance, and adoption growth. That argues for pilots being evaluated partly on refresh burden, fixture upkeep, and maintainer load, not only on launch excitement.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
  https://rustfoundation.org/strategic-plan/

Taken together, those signals say the repo needed a note for **pilot-proof discipline**.

## Headline answer
A worthy pilot is not proven by:
- a compelling demo,
- a big local speedup with no control,
- a nice dashboard,
- a clever agent integration,
- or a long list of hypothetical consumers.

A worthy pilot is proven when it can show, on a named lane:
1. **lane reality** — the pilot attacked a real recurring tax rather than a toy scenario;
2. **artifact honesty** — it emitted reviewable artifacts with explicit freshness, authority, and partiality;
3. **decision improvement** — at least one real downstream decision got better, faster, safer, or more auditable;
4. **stewardability** — the pilot can be refreshed and maintained without heroic archaeology.

In archive terms, every serious pilot should leave behind a **scorecard** with:
- the lane and baseline,
- the artifacts produced,
- the downstream decisions exercised,
- the observed deltas,
- the unsupported/stale/failure cases,
- and a final verdict of **graduate / deepen / fold / delay / kill**.

## The four proof families

### 1) Lane proof
Questions:
- What exact lane or scenario was exercised?
- Who is blocked today, and how is the pain observed?
- Is the lane strategically representative or merely convenient?

Required evidence:
- named lane;
- baseline workflow and time/effort/error folklore before the pilot;
- why this lane matters to the target seam;
- and what external assumptions were held constant.

Good pilots:
- use a lane that resembles real Cargo / docs / CI / upgrade / interop usage;
- include enough complexity to stress the seam;
- and say why easier lanes were rejected as insufficient.

Weak pilots:
- only use toy crates;
- only show a greenfield happy path;
- or silently depend on hand-patched fixtures the future steward cannot reproduce.

### 2) Artifact proof
Questions:
- What canonical packs, briefs, receipts, or attachments did the pilot emit?
- Can another human or tool inspect lineage, freshness, and partiality?
- Does the artifact stay distinct from adjacent seams?

Required evidence:
- canonical artifact samples or fixtures;
- validator or schema/lint outputs where relevant;
- explicit import-versus-derived separation;
- explicit unsupported/fallback/stale states.

Good pilots:
- emit one clear artifact family;
- distinguish canonical pack from weaker brief/receipt views;
- and can be diffed or replayed without reverse-engineering screenshots.

Weak pilots:
- rely on hosted UI state;
- mix imported and inferred truths together;
- or only export prose summaries after the fact.

### 3) Decision proof
Questions:
- What real decision became easier or safer?
- Which consumer actually used the artifact?
- What got better: latency, false positives, operator confidence, auditability, or scope control?

Required evidence:
- one or more exercised consumer decisions;
- before/after notes or measurements;
- explicit confidence and residue;
- whether the decision improvement came from substrate truth or from a one-off manual intervention.

Good pilots:
- improve a concrete decision such as rebuild diagnosis, semver boundary review, ingress policy review, crate-choice briefing, or foreign-build handoff;
- and make the improvement legible enough that another team could reproduce the gain.

Weak pilots:
- produce lots of output but leave operators deciding by lore anyway;
- or demonstrate a fancy slice with no proof that anyone trusted it enough to act on it.

### 4) Steward proof
Questions:
- Who could keep this pilot alive?
- What fixtures, corpora, or renewal work does it require?
- Is the maintenance burden proportional to the leverage?

Required evidence:
- named steward model or plausible owner class;
- renewal sources and cadence;
- compatibility promise or deliberate non-promise;
- rough failure/rot modes.

Good pilots:
- can explain what breaks when upstream formats shift;
- can refresh canonical examples without bespoke archaeology;
- and have a believable path from prototype energy to boring maintenance.

Weak pilots:
- require permanent high-touch curation;
- rely on one expert's tacit local knowledge;
- or make no distinction between “works once” and “can be kept working.”

## Required pilot scorecard
Every serious pilot should leave a scorecard with these fields.
The repo-level template lives in `meta/PILOT_SCORECARD_PROTOCOL.md`.

### A) Identity
- seam name;
- ranking class;
- pilot title;
- steward/owner class;
- date and revision.

### B) Lane statement
- exact lane;
- target user/operator;
- why this lane is representative;
- baseline workflow and pain.

### C) Inputs and imports
- what official/maintainer-authored substrate was imported;
- freshness/version caveats;
- what was simulated or manually supplied.

### D) Artifacts emitted
- canonical pack(s);
- brief/receipt/attachment slices;
- validators or lint outputs;
- explicit unsupported/fallback states.

### E) Decisions exercised
- what downstream decision the pilot tried to improve;
- who consumed it;
- what action changed because of the pilot.

### F) Outcome deltas
- latency/time delta where meaningful;
- correctness / false-positive / false-negative posture where meaningful;
- operator-confidence or auditability improvements where numerical metrics are weak;
- and what stayed unimproved.

### G) Steward cost
- fixture renewal work;
- compatibility burden;
- brittle dependencies;
- expected maintenance cadence.

### H) Verdict
- **graduate** — strong enough to widen or become default for its stage;
- **deepen** — seam is right, but proof is incomplete;
- **fold** — useful result, but belongs under another seam;
- **delay** — promising, but blocked by substrate or steward reality;
- **kill** — not worth carrying forward.

## Default exit criteria
A pilot should not graduate just because the builders love it.
The default exit gates are:

### Gate 1 — honest lane gate
The lane must be non-toy and representative enough that failure would have been informative.
If the lane was too small or too hand-curated, the verdict should default to **deepen** or **delay**.

### Gate 2 — artifact gate
The pilot must emit at least one canonical artifact plus one weaker handoff form.
Dashboard-only or transcript-only pilots fail this gate.

### Gate 3 — consumer gate
At least one real downstream decision must have been exercised.
If nobody trusted the output enough to act on it, the pilot has not yet proven its worth.

### Gate 4 — residue gate
The pilot must say what remained unsupported, ambiguous, stale, or manual.
A pilot that cannot say “we don't know” fails this gate.

### Gate 5 — steward gate
Someone must be able to explain how fixtures and examples would be refreshed.
Without this, the default verdict is **delay** or **kill** no matter how impressive the demo looked.

## Seam-specific evaluation guidance
Different seams need different proof emphases.
Use the same outer scorecard, but change what “good proof” means.

### Build-State Evidence
A good pilot should prove that operators can answer:
- what rebuilt,
- why it rebuilt,
- what evidence is trusted,
- and what change or contention pattern is actually worth addressing.

High-value proof:
- rebuild-reason clarity;
- timing/resource attribution;
- fewer folklore-driven debugging loops;
- useful diff/doctor artifacts without a hosted service.

Bad proof:
- “we collected lots of metrics” with no diagnosis improvement;
- or “the build felt faster” with no evidence spine.

### Semantic Context
A good pilot should prove that consumers can distinguish:
- imported semantic facts,
- inferred facts,
- freshness gaps,
- and cross-crate or type-precision limits.

High-value proof:
- better semver/docs/review reasoning than `cargo metadata` or raw docs alone;
- explicit `format_version` handling;
- reusable packs for at least two consumers.

Bad proof:
- one assistant context bundle that cannot justify its claims;
- or silent flattening of canonical docs, rustdoc JSON, and inference output.

### Migration/Public API
A good pilot should prove stronger release or upgrade decisions.

High-value proof:
- witness-backed or otherwise bounded compatibility checks;
- explicit false-positive / false-negative posture;
- ability to represent configuration-sensitive migrations and residue.

Bad proof:
- one green `cargo fix` pass treated as full migration truth;
- or a semver diff that cannot say what was actually verified.

### Package Intake Gateway
A good pilot should prove that ingress truth became more reviewable.

High-value proof:
- route/payload/staging/resolution receipts;
- fail-closed behavior when extraction or route evidence is missing;
- useful handoff to security/policy/review consumers.

Bad proof:
- another malware score or trust dashboard;
- or an installer-side experience with no ingress evidence lineage.

### Adoption Navigation
A good pilot should prove that a concrete project-scoped choice got easier with less tacit knowledge.

High-value proof:
- a named question and lane;
- imported canon/evidence/local-fit packs;
- renewal receipts;
- a better starter-set or crate-choice decision with visible uncertainty.

Bad proof:
- a generic crate ranking page;
- or a recommendation that cannot say why it should stay fresh.

### Native Edge
A good pilot should prove that a real foreign-code or native-provider lane became easier to reason about.

High-value proof:
- explicit subject/boundary/provider/context/handoff separation;
- host-vs-target/toolchain truth;
- clearer foreign-build handoff or adoption review.

Bad proof:
- a one-language demo pretending to prove a cross-language boundary seam;
- or a bridge generator with no boundary review story.

## Anti-goals
This note should not be used to:
- turn the archive into a fake KPI empire;
- require precise numeric metrics where qualitative evidence is more honest;
- force every seam to share the same inner payload;
- or allow a pilot scorecard to replace the seam's own artifact truth.

It exists to force one thing:
**a serious Rust ecosystem pilot should leave behind enough evidence that another careful person could judge whether it is worth widening, deepening, folding, delaying, or killing.**
