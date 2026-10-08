# Design: Epic contribution reference architectures (2026 Q1)

## Goal
The archive already has strong answers to three big questions:
- which Rust ecosystem gaps rank highest;
- what practical build shape they should take; and
- how those answers fold into a smaller number of macro-programs.

What it still lacked was one sharper answer to a different repo-construction question:

> once the macro-programs are known, what should each one actually contain as a **minimum viable reference architecture** — kernel, interfaces, proof assets, proving grounds, and exit criteria — so future revisions deepen the programs instead of rephrasing them?

This note is a **spec-first / reference-architecture / proof-asset** pass.
It does **not** rerank the broad ladder.
It does **not** promote a new frontier.
It exists to keep the repo from stopping at elegant names for macro-programs.

Read with:
- `design/epic-contribution-program-stack-2026Q1.md`
- `design/practical-epic-contribution-briefs-2026Q1.md`
- `design/territory-priority-refresh-2026Q1.md`
- `design/portfolio-artifact-conventions-2026Q1.md`
- `design/portfolio-proving-grounds-2026Q1.md`
- `design/portfolio-anchor-corpus-2026Q1.md`
- `design/portfolio-exemplar-federation-2026Q1.md`
- `meta/BROAD_SYNTHESIS_DEDUP_PROTOCOL.md`
- `meta/PROGRAM_SPEC_DEEPENING_PROTOCOL.md`

## Why this pass is merited now
The current public signals reinforce missing **program kernels and evidence flows**, not missing mega-frameworks.

Signals that matter here:
- The March 2026 Rust challenges writeup concentrates pain around **async**, **crate choice/trust**, **embedded constraints**, **safety-critical tooling maturity**, and **GUI compile-loop tax** rather than one absent application framework.  
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says **resource usage** remains a major productivity limit, **debugging** remains a meaningful pain point, and online docs remain canonical while LLM/editor-mediated learning rises.  
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2026 debugging survey still names **debugger-version coverage**, **visualizers**, **async debugging**, and **Rust-expression evaluation** as incomplete, which points to an acceptance-corpus problem more than a missing frontend.  
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Cargo’s build-analysis goal is explicitly about **rebuild reasons**, **timing data**, **CLI arguments**, **build identifiers**, and `cargo report` review commands, which is reference-architecture fuel for an evidence spine.  
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Cargo’s build-dir-layout goal keeps pushing toward **fine-grained locking**, **cacheable units**, and a **user-wide shared cache**, which means build-state work needs clear import boundaries and proofgrounds.  
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- The March 2026 Cargo security advisory shows package extraction is still a live **boundary-review** seam, especially for alternate registries and older Cargo versions.  
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- The January 2026 crates.io update and February 2026 malicious-crate policy change make the package boundary look increasingly like a mix of **registry surface**, **RustSec route**, and **local review posture**, not one universal trust score.  
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/  
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- The 2026 goals page keeps **SBOM support**, **public/private dependencies**, **sanitizers**, **building blocks**, and **safety-critical** work inside Rust’s own flagship themes, which means the repo should specify interfaces and proof assets rather than drifting into wish-list mode.  
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The safety-critical writeup still says the missing work looks like **checklists**, **dependency lifecycle playbooks**, **safety-case-friendly async guidance**, and **interop/tooling maturity**, which is a reference-architecture problem more than a single library gap.  
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

Taken together, the missing layer is:
**what does each serious program have to contain before it deserves widening?**

## Headline answer
A worthy repo should now treat each macro-program as a **reference architecture** with seven required parts:
1. a **kernel artifact family**;
2. a small set of **declared import surfaces**;
3. one or more **proof assets**;
4. named **proving grounds**;
5. a bounded **v0 launch surface**;
6. explicit **exit criteria** for “real enough to widen”; and
7. an explicit **wrong shape to refuse**.

The archive should prefer **spec-first deepening** over fresh broad ranking notes unless a genuinely new comparative layer is missing.

## Cross-program rules
These rules should hold across all top programs.

### 1) Start with local, reviewable artifacts
The first shipped thing should usually be a pack, corpus, validator, brief family, or lane card set that a team can inspect locally.
Do not start with a hosted portal if the truth is still disputed.

### 2) Import upstream surfaces; do not impersonate them
Each program should list exactly which upstream or service surfaces it imports.
It should not pretend those imports are stronger than they are.

### 3) Proof assets come before automation theater
Before adding recommendation layers, policy ratchets, or product polish, the repo should demand proof assets such as specimens, invalid fixtures, anchor bindings, exemplar repos, or scenario matrices.

### 4) Every program needs at least one refusal clause
A reference architecture is incomplete if it never says what seductive shape must be refused.

### 5) A v0 should answer one painful review question within a working day
If a v0 cannot answer a real review, routing, or support question quickly and honestly, it is still a concept note, not a worthy contribution.

