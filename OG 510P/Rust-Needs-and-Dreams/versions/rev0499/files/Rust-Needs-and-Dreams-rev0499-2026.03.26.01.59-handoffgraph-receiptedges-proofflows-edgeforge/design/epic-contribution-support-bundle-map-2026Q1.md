# Design: Epic contribution support-bundle map (2026Q1)

## Goal
The archive now has:
- a broad ladder for what matters most;
- scorecards for comparing already-worthy contributions;
- a delivery matrix for what each candidate should ship;
- an incubation map for what vehicle each candidate should start in;
- a proof-burden map for what each candidate must prove;
- a bet-sizing map for what capital band each candidate honestly needs; and
- a compounding map for what unlocks later work.

What it still lacked was one sharper cross-seam answer to a different practical question:

> once we know a contribution is worthy, **what exactly should it ask for from the ecosystem**? Which asks belong to upstream teams, which to maintainers, which to vendors or operators, which to a consortium, which to the Foundation, and which asks are category errors that would distort the work before it lands?

This note is the archive's answer to that question.
It does **not** rerank the broad ladder.
It does **not** promote a new frontier.
It does **not** replace seam-local blueprints.
It explains which worthy contributions want which **support bundles**, what those bundles should contain in practice, what order those asks should happen in, and which tempting requests should be **refused because they mismatch the contribution**.

Read with:
- `design/epic-contribution-bet-sizing-map-2026Q1.md`
- `design/epic-contribution-incubation-map-2026Q1.md`
- `design/epic-contribution-delivery-matrix-2026Q1.md`
- `design/epic-contribution-proof-burden-map-2026Q1.md`
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
The public Rust picture is no longer just telling us what hurts or even what deserves funding.
It is now telling us something more operational:
**serious work lands only when the ask bundle matches the seam.**

The 2026 goals overview says new goals may be added during the year only when all required resources — including champions and funding — are already known. The task-owners guidance says goals without owners can only be accepted provisionally. That means execution realism in Rust now includes precommitted support shape, not just a good idea.
https://rust-lang.github.io/rust-project-goals/2026/
https://rust-lang.github.io/rust-project-goals/about/owners.html

The January 2026 program-management update says roadmaps and application areas are meant to help focus industry funding, and explicitly asks teams to review proposed goals against capacity and champions. That means the ecosystem is already moving toward "support bundle first" thinking even when it does not call it that.
https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/

The Rust Foundation's 2026–2028 strategy distinguishes stable infrastructure, sustainable maintenance, adoption & innovation, and community support. The Foundation's January 2026 annual-report/strategy post says the Foundation raised $5.1M in 2025 and invested $2.7M directly into Rust Project and community support, including maintenance work, infrastructure, grants, and ecosystem events. That means there are now multiple real institutional support lanes, not one undifferentiated pile of sponsorship.
https://rustfoundation.org/strategic-plan/
https://rustfoundation.org/media/annual-report-strategy-2025/

The Maintainers Fund announcement says direct long-term maintainer support is now an explicit vehicle. The community-grants page says the Foundation also has grants/support lanes for community members and organizers, though it is currently redesigning that program. Those are important because some worthy asks are really "fund the people and renewal work" rather than "start a new platform".
https://rustfoundation.org/media/announcing-the-rust-foundation-maintainers-fund/
https://rustfoundation.org/grants/

The Rust Innovation Lab says there is now a real fiscal-sponsorship / governance / legal / administration home for funded Rust projects, but it also says participating projects bring their own vision and funding or sustainable financial model. That means the Lab is a real answer for some mature commons and keystone projects, but not a universal first home for every worthy bet.
https://blog.rust-lang.org/2025/09/03/welcoming-the-rust-innovation-lab/
https://rustfoundation.org/media/rust-foundation-launches-rust-innovation-lab-with-rustls-as-inaugural-project/

On the technical side, current signals remain asymmetric. The March 2026 challenges writeup and the 2025 State of Rust survey still cluster broad pain around compile/resource taxes, debugging friction, async friction, and ecosystem-choice problems. Cargo build-analysis is still turning toward recorded rebuild reasons and richer reports. The debugging survey says truly stellar support must span debuggers and operating systems. The March 2026 Cargo advisory shows that some urgent work lives at an operational boundary where registry operators and security response are part of the ask bundle. And the safety-critical writeup keeps proving that some worthy contributions only become real when the ask includes shared maintenance and industry participation.
https://blog.rust-lang.org/2026/03/20/rust-challenges/
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

