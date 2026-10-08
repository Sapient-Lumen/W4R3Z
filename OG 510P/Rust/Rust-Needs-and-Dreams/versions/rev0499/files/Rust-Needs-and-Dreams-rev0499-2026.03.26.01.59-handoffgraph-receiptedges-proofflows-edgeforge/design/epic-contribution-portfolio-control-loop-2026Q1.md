# Design: Epic contribution portfolio control loop (2026 Q1)

## Goal
The archive already has:
- a broad ranking of what matters most;
- live packets and dossiers for current posture;
- bounded kernels, slices, contracts, witnesses, fixtures, and schemas for the first serious builds;
- buildout order and shared operating grammar;
- residency / graduation guidance;
- program charters, stage gates, and standard review packets.

What it still lacked was one practical answer to a different question:

> once the repo knows **what is worthy**, **how it should look**, **where it should live**, and **how it should widen**, what recurring control loop should keep those judgments alive without either freezing them forever or rewriting them every time a new blog post appears?

This note is the archive's answer to that question.
It is a **control-loop / renewal-cadence / decision-governor** pass.
It does **not** rerank the broad ladder.
It does **not** promote a new frontier.
It exists so the repo can keep maturing the strongest contributions as living programs rather than as one-off persuasive essays.

Read with:
- `design/epic-contribution-live-ecosystem-refresh-2026Q1.md`
- `design/epic-contribution-worthy-repo-buildout-2026Q1.md`
- `design/epic-contribution-operating-surface-2026Q1.md`
- `design/epic-contribution-stewardship-and-graduation-map-2026Q1.md`
- `design/epic-contribution-program-charters-2026Q1.md`
- `design/epic-contribution-stage-gates-and-proof-budgets-2026Q1.md`
- `design/epic-contribution-review-packets-2026Q1.md`
- `design/epic-contribution-review-packet-specimens-2026Q1.md`
- `design/portfolio-evidence-renewal-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/portfolio-pilot-evaluation-2026Q1.md`
- `meta/PORTFOLIO_CONTROL_LOOP_PROTOCOL.md`
- `meta/LIVE_ECOSYSTEM_REFRESH_PROTOCOL.md`
- `meta/REVISION_OPERATING_PROTOCOL.md`
- `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`
- `meta/AMNESIA_RESISTORS.md`

## Why this pass is merited now
Current official Rust signals keep pointing at the same meta-truth: strong work only stays strong when it is renewed on the cadence that matches its real drift.

Signals that matter here:
- The January 2026 program-management update says goals now run on a year-long cycle with feedback in February, an RFC in March, and implementation season from April to December; it also says goals sit inside roadmaps and application areas meant to focus funding. That is a direct reminder that serious Rust work already lives inside explicit cadence, capacity, and owner loops rather than timeless wishlists.
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- The 2026 project-goals overview and task-owner guidance are even more explicit: goals are a contract among contributors and teams; owners are expected to provide regular progress updates; and goals without owners are only provisional. The archive needed a matching rule for worthy ecosystem programs.
  https://rust-lang.github.io/rust-project-goals/2026/
  https://rust-lang.github.io/rust-project-goals/about/owners.html
- The maintenance writeup says maintenance work is diverse, often invisible, and multiplicative. That is exactly why the repo should not let a one-time launch artifact impersonate a durable program state.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- The Rust Foundation's 2026–2028 strategy centers stable infrastructure, sustainable maintainer support, and responsible adoption. That means the strongest contributions should be reviewed not just for technical promise, but also for whether their renewal burden matches the kind of host they need.
  https://rustfoundation.org/strategic-plan/
- The Rust Innovation Lab is a concrete new hosting mode: governance/legal/administrative support can move under the Foundation while technical direction remains with maintainers. That is a good reason not to flatten all maturation paths into core-vs-external rhetoric.
  https://blog.rust-lang.org/2025/09/03/welcoming-the-rust-innovation-lab/
- Cargo's external-tools chapter still says the stable extension model is structured outputs plus custom subcommands, while `cargo clippy` remains the clearest example of a toolchain-distributed optional component. Those are different residency classes with different refresh rhythms.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
  https://doc.rust-lang.org/cargo/commands/cargo-clippy.html
- Cargo build analysis is still explicitly a prototype with unstable `cargo report` surfaces and evolving recorded facts. That is a strong reminder that substrate maturity and program maturity must be reviewed on different loops.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html

