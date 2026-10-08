# Design: Epic contribution renewal-burden map (2026Q1)

## Goal
The archive now has:
- a broad ladder for what matters most;
- scorecards for comparing already-worthy contributions;
- a delivery matrix for what each candidate should ship;
- an incubation map for what vehicle each candidate should start in;
- a proof-burden map for what each candidate must prove;
- a bet-sizing map for what capital band each candidate honestly needs;
- a compounding map for what unlocks later work;
- a shared-spine execution blueprint for common artifact glue;
- an exemplar federation for shared proving terrain; and
- a support-bundle map for what each worthy contribution should ask from the ecosystem.

What it still lacked was one sharper cross-seam answer to a different practical question:

> once we know a contribution is worthy, **what ongoing renewal burden does it create**? What has to be refreshed every release, every tuple, every incident, every quarter, or every standards cycle to keep the contribution honest after the launch blog post is over?

This note is the archive's answer to that question.
It does **not** rerank the broad ladder.
It does **not** promote a new frontier.
It does **not** replace seam-local blueprints.
It explains which worthy contributions create which **renewal burdens**, what cadence those burdens run on in practice, what should be automated versus staffed, which contributions are deceptively expensive to keep current, and which tempting project shapes should be refused because they smuggle in an unstaffed permanent obligation.