## Program 1 — Evidence Spine reference architecture
**Portfolio role:** strongest first build

### Kernel
A **pack-and-report family** for build-state truth:
- `build-state-pack/v0`
- rerun/diff receipts
- a doctor flow for unknowns, lossiness, and stale imports

### Import surfaces
Import only bounded surfaces first:
- `cargo metadata`
- `--message-format=json`
- build-analysis / `cargo report` lanes when they are real
- libtest JSON or adjacent machine-usable test surfaces when needed
- narrowly declared adapter imports for CI or editor-triggered builds

### Proof assets
- canonical specimens for packs, diffs, and lineage receipts;
- invalid fixtures showing stale, partial, or lossy imports;
- anchor bindings for workspace, CI, and native-dependency profiles;
- exemplar repos that prove warm-build, rebuild-reason, and contention cases.

### Proving grounds
- large workspace incremental rebuild diff;
- Rust Analyzer + Cargo lock-contention case;
- clean versus warm CI run comparison;
- one native-dependency case where evidence remains honest despite impurity.

### Bounded v0
A worthy v0 is not “all build intelligence”.
It is:
- one import pipeline;
- one reviewable pack format;
- one diff path;
- one doctor path;
- and one scenario corpus with clear unknowns.

### Exit criteria
Do not widen until the program can:
- attach evidence across more than one invocation;
- show rebuild reasons and timing truth without scraping internals as canon;
- preserve adapter lossiness explicitly; and
- survive at least one shared-workspace and one CI proving ground.

### Refuse first
- universal build daemons;
- target-dir archaeology sold as stable truth;
- hosted score portals;
- cache empires that erase evidence provenance.

## Program 2 — Feedback / Debug Acceptance Commons reference architecture
**Portfolio role:** strongest second build

### Kernel
An **acceptance corpus + session-pack family**:
- debugger tuple records;
- async-debug acceptance lanes;
- visualizer records;
- session export / issue handoff packs.

### Import surfaces
- build-state pack imports from Program 1;
- declared debugger tuple descriptors;
- runtime / async-mode descriptors;
- issue/support/export attachment rules.

### Proof assets
- tuple matrix fixtures with supported, unsupported, and degraded states;
- session-export specimens;
- example handoffs for issue filing and support routing;
- negative cases where a debugger cannot evaluate expressions or display async state correctly.

### Proving grounds
- LLDB, GDB, and one Windows debugger tuple family;
- at least one async runtime scenario;
- visualizer roundtrip samples;
- issue/export re-import test.

### Bounded v0
A worthy v0 does not need to “solve debugging Rust”.
It needs to answer:
- what worked,
- on which tuple,
- with which unsupported states,
- and what can be exported without fiction.

### Exit criteria
Do not widen until the program can:
- preserve tuple identity and debugger version identity;
- state unsupported async or expression-evaluation gaps plainly;
- roundtrip a session export into issue/support context; and
- import build-state evidence instead of forcing every session to restate the world.

### Refuse first
- a debugger fork sold as the whole answer;
- IDE-only magic with no export;
- one green demo tuple impersonating support reality.

## Program 3 — Navigation / Defaults / Claims Commons reference architecture
**Portfolio role:** strongest widener once evidence exists

### Kernel
An **editorial defaults + claims pack** family:
- lane cards;
- conservative default stacks;
- local-fit overlays;
- renewal receipts;
- claim packs with evidence posture and drift state.

### Import surfaces
- evidence and acceptance imports from Programs 1 and 2;
- release-boundary and compatibility imports where available;
- docs.rs or target-support facts only with declared caveats;
- service / registry facts only through named routes.

### Proof assets
- lane-default cards for a small starter set;
- renewal receipts showing freshness bounds;
- claims specimens that distinguish imported fact from editorial recommendation;
- consumer-routing fixtures that prove derived slices stay weaker than canon.

### Proving grounds
- one internal CLI lane;
- one HTTP-service lane;
- one library or SDK lane only after evidence imports are real;
- one compatibility-claims roundtrip with explicit unknowns.

### Bounded v0
A worthy v0 is not a universal “best crates” portal.
It is a small, renewable editorial corpus whose choices can be reviewed and whose claims can expire.

### Exit criteria
Do not widen until the program can:
- cite the evidence sources each recommendation actually depends on;
- carry renewal receipts and drift budgets;
- keep derived consumer slices weaker than canonical lane cards; and
- refuse score-only or popularity-only recommendations.

### Refuse first
- winner tables;
- trust-score dashboards;
- assistant-memory canon projects;
- badges pretending to settle support truth.

## Program 4 — Package Intake + Release Boundary Review reference architecture
**Portfolio role:** urgent local-first bridge

