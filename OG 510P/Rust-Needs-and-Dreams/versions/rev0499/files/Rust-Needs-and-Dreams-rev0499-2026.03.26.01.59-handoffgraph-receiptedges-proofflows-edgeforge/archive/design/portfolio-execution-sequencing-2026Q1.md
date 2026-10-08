## Addendum (rev0465)
For questions about **what Stage 0 itself should actually build before Stage 1 widens into Build-State Evidence**, read `design/shared-spine-execution-blueprint-2026Q1.md` before this note.

Interpretation rule:
- sequencing still owns **stage order and stage gates**;
- the new note owns the **concrete stage-0 artifact family, validator/fixture shape, and assistant-handoff discipline**;
- and future revisions should now stop leaving Stage 0 as only a sentence in a sequence.


## Addendum (rev0459)
For questions about why certain seams are sequenced first or later even when several are already strong, read `design/epic-contribution-scorecards-2026Q1.md` before this note.

Interpretation rule:
- scorecards own comparative priority type;
- sequencing still owns staged build order and stage gates.

## Addendum (rev0427)
For questions about **what evidence a stage-appropriate pilot must leave behind before the next stage should widen or harden around it**, read `design/portfolio-pilot-evaluation-2026Q1.md` and `meta/PILOT_SCORECARD_PROTOCOL.md` after this note.

Interpretation rule:
- sequencing still owns **what comes first**;
- the new note owns **what counts as enough proof to graduate, stall, deepen, fold, delay, or kill a pilot within that sequence**;
- and the repo should now treat stage progression as requiring a visible pilot scorecard rather than only a persuasive demo or launch post.


## Addendum (rev0426)
For questions about **whether a fresh candidate even deserves a place in the staged portfolio before arguing about build order**, read `design/portfolio-selection-rubric-2026Q1.md` first.

Interpretation rule:
- sequencing assumes the candidate already passed selection;
- the new note owns proposal triage, fold/kill criteria, and candidate-card minimums;
- this note still owns build order, stage gates, and stewardship timing;
- and recommendation/frontier widenings should still not outrun the evidence spine just because a new idea sounds attractive.

## Addendum (rev0425)
For questions about **what order to actually build, fund, or staff the archive's strongest seams**, read this note right after `design/worthy-contribution-shortlist-2026Q1.md` and `design/portfolio-artifact-conventions-2026Q1.md`.

Interpretation rule:
- this note does **not** change the broad ladder;
- it does **not** promote a new frontier;
- it exists to answer the missing practical question: **what should a serious lab, funder, or maintainer group build first, second, and only later?**
- keep **Build-State Evidence** as the strongest one-project answer overall;
- keep the strongest multi-project answer as **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- keep **Adoption Navigation** and **Native Edge** as later consumers/frontiers that become stronger once the evidence spine exists;
- and require every staged contribution to have an explicit maintenance/stewardship story rather than only a launch story.

# Design: Portfolio execution sequencing (2026 Q1)

## Goal
The archive now has strong seam-level blueprints and a thin shared grammar.
What it still lacked was a canonical answer to a very practical question:

> in what order should a serious team, lab, or funder actually build the strongest Rust ecosystem contributions, and what gates should each stage satisfy before the next one begins?

This note is not another ranking note.
It is the archive's answer to **sequencing, staffing, and funding shape**.

