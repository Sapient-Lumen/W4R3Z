# Design: Epic contribution scorecards 2026Q1

## Goal
The archive already has a broad ladder, a selection rubric, and a sequencing note.
What it still lacked was one side-by-side answer to a more practical question:

> when several Rust ecosystem contributions are all genuinely worthy, how should we compare them **without** collapsing breadth, urgency, multiplier value, specialist weight, and consortium-shaped work into one fake total rank?

This note exists to make the repo better at **comparative prioritization**.
It is the archive’s answer to:
- what should be built first,
- what should be built second,
- what is a hidden multiplier rather than a first build,
- what is operationally urgent without becoming the broad #1,
- and what deserves consortium/program ownership rather than one-tool framing.

Read with:
- `design/territory-priority-refresh-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/ideal-rust-worthy-contributions-2026Q1.md`
- `design/portfolio-selection-rubric-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/tooling-contract-execution-blueprint-2026Q1.md`
- `design/compatibility-claims-execution-blueprint-2026Q1.md`
- `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/semantic-context-execution-blueprint-2026Q1.md`

## Why this note is needed now
The archive’s recent work sharpened a lot of individual seams.
That made a new failure mode more likely: once many candidates become well-argued, future revisions can start over-ranking whichever one is most recent, most glamorous, or attached to the sharpest incident.

Current official signals make that especially dangerous:
- Rust’s March 2026 challenges writeup again clusters pain around compile/resource friction, tacit knowledge, async complexity, and domain-maturity gaps rather than one isolated complaint.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says the broad challenge pattern is stable, online docs remain canonical, debugging remains painful, and editor/LLM-mediated learning is rising.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The compiler-performance survey says incremental rebuilds, IDE/type-checking cost, debug-info cost, and poor bottleneck explanation are still real taxes.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Cargo’s build-analysis, build-dir-layout, and recent `cargo report` work make build-state and machine-facing evidence seams unusually ripe.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The debugging survey says Rust still lacks “truly stellar” support across debugger tuples, visualizers, async debugging, and Rust-expression evaluation.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- The safety-critical synthesis says readiness checklists, dependency lifecycle playbooks, async-runtime qualification, and interop evidence remain underbuilt.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- crates.io’s January 2026 update and the March 2026 Cargo extraction advisory make supply-chain/intake work more urgent, but not automatically broader than build-state or debugger acceptance.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- StableMIR / `rustc_public` progress keeps validating compiler-facing substrate work as a multiplier rather than a user-facing epic on its own.
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/

Taken together, those signals say the archive needs a note that can compare strong candidates **honestly**.

## Reading rule
Do **not** turn this into one fake scoreboard.
This note uses five comparison classes:

1. **Broad first build** — the best answer if one serious team can only build one thing.
2. **Second build / day-to-day acceptance companion** — the next highest-leverage investment after the broad first build.
3. **Hidden multiplier / substrate** — a contribution that improves many later seams but is not automatically the best first public build.
4. **Operational bridge / urgent narrow seam** — current incidents or governance pressure make it important, but it still should not impersonate the broad #1.
5. **Program / consortium seam** — the contribution is real and strategically large, but it should be framed as a multi-party readiness program rather than a single crate or dashboard.

The scorecards below therefore compare candidates across the rubric axes **without** forcing them into a false single dimension.

## Headline answer
If the archive had to state the current answer in one paragraph, it should now say:

> **Build-State Evidence** is still the strongest first build overall.
> **Feedback Loop / Debuggability Acceptance** is the clearest second build because it closes the everyday “build → inspect → explain → handoff” gap that the ecosystem is now naming openly.
> **Adoption Navigation + Ecosystem Atlas** is the strongest first consumer-facing widening once the evidence spine exists.
> **Tooling Contract** and **Semantic Context** are the most important hidden multipliers, but for different reasons: Tooling Contract stabilizes machine-facing Cargo handoffs, while Semantic Context stabilizes semantic import truth.
> **Compatibility Claims** is the claim-routing seam that turns several narrower facts into bounded support verdicts.
> **Package Intake Gateway** is more urgent than its broad rank because of current supply-chain/extraction pressure.
> **Safety-Critical Readiness Commons** is the clearest rising consortium-shaped program seam.

That is the current comparative map.

## Scorecards

### 1) Build-State Evidence
**Portfolio class:** broad first build

**Rubric posture**
- Recurring pain / breadth: **very high**
- Substrate readiness: **high**
- Seam clarity: **high**
- Artifact honesty: **very high**
- Thin-shippable v0: **high**
- Reuse / multiplier value: **very high**
- Steward realism: **medium-high**