The missing layer is therefore not another ranking rewrite.
It is an **ask-discipline map**.

## Headline answer
The archive should now assume:

> not every worthy Rust contribution wants "funding" in the same shape.
> The honest question is not just how much money or how many people.
> The honest question is **who must say yes, to what, in what order, and for what bounded reason**.

That means future portfolio work must keep these distinct:
- **importance** — how strategically worthy the seam is;
- **delivery shape** — what it should ship;
- **incubation vehicle** — where it should start;
- **proof burden** — what it must prove;
- **bet size** — what staffing/runway it honestly needs;
- **support bundle** — which concrete asks belong to which actors;
- **sequencing of asks** — what must happen before larger institutionalization is even honest; and
- **wrong ask** — what kind of support would distort or overbuild the seam.

## The seven support-bundle lanes

### 1) Upstream team ask
Ask this lane for:
- champions;
- design meetings;
- review time;
- acceptance criteria;
- unstable experimentation permission;
- publication or stabilization guidance.

Use when:
- the contribution touches Cargo, rustc, rustdoc, target support, standard tooling, or core governance assumptions;
- the real blockage is lack of review or lack of an accepted boundary.

Do not ask this lane for:
- ongoing product operations;
- routine hosted support;
- vague endorsement without bounded technical scope.

### 2) Maintainer-time ask
Ask this lane for:
- sustained implementation time;
- janitorial work;
- review continuity;
- issue triage;
- refactors and release continuity;
- renewal and support work that is easy to undervalue but multiplicative.

Use when:
- the best move is to strengthen an existing upstream or shared-commons lane;
- the missing thing is continuity more than invention.

Do not ask this lane for:
- a net-new institution or hosted platform as proof of seriousness.

### 3) Companion-team ask
Ask this lane for:
- one to three maintainers or engineers;
- bounded tooling/product work;
- fixture and adapter maintenance;
- local-first UX and CI/import layers;
- a reusable artifact family.

Use when:
- a contribution can become real as a bootstrap companion build without needing large governance machinery first.

Do not ask this lane for:
- coalition-grade acceptance guarantees;
- universal schema empires;
- a heavy service business before the artifact family is even useful.

### 4) Operator / vendor exemplar ask
Ask this lane for:
- real workspaces and specimen repos;
- shadow/private twins of proving grounds;
- incident examples;
- CI or fleet constraints;
- cross-platform tuples;
- engineers who can verify whether the artifact is useful in practice.

Use when:
- the contribution claims to reflect real operator or product reality;
- exemplar fidelity matters more than brand endorsement.

Do not ask this lane for:
- product strategy control;
- broad governance power disproportionate to the proving-ground contribution.

### 5) Consortium / interoperability ask
Ask this lane for:
- multiple tool owners;
- acceptance tuples;
- shared device or OS labs;
- cross-vendor compatibility targets;
- recurring neutral coordination;
- agreement on regression receipts and escalation rules.

Use when:
- the contribution only becomes honest if several independent tools or institutions keep it working together.

Do not ask this lane for:
- a generic steering committee without concrete tuples, fixtures, or proof lanes.

### 6) Foundation / institutional ask
Ask this lane for:
- fiscal sponsorship;
- legal and administrative support;
- security or infrastructure staffing;
- neutral convening;
- grants and maintainer support;
- support for keystone commons with real long-term stewardship needs.

Use when:
- the contribution needs neutral governance or durable administration that a small companion team cannot plausibly provide.

Do not ask this lane for:
- early prestige;
- a substitute for proving the artifact family;
- blanket institutionalization of every worthy tool idea.

### 7) Non-ask / refusal lane
For every serious contribution, state explicitly what it should **not** ask for yet.
Typical refusals:
- hosted platform first;
- giant marketplace first;
- Cargo replacement dreams;
- universal ranking/score portals;
- institution aura without artifacts;
- one-off corporate sponsorship replacing shared proof lanes.

## What a good support bundle looks like
A good bundle is:
- **bounded** — names concrete asks, not vibes;
- **sequenced** — starts with the smallest truthful dependency;
- **proof-coupled** — every ask is tied to a proving ground or artifact family;
- **anti-aura** — does not ask for institution shape before artifact truth;
- **portable** — leaves reusable receipts behind if the hosted layer disappears.

A bad bundle is:
- everything at once;
- mostly prestige or access theater;
- detached from proving grounds;
- missing the actual owners who must review the work;
- or written as if all support can be replaced by money alone.

