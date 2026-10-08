# Design: Epic contribution compounding map (2026Q1)

## Goal
The archive now has:
- a broad ladder for what matters most;
- comparative scorecards for worthy contributions;
- a delivery matrix for what they should ship;
- an incubation map for where they should begin;
- a proof-burden map for what they must prove;
- a bet-sizing map for what kind of team or capital band they honestly need; and
- a sequencing note for what a serious program should stage first.

What it still lacked was one sharper cross-seam answer to a different practical question:

> once we know several contributions are worthy, **which ones actually compound into later ones**? Which bets create reusable evidence, contracts, or receipts that make later bets more honest, and which bets should be refused when somebody tries to build them “front door first” before their upstream unlocks exist?

This note is the archive's answer to that question.
It does **not** rerank the broad ladder.
It does **not** replace the sequencing note.
It does **not** promote a new frontier.
It explains which worthy contributions are **unlock bets**, which are **contract multipliers**, which are **consumer wideners**, which are **program seams that should come later**, and which upstream efforts are best read as **substrate unlocks rather than public-platform epics**.

Read with:
- `design/epic-contribution-bet-sizing-map-2026Q1.md`
- `design/epic-contribution-proof-burden-map-2026Q1.md`
- `design/epic-contribution-incubation-map-2026Q1.md`
- `design/epic-contribution-delivery-matrix-2026Q1.md`
- `design/epic-contribution-scorecards-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/tooling-contract-execution-blueprint-2026Q1.md`
- `design/compatibility-claims-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- `design/semantic-context-execution-blueprint-2026Q1.md`

## Why this note is needed now
The current Rust picture is saying more than “these things hurt.”
It is also saying that several of the most promising answers only become **honest** once earlier layers exist.

The March 2026 challenges writeup keeps clustering the big recurring pain around practical productivity and adoption taxes: compile/resource pain, async pain, choice paralysis, and maturity gaps. That means a serious portfolio should privilege reusable unlocks over polished but premature consumer surfaces.
https://blog.rust-lang.org/2026/03/20/rust-challenges/

The 2025 State of Rust survey says the broad challenge pattern remains stable, docs remain canonical, and editor/LLM mediation is rising. That makes it more important that later consumer-facing help layers import durable reviewable artifacts instead of acting like primary sources.
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

The compiler-performance survey plus Cargo build-analysis, build-dir-layout, and the 1.94 Cargo cycle together say build pain is broad while Cargo is only now gaining better recorded rebuild reasons, timing history, structured logging, and `cargo report`-style surfaces. That is strong evidence that **Build-State Evidence** is not merely a standalone product idea; it is a first unlock for several later machine-facing and human-facing answers.
https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

The `relink-don't-rebuild` goal reinforces that point. Some of Rust's future wins depend not on another dashboard but on sharper change-impact and reuse semantics. That is unlock-substrate work whose effects should compound into later tools.
https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html

The docs.rs rustdoc JSON surface, `cargo-semver-checks` work, and StableMIR / `rustc_public` progress say the semantic substrate is also maturing. That makes **Semantic Context** and closely related contract work more real as second-wave multipliers, but only if they stay explicit about imported versus inferred meaning.
https://docs.rs/about/rustdoc-json
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
https://blog.rust-lang.org/2025/08/05/july-project-goals-update/

The debugging survey points in a similar but distinct direction. It defines a coalition-grade acceptance bar across debuggers, operating systems, async scenarios, visualizers, and expression evaluation. That means **Feedback Loop / Debuggability Acceptance** is a major unlock, but of the acceptance-corpus kind rather than the artifact-report kind.
https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

The 2026 flagships page and the safety-critical writeup show how later program-shaped bets depend on earlier ones. Supply-chain, cross-language interop, and safety-critical readiness all benefit from better contracts, evidence, and acceptance receipts. The safety-critical writeup is explicit about dependency-lifecycle patterns, async requirements, and interop guidance. That is a sign that readiness commons should consume earlier layers rather than pretending to replace them.
https://rust-lang.github.io/rust-project-goals/2026/flagships.html
https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

The missing layer is therefore not another ranking rewrite.
It is a **compounding map**.

## Headline answer
The archive should now assume:

> the strongest portfolio is not a flat top-10 list.
> It is a compounding graph.
> Some contributions primarily **generate reusable truth**, some **route and normalize it**, some **consume it to widen guidance or operations**, and some should only be attempted once those earlier layers exist.

That means future comparative work must keep these distinct:
- **upstream substrate unlocks** — narrower upstream work that later bets should import;
- **evidence generators** — contributions that make hidden recurring state legible;
- **contract multipliers** — contributions that make machine-facing meaning reusable across tools;
- **boundary bridges** — contributions that act at release, intake, or compatibility boundaries;
- **consumer wideners** — contributions that turn earlier artifacts into bounded advice or operator workflows;
- **program seams** — contributions that only become honest when several earlier layers are already real.

## The six portfolio roles

### 1) Upstream substrate unlocks
These are not the same thing as the archive's main public-facing worthy contributions.
They are narrower upstream efforts that materially increase what later bets can import.