**Why it stays first**
This seam still hits the broadest recurring pain with the strongest upstream pull.
Rust’s challenges and survey material keep naming compile/resource friction, while Cargo’s build-analysis/report motion is increasingly explicit that build-state facts can be recorded, surfaced, and reused rather than reconstructed from folklore.
The compiler-performance survey further validates that developers want to know **what rebuilt, why, where time went, and what the bottleneck actually was**.

**What the worthy contribution should look like in practice**
- one `build-state-pack/v0` family;
- import-first capture from Cargo-native and tool-native evidence rather than `target/` archaeology;
- explain/diff/doctor flows;
- explicit rebuild-reason, timing/resource, cache/contention, and human-diagnosis fields;
- lineage receipts that let CI, support, editors, and assistants consume the same bounded truth.

**First proof lanes**
- editor/Cargo contention and duplicate-artifact pain;
- incremental rebuild explanation;
- clean/CI build comparison;
- large-workspace regression and renewal receipts.

**Why it is not displaced**
- Debuggability is crucial, but it imports build truth.
- Adoption Navigation matters, but it becomes more honest once evidence layers exist.
- Package Intake is urgent, but not as broad.
- Semantic Context is a multiplier, but not the broadest first public build.

**Refuse first**
- cache-wrapper empires;
- build-health score dashboards;
- daemons or universal build control planes.

### 2) Feedback Loop / Debuggability Acceptance
**Portfolio class:** second build / day-to-day acceptance companion

**Rubric posture**
- Recurring pain / breadth: **high**
- Substrate readiness: **medium-high**
- Seam clarity: **high**
- Artifact honesty: **high**
- Thin-shippable v0: **medium-high**
- Reuse / multiplier value: **high**
- Steward realism: **medium**

**Why it rises now**
The debugging survey made the capability bar unusually explicit: debugger tuple support, good visualizers, async debugging, and Rust-expression evaluation are all still incomplete.
That shifts this seam from “important missing middle” to “best second serious build”.
It also aligns with the compiler-performance survey and Cargo reporting work: the more build-state truth exists, the less acceptable it is that session/debug truth still evaporates into local debugger lore.

**What the worthy contribution should look like in practice**
- one `feedback-loop-pack/v0` family;
- build-state imports rather than fresh disconnected session lore;
- debugger-tuple acceptance profiles;
- visualizer acceptance corpus;
- async-debug and split-debug posture;
- bounded handoffs for issue filing, CI, support, docs, and editors.

**First proof lanes**
- LLDB/GDB/CDB tuple matrix with explicit unsupported states;
- async-debug acceptance on one real runtime family;
- expression-evaluation and visualizer acceptance lanes;
- support/export bundle for issue and docs consumers.

**Why it is not first**
It is narrower than build-state and depends more heavily on external debugger variation.
But once one first build exists, it is the clearest next daily-experience investment.

**Refuse first**
- another debugger fork sold as the whole answer;
- IDE-only integrations that cannot export portable truth;
- hosted “developer experience” portals.

### 3) Adoption Navigation + Ecosystem Atlas + renewal receipts
**Portfolio class:** first consumer-facing widening

**Rubric posture**
- Recurring pain / breadth: **high**
- Substrate readiness: **medium-high**
- Seam clarity: **high**
- Artifact honesty: **high**
- Thin-shippable v0: **medium-high**
- Reuse / multiplier value: **high**
- Steward realism: **medium**

**Why it remains top-band**
The March 2026 challenges writeup makes the pain explicit: teams struggle with choice paralysis and tacit knowledge.
The survey says docs remain canonical while LLM/editor mediation rises.
That combination means Rust increasingly needs **bounded recommendation artifacts** rather than more private canon.

**What the worthy contribution should look like in practice**
- domain records and lane definitions;
- slot maps and local-fit overlays;
- imported maintenance, build, compatibility, trust, and learning evidence;
- renewal receipts and drift budgets;
- project-scoped decision reviews instead of global winners.

**First proof lanes**
- internal CLI or HTTP service lane with conservative defaults;
- one public SDK or library lane only after renewal discipline exists;
- explicit “watch” and “uncertain-owner” outcomes.

**Why it is not first**
Without the earlier evidence spine, this seam becomes another recommendation portal or assistant-memory canon.
It is strongest once it can import real packs.

**Refuse first**
- “best crates for Rust” sites;
- leaderboards disguised as guidance;
- opaque assistant recommendation memory.

### 4) Tooling Contract
**Portfolio class:** hidden multiplier / machine-facing substrate