Read with:
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/portfolio-artifact-conventions-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/semantic-context-execution-blueprint-2026Q1.md`
- `design/migration-public-api-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/native-edge-execution-blueprint-2026Q1.md`

## Why this note is needed now
The repo already knew which seams were strongest.
What it still did **not** say clearly enough was how a real builder should stage them.
That matters more now because the official ecosystem signals are unusually specific about both **what hurts** and **how work gets adopted**:

- Rust's March 2026 challenges writeup says the recurring pain is not just syntax learning; it includes **compile/resource pain**, **choice paralysis / tacit knowledge**, and domain-specific maturity gaps. That argues for sequencing around broad pain first rather than flashy edge tooling.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says the challenge pattern is fairly stable, docs remain canonical, and machine-mediated/editor-mediated learning is rising. That argues for reviewable evidence and stable handoff layers before assistant-heavy consumer surfaces.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2026 goals overview says goals are proposed by contributors and accepted by Rust teams; goals work best when a contributor is ready to do the work and a team can champion it. That argues for contributions that can start as bounded companion layers with realistic maintainership, not giant "the project should solve everything" demands.
  https://rust-lang.github.io/rust-project-goals/2026/
- Rust's 2026 flagships bundle **Secure your supply chain**, **Building blocks**, and roadmap/application-area work like **cross-language interop** and **safety-critical**. That argues for a sequence that starts from shared evidence/control surfaces and only later broadens into specialist consumers.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The January 2026 program-management update says roadmaps/application areas are intended to help **focus industry funding** and that the project hired a second program manager once funding clarified. That argues for staging contributions in ways that sponsors, champions, and maintainers can actually coordinate.
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- The January 2026 maintenance writeup says maintenance includes triage, CI failures, regressions, docs, dependency updates, and review/unblocking work, and describes maintainership as having a **multiplicative effect**. The Rust Foundation's 2026–2028 strategy likewise pairs stable infrastructure, sustainable maintenance, and adoption growth. That argues against sequencing that maximizes launch surface while ignoring upkeep.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
  https://rustfoundation.org/strategic-plan/
- Cargo build-analysis / build-dir-layout work, docs.rs rustdoc JSON, `cargo-semver-checks` integration work, crates.io's newer trust/security surfaces, and the March 2026 Cargo extraction advisory all say important substrate is becoming more machine-usable **now**. That argues for sequencing around the seams whose official inputs are ripest, rather than starting with the most speculative consumer.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
  https://docs.rs/about/rustdoc-json
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/

Taken together, those signals say the repo needed a note for **staging discipline**.

## Headline answer
The right build order is **not** “start with the most exciting interface”.
It is:

1. **establish the common honesty/lineage spine**;
2. **ship the broadest evidence win first**;
3. **add the hidden multiplier that improves multiple later seams**;
4. **add bounded release/ingress bridges that consume the same evidence grammar**;
5. **only then widen into recommendation and specialist consumers**.

In archive terms:

> first build **Build-State Evidence**,
> then add **Semantic Context**,
> then deepen the same portfolio with **Migration/Public API** and **Package Intake**,
> and only then widen into **Adoption Navigation** and **Native Edge** as heavier downstream/frontier consumers.

That is the strongest practical answer for theory, execution, and maintenance economics.

## The staged program

### Stage 0 — minimum shared spine before new surface area
Before widening any seam, require a thin cross-portfolio spine:
- the shared envelope/lineage rules from `design/portfolio-artifact-conventions-2026Q1.md`;
- a validator/linter for required honesty fields;
- fixture packs that prove the grammar across at least the core four-seam portfolio;
- explicit brief/handoff artifacts that remain weaker than the canonical pack;
- and a repo-visible rule that assistant summaries never overwrite canonical evidence.

Why first:
without this, later seams become six incompatible mini-languages and the repo forgets what is import truth versus derived truth.

What counts as enough:
- envelope fields are stable enough to lint;
- canonical pack vs brief vs receipt is visibly separate;
- compatibility/freshness/partiality are explicit;
- and at least one non-human consumer can ingest the output without reverse-engineering prose.

### Stage 1 — Build-State Evidence as the first serious build
If one team can only start one high-leverage contribution, it should still start here.

Why first:
- the pain is broad;
- Cargo is already moving in this direction;
- the artifacts improve local loops, CI, editors, and large workspaces at once;
- and the seam forces the discipline of observed/imported/derived/hypothetical truth separation.

What the first funded tranche should include:
- canonical build-state pack + explain/diff/doctor flows;
- at least one pilot lane for editor-vs-build contention;
- at least one lane for rebuild reason + timing/resource evidence;
- lineage receipts tied to imported Cargo-native evidence;
- and explicit unsupported/partial/fallback outcomes.

Stage-1 gate to pass before Stage 2:
- builders can answer "what rebuilt, why, and what evidence do we trust?" without terminal-log folklore;
- the project has at least one maintainer/steward who owns compatibility and fixture refresh;
- and the output is already useful without a hosted service.

### Stage 2 — Semantic Context as the first multiplier
Do **not** start here if Stage 1 has not proven its review/evidence discipline.
But once Stage 1 exists, Semantic Context is the next best multiplier.

Why second:
- it improves semver, docs, edit, CI, and assistant consumers at once;
- docs.rs rustdoc JSON and compiler-facing publication work now make a thinner import lane realistic;
- and it helps later release/upgrade and recommendation work stay grounded.

What the first funded tranche should include:
- exact subject capture;
- ranked input lanes with freshness and completeness truth;
- bounded query/result artifacts;
- comparison/handoff artifacts that never pretend to be the canonical source;
- and at least one proof lane that shows better downstream semver or docs reasoning than `cargo metadata`-level approximations alone.

Stage-2 gate to pass before Stage 3:
- consumers can tell which semantic facts were imported versus inferred;
- lane freshness and format-version mismatches are explicit;
- and at least two downstream consumers reuse the same semantic pack rather than inventing one-off side channels.

### Stage 3A — Migration/Public API as the release/upgrade bridge
This should be the first boundary-oriented portfolio extension after the evidence spine exists.

Why now:
- by this point the program has reusable grammar, build evidence, and semantic imports;
- the release/upgrade seam benefits directly from those prior layers;
- and the official project already treats public API dependency control and breaking-change detection as active supply-chain work.

What the tranche should include:
- public-boundary and upgrade-program bridge artifacts;
- diff + verify receipts with explicit proof strength;
- witness-backed stronger checks where available;
- import truth for docs/support/downstream evidence;
- and a lane that proves value on an edition/configuration-sensitive migration rather than only a toy semver diff.

### Stage 3B — Package Intake Gateway as the operational bridge
This belongs in the same broad stage as Migration/Public API, even if a specific advisory makes it feel more urgent in a given month.

Why now instead of first:
- the seam is operationally important, but it becomes much stronger once the portfolio already knows how to express route/payload/staging/resolution/handoff truth cleanly;
- and starting with ingress panic alone risks producing another security dashboard instead of a review layer.

What the tranche should include:
- route and payload truth capture;
- staging/extraction and resolution receipts;
- alternate-registry / mirror posture made explicit where possible;
- handoff artifacts for policy/review consumers;
- and fail-closed behavior whenever route or extraction evidence is missing or stale.

Stage-3 gate before Stage 4:
- the core four seams reuse the same thin outer grammar;
- at least one team outside the builders consumes the artifacts in review or CI;
- and maintenance overhead is visible enough to budget rather than guessed away.

### Stage 4 — Adoption Navigation as the first consumer-facing widening
Only after the evidence spine and boundary bridges exist should the program widen into project-scoped recommendations.

Why later:
- recommendation without evidence discipline becomes another curated canon empire;
- the newer crates.io/docs.rs/security signals become far more useful once the program already has lineaged imports and freshness rules;
- and recommendation is easier to keep honest when it imports real packs from earlier stages.

What the tranche should include:
- question and lane records;
- imported canon/evidence/local-fit packs;
- bounded brief/handoff artifacts;
- renewal receipts;
- and explicit uncertainty/manual-review posture.

### Stage 5 — Native Edge as the specialist frontier widening
Native Edge remains strategically real, but it is usually **not** the right first program build unless a sponsor has a very specific interop mandate.

Why later in the generic sequence:
- the frontier is specialist and integration-heavy;
- it benefits from the same lineage, diff, verify, and handoff discipline built earlier;
- and real-world success depends heavily on existing adoption context, toolchain/provider choices, and foreign-build handoff posture.

What the tranche should include:
- subject/boundary/provider/context/handoff separation;
- at least one concrete lane for a large existing foreign codebase or build-system handoff;
- explicit host-vs-target/toolchain truth;
- and bounded conclusions rather than universal interop promises.

## Portfolio staffing shapes

### One-team answer
If one serious team is available, it should build:
1. shared spine,
2. Build-State Evidence,
3. then the thinnest Semantic Context lane.

Do **not** ask one team to start all four core seams simultaneously.
That is how portfolios turn into half-maintained empires.

### Two-team answer
If two serious teams are available:
- Team A owns **Build-State Evidence** and the shared spine.
- Team B joins on **Semantic Context** once Stage 1 gates are passing.

Only after those two stabilize should the teams split into:
- **Migration/Public API** and/or
- **Package Intake Gateway**.

### Sponsor / funder answer
If funding is available but contributor bandwidth is scarce, prefer:
- maintainership and compatibility funding for the shared spine and Stage 1 artifacts;
- named champions/maintainers for Stage 2;
- and stage-gated follow-on funding for Stages 3–5.

Do **not** fund a recommendation site, assistant layer, or hosted portal first.
Those surfaces consume attention faster than they generate trustworthy substrate.

## Funding and review gates
A contribution should not advance stages just because the demo looks good.
Require these gates:

### Gate A — substrate gate
The stage must import a real official or ecosystem substrate that already exists or is on an accepted path.
No stage should depend entirely on reverse-engineering private tool internals.

### Gate B — artifact gate
The stage must emit at least one canonical pack and one weaker brief/receipt.
A dashboard-only stage fails this gate.

### Gate C — partiality gate
The stage must be able to say unsupported, stale, inconclusive, or fallback-only.
A best-effort blob fails this gate.

### Gate D — stewardship gate
A named maintainer/steward or maintainer budget must exist.
Launch without upkeep is not a pass.

### Gate E — adoption gate
At least one real downstream consumer must import the artifact family in review, CI, docs, or support.
Not just screenshots.

### Gate F — compatibility gate
If schema/toolchain/format changes materially affect trust, the stage must fail closed or record the mismatch explicitly.

## What to avoid
Do **not** start the program with:
- a universal hosted platform;
- an assistant-first canon or recommendation engine;
- a mega-schema that attempts to unify all payload semantics;
- a security-score or crate-score empire;
- or a specialist frontier whose value depends on substrate that the program has not yet built.

Those moves look exciting and usually age badly.

## Why this sequencing is better than the tempting alternatives

### Better than “start with Adoption Navigation”
Because recommendation consumes freshness, maintenance, route, and evidence truth faster than it can create them.

### Better than “start with Native Edge”
Because Native Edge is strategically real but sponsor-specific; it is not the best generic first build unless the sponsor already lives at the native boundary.

### Better than “start with Package Intake because security is urgent”
Because urgency alone can produce panic tooling.
The review layer gets better once the portfolio already knows how to express lineage, partiality, and bounded handoff.

### Better than “start with Semantic Context because everything will need it”
Because hidden multipliers are easiest to overbuild.
Starting with Build-State Evidence forces a user-visible, bounded artifact discipline first.

## Repo consequence
Treat this note as **deepening + hygiene**, not promotion.

Future revisions that claim to improve the portfolio should now say explicitly:
- which stage they belong to;
- which gate they are trying to pass;
- whether they are evidence spine work, boundary bridge work, or consumer/frontier widening;
- and what stewardship model keeps the result alive after launch.

If a revision cannot answer those questions, it is probably adding surface area faster than the archive can honestly maintain.