## The current best support bundles by candidate

### Build-State Evidence
Primary ask bundle:
- **companion-team ask** for the local-first report/pack tooling;
- **upstream team ask** to Cargo for review windows, boundary discussion, and import-surface honesty;
- **operator/vendor exemplar ask** for real workspaces and rebuild scenarios.

Why this fits:
- build pain is broad;
- Cargo is only now making recorded build evidence more available;
- the first proof lane is repeatable without a big institution;
- but the work will be unconvincing without real workspace diversity.

What the first bundle should contain in practice:
- 1–2 maintainers building the report/pack layer;
- 3–6 exemplar workspaces across different product shapes;
- one upstream liaison loop with Cargo and rustc-perf adjacent contributors;
- explicit artifact family, fixture corpus, and renewal receipts.

What it should **not** ask for:
- a foundation-hosted performance portal first;
- a universal build daemon;
- a consortium before the pack family has proven itself on exemplars.

Default reading:
- strongest broad first build;
- strongest first support bundle to fund now;
- and the clearest case where money without exemplar access would still be insufficient.

### Feedback Loop / Debuggability Acceptance
Primary ask bundle:
- **consortium / interoperability ask** across debugger owners, IDE/plugin owners, and platform tuples;
- **operator/vendor exemplar ask** for real async-heavy and cross-platform debugging cases;
- a narrower **companion-team ask** only for corpus/fixture tooling, not for the whole answer.

Why this fits:
- the debugging survey explicitly frames quality as cross-debugger and cross-OS;
- a small team can build fixtures and receipts, but not guarantee ecosystem-wide acceptance alone.

What the first bundle should contain in practice:
- named tuples (OS + debugger + editor/plugin + runtime style);
- a shared acceptance corpus;
- regression receipts and escalation rules;
- recurring coordination between the tool owners whose combinations matter most.

What it should **not** ask for:
- a single debugger fork pretending to solve the ecosystem;
- a generic foundation grant with no tuple matrix;
- a one-team UX demo treated as ecosystem proof.

Default reading:
- clearest second serious build overall;
- clearest consortium-grade ask bundle;
- and the strongest case where coalition support is part of the contribution, not just a scaling afterthought.

### Adoption Navigation + Ecosystem Atlas
Primary ask bundle:
- **companion-team ask** for editorial/defaults tooling and renewal receipts;
- **operator/vendor exemplar ask** for real lane defaults and migration stories;
- selective **maintainer-time ask** for docs/defaults review and freshness signals;
- small **Foundation/community support asks** when community editorial capacity needs funding.

Why this fits:
- the pain is real, but the work stays honest only when guidance is renewed and bounded;
- it wants real stories and defaults more than it wants heavy governance.

What the first bundle should contain in practice:
- renewal queue discipline;
- default-card maintenance;
- exemplar-backed lane guidance;
- editorial review loops with maintainers and practitioners.

What it should **not** ask for:
- a global crate-scoring portal;
- institution aura as a substitute for freshness;
- broad recommendation claims without renewal receipts.

Default reading:
- strongest consumer-facing widener;
- asks for an editorial corps and exemplar donors more than for a lab or consortium.

### Tooling Contract / Shared Spine / Compatibility Claims
Primary ask bundle:
- **companion-team ask** for protocol, validator, and adapter work;
- **upstream team ask** for boundary review and publication posture;
- **operator/vendor exemplar ask** for real consuming tools and CI paths;
- occasional **maintainer-time ask** where upstream adapters or public surfaces need continuity.

Why this fits:
- these are hidden multipliers and routing layers;
- they become valuable by importing existing evidence honestly, not by owning the whole public surface.

What the first bundle should contain in practice:
- thin schemas or envelopes;
- compatibility gates;
- adapters with explicit lossiness;
- fixture corpora and exemplar consumers.

What it should **not** ask for:
- a universal registry or mega-schema;
- full institutionalization before adapters exist;
- claims of permanence stronger than the imported surfaces support.

Default reading:
- strongest hidden support-bundle cluster after Build-State Evidence;
- a place where upstream review and exemplar consumers matter more than marketing or heavy fundraising.

### Semantic Context / StableMIR-adjacent work
Primary ask bundle:
- **upstream team ask** for publication posture and design constraints;
- **maintainer-time ask** for the hard substrate work itself;
- optional **companion-team ask** for bounded consumer tools once a public-enough surface exists.

