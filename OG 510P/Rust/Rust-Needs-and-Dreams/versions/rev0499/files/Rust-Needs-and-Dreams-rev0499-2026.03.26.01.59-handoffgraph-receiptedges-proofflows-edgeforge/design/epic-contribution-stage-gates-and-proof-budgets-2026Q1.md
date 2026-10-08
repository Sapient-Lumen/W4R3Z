## Addendum (rev0478)
For questions about **how a top worthy Rust ecosystem program should widen honestly over time**, **what proof budget it gets at each phase**, **what launch promises are premature**, **when it earns broader claims or upstream asks**, or **how to keep a promising contribution from inflating into platform theater before it has passed smaller gates**, read this note right after:
- `design/epic-contribution-program-charters-2026Q1.md`
- `design/epic-contribution-reference-architectures-2026Q1.md`
- `design/portfolio-pilot-evaluation-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `meta/PROGRAM_CHARTER_PROTOCOL.md`

Interpretation rule:
- this note does **not** promote a new seam;
- it does **not** rerank the broad ladder;
- it exists to answer the missing practical question: **how does a worthy program move from kernel to pilot to widening without over-promising, over-building, or asking upstream for too much too early?**
- keep **Evidence Spine / Build-State Evidence** as the strongest first build;
- keep **Feedback / Debug Acceptance Commons** as the strongest second build;
- keep **Navigation / Defaults / Claims Commons** as the strongest widener;
- keep **Package Intake + Release Boundary Review** as the urgent boundary bridge; and
- keep **Safety-Critical + Institutional Readiness Commons** as the clearest stewarded program seam.

# Design: Epic contribution stage gates and proof budgets (2026 Q1)

## Goal
The archive already has:
- rankings and scorecards for what matters most;
- execution blueprints for many seams;
- macro-program grouping notes;
- reference architectures that say what top programs should contain;
- program charters that say who should own them and where they should live first; and
- pilot-evaluation notes that say how to judge a serious pilot after it has been run.

What it still lacked was one direct answer to a narrower but now unavoidable practical question:

> once a worthy Rust ecosystem program has a real kernel and a plausible owner, **what stages should it pass through, what proof budget does it get at each stage, and what wider promises must it refuse until the smaller gates are cleared?**

This note is the archive's answer to **stage-gate discipline**.
It is not a new ranking note.
It is not a substitute for seam-local execution blueprints.
It exists because the repo is now good enough at imagining strong programs that its next failure mode is obvious: **a good program can still become a bad build if it tries to widen before it has earned the next layer of claims**.

Read with:
- `design/epic-contribution-program-charters-2026Q1.md`
- `design/epic-contribution-reference-architectures-2026Q1.md`
- `design/epic-contribution-program-stack-2026Q1.md`
- `design/practical-epic-contribution-briefs-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/portfolio-pilot-evaluation-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- `meta/PROGRAM_CHARTER_PROTOCOL.md`
- `meta/PILOT_SCORECARD_PROTOCOL.md`

## Why this note is needed now
The current Rust picture strongly suggests that the missing work is not “invent one giant replacement platform”, but **grow a handful of honest programs through bounded stages**.

Official signals point the same way:

- The March 2026 challenges writeup says the hard problems remain practical and recurring: compilation performance, async complexity, crate selection / tacit knowledge, embedded constraints, and safety-critical maturity. That argues for stage-gated programs that reduce real taxes, not theater that widens before it proves a lane.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey still says resource usage and debugging remain meaningful productivity problems while documentation remains canonical even as editor and LLM-mediated learning rises. That argues for artifacts and renewal receipts before broad consumer promises.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo build analysis is explicitly a **prototype** with unstable `cargo report` surfaces, opt-in collection, evolving stored data, and no user-facing stability guarantees during the prototyping phase. That is exactly the kind of substrate that should inform stage-gate budgeting: prove value first, stabilize later.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The Build Dir Layout v2 testing call says many tools still rely on unspecified internals and specifically asks users to test nightly changes and report fallout. That is another sign that worthy work should earn stronger promises only after proving ground truth exists.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- The debugging survey describes an ecosystem-wide acceptance problem across debuggers, operating systems, async cases, visualizers, and Rust expression evaluation. That points toward staged acceptance widening, not a one-shot “we fixed debugging” claim.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- The Rust project-goals process says goals are a contract, and the task-owner guidance says owners are expected to provide regular updates on tracking issues. That reinforces a milestone/stage mentality rather than a vibes-based launch mentality.
  https://rust-lang.github.io/rust-project-goals/2024h2/Project-goal-slate.html
  https://rust-lang.github.io/rust-project-goals/about/owners.html
- The maintenance writeup and the Rust Foundation strategy both reinforce that sustainable maintenance and stable infrastructure are central constraints. That means proof budget must include steward budget, not only technical possibility.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
  https://rustfoundation.org/strategic-plan/