Taken together, those signals say the repo needed one more explicit layer:
**a portfolio control loop that keeps hot substrate drift, monthly decision packets, quarterly stewardship review, slow canon refresh, and per-revision hygiene visibly separate.**

## Headline answer
A worthy Rust ecosystem repo should now run **five distinct loops**, not one:

1. **Hot substrate watch** — for fast-moving service behavior, security incidents, and unstable upstream surfaces.
2. **Decision-packet loop** — for current pilot/program posture and requested verdict changes.
3. **Charter / stewardship loop** — for owner shape, host shape, funding mode, graduation path, and kill/fold decisions.
4. **Canon / territory loop** — for slower changes to the broad ladder, frontier posture, and worthiness map.
5. **Archive hygiene loop** — for continuity rails, fileset truth, source-atlas coverage, and doctor/check outputs.

The key discipline is:

> do not rerank the territory every time a hot signal moves, and do not let a fast-moving seam wait for a grand annual rewrite before its packet, charter, or evidence posture changes.

## The five-loop model

### 1) Hot substrate watch
This loop owns facts that can change quickly and materially alter a seam's practical truth.

Typical triggers:
- Cargo / rustc / docs.rs / crates.io behavior changes;
- security advisories or operator-facing policy changes;
- unstable-substrate progress or regressions;
- route changes that can break imports, expectations, or claims.

Expected outputs:
- research-log entry;
- source-atlas refresh when a new source becomes recurrently authoritative;
- narrowed or refreshed packet fields where needed;
- explicit hot-lane receipt saying what changed and what did **not**.

What it may change:
- current packet posture;
- caveats, refusals, or proving-ground assumptions;
- narrow implementation guidance.

What it should not change casually:
- the broad ranking;
- the canonical home of a contribution;
- the whole program charter.

### 2) Decision-packet loop
This loop owns current requested verdicts for the strongest candidates.

Cadence:
- typically monthly, or sooner when a hot substrate change clearly changes one top candidate's current posture.

Expected outputs:
- updated or reissued review packet;
- explicit `advance` / `deepen` / `hold` / `fold` / `kill` request;
- scorecard delta and proof-budget note;
- specimen refresh only if packet shape, not just content, had drifted.

What it may change:
- whether a candidate should advance now, deepen, or wait;
- which proving grounds are next;
- what proof is still missing.

What it should not change casually:
- the program's broad residency class;
- the broad territory map;
- the operator grammar for the whole family.

### 3) Charter / stewardship loop
This loop owns the question of who carries the burden and where the work should actually live.

Cadence:
- usually quarterly, or when a host/funding/governance change materially changes the credible home for a seam.

Expected outputs:
- charter refresh;
- stewardship/graduation update;
- host-shape or funding-lane delta;
- explicit fold / widen / kill rule if the old owner shape no longer fits.

What it may change:
- companion vs service vs optional-component vs consortium/program posture;
- proving-partner expectations;
- maintenance envelope;
- narrow upstream ask timing.

What it should not change casually:
- the broad worthiness of the seam itself;
- hot operational caveats that belong in packets or receipts.

### 4) Canon / territory loop
This loop owns the broad map.

Cadence:
- semiannual by default, or earlier only when multiple independent official signals show that the old strategic reading is materially wrong.

Expected outputs:
- ladder/frontier refresh if truly warranted;
- sharpened strategic reading;
- explicit statement of what remained unchanged.

What it may change:
- broad rank order;
- whether a seam is frontier, core, or folded;
- large-scale strategic interpretation.

What it should not change casually:
- packet-level requested verdicts that belong to the monthly loop;
- one-off host decisions that belong to the quarterly loop.

### 5) Archive hygiene loop
This loop owns continuity rather than judgment.

Cadence:
- every revision.

Expected outputs:
- refreshed front-door files;
- refreshed latest-fileset note;
- refreshed continuity and amnesia rails if the repo learned a new failure mode;
- source-atlas updates when repeated sources changed practical meaning;
- manifest regeneration;
- hygiene/doctor runs.

What it may change:
- routing, continuity, and anti-drift machinery.

What it should not change casually:
- strategic rank, packets, or charters without corresponding substantive notes.

## Control-loop mapping for the current top band