Why this fits:
- the leverage is real, but the lane is close to compiler internals and public-surface maturity;
- sidecar products should follow, not lead.

What it should **not** ask for:
- consumer-facing platform work that outruns public-surface reality;
- keystone institutional posture before the publication contract is clear.

Default reading:
- strongest upstream sponsorship lane in the top band;
- should usually import support through owners and maintainers first.

### Package Intake Gateway
Primary ask bundle:
- **operator/vendor exemplar ask** from registry operators, security teams, and internal package consumers;
- **upstream team ask** from crates.io/Cargo/security owners on route boundaries and fail-closed posture;
- a focused **companion-team ask** for the bridge tooling and review artifacts;
- optional **Foundation/security initiative ask** where neutral incident-handling or convening materially helps.

Why this fits:
- this seam sits at a live operational and security boundary;
- the March 2026 advisory shows real route/extraction consequences;
- but it still does not need a trust-score marketplace to be useful.

What it should **not** ask for:
- a public ranking portal first;
- a vague “more secure crates” grant without route/policy detail;
- cargo-replacement ambitions.

Default reading:
- strongest operator-shaped bridge;
- one of the clearest cases where operator participation is non-optional proof input.

### Safety-Critical Readiness Commons
Primary ask bundle:
- **consortium / interoperability ask** from regulated-domain practitioners;
- **Foundation / institutional ask** for neutral coordination and program support;
- **operator/vendor exemplar ask** for domain-specific proving grounds and maintenance commitments;
- selective **maintainer-time asks** for shared checklists and long-lived readiness artifacts.

Why this fits:
- the gap is not just a technical missing library;
- it is a readiness commons that depends on shared ownership, maintenance, and qualified exemplars.

What the first bundle should contain in practice:
- recurring working groups with named stakeholders;
- maintained readiness packs and checklists;
- exemplar systems and policy/interop overlays;
- explicit long-term stewardship commitments.

What it should **not** ask for:
- one heroic crate;
- one flashy industry demo;
- a companion tool pretending to replace consortium-grade governance.

Default reading:
- clearest keystone / consortium ask bundle in the archive;
- should widen only when shared ownership is already real.

## The ask-sequencing rule
For almost every candidate, the archive should now prefer this order:
1. prove the artifact family;
2. secure the minimal upstream review/support loop;
3. secure exemplar donors and proving grounds;
4. only then widen into consortium or institution shape if the proof burden actually demands it.

Exceptions exist, but they are rare.
Debugging acceptance and safety-critical readiness are the clearest ones because coalition support is part of the problem definition itself.

## Current ranking by support-bundle ripeness
### Ripest to ask for now
1. **Build-State Evidence** — clear artifact family, broad pain, real upstream surfaces, exemplars available.
2. **Tooling Contract / Shared Spine / Compatibility Claims** — thin companion/protocol asks with obvious upstream liaison needs.
3. **Adoption Navigation + Ecosystem Atlas** — editorial/defaults support and exemplar donation are straightforward.

### Real but coalition-shaped
4. **Feedback Loop / Debuggability Acceptance** — valuable now, but only honest with cross-tool tuples and ongoing coordination.
5. **Package Intake Gateway** — urgent and buildable, but depends on operator/security boundary participation.

### Real but institution/program-shaped
6. **Safety-Critical Readiness Commons** — worthy, but the ask bundle is large and must be shared from the start.

### Primarily upstream-support shaped
7. **Semantic Context / StableMIR-adjacent work** — high leverage, but much of the honest ask is still owner/maintainer/upstream review time.

## Wrong-shape refusal rules
The archive should now refuse these moves faster:
- treating a Foundation or Innovation Lab mention as proof that a contribution should start institution-sized;
- treating maintainer funding as equivalent to a complete product plan;
- treating one vendor's sponsorship as evidence that coalition support is unnecessary;
- treating coalition-grade work as if a two-person team can guarantee it alone;
- treating a generic grant or sponsorship request as sufficient when the real missing thing is exemplar access or upstream review;
- and treating support bundles as interchangeable with ranking.

## Consequence for future revisions
Future portfolio revisions should now answer four questions explicitly whenever they recommend a serious build:
1. **who must say yes first**;
2. **what exact support is being asked from them**;
3. **what support is intentionally not being asked for yet**; and
4. **what artifact or proof lane makes the ask justified**.

That is the archive's best defense against fake realism.
A contribution is not operationally real because it has a budget line.
It becomes operationally real when its support bundle matches its seam.