Taken together, those signals say the archive needed a note for **stage gates and proof budgets**.

## Headline answer
A worthy Rust ecosystem program should usually move through **four bounded stages**:

1. **Kernel proof** — prove the artifact family and import seams are real on one lane.
2. **Local decision proof** — prove that one real user/operator decision gets better on named proving grounds.
3. **Cross-lane widening** — widen only after unsupported, partial, and regressed states are explicit and renewable.
4. **Stewarded contract** — ask for broader defaults, upstream surfaces, consortium promises, or institutional backing only after the earlier stages have left durable receipts.

The missing discipline is not “more rigor” in the abstract.
It is a sharper refusal:

> do not let a stage-0 kernel impersonate a stage-3 common good.

## What a stage gate is
A stage gate is not a corporate ceremony.
It is the smallest honest boundary that keeps a worthy program from widening its claims faster than its proof.

Every stage gate should answer five things:
- what the program is allowed to promise now;
- what artifact family it must emit now;
- which proving grounds it must survive now;
- what it is **not** yet allowed to ask from upstream, consumers, or institutions;
- and what evidence earns the next stage.

## The four-stage model

### Stage 0 — kernel proof
**Question:** is there a real kernel here, or only a smart summary of pain?

Allowed promises:
- one narrow lane;
- one canonical artifact family or bounded kernel;
- explicit partiality and unsupported states;
- no claim of broad ecosystem coverage.

Required assets:
- a named kernel artifact family;
- declared imports;
- one doctor/checker path;
- one or two proving-ground fixtures;
- one refusal clause saying what seductive larger build is out of scope.

Refuse at this stage:
- universal portals;
- ecosystem-wide ranking claims;
- hosted control-plane ambitions;
- early standardization pressure.

Promotion rule:
- advance only if the kernel survives one real lane and leaves reviewable artifacts that another maintainer could inspect.

### Stage 1 — local decision proof
**Question:** does this kernel improve one real developer/operator decision rather than merely producing output?

Allowed promises:
- one real decision becomes faster, safer, or more auditable;
- one owner class can plausibly run the pilot;
- one local proving-ground bundle can be rerun.

Required assets:
- pilot scorecard;
- before/after lane statement;
- decision receipts;
- explicit residue and manual steps;
- first steward-cost estimate.

Refuse at this stage:
- broad defaults;
- “official” ecosystem guidance claims;
- universal compatibility claims;
- large upstream asks.

Promotion rule:
- advance only if the pilot improved a real decision and left enough residue reporting that failures are legible, not hidden.

### Stage 2 — cross-lane widening
**Question:** does this work remain honest when it widens beyond its first lucky lane?

Allowed promises:
- a small lane family rather than one bespoke case;
- explicit accepted / partial / unsupported / regressed states;
- bounded consumer exports;
- renewal receipts and drift budgets.

Required assets:
- at least two distinct proving contexts or tuples;
- capability/acceptance posture if cross-tool or cross-platform;
- renewal plan;
- failure ledger and fold/kill criteria.

Refuse at this stage:
- claims of default status for the whole ecosystem;
- hosted authority portals;
- institution-grade endorsements without steward backing;
- language/toolchain changes justified only by anticipated future value.

Promotion rule:
- advance only if widening still leaves explicit unsupported states and a believable renewal story.

### Stage 3 — stewarded contract
**Question:** has the work earned broader social or technical commitments?

Allowed promises:
- conservative default or recommended posture for a bounded audience;
- narrow upstream asks with clear imported evidence;
- Foundation/lab/consortium support asks where appropriate;
- long-horizon maintenance commitments.

Required assets:
- durable owner shape;
- renewal cadence;
- narrow and reviewable upstream asks;
- governance or succession story where the seam requires it;
- explicit contract limits.

Refuse even here:
- pretending one artifact settles all adjacent truths;
- converting a stewarded commons into a trust-score or winner table;
- using institutional support as a substitute for artifact honesty.

## The five proof budgets
A stage gate should also cap the **budget** each program is allowed to spend at that phase.

### 1) Import budget
How many upstream/internal surfaces may the program depend on before it can remain reviewable?

Default rule:
- spend lightly at Stage 0;
- widen imports only when adapter lossiness is named;
- do not quietly depend on unstable internals without receipts.

### 2) Promise budget
How broad a claim can the program honestly make now?

Default rule:
- a stronger artifact may still deserve a smaller promise;
- do not turn one working lane into ecosystem-wide prose.

### 3) Consumer budget
How many consumer views may the program serve now?

Default rule:
- one or two consumers early;
- broader docs/support/editor/assistant exports only after the canonical pack is stable enough to prevent summary drift.

### 4) Steward budget
How much upkeep is the program allowed to assume now?

Default rule:
- if the first stage already requires constant manual curation, the shape is probably wrong;
- if the second stage already needs consortium-scale operations, the entry stage was mis-scoped.