**Rubric posture**
- Recurring pain / breadth: **medium-high**
- Substrate readiness: **high**
- Seam clarity: **high**
- Artifact honesty: **very high**
- Thin-shippable v0: **medium-high**
- Reuse / multiplier value: **very high**
- Steward realism: **medium**

**Why it matters so much**
Cargo still documents only partial machine-facing surfaces: `cargo metadata`, `--message-format=json`, and custom subcommands.
Cargo’s recent work also keeps separating `target-dir` from `build-dir`, adding reporting lanes, and acknowledging plugin/companion-tool roles.
That means the ecosystem still lacks one honest discovery → scope → plan → evidence → handoff contract.

**What the worthy contribution should look like in practice**
- a `tooling-contract-pack/v0` family;
- separate subject, discovery/scope, graph/plan, execution/evidence, stability posture, and adapter-lossiness truth;
- adapter reports for rust-analyzer, CI, outer-build, BSP, docs, and assistant consumers.

**First proof lanes**
- rust-analyzer and Cargo coexistence with explicit lossiness;
- CI/build-tool imports;
- one non-Cargo outer-build handoff lane.

**Why it is not the broad first build**
It is more infrastructural than directly user-visible.
Its leverage is enormous, but it is easier to justify once Build-State Evidence already demonstrates the value of portable evidence.

**Refuse first**
- Cargo daemons;
- BSP-only protocols;
- target-dir/build-dir scrapers;
- universal monorepo platforms.

### 5) Compatibility Claims
**Portfolio class:** claim-routing spine

**Rubric posture**
- Recurring pain / breadth: **medium-high**
- Substrate readiness: **high**
- Seam clarity: **high**
- Artifact honesty: **very high**
- Thin-shippable v0: **medium-high**
- Reuse / multiplier value: **high**
- Steward realism: **medium-high**

**Why it now looks more strategic**
As more of the ecosystem emits machine-usable facts, someone still has to answer:
what is actually supported, on which terms, with which drift posture, and what may downstream consumers conclude?
This is especially important for safety-critical, target-heavy, and long-support environments.

**What the worthy contribution should look like in practice**
- one `compatibility-claims-pack/v0` family;
- claim-family separation for target/support, toolchain/MSRV, docs/debugger acceptance, public-boundary compatibility, and explicit unknowns;
- imported evidence from support-envelope, public-api, release, and feedback-loop layers;
- bounded exports for docs, release, support, policy, and audit consumers.

**First proof lanes**
- MSRV/toolchain compatibility with explicit evidence posture;
- docs/debugger acceptance drift;
- public-boundary compatibility handoff into release/support.

**Why it is not a glamour build**
It is less exciting than build-state or debug work, but more strategically necessary than many leaf tools once the ecosystem gets serious about supported claims.

**Refuse first**
- badge farms;
- one matrix pretending to be the total verdict;
- one semver or MSRV result treated as the whole claim.

### 6) Safety-Critical Readiness Commons
**Portfolio class:** program / consortium seam

**Rubric posture**
- Recurring pain / breadth: **medium**
- Substrate readiness: **medium**
- Seam clarity: **high**
- Artifact honesty: **high**
- Thin-shippable v0: **medium**
- Reuse / multiplier value: **high**
- Steward realism: **medium, but only with consortium ownership**

**Why it is rising**
The safety-critical synthesis is one of the clearest official arguments that the missing work is not a crate.
The gaps are readiness checklists, dependency lifecycle playbooks, async-runtime qualification requirements, interop/audit evidence, and better support/compatibility posture.
Those are ecosystem-program problems with real industrial pull.

**What the worthy contribution should look like in practice**
- target-readiness profiles;
- dependency-lifecycle playbooks;
- async/runtime qualification criteria;
- interop boundary evidence;
- attachable assurance and waiver imports;
- consortium-friendly ownership and renewal discipline.

**First proof lanes**
- one target-readiness checklist;
- one dependency lifecycle profile;
- one mixed-language or boundary-evidence pilot;
- one async/runtime requirement profile.

**Why it is not a generic first build**
It is narrower than build-state in breadth and much more dependent on program ownership, domain standards, and industrial maintenance commitments.
But it is a worthy and increasingly epic **program seam**.

**Refuse first**
- “certified Rust” brands with thin evidence;
- one runtime trying to declare victory;
- compliance badges replacing traceability.

### 7) Package Intake Gateway
**Portfolio class:** operational bridge / urgent narrow seam

**Rubric posture**
- Recurring pain / breadth: **medium-high**
- Substrate readiness: **high**
- Seam clarity: **high**
- Artifact honesty: **very high**
- Thin-shippable v0: **high**
- Reuse / multiplier value: **medium-high**
- Steward realism: **medium-high**