### Build-State Evidence
Primary loops:
- **hot substrate watch** for Cargo build-analysis/report, build-dir-layout, and related build-fact surfaces;
- **monthly decision-packet loop** for whether the evidence spine is ready to advance or should deepen on proving grounds;
- **quarterly charter loop** for companion-first vs substrate-ask balance.

Theory:
- this seam depends on fast-moving upstream facts, so it cannot wait for slow canon review.

Practice:
- treat new Cargo evidence/report changes as packet-changing first, charter-changing second, and canon-changing only rarely.

### Package Intake + Release Boundary Review
Primary loops:
- **hot substrate watch** for advisories, crates.io policy/behavior changes, trusted-publishing shifts, and registry route changes;
- **monthly decision-packet loop** for operator-path readiness;
- **quarterly charter loop** for split-home service/import/product boundaries.

Theory:
- this seam is boundary- and incident-shaped, so it has the fastest operator loop in the portfolio.

Practice:
- do not let one incident rerank the seam upward or downward broadly; let it change route receipts, caveats, and packet posture first.

### Feedback / Debug Acceptance Commons
Primary loops:
- **monthly decision-packet loop** for debugger-tuple acceptance widening;
- **quarterly charter loop** for partner tuples, steward burden, and widening pace;
- **canon loop** only when acceptance proof changes the broad strategic read.

Theory:
- this seam moves slower than security/service truth but faster than broad canon because tuple acceptance accumulates over releases and proofs.

Practice:
- widen by tuple family, not by vibes; keep `partial`, `unsupported`, and `regressed` visible on every loop.

### Safety-Critical + Institutional Readiness Commons
Primary loops:
- **quarterly charter / stewardship loop** as the main loop;
- **hot watch** only for stale cards, spec/readiness incidents, or major host/steward changes;
- **canon loop** rarely.

Theory:
- this is the clearest consortium/program seam, so steward shape matters more than day-to-day product motion.

Practice:
- prefer slow card/pack renewal and explicit stale-state receipts over false real-time dashboards.

### Compatibility Claims
Primary loops:
- **monthly decision-packet loop** for bounded claims and drift receipts;
- **hot watch** for release-, target-, or service-driven contradictions;
- **quarterly charter loop** only when claim ownership or distribution shape changes.

### Adoption Navigation + Ecosystem Atlas
Primary loops:
- **quarterly charter / renewal loop** for defaults corpus burden;
- **canon loop** for broad strategic posture;
- hot watch only when a source or default card becomes actively misleading.

Theory:
- this seam remains strategically huge but renewal-heavy, so its control loop should be conservative.

Practice:
- refresh default cards and canon sources before expanding breadth.

## What each loop should emit
Every loop should leave one dominant artifact family:
- hot substrate watch → **renewal receipt / research-log delta**
- decision-packet loop → **review packet / scorecard delta**
- charter loop → **charter or stewardship delta**
- canon loop → **front-door/canon refresh note**
- archive hygiene loop → **fileset/continuity/doctor refresh**

If a revision touches multiple loops, it should say so explicitly.
The archive should stop pretending one artifact can do all five jobs.

## Wrong control-loop shapes to refuse
1. **One-loop theater** — one monthly or annual memo that tries to stand in for packet review, charter review, canon refresh, and hygiene all at once.
2. **Rerank-on-every-post behavior** — every new official blog or goal update is treated as a ladder rewrite.
3. **Stale-packet complacency** — the broad seam judgment still sounds right, so current packet posture is left to rot.
4. **Dashboard fantasy** — fast-moving hosted status boards are treated as a substitute for steward review and explicit packet/charter deltas.
5. **LLM-smooth continuity loss** — later summaries repeat the broad map but quietly forget which loop a given change was actually supposed to affect.

## Archive decision
Keep the broad ladder unchanged.
Add one explicit control-loop layer so future continuations can answer:
- what changed **now**,
- what deserves a **packet** change,
- what deserves a **charter/stewardship** change,
- what deserves a **canon** change,
- and what is only a **hygiene** change.

The immediate practical rule is:
- keep **Build-State Evidence** first overall;
- keep **Package Intake + Release Boundary Review** second overall;
- keep **Feedback / Debug Acceptance Commons** and **Safety-Critical + Institutional Readiness Commons** as the strongest deepen lanes;
- but now govern them with different loops instead of one blended “latest thinking” pass.