Typical examples right now:
- Cargo build-analysis and build-dir work;
- `relink-don't-rebuild`;
- libtest JSON stabilization;
- StableMIR / `rustc_public` publication progress;
- Rust-for-Linux stable-tooling work.

Why they matter:
- they create more honest inputs for later tooling;
- they reduce how much later bets must scrape, infer, or guess;
- and they should often be funded as upstream sponsorship or stabilization work, not launched as separate products.

Wrong shape:
- mistaking one of these substrate lanes for a complete public-platform answer.

### 2) Evidence generators
These are the first serious bets that make recurring but hidden state reviewable.

Typical examples right now:
- **Build-State Evidence**
- **Feedback Loop / Debuggability Acceptance**

Why they matter:
- they create canonical receipts that later consumer layers can import;
- they force explicit negative and partial states;
- and they prevent later recommendation or operational layers from running on folklore.

### 3) Contract multipliers
These are the layers that make evidence or semantic meaning portable across tools, CI, editors, review flows, docs, and machine-mediated consumers.

Typical examples right now:
- **Semantic Context**
- **Tooling Contract**
- **Compatibility Claims**

Why they matter:
- they turn one good local artifact into something multiple downstream consumers can reuse honestly;
- they preserve imported-versus-inferred boundaries;
- and they reduce adapter folklore.

### 4) Boundary bridges
These are important but narrower seams that live on publish, intake, migration, or policy boundaries.

Typical examples right now:
- **Package Intake Gateway**
- **Migration / Public API**-family work

Why they matter:
- they convert earlier evidence and contract layers into operator- or release-grade decisions;
- they are strategically real;
- but they are easier to overbuild if they are started before the underlying artifact grammar is stable enough.

### 5) Consumer wideners
These are the first user-facing or operator-facing layers that widen reach.

Typical example right now:
- **Adoption Navigation + Ecosystem Atlas**

Why they matter:
- they reduce tacit knowledge and choice paralysis;
- but they should import earlier evidence, compatibility, and semantic packs rather than fabricate authority from summaries alone.

### 6) Program seams
These are worthy contributions whose honest shape is a continuing commons or readiness program.

Typical example right now:
- **Safety-Critical Readiness Commons**

Why they matter:
- they unify several earlier truths into a portable adoption threshold;
- but they should come after the necessary receipts and compatibility layers exist.

## Mapping the strongest current contributions by unlock leverage

### 1) Build-State Evidence — strongest first unlock
**Role:** evidence generator

**Why it compounds so strongly:**
- it attacks broad recurring pain directly;
- Cargo and compiler work are making its imports more machine-usable right now;
- its artifacts are reusable by CI, editors, build-system integration, package review, adoption guidance, and future tool contracts.

**What it unlocks next:**
- stronger **Tooling Contract** exemplars instead of abstract schema talk;
- better **Adoption Navigation** around build and workflow choices;
- more honest **Package Intake** and operational review around build scripts, extraction, and repeated execution behavior;
- sharper change-impact and relink-oriented work because repeated build-state truth becomes observable.

**What should be built first:**
- canonical build-state packs;
- `explain`, `diff`, and `doctor` flows;
- repeated-workspace fixtures;
- explicit unsupported / partial states.

**Wrong shape:**
- starting with a hosted cache/control plane and only later trying to explain what happened.

### 2) Semantic Context — strongest hidden unlock
**Role:** contract multiplier

**Why it compounds so strongly:**
- it can feed semver, docs, migration, CI, edit, and assistant consumers;
- docs.rs rustdoc JSON and StableMIR / `rustc_public` progress are making import lanes more real;
- it gives later recommendations and compatibility claims a better substrate than string-matching or `cargo metadata` folklore.

**What it unlocks next:**
- stronger **Compatibility Claims**;
- stronger **Migration / Public API** work;
- more honest **Adoption Navigation** cards that cite actual semantic surfaces;
- later machine consumers that need exact imported subject truth.

**What should be built first:**
- exact subject capture;
- ranked input lanes with format-version truth;
- bounded query/result artifacts;
- import-lossiness receipts.

**Wrong shape:**
- a giant semantic platform before a thin versioned import lane exists.

### 3) Feedback Loop / Debuggability Acceptance — strongest acceptance unlock
**Role:** evidence generator

**Why it compounds so strongly:**
- it creates tuple receipts across debugger × OS × runtime × optimization combinations;
- later compatibility, support, and industrial-readiness claims can import those receipts instead of repeating hand-wavy “debugging support” prose;
- it gives later recommendation layers something honest to point at.

**What it unlocks next:**
- better debugger-related **Compatibility Claims**;
- stronger **Adoption Navigation** in domains where debugging posture matters;
- more credible **Safety-Critical** or mixed-language readiness guidance where acceptance evidence matters.

**What should be built first:**
- a narrow but portable tuple matrix;
- accepted / partial / unsupported / regressed receipts;
- one visualizer corpus;
- one async scenario track.