### 5) Upstream-ask budget
How much project-team or institutional attention has the program earned?

Default rule:
- ask upstream for narrow enabling surfaces only after the companion kernel proves why the ask matters;
- ask institutions for continuity only after the work shows recurring public leverage and believable stewardship.

## Stage-gate guidance for the top macro-programs

### 1) Evidence Spine / Build-State Evidence
**Stage 0**
- Ship a local-first `build-state-pack/v0`, one doctor path, and one diff/explain flow.
- Import Cargo-native surfaces before scraping internal directories.
- Refuse cache empires, hosted dashboards, or universal build control stories.

**Stage 1 gate**
- One real workspace can answer “what rebuilt, why, and where did time go?” after the fact.
- The pack is inspectable enough that another maintainer can rerun and audit it.

**Stage 2**
- Add cross-workspace or CI/local comparison only after explicit partiality is visible.
- Widen to editor/build contention and cache-layout facts only with lineage receipts.

**Stage 3**
- Only then seek narrower upstream asks around import surfaces, report stability, or better artifact boundaries.

### 2) Feedback / Debug Acceptance Commons
**Stage 0**
- Start with one session-pack family, one debugger tuple, and explicit unsupported states.
- Refuse “just bless this debugger” or IDE-only magic.

**Stage 1 gate**
- One maintainer/operator decision gets easier: issue triage, session handoff, or debugger-capability review.

**Stage 2**
- Widen only through explicit tuple acceptance: debugger × OS × runtime × toolchain.
- Make async and visualizer posture visible before claiming broad debug readiness.

**Stage 3**
- Only then justify cross-upstream coordination, acceptance working-group commitments, or documentation-default changes.

### 3) Navigation / Defaults / Claims Commons
**Stage 0**
- Start with a very small lane-default corpus and imported evidence.
- Refuse winner tables, trust scores, or broad “best crates” rhetoric.

**Stage 1 gate**
- One real project selection or migration decision becomes easier and more auditable.

**Stage 2**
- Widen only after renewal receipts and drift budgets exist.
- Every widened recommendation must keep unknown/manual-review-required posture explicit.

**Stage 3**
- Only then seek broader editorial/default status for bounded audiences.

### 4) Package Intake + Release Boundary Review
**Stage 0**
- Start with extraction, quarantine, waiver, and replay receipts on one local route.
- Refuse vague reputation layers or trust-score dashboards.

**Stage 1 gate**
- One operator can review ingress or release-boundary truth faster and with fewer silent assumptions.

**Stage 2**
- Widen to alternate registries, artifact attachments, or incident drills only after route identity and residue are explicit.

**Stage 3**
- Only then justify policy hooks, shared operator practices, or broader release-boundary commons.

### 5) Safety-Critical + Institutional Readiness Commons
**Stage 0**
- Start with one readiness profile, one evidence recipe family, and explicit non-certification posture.
- Refuse “one crate solves certification” fantasies.

**Stage 1 gate**
- One institution-shaped user can use the recipe/checklist/profile to make a real readiness or evidence decision.

**Stage 2**
- Widen only with plural exemplars, lifecycle guidance, dependency-lifecycle playbooks, and long-horizon evidence discipline.

**Stage 3**
- Only then justify consortium-style stewardship, stronger institutional asks, or shared readiness contracts.

## Fold, delay, and kill rules
A worthy program should **fold** when the kernel is useful but obviously belongs under a stronger parent seam.
It should **delay** when current substrate motion is too active to promise a stable import story.
It should **kill** when the first honest stage already demands more upkeep, authority, or scope than the program's leverage can justify.

Practical red flags:
- Stage 0 already needs a hosted service to look convincing.
- Stage 1 cannot point to a changed decision.
- Stage 2 can only widen by hiding unsupported states.
- Stage 3 depends on institutional blessing but still lacks durable artifacts.

## Default interpretation for future revisions
Until stronger evidence arrives:
- the broad ladder is unchanged;
- the missing new layer is **stage-gate / proof-budget discipline**, not another ranking rewrite;
- future “make it practical” revisions should usually say **current stage**, **next gate**, **proof budget**, and **premature promises to refuse**;
- **Evidence Spine / Build-State Evidence** remains the clearest first program because it has the cleanest stage-0 and stage-1 story;
- **Feedback / Debug Acceptance Commons** remains the clearest second program because it is the strongest example of stage-2 acceptance widening;
- **Navigation / Defaults / Claims Commons** remains the clearest widener but should widen the slowest because recommendation claims are cheap to state and expensive to renew;
- **Package Intake + Release Boundary Review** remains the urgent boundary bridge and should be evaluated harshly on route truth and incident realism; and
- **Safety-Critical + Institutional Readiness Commons** remains the clearest stewarded long-horizon program and should be allowed the strictest stage discipline of all.