**Why urgency rose but broad rank did not**
crates.io’s trusted-publishing improvements and the March 2026 Cargo advisory make ingress/extraction/staging truth more urgent.
That sharpens the need for route, payload, staging, resolution, and handoff review.
But one recent advisory still should not erase the broader everyday taxes represented by build-state and debugger acceptance.

**What the worthy contribution should look like in practice**
- one `package-intake-pack/v0` family;
- route and publisher/source posture capture;
- extraction/staging and resolution receipts;
- registry/mirror/alternate-route posture;
- fail-closed review handoffs for policy, security, and enterprise consumers.

**First proof lanes**
- crates.io ingest with trusted-publishing posture;
- alternate registry and mirror lane;
- extraction/staging receipts;
- policy review handoff.

**Why it should not be mistaken for the broad #1**
Its urgency is real, but its day-to-day breadth is still narrower than build-state and feedback-loop work.
Treat it as an urgent bridge, not the whole ecosystem story.

**Refuse first**
- security theater dashboards;
- generic crate-score portals;
- policy engines with no route or staging evidence.

### 8) Semantic Context
**Portfolio class:** hidden multiplier / semantic substrate

**Rubric posture**
- Recurring pain / breadth: **medium**
- Substrate readiness: **medium-high**
- Seam clarity: **high**
- Artifact honesty: **high**
- Thin-shippable v0: **medium**
- Reuse / multiplier value: **very high**
- Steward realism: **medium**

**Why it stays crucial**
StableMIR / `rustc_public`, docs.rs rustdoc JSON, and semver/public-API work all point the same way: many future tools need richer semantic imports, but those imports must remain freshness-aware, version-aware, and explicitly partial.
This is exactly the kind of contribution that can improve many later seams while still being the wrong first public build if treated as a standalone empire.

**What the worthy contribution should look like in practice**
- semantic subject and lane identity;
- ranked input lanes with format/freshness truth;
- bounded query and comparison artifacts;
- consumer exports for semver, docs, edit, CI, and assistant consumers;
- lossiness made explicit.

**First proof lanes**
- public-API / semver consumer;
- docs-analysis consumer;
- bounded assistant or editor import lane.

**Why it is not first**
It is an enabling substrate, not the broadest first visible pain-killer.
Treat it as a multiplier that deserves protection from hype rather than a reason to flatten the ladder.

**Refuse first**
- one giant semantic server that claims to own all compiler truth;
- assistant-first surfaces with no import discipline;
- version-blind query APIs.

## What should be built under different ownership shapes

### If one serious team can only build one thing
Build **Build-State Evidence**.

### If one serious team can build two linked things
Build **Build-State Evidence** and then **Feedback Loop / Debuggability Acceptance**.
That pair best attacks everyday developer pain while keeping a shared evidence spine.

### If two cooperating teams exist
Use one team for **Build-State Evidence + Tooling Contract** and the second for **Feedback Loop / Debuggability Acceptance** with imports from the first.
That gives the archive the strongest shared machine-facing and day-to-day proof surface.

### If the goal is recommendation or ecosystem guidance
Do not start with a recommendation portal.
Start with the earlier evidence layers, then build **Adoption Navigation + Ecosystem Atlas** as the first consumer-facing widening.

### If the sponsor is security- or policy-led
Treat **Package Intake Gateway** as the earliest urgent bridge.
But keep the archive honest that this is urgency, not total breadth.

### If the sponsor is industrial / standards / consortium-led
Treat **Safety-Critical Readiness Commons** as a program seam that should import Compatibility, Support, Interop, and Assurance layers rather than competing with them.

## Anti-cheating rules for future comparisons
- Do not let one recent advisory silently outrank broad recurring pain.
- Do not let one enabling substrate silently outrank direct user pain just because it is elegant.
- Do not let one specialist frontier silently claim to be the generic first build.
- Do not let recommendation layers outrun evidence layers.
- Do not let a candidate win by being easiest to imagine as a product or startup.

## Practical repo consequence
Future ranking questions should now move through three distinct notes in order:
1. `design/portfolio-selection-rubric-2026Q1.md` — is the candidate worthy at all?
2. `design/territory-priority-refresh-2026Q1.md` — which broad band or parent seam does it belong in?
3. `design/epic-contribution-scorecards-2026Q1.md` — how does it compare against the strongest current candidates without collapsing different priority types?

That is the cleanest current answer to “what is Rust really missing, what is merely interesting, what is epic, and what should actually be built next?”