**Wrong shape:**
- a blessed debugger narrative before tuple receipts exist.

### 4) Tooling Contract — routing unlock, not the first raw build
**Role:** contract multiplier

**Why it compounds:**
- it can normalize machine-facing Cargo truth across CI, editors, docs, outer build systems, and assistants;
- but it becomes much more grounded once **Build-State Evidence** and **Semantic Context** already have real exemplar packs.

**What it unlocks next:**
- better importer discipline across tool categories;
- less target-dir/build-dir folklore;
- bounded assistant and editor handoffs that consume named artifacts.

**What should be built first:**
- reference layer;
- report/pack command family;
- adapter/import corpus with visible lossiness.

**Wrong shape:**
- trying to solve the whole machine-facing world before the first high-value packs exist.

### 5) Compatibility Claims — claims unlock after evidence and semantics
**Role:** contract multiplier / boundary bridge

**Why it compounds:**
- it turns support, debugger, MSRV, target, and public-boundary facts into reviewable claims;
- but it is stronger once semantic context and acceptance receipts exist.

**What it unlocks next:**
- later **Adoption Navigation** without score-theater;
- later **Safety-Critical** readiness profiles;
- better release and migration handoffs.

**Wrong shape:**
- starting with badges, hosted matrices, or one-field verdicts.

### 6) Package Intake Gateway — operational bridge with strong downstream leverage
**Role:** boundary bridge

**Why it compounds:**
- it acts at a real registry/extraction/policy boundary;
- recent Cargo and crates.io security signals make it urgent;
- but its strongest form imports earlier artifact and contract discipline instead of inventing a free-floating trust portal.

**What it unlocks next:**
- later operator policy and review workflows;
- better incident and intake handling;
- clearer handoff into install, trust, and security surfaces.

**Wrong shape:**
- a reputation marketplace before route, extraction, and fail-closed evidence are first-class.

### 7) Adoption Navigation + Ecosystem Atlas — first honest widener, not the first unlock
**Role:** consumer widener

**Why it matters:**
- it addresses tacit knowledge and choice paralysis directly;
- but it should widen **after** evidence, semantic, and compatibility layers exist, because those layers make its cards renewable and reviewable.

**What it should consume:**
- build-state packs;
- semantic-context packs;
- compatibility and support receipts;
- explicit freshness and local-fit caveats.

**Wrong shape:**
- a crate-score or framework-winner portal that outruns the evidence spine.

### 8) Safety-Critical Readiness Commons — late compound consumer/program seam
**Role:** program seam

**Why it matters:**
- it is strategically real and institution-shaped;
- but it becomes honest only after earlier layers provide concrete compatibility, acceptance, intake, and support receipts.

**What it should consume:**
- debugger and acceptance receipts where relevant;
- compatibility/support evidence;
- package-intake and dependency-lifecycle posture;
- Rust-for-Linux / interop / target-readiness imports where relevant.

**Wrong shape:**
- treating one demo or one checklist as if it replaces the broader evidence and compatibility work underneath.

## The main dependency rules the archive should now remember

### Rule 1: do not build consumer wideners before evidence generators
If a proposal starts with recommendation, ranking, or guidance surfaces before it has reusable build-state, compatibility, or acceptance receipts, it is probably front-door-first in the wrong way.

### Rule 2: do not build giant contracts before exemplar packs
A tooling or semantic “contract” becomes more believable when at least one narrow but high-value canonical pack already exists.

### Rule 3: treat substrate milestones as unlocks, not rival epics
Cargo build-analysis, build-dir-layout work, relink work, libtest JSON, StableMIR / `rustc_public`, and Rust-for-Linux stable-tooling all matter a great deal, but many of them should be read as upstream unlock lanes.

### Rule 4: the strongest later bets are often compound consumers
Several strategically exciting efforts are not first because they are weak. They are later because their best form consumes earlier evidence and contract layers.

### Rule 5: ask what reusable artifact survives if the hosted layer disappears
A good unlock bet leaves behind reviewable artifacts that other teams can import even without a central service.

## Practical portfolio reading after this note
Until stronger evidence arrives:
- **Build-State Evidence** remains the strongest broad first build and now also the strongest **first unlock**;
- **Semantic Context** remains the strongest hidden **substrate multiplier**;
- **Feedback Loop / Debuggability Acceptance** remains the strongest **acceptance unlock**;
- **Tooling Contract** remains the broad routing layer, but it should usually import earlier exemplar packs instead of leading with abstraction;
- **Compatibility Claims** remains the strongest claims router once semantic and acceptance lanes exist;
- **Package Intake Gateway** remains the strongest operational bridge, but one that should consume earlier artifact discipline;
- **Adoption Navigation** remains the first honest consumer widener;
- **Safety-Critical Readiness Commons** remains a late compound program seam;
- and upstream efforts like Cargo build-analysis, build-dir work, relink, libtest JSON, StableMIR / `rustc_public`, and Rust-for-Linux tooling should be treated as real unlock inputs rather than forced into fake standalone-epic slots.
