# Design: Epic contribution program stack (2026 Q1)

## Goal
The archive already has plenty of blueprints, scorecards, and specialist notes.
What it still lacked was one sharper answer to a practical repo-construction question:

> if we were building a truly worthy Rust-needs-and-dreams repo rather than collecting ever more adjacent ideas, which proposals should be treated as **macro-programs**, which should be folded under them, and what should those programs actually contain in theory and practice?

This note is a **program-stack + pruning + implementation-shape** pass.
It does **not** rerank the broad ladder.
It does **not** promote a new active frontier.
It exists to keep the archive from mistaking a large set of interesting proposals for a healthy build plan.

Read with:
- `design/practical-epic-contribution-briefs-2026Q1.md`
- `design/territory-priority-refresh-2026Q1.md`
- `design/epic-contribution-scorecards-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/tooling-contract-execution-blueprint-2026Q1.md`
- `design/compatibility-claims-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- `meta/BROAD_SYNTHESIS_DEDUP_PROTOCOL.md`

## Why this pass is merited
The latest public signals keep pointing at a smaller number of **program-shaped gaps** than the archive’s raw proposal count might suggest.

Signals that matter here:
- The March 2026 Rust challenges writeup says the practical pain is concentrated around **async difficulty**, **crate-choice / trust / maturity questions**, **embedded constraints**, **safety-critical tooling maturity**, and a GUI-specific compile-loop tax rather than around one missing framework.  
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says **resource usage** remains a major non-trivial productivity limit, **debugging** remains a major pain point, docs remain canonical, and LLM/editor-mediated learning is rising.  
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo’s external-tools chapter still defines the official machine-facing lanes as **`cargo metadata`**, **`--message-format=json`**, and **custom subcommands**, which means honest companion tooling still has to respect partial documented surfaces instead of inventing a fake universal API.  
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo’s build-analysis and build-dir-layout goals make it clearer than before that Rust is missing **attachable build-state evidence**, not just more bespoke build wrappers.  
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html  
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- The 2026 debugging survey says debugger tuple support, visualizers, async debugging, and Rust-expression evaluation are all still incomplete, which means the missing contribution is an **acceptance commons** problem, not merely one more frontend.  
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Cargo’s packaging docs still say `.cargo_vcs_info.json` is only a **best-effort snapshot** and explicitly does **not** verify provenance, which is a sharp reminder that package-boundary truth and intake truth are still under-built.  
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- The 2026 flagships page keeps supply-chain, safety-critical, and building-block/tooling work in the strategic core of Rust’s own roadmap.  
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The safety-critical synthesis still says the missing pieces are readiness checklists, dependency lifecycle playbooks, safety-case-friendly async requirements, and long-lived interop guidance.  
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

Taken together, the practical problem is no longer “find more interesting things”.
It is “fold the territory into a smaller number of buildable macro-programs without losing the archive’s distinctions”.

## Headline answer
The worthy repo should now be treated as **five macro-programs plus one archive discipline**, not as one giant flat backlog:

1. **Evidence Spine**
2. **Feedback / Debug Acceptance Commons**
3. **Navigation / Defaults / Claims Commons**
4. **Package Intake + Release Boundary Review**
5. **Safety-Critical + Institutional Readiness Commons**
6. **Broad-synthesis dedup / continuity rails** for the archive itself

These are not equal in urgency.
The default build order remains:
1. Evidence Spine
2. Feedback / Debug Acceptance Commons
3. Navigation / Defaults / Claims Commons
4. Package Intake + Release Boundary Review
5. Safety-Critical + Institutional Readiness Commons

## Program 1 — Evidence Spine
**Portfolio role:** strongest first build  
**Fold under this program:** Build-State Evidence, Tooling Contract, Shared Spine, Semantic Context, and most raw build/resource evidence notes.

### Theory
Rust still lacks one attachable, reviewable evidence family for everyday build truth.
Without it, later layers keep rebuilding partial truths from logs, local memory, tool internals, or fragile scraping.

### What a worthy contribution should contain in practice
Ship a small family of **spec + adapter + pack + doctor** artifacts:
- one `build-state-pack/v0` family;
- one `scope-plan-evidence/v0` or equivalent machine-facing contract layer;
- Cargo-native imports first (`cargo metadata`, `--message-format=json`, and future `cargo report` lanes where real);
- explicit fields for subject, scope, plan, execution evidence, rebuild reason, timing/resource evidence, cache/contention posture, adapter lossiness, and unknowns;
- a doctor flow that keeps partial or weak evidence visible instead of flattening it into “healthy” or “slow”.

### First proofgrounds
- large-workspace incremental rebuild diff;
- Rust Analyzer / Cargo lock-contention case;
- clean versus warm CI comparison;
- one native-dependency case that proves imports can survive less-pure builds.

### What should live in the repo
- `specimens/` for canonical example packs;
- `fixtures/` for invalid or lossy cases;
- `proofgrounds/` for replayable build scenarios;
- `tools/` for pack/contract validators;
- thin CLI companions, not one hosted service.

### Refuse first
- Cargo daemon dreams;
- hosted build score portals;
- target-dir/build-dir archaeology treated as canon;
- cache empire products that replace evidence with policy.

## Program 2 — Feedback / Debug Acceptance Commons
**Portfolio role:** strongest second build  
**Fold under this program:** Feedback Loop / Debuggability Acceptance, Defect Escalation, debugger tuple notes, most session-export and runtime-inspection seams, and the more user-facing part of benchmark/diagnostic evidence.

### Theory
Even with better build truth, Rust still lacks one portable answer to:
- can I inspect this program honestly,
- across which debugger tuples,
- with what async posture,
- with what visualizer quality,
- and what can I export for issue filing, support, docs, or editor/assistant help?

### What a worthy contribution should contain in practice
Ship an **acceptance commons + session pack**:
- one `feedback-loop-pack/v0` family;
- debugger-tuple capability records with explicit unsupported states;
- visualizer acceptance corpus;
- async-debug acceptance lanes;
- session exports that import build-state packs instead of starting from scratch;
- issue/support/docs/editor handoff packs that preserve unknowns and tuple limits.

### First proofgrounds
- LLDB/GDB/CDB tuple samples across at least one shared scenario family;
- async runtime debugging on one representative runtime family;
- expression-evaluation and pretty-printer / visualizer lanes;
- issue and support export roundtrip.

### What gets folded instead of promoted
- most free-floating debugger ideas;
- standalone issue-report dreams;
- one-off visualization layers that cannot emit reusable acceptance truth.

### Refuse first
- another debugger fork presented as the whole answer;
- IDE-only magic with no portable export;
- “developer experience” dashboards that hide tuple weakness.

## Program 3 — Navigation / Defaults / Claims Commons
**Portfolio role:** strongest widener once evidence exists  
**Fold under this program:** Adoption Navigation, Ecosystem Atlas, reviewable defaults, Canonical Learning, Compatibility Claims, Support Envelope, and most recommendation-layer or docs/assistant derivation ideas.

### Theory
Rust increasingly needs a bounded answer to “what should I choose, what is supported, how fresh is that advice, and what claim can I safely repeat?”
That is no longer just community polish.
It is core infrastructure for a world where docs stay canonical but LLM/editor-mediated learning keeps rising.

### What a worthy contribution should contain in practice
Ship an **editorial commons with receipts**:
- lane definitions and slot maps;
- conservative defaults and local-fit overlays;
- claim packs with evidence posture, drift status, and unknowns;
- renewal receipts and drift budgets;
- bounded assistant/export slices derived from canonical artifacts instead of becoming the canon themselves.

### First proofgrounds
- internal CLI or HTTP-service lane;
- one public SDK or library lane only after renewal discipline is real;
- one compatibility claim family that imports support, public-API, and debug acceptance facts together.

### What gets folded instead of promoted
- “best crates” portals;
- global winner tables;
- assistant memory canon projects;
- badge farms for support/compatibility.

### Refuse first
- opaque trust scores;
- universal framework rankings;
- one static matrix pretending to settle support truth.

## Program 4 — Package Intake + Release Boundary Review
**Portfolio role:** urgent bridge, narrower than the first three but strategically real  
**Fold under this program:** Package Intake Gateway, Release Truth, Publisher & Source Identity, public-boundary and publish-surface facts that matter specifically at ingress or release boundaries.

### Theory
Rust still lacks a first-class portable ingress boundary for “what are we about to trust, publish, extract, verify, waive, or replay?”
Cargo’s own packaging docs keep warning that some package-side metadata is only best-effort and not verified.
Recent advisories also keep reminding the ecosystem that intake truth and alternate-registry posture cannot be hand-waved.  
https://blog.rust-lang.org/2026/03/21/cve-2026-33056/

### What a worthy contribution should contain in practice
Ship a **local-first intake review layer**:
- one `intake-receipt/v0` or equivalent family;
- extraction / quarantine / waiver / replay artifacts;
- route-owner and registry posture fields;
- imported publish and package facts, but with provenance caveats carried forward;
- explicit handoffs for humans and automated policy.

### First proofgrounds
- crates.io versus alternate-registry contrast;
- packaged tarball inspection with best-effort VCS receipt carried as weak evidence, not proof;
- synthetic malicious-package and typosquat review drills;
- release-boundary replay where semver/public-API and intake concerns meet.

### What gets folded instead of promoted
- generic trust-score portals;
- provenance-brand theater;
- registry-specific fixes advertised as the whole package-ingress answer.

### Refuse first
- one universal “safe crate” badge;
- one security brand without route truth;
- a hosted portal that hides waivers, caveats, or provenance weakness.

## Program 5 — Safety-Critical + Institutional Readiness Commons
**Portfolio role:** clearest program/consortium seam  
**Fold under this program:** Safety-Critical Readiness Commons, high-assurance support-envelope work, and the strongest stewardship/institutional-readiness layers.

### Theory
Some of Rust’s most valuable missing work is not one crate or one subcommand.
It is a reusable readiness commons for teams that need evidence, lifecycle discipline, qualification posture, and interop guidance.

### What a worthy contribution should contain in practice
Ship a **commons + program**:
- target-focused readiness checklists;
- dependency lifecycle playbooks;
- safety-case-friendly async requirements;
- interop / FFI evidence guidance;
- a place for attachable toolchain, runtime, claim, and boundary evidence.

### First proofgrounds
- one target-family onramp;
- one dependency lifecycle playbook;
- one async-runtime requirements draft;
- one interop evidence sample for C/C++ boundary maintenance.

### What gets folded instead of promoted
- vendor-specific “certified Rust” brands;
- one runtime claiming to solve readiness by declaration;
- thin compliance badge systems.

### Refuse first
- certification theater without traceable evidence;
- flattening institutional readiness into ordinary crate ranking.

## Cross-cutting fold / keep / eliminate decisions

### Fold under stronger parents
- Benchmark-evidence work should usually be read through **Evidence Spine** or **Feedback Commons** depending on whether the question is machine-readable measurement truth or session/acceptance truth.
- Support Envelope should usually be read through **Navigation / Defaults / Claims Commons** unless the question is explicitly high-assurance / safety-critical.
- Public-API, semver, and release-boundary work should usually be read through **Navigation / Claims** or **Package Intake + Release Boundary Review**, not as freestanding top-band empires.
- Canonical-learning and assistant-boundary work should usually be read through **Navigation / Defaults / Claims Commons**, not as a separate AI strategy frontier.

### Keep separate even after pruning
Do **not** collapse these distinctions:
- evidence spine versus feedback/session acceptance;
- recommendation/defaults commons versus claim routing;
- package-ingress boundary work versus safety-critical institutional readiness;
- archive hygiene about LLM editing versus ecosystem guidance about Rust itself.

### Eliminate as top-band answers
- framework winner-hunting;
- workspace-control empires;
- score portals and trust dashboards;
- assistant memory canonization;
- badge-first compatibility or security schemes.

## Practical repo-construction recommendation
The archive should now bias toward this working habit:
1. deepening one macro-program note or one seam-local blueprint;
2. updating the routing layer to point at the new canonical reading path;
3. leaving explicit fold/refusal decisions behind;
4. avoiding new broad synthesis files unless a genuinely new comparison or construction layer is missing.

That is the healthier way to make the repo feel worthy rather than merely exhaustive.