### Kernel
A **local-first intake review pack** with release-boundary receipts:
- extraction review receipts;
- quarantine / waiver / replay paths;
- package identity and route notes;
- release-boundary review outputs.

### Import surfaces
- `cargo package` and related package-boundary facts;
- registry/service facts from crates.io;
- RustSec and security-route imports;
- SBOM precursor and public/private dependency facts when present;
- alternate-registry posture only when explicitly declared.

### Proof assets
- malicious-crate or suspicious-package replay fixtures;
- waiver lineage receipts;
- extraction-boundary negative cases;
- release-boundary review examples that remain local and reviewable.

### Proving grounds
- local publish candidate review;
- alternate registry intake case;
- compromised or suspicious package replay;
- one “older Cargo / non-default route” edge case.

### Bounded v0
A worthy v0 is not a supply-chain brand.
It is a review layer that can say what was inspected, what route facts were imported, what remains unknown, and why a package was admitted, quarantined, or escalated.

### Exit criteria
Do not widen until the program can:
- distinguish provenance hints from verified facts;
- preserve registry-route and tool-version caveats;
- carry waiver and replay lineage;
- and survive at least one malicious-package replay without collapsing into trust-score theater.

### Refuse first
- universal trust scores;
- registry-specific hacks sold as general intake truth;
- cloud-only scanners with no local receipts.

## Program 5 — Safety-Critical + Institutional Readiness Commons reference architecture
**Portfolio role:** high-value stewarded program

### Kernel
A **readiness profile + evidence-recipe commons**:
- target readiness profiles;
- dependency lifecycle playbooks;
- toolchain / lint / coverage / interop requirement ledgers;
- consortium or working-group agenda notes for the gaps no one team can settle alone.

### Import surfaces
- project goals and flagship milestones;
- FLS, lint, sanitizer, coverage, and tool-qualification developments where relevant;
- declared interop or target facts;
- imported evidence from the earlier programs when safety claims depend on them.

### Proof assets
- readiness profile cards for representative environments;
- long-lived dependency governance examples;
- evidence recipe bundles showing what must be collected and what is still absent;
- example policy/playbook documents rather than a fake certification badge.

### Proving grounds
- one automotive-style or embedded high-assurance anchor;
- one long-lived product maintenance anchor;
- one async-in-safety constraints review;
- one interop boundary profile.

### Bounded v0
A worthy v0 is not “certified Rust”.
It is a readiness commons that helps teams understand what evidence, tooling maturity, and process layers are still missing.

### Exit criteria
Do not widen until the program can:
- distinguish compiler guarantee from certifiable-toolchain evidence;
- show a dependency lifecycle posture for long-lived products;
- produce reusable readiness profiles for at least one real anchor class; and
- state clearly what still requires consortium, standards, vendor, or institutional work.

### Refuse first
- a certification halo with no evidence recipe;
- one crate or lint sold as “safety-critical solved”;
- optimistic claims that skip long-lived dependency and interop reality.

## Shared infrastructure the repo should keep investing in
These are not separate top-band public epics, but they are necessary rails:
- specimens and invalid fixtures for the shared honesty grammar;
- proving-ground scenario matrix and anchor corpus;
- exemplar federation tying programs to real repo shapes;
- changed-files continuity and archive-doctor output;
- bounded assistant/derived slices that remain weaker than canon.

## What got folded, what got refused, what stayed unchanged
### Folded under stronger parents
- Tooling Contract, Shared Spine, and Semantic Context stay mostly folded under **Evidence Spine** unless the question is specifically about those thin multipliers.
- Defect Escalation and most free-floating session-export ideas stay folded under **Feedback / Debug Acceptance Commons**.
- Compatibility Claims, Canonical Learning, and conservative defaults stay folded under **Navigation / Defaults / Claims Commons**.

### Refused as wrong front-door answers
- dashboards as the first answer;
- framework-empires and universal control planes;
- trust-score or badge farms;
- assistant-memory canon systems;
- certification halo projects with no evidence recipe.

### Unchanged canon
- the broad ladder is unchanged;
- **Build-State Evidence / Evidence Spine** remains the strongest first serious build;
- **Feedback / Debug Acceptance** remains the strongest second build;
- **Navigation / Defaults / Claims** remains the widener;
- **Package Intake + Release Boundary Review** remains the urgent bridge;
- **Safety-Critical + Institutional Readiness** remains the stewarded program seam.

## Recommended archive move
Treat this as a **construction-layer deepening** note.
The next healthy revisions should usually do one of three things:
1. deepen one macro-program with seam-local blueprint work;
2. improve proof assets and proving grounds for an existing program; or
3. tighten one reference architecture’s import and exit criteria.

They should usually **not** create another fresh broad “top missing things in Rust” note unless a genuinely missing comparative layer appears.

