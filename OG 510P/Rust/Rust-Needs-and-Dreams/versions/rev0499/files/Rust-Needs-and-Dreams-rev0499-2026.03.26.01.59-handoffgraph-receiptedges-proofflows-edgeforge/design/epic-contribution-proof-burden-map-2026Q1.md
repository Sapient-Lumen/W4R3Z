# Design: Epic contribution proof-burden map (2026Q1)

## Goal
The archive now has:
- a broad ladder for what matters most;
- comparative scorecards for worthy contributions;
- a delivery matrix for what each strong candidate should ship;
- an incubation map for what vehicle each candidate should start in; and
- a portfolio-level pilot-evaluation note for generic stage exits.

What it still lacked was one sharper cross-seam answer to a different practical question:

> once we know a contribution is worthy and we know roughly what vehicle it belongs in, **what does it actually have to prove before it deserves widening, institutional support, or canon status as a serious ecosystem answer?**

This note is the archive's answer to that question.
It does **not** rerank the broad ladder.
It does **not** promote a new frontier.
It does **not** replace seam-local blueprints.
It explains which worthy contributions carry which **proof burden**, which **proving grounds** fit them, what their first **credible artifacts** should be, and what kinds of evidence are still too weak to count as “proven”.

Read with:
- `design/epic-contribution-incubation-map-2026Q1.md`
- `design/epic-contribution-delivery-matrix-2026Q1.md`
- `design/epic-contribution-scorecards-2026Q1.md`
- `design/portfolio-pilot-evaluation-2026Q1.md`
- `design/portfolio-proving-grounds-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/tooling-contract-execution-blueprint-2026Q1.md`
- `design/compatibility-claims-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- `design/semantic-context-execution-blueprint-2026Q1.md`

## Why this note is needed now
The public Rust picture is no longer merely saying “here are some missing pieces.”
It is also saying something stricter:
**different worthy contributions fail in different ways because they are asked to prove the wrong thing.**

The March 2026 challenges writeup keeps pointing to recurring taxes such as async pain, crate-choice uncertainty, constrained-resource pain, and weak maturity in some domains. That means a worthy contribution has to prove it reduces a real recurring tax, not merely that it is clever or architecturally elegant.
https://blog.rust-lang.org/2026/03/20/rust-challenges/

The 2025 State of Rust survey says the broad pain pattern is stable, resource usage is still a major productivity problem, the debugging story remains weak enough that a dedicated survey was launched, online docs remain the canonical reference, and LLM/editor mediation is rising. That means new contributions need reviewable artifacts and renewal discipline, not just polished demos.
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

Cargo's current direction is unusually relevant because it keeps turning pain into machine-usable proving grounds:
- Cargo build analysis is explicitly about recorded build metadata, rebuild reasons, and timing history.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- build-dir work is explicitly about lock contention, finer-grained units, and shared-cache futures rather than hand-wavy build speed dreams.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- the March 2026 build-dir-layout v2 testing call makes it clear that real release/test/process breakage is part of the proving ground for tooling changes.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/

Other key seams now have equally explicit proof expectations:
- docs.rs rustdoc JSON is powerful, but it explicitly requires `format_version` awareness and can be built with older `rustdoc`, so semantic-context claims have a versioned import-fidelity burden.
  https://docs.rs/about/rustdoc-json
- `cargo-semver-checks` is important exactly because SemVer violations are common enough that better proof is needed before publish-time conclusions become default.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- the March 2026 Cargo advisory and the February 2026 malicious-crate notification policy update both show that intake/security work lives at an operational boundary and must prove route/extraction/policy truth, not just present “risk scores”.
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- the safety-critical writeup says earlier MC/DC work stalled not because the technical idea was absurd, but because there was no sustained owner and no shared maintenance commitment. That means some contributions have a consortium-readiness burden, not just a technical one.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- the project-goals owner guidance says fully accepted goals need owners, and goals without owners can only be provisional. That makes owner-shaped proof part of the product, not a postscript.
  https://rust-lang.github.io/rust-project-goals/about/owners.html

The missing layer is therefore not another rank rewrite.
It is a **proof-burden map**.

## Headline answer
The archive should now assume:

> a worthy Rust contribution is not proven by “interest”, “elegance”, or even “demand”.
> It is proven by surviving the right proving ground with the right artifact family and the right negative cases.

That means future portfolio work must keep these distinct:
- **importance** — how strategically worthy the seam is;
- **delivery shape** — what it should ship;
- **incubation vehicle** — where it should start;
- **proof burden** — what kind of evidence it must satisfy before widening;
- **proving ground** — what real lane should stress it;
- **graduation line** — what counts as enough proof to harden, expand, or get institutional backing.

## The six proof families

### 1) Observational truth burden
Best for contributions whose main promise is: “we will make real hidden state legible.”

What they must prove:
- observed state is distinct from folklore or inference;
- multi-run differences are preserved honestly;
- negative and partial outcomes are first-class;
- and the artifact remains useful without a hosted service.

Typical seams:
- **Build-State Evidence**
- parts of **Tooling Contract**

### 2) Cross-tuple acceptance burden
Best for contributions whose main promise is: “we will make a fragmented cross-tool experience reviewable.”

What they must prove:
- tuple coverage is explicit;
- accepted / partial / unsupported / regressed states stay distinct;
- issue routing is exportable;
- and success is not dependent on one privileged tool stack.

Typical seam:
- **Feedback Loop / Debuggability Acceptance**

### 3) Renewal and bounded-guidance burden
Best for contributions whose main promise is: “we will reduce tacit knowledge without pretending to be timeless canon.”

What they must prove:
- recommendations are scoped and reviewable;
- source freshness and local-fit caveats survive the summary;
- renewal receipts exist;
- and stale guidance fails visibly instead of silently.

Typical seam:
- **Adoption Navigation + Ecosystem Atlas**

### 4) Import-fidelity burden
Best for contributions whose main promise is: “we will make compiler/docs/package meaning machine-usable without inventing fake certainty.”

What they must prove:
- imported versus inferred facts remain separate;
- format/version caveats are attached;
- adapter lossiness is visible;
- and consumers do not silently over-read weak inputs.

Typical seams:
- **Semantic Context**
- **Tooling Contract**
- **Compatibility Claims / Migration / Public API**

### 5) Operational-boundary burden
Best for contributions whose main promise is: “we will improve real intake, policy, or execution safety at a live system boundary.”

What they must prove:
- route and subject identity are explicit;
- missing evidence fails closed where appropriate;
- operator/policy handoffs are reviewable;
- and incident posture is part of the design, not an afterthought.

Typical seam:
- **Package Intake Gateway**

### 6) Consortium-readiness burden
Best for contributions whose main promise is: “we will make an adoption threshold portable across organizations and over time.”

What they must prove:
- named readiness profiles and shared requirements exist;
- maintenance and qualification work has committed owners;
- real mixed-language or regulated scenarios are exercised;
- and the output is a continuing program of receipts, not a one-time demonstration.

Typical seam:
- **Safety-Critical Readiness Commons**

## Mapping the strongest current contributions to their real proof burdens

### 1) Build-State Evidence
**Primary proof family:** observational truth burden  
**Why this is the right burden:** its promise is not only “faster builds someday”. Its stronger promise is “tell me what rebuilt, why it rebuilt, what changed between runs, and what evidence we actually trust.” Cargo build analysis and build-dir work make that a live proving ground right now.

**What must be proven in practice:**
- at least one real multi-crate workspace lane with incremental churn;
- at least one editor-vs-build contention lane;
- at least one CI-vs-local comparison lane;
- explicit lineage from imported Cargo facts to derived verdicts;
- and explicit unsupported / partial states when the inputs are weaker than the claim.

**What credible v0 looks like:**
- canonical build-state packs for repeated runs;
- `explain`, `diff`, and `doctor` flows;
- reason/timing/resource slices that survive export;
- and fixtures that show both helpful and inconclusive outcomes.

**What does *not* count as proof:**
- one dramatic screenshot;
- one synthetic benchmark;
- a giant remote-cache sales pitch;
- or a target-dir scraper that cannot say what is imported versus guessed.

### 2) Feedback Loop / Debuggability Acceptance
**Primary proof family:** cross-tuple acceptance burden  
**Why this is the right burden:** the problem is not one missing debugger feature; it is the fragmentation of debugger × OS × runtime × visualizer × optimization combinations. The survey launch itself says the Rust project needs specific insight into debugging struggles.

**What must be proven in practice:**
- tuple coverage is explicit, not implied;
- visualizer behavior is separately tested from attach/step/evaluate behavior;
- async and native cases are not silently collapsed;
- regressions produce exportable receipts;
- and unsupported tuples are recorded honestly.

**What credible v0 looks like:**
- a narrow but portable tuple matrix;
- `accepted / partial / unsupported / regressed` receipts;
- one visualizer corpus;
- one async scenario track;
- and issue-routing bundles that upstream maintainers can consume.

**What does *not* count as proof:**
- one debugger demo on one operating system;
- an IDE plugin that works in-house;
- a “stellar debugging” claim without tuple receipts;
- or a blessed-debugger narrative that hides cross-tool reality.

### 3) Adoption Navigation + Ecosystem Atlas
**Primary proof family:** renewal and bounded-guidance burden  
**Why this is the right burden:** the main risk is not under-building a portal. The main risk is overclaiming timeless guidance in a fast-moving ecosystem where docs remain canonical and machine mediation is increasing.

**What must be proven in practice:**
- default cards are scenario-bounded;
- imported source packs are named;
- freshness and local-fit caveats survive every handoff;
- at least one renewal pass shows real drift handling;
- and manual-review posture remains explicit when evidence is weak.

**What credible v0 looks like:**
- a small set of conservative lane cards;
- evidence bundles and renewal receipts;
- bounded briefing artifacts for real questions;
- and visible changes between review dates.

**What does *not* count as proof:**
- crate popularity charts;
- one-off “best crates for X” blog prose;
- LLM summaries without source routing;
- or a recommendation engine that cannot explain freshness and scope.

### 4) Tooling Contract
**Primary proof family:** observational truth burden + import-fidelity burden  
**Why this is the right burden:** this seam only matters if it can separate subject truth, discovery truth, graph/plan truth, execution truth, and adapter lossiness without pretending that one Cargo output already answers all of them.

**What must be proven in practice:**
- clear subject identity across package/workspace/member lanes;
- explicit import lanes for Cargo-native facts;
- side-by-side examples of strong versus lossy adapters;
- honest fallback states when upstream surfaces are incomplete;
- and at least one external consumer that benefits from the contract instead of another ad hoc integration.

**What credible v0 looks like:**
- a small reference layer;
- report/pack commands;
- an adapter/import corpus;
- lossiness notes across current surfaces;
- and one consumer handoff that reuses the same pack.

**What does *not* count as proof:**
- one `cargo metadata` dump;
- one `--unit-graph` decoder;
- a `rust-project.json` bridge that silently widens scope;
- or a daemon story that redefines the seam as “keep a server warm”.

### 5) Semantic Context / StableMIR-adjacent work
**Primary proof family:** import-fidelity burden  
**Why this is the right burden:** the value here is enormous, but it is easy to overread unstable or versioned semantic surfaces. docs.rs rustdoc JSON explicitly warns about `format_version`, and the `rustc_public` / StableMIR line still looks more like a substrate with release automation and version discipline than a turnkey ecosystem product.

**What must be proven in practice:**
- exact subject capture;
- explicit schema and freshness posture;
- imported versus inferred semantic facts kept separate;
- query/result receipts that show why an answer is strong or weak;
- and downstream consumers that improve without silently depending on compiler internals.

**What credible v0 looks like:**
- a narrow semantic pack;
- version-aware import and adapter layers;
- bounded query artifacts;
- and one or two downstream wins such as stronger semver or docs reasoning.

**What does *not* count as proof:**
- a broad “semantic API for everything” pitch;
- scraping plus confidence theater;
- or one nightly-only happy path that cannot survive version churn.

### 6) Compatibility Claims / Migration / Public API
**Primary proof family:** import-fidelity burden with stronger witness checks where possible  
**Why this is the right burden:** this seam is about making claims reviewable — not about pretending a single MSRV field, one API diff, or one lint can own the verdict.

**What must be proven in practice:**
- support-envelope facts, public-boundary facts, and observed verification facts stay separate;
- imported claims can be overridden or downgraded explicitly;
- stronger checks are visible as stronger, not as silent defaults;
- and downstream consumers can see what kind of compatibility claim they are importing.

**What credible v0 looks like:**
- claim-family routing;
- report packs with proof-strength markers;
- witness-backed or semver-backed stronger checks where available;
- and explicit “unknown / partial / not verified here” states.

**What does *not* count as proof:**
- one matrix badge;
- one publish gate;
- or one API diff tool pretending to answer platform/runtime/support compatibility too.

### 7) Package Intake Gateway
**Primary proof family:** operational-boundary burden  
**Why this is the right burden:** the seam lives at a live registry/download/extraction/policy boundary. Recent security and notification-policy changes show why intake work has to prove route and response posture, not just give consumers one more reputation score.

**What must be proven in practice:**
- exact route and payload facts for the package being admitted;
- extraction/staging receipts;
- explicit alternate-registry posture;
- operator-facing handoffs for missing or stale evidence;
- and fail-closed behavior when core intake facts are absent.

**What credible v0 looks like:**
- route and payload reports;
- review packs for locked-down or regulated intake lanes;
- clear RustSec / registry / Cargo handoffs;
- and post-incident receipts that show what changed.

**What does *not* count as proof:**
- a trust-score portal;
- package popularity rankings;
- advisory scraping without route evidence;
- or intake UX that cannot explain what was actually verified.

### 8) Safety-Critical Readiness Commons
**Primary proof family:** consortium-readiness burden  
**Why this is the right burden:** the safety-critical post is unusually explicit that earlier technically plausible work stalled because there was no durable owner and no shared maintenance commitment. This seam is only honest if it proves shared stewardship along with technical readiness.

**What must be proven in practice:**
- named readiness profiles and checklists;
- company- or institution-backed maintenance commitments for key proof lanes;
- real mixed-language and tooling-boundary scenarios;
- dependency lifecycle posture;
- async/runtime qualification posture where relevant;
- and renewal receipts over time.

**What credible v0 looks like:**
- a narrow readiness profile family;
- attachable evidence bundles;
- explicit “ready / partial / blocked / research” verdicts;
- and at least one company-backed proving ground that commits to upkeep.

**What does *not* count as proof:**
- a manifesto;
- a certification-adjacent badge;
- one audited demo;
- or a “Rust is ready for safety-critical” claim without shared requirement ownership.

### 9) Roadmap substrates: Cranelift local-dev acceleration, relink-don’t-rebuild, build-std, Rust-for-Linux stable tooling
**Primary proof family:** narrow leverage burden  
**Why this is the right burden:** these are important, but they are usually misread when they are judged as if they were public-platform epics. Their job is to prove leverage at a narrow, real substrate boundary.

**What must be proven in practice:**
- the lane is sharply named;
- the measurable win is real for that lane;
- the compatibility or stabilization story is explicit;
- and the contribution does not pretend to solve a much broader ecosystem problem than it really does.

**What credible v0 looks like:**
- one narrow productivity or stabilization win;
- one honest compatibility envelope;
- and one clear statement of what later consumers could import if it succeeds.

**What does *not* count as proof:**
- turning a substrate into a total strategy;
- using a local acceleration win to claim full build-story completion;
- or confusing upstream experimentation with a ready ecosystem platform.

## Proof-ripeness: which strong contributions are easiest to prove *now*
This is **not** the same as overall importance.
It answers a narrower question: which worthy contributions currently have the ripest proving grounds and the clearest first evidence burden?

### 1) Build-State Evidence
Ripest now because Cargo build-analysis and build-dir work create real measurable proving grounds, and because the pain is broad.

### 2) Package Intake Gateway
Operationally narrower, but the proving ground is live and concrete because the route/extraction/security boundary already exists and incidents make the failure modes legible.

### 3) Feedback Loop / Debuggability Acceptance
Clear burden and clear pain, but proof is heavier because it requires cross-tool coordination and a shared corpus.

### 4) Adoption Navigation + Ecosystem Atlas
Important and buildable, but only honest once imported evidence and renewal discipline are already in place.

### 5) Compatibility Claims / Migration / Public API
Powerful once import and witness layers are reusable, but still easier to overclaim than the top two.

### 6) Safety-Critical Readiness Commons
Strategically major, but proof remains owner-heavy because real readiness receipts require committed institutions.

### 7) Semantic Context / StableMIR-adjacent work
Potentially huge multiplier, but still best treated as substrate-shaping proof rather than immediate broad-epic proof.

## Cross-seam graduation ladder
The archive should now assume a stronger default proof ladder for worthy contributions:

### Step 0 — named proving ground
The contribution names one real lane and one real failure mode.

### Step 1 — canonical artifact family
It emits a pack, receipt, corpus, or profile that another human or tool can inspect.

### Step 2 — negative cases
It shows partial, unsupported, stale, regressed, or blocked outcomes explicitly.

### Step 3 — one real consumer decision
Someone outside the builders uses the artifact to make a real decision differently.

### Step 4 — renewal or repeated execution
The same proving ground is revisited or replayed, and the artifact still makes sense.

### Step 5 — stewardable path
The contribution can explain who keeps the proving ground alive and what maintenance burden follows.

If a contribution cannot pass Step 2, it is still mostly a demo.
If it cannot pass Step 3, it has not yet become an ecosystem answer.
If it cannot pass Step 5, it is not yet a serious funding or canon candidate.

## What this note changes in practice
Future “worthy contribution” comparisons should now say not only:
- what the candidate is,
- what it should ship,
- and what vehicle it should start in,

but also:
- what proof family it carries,
- what the first credible proving ground is,
- what the first canonical artifact family is,
- what negative cases are mandatory,
- and what graduation line should be required before widening.

That is the missing practical layer between “good idea” and “worthy ecosystem contribution”.