Read with:
- `design/epic-contribution-support-bundle-map-2026Q1.md`
- `design/epic-contribution-bet-sizing-map-2026Q1.md`
- `design/epic-contribution-proof-burden-map-2026Q1.md`
- `design/epic-contribution-incubation-map-2026Q1.md`
- `design/epic-contribution-delivery-matrix-2026Q1.md`
- `design/epic-contribution-compounding-map-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/portfolio-exemplar-federation-2026Q1.md`
- `design/shared-spine-execution-blueprint-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/tooling-contract-execution-blueprint-2026Q1.md`
- `design/compatibility-claims-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- `design/semantic-context-execution-blueprint-2026Q1.md`

## Why this note is needed now
Current Rust signals do not only say what hurts and what deserves help.
They also say that **some contributions are cheap to launch but expensive to keep honest**.

Rust's 2026 goals overview says contributors propose goals and teams accept them, with champions helping to secure review and navigation support. The design axioms say goals are a contract between owners and project teams. That means the ecosystem is already explicit that a good idea without durable execution support is not an honest plan.
https://rust-lang.github.io/rust-project-goals/2026/
https://rust-lang.github.io/rust-project-goals/about/design_axioms.html

The January 2026 program-management update says roadmaps and application areas are meant to focus industry funding. That makes recurring capacity and renewal obligations first-class portfolio questions rather than afterthoughts.
https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/

The Maintainer Fund design post says Rust ships a nightly every day and a stable release every six weeks, and frames maintainer work as keeping things working tomorrow, not just landing novel features once. That is almost a direct statement of renewal burden.
https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/

The Rust Foundation's 2026–2028 strategy elevates stable infrastructure and sustainable maintenance as core pillars. That means the ecosystem now has institutional language for recurring upkeep, not just invention.
https://rustfoundation.org/strategic-plan/

The March 2026 challenges writeup and the 2025 State of Rust survey still cluster pain around compilation/resource taxes, debugging friction, tacit knowledge, uneven maturity, and canonical-doc reliance while editor / LLM mediation rises. That means many seemingly “content” or “tooling” bets are really ongoing renewal bets in disguise.
https://blog.rust-lang.org/2026/03/20/rust-challenges/
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

The March 2026 build-dir-layout testing call says a crater run will not cover everything and explicitly asks downstream tools and processes to retest against nightly changes. The debugging survey says support quality varies across debuggers and operating systems and must keep working across debugger versions and internal representation changes. Those are not one-time proof problems; they are continuing tuple-renewal problems.
https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

The crates.io malicious-crate notification policy change and the March 2026 Cargo advisory show that package-security work includes live operational response and policy tuning, not just better dashboards. The FLS upkeep goal says safety-critical Rust needs a capability to keep the FLS updated at the cadence required by its users and stakeholders. Those are explicit reminders that some worthy seams are long-lived service or consortium obligations.
https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html

The missing layer is therefore not another ranking refresh.
It is a **renewal-burden map**.

## Headline answer
The archive should now assume:

> every worthy contribution has two costs:
> the cost to make it real the first time,
> and the cost to keep it true after reality moves.
>
> Future portfolio work must stop smuggling the second cost inside vague words like “maintenance”, “docs”, “ownership”, or “adoption”.

That means future portfolio work must keep these visibly distinct:
- **importance** — how strategically worthy the seam is;
- **delivery shape** — what it should ship;
- **incubation vehicle** — where it should start;
- **proof burden** — what it must prove;
- **bet size** — what staffing/runway it honestly needs;
- **support bundle** — who must say yes and what they supply;
- **renewal burden** — what recurring refresh, tuple coverage, incidents, or editorial upkeep it creates;
- **automation share** — what part of renewal can be machine-assisted;
- **human steward share** — what part still needs human review or operational ownership;
- and **wrong upkeep story** — what kind of “we will just keep it updated” hand-wave should be refused.

## The six renewal-burden families

### 1) Release-cadence evidence renewal
Use this family when a contribution must keep pace with toolchain releases, nightly experiments, unstable flags, target defaults, or command-surface changes.

Typical burden:
- rerun exemplars on new stable and nightly windows;
- reimport or diff machine-readable outputs;
- update fixtures, adapters, or compatibility notes;
- keep lineages tied to actual toolchain versions.

Good fits:
- Build-State Evidence
- Tooling Contract
- Shared Spine adapters
- Compatibility Claims
- narrow Semantic Context imports

Wrong story:
- “We proved it once on one release, therefore it is maintained.”

### 2) Tuple-matrix acceptance renewal
Use this family when the real promise spans tool / OS / target / debugger / runtime combinations rather than one surface.

Typical burden:
- keep a living matrix of accepted tuples;
- rerun representative scenarios across debugger or target changes;
- accept partial green states and keep failure lineage;
- maintain enough donor environments to avoid paper compliance.

Good fits:
- Feedback Loop / Debuggability Acceptance
- target-facing Compatibility Claims
- some async or browser / mobile / edge guidance bundles

Wrong story:
- “We tested on one debugger and one OS, therefore the ecosystem answer exists.”

### 3) Editorial/default renewal
Use this family when the contribution emits defaults, maps, recommendations, curation, or class-specific guidance.

Typical burden:
- periodic review against ecosystem drift;
- explicit expiry or freshness receipts;
- deletion / demotion of stale recommendations;
- bounded guidance that can say “unknown” instead of bluffing.

Good fits:
- Adoption Navigation + Ecosystem Atlas
- class defaults and starter guidance
- some consumer-facing Compatibility Claims layers

Wrong story:
- “We published a beautiful map, therefore the map is still right.”

### 4) Operational / incident renewal
Use this family when the contribution sits on a security, package-intake, registry, CI, or operator boundary.

Typical burden:
- on-call or named response ownership;
- incident routing and policy adjustment;
- advisory integration;
- audit or mitigation playbooks;
- logs, notices, and response receipts.

Good fits:
- Package Intake Gateway
- some defect-escalation or incident-routing layers
- operator-facing parts of Compatibility Claims

Wrong story:
- “We built a portal, therefore operations are handled.”

### 5) Stewardship / consortium renewal
Use this family when the contribution depends on sustained cross-organization participation, standards alignment, or domain governance.

Typical burden:
- regular working sessions;
- charter / scope upkeep;
- contributor recruitment and retention;
- document and checklist updates;
- continuity across staff turnover.

Good fits:
- Safety-Critical Readiness Commons
- debugger consortium layers if they become multi-vendor
- FLS upkeep capability

Wrong story:
- “We shipped one technical artifact, therefore the shared program now exists.”

### 6) Substrate watch renewal
Use this family when the contribution mostly consumes or exposes upstream-enabling surfaces and mainly needs careful tracking rather than a thick public service.

Typical burden:
- watch upstream milestones and breakage signals;
- update narrow import adapters;
- keep version and caveat boundaries sharp;
- avoid promising a public product before the substrate stabilizes.

Good fits:
- StableMIR / `rustc_public` consumers
- rustdoc JSON or libtest-JSON consumers
- relink / build-dir / build-analysis watchers
- some Shared Spine and Semantic Context lanes

Wrong story:
- “Because the substrate is exciting, we should build a permanent public platform around it immediately.”

## Renewal-adjusted comparison of the strongest worthy contributions

### Build-State Evidence
Renewal family:
- primarily **release-cadence evidence renewal** with a smaller substrate-watch component.

Why the burden is real:
- Cargo build-analysis and build-dir work are still moving;
- downstream tools depend on internal details because some Cargo features are still missing;
- exemplar replays and report packs must be rerun across releases to stay trustworthy.

Why the burden is still acceptable:
- much of it can be automated with fixed exemplar worlds, report packs, and lineage receipts;
- the burden aligns with one of Rust's most visible recurring pain taxes;
- and the artifacts it leaves behind remain useful even when UI layers change.

What the first honest upkeep model looks like:
- a small exemplar federation;
- automatic reruns on stable/nightly windows;
- explicit diff receipts;
- and a policy that old evidence expires rather than silently remaining green forever.

Wrong shape to refuse:
- a polished hosted dashboard with no renewable exemplar corpus underneath it.

### Feedback Loop / Debuggability Acceptance
Renewal family:
- primarily **tuple-matrix acceptance renewal**.

Why the burden is real:
- debugger support varies across debuggers and operating systems;
- async support, expression evaluation, and visualizers can regress independently;
- and “keeps working” is part of the promise, not a bonus.

Why the burden is heavy:
- much less can be fully automated than build evidence;
- donor environments and cross-tool acceptance still matter;
- and good local demos do not substitute for matrix continuity.

What the first honest upkeep model looks like:
- a bounded accepted-tuple matrix;
- reference scenarios rather than every project on earth;
- visible yellow/red states instead of fake universal support;
- and consortium-grade donors before big promises.

Wrong shape to refuse:
- one sidecar tool claiming to have solved “Rust debugging” without recurring cross-tuple acceptance work.

### Adoption Navigation + Ecosystem Atlas
Renewal family:
- primarily **editorial/default renewal**.

Why the burden is real:
- recommendations, defaults, and map layers rot quickly;
- docs remain canonical while LLM/editor mediation rises;
- and stale guidance is often worse than missing guidance because it is confidently repeated.

Why the burden is underappreciated:
- the launch artifact looks like content,
- but the real work is recurring review, demotion, class-bound freshness, and explicit uncertainty.

What the first honest upkeep model looks like:
- bounded project-class cards;
- freshness windows and renewal receipts;
- explicit “unknown / contested / changing” states;
- and strong imports from earlier evidence and compatibility layers.

Wrong shape to refuse:
- a giant evergreen recommendation portal with no expiration discipline.

### Tooling Contract, Shared Spine, and narrow Semantic Context
Renewal family:
- mostly **release-cadence evidence renewal** plus **substrate watch renewal**.

Why the burden is real:
- these layers live near Cargo, rustdoc JSON, libtest JSON, build-dir changes, and other moving machine-facing surfaces;
- their main failure mode is silent adapter rot.

Why the burden is manageable:
- the scope can remain thin;
- fixtures and validators help catch drift early;
- and the archive already has a doctor loop and corpus-style maintenance patterns.

What the first honest upkeep model looks like:
- versioned fixtures and contract validators;
- narrow adapters instead of giant product surfaces;
- explicit unstable-vs-stable posture;
- and aggressive refusal of hosted-platform expansion.

Wrong shape to refuse:
- turning thin protocol and adapter work into a general ecosystem operating system.

### Compatibility Claims
Renewal family:
- mixed **release-cadence evidence renewal** and **editorial/default renewal**.

Why the burden is real:
- MSRV, target posture, docs.rs defaults, semver checks, and support claims all drift;
- the claims often sit at the boundary between machine evidence and human promise.

What the first honest upkeep model looks like:
- imported facts first;
- bounded claim families;
- renewable receipts for public claims;
- and clear expiration on inferred compatibility posture.

Wrong shape to refuse:
- a static compatibility badge farm detached from imported evidence.

### Package Intake Gateway
Renewal family:
- primarily **operational / incident renewal**.

Why the burden is real:
- registry and extraction boundaries are live security surfaces;
- advisories, audits, policy tuning, and alternate-registry communication all matter;
- and recent Rust signals keep showing that operator posture is part of the design.

Why the burden is narrow but intense:
- it is not the broadest first build,
- but the work is live, policy-shaped, and cannot be staffed like a passive data portal.

What the first honest upkeep model looks like:
- an operator-shaped bridge with named response owners;
- incident receipts and playbooks;
- strong advisory and registry inputs;
- and no fantasy that “trust scoring” replaces security operations.

Wrong shape to refuse:
- an aesthetic trust dashboard with no operational or policy loop.

### Safety-Critical Readiness Commons
Renewal family:
- primarily **stewardship / consortium renewal** with some editorial/default renewal.

Why the burden is real:
- readiness checklists, standards alignment, dependency-lifecycle guidance, and FLS continuity all require recurring human participation;
- some of the hardest work is document and process upkeep, not just software.

Why the burden is slow but serious:
- cadence may be slower than package security or release testing,
- but the burden cannot be wish-cast away because safety claims outlive the people who first wrote them.

What the first honest upkeep model looks like:
- a consortium or standards-linked commons;
- explicit cadence and charter;
- named maintainers for readiness artifacts;
- and a split between general readiness assets and domain-specific overlays.

Wrong shape to refuse:
- one crate or one PDF pretending to solve ecosystem readiness.

## Renewal-adjusted portfolio guidance

### What still deserves to be built first
**Build-State Evidence** remains the strongest broad first build.
The new reason to stay with it is not that its upkeep is trivial.
It is that its renewal burden is:
- directly aligned with recurring user pain,
- comparatively automatable,
- and capable of leaving behind reusable evidence receipts that later layers can import.

### What should not outrun its upkeep model
**Adoption Navigation** should still not be built “front door first” unless its renewal model is already budgeted.
Without explicit freshness windows, renewal receipts, and imports from earlier evidence layers, it collapses into stale advice theater.

### What is the easiest to underestimate
**Feedback Loop / Debuggability Acceptance** is the easiest strong candidate to underbudget.
Its v0 can look small, but its honest promise is matrix continuity, not just one elegant debugger integration.

### What needs named operations from day one
**Package Intake Gateway** should only be started with named operational ownership.
This is where a narrow bridge with the right response posture beats a broad portal with no one on point.

### What only becomes real with recurring human institutions
**Safety-Critical Readiness Commons** should be judged partly by its renewal charter.
If there is no plan for sustaining document, checklist, and standards-facing upkeep, the “commons” does not exist yet.

## Default archive rules after this note
1. Never discuss a worthy contribution's launch plan without also saying what part of it expires, drifts, or must be rerun.
2. Never confuse **proof burden** with **renewal burden**. A contribution can be easy to prove once and expensive to keep current.
3. Never confuse **bet size** with **renewal burden**. A small v0 may hide a large permanent upkeep tax.
4. Prefer contributions whose renewal receipts can be partially automated and lineaged into shared exemplar worlds.
5. Refuse any proposal whose upkeep story is only “the community will keep this updated”.
6. When a contribution mainly emits guidance, defaults, badges, or scores, require explicit expiry and demotion logic.
7. When a contribution mainly emits operator or safety promises, require named human owners and cadence before expansion.

## Anti-goals
Do **not** let this note become:
- an excuse to only fund cheap-to-maintain work,
- an excuse to demote worthy but institution-shaped programs,
- a new fake scalar that replaces rank, proof, vehicle, and support bundle,
- or a ritual where “automation” is used to erase human review where human review is the work.

## Default archive conclusion after this addition
- The broad ladder is unchanged.
- **Build-State Evidence** remains the strongest broad first build and now also the clearest **renewal-aligned first build**.
- **Feedback Loop / Debuggability Acceptance** remains the clearest heavy **tuple-renewal** build.
- **Adoption Navigation + Ecosystem Atlas** remains the clearest heavy **editorial-renewal** build.
- **Package Intake Gateway** remains the clearest **operational-renewal** bridge.
- **Safety-Critical Readiness Commons** remains the clearest **consortium-renewal** program seam.
- Future portfolio revisions should now keep **importance**, **delivery shape**, **vehicle**, **proof burden**, **bet size**, **support bundle**, and **renewal burden** separate before rewriting canon.
