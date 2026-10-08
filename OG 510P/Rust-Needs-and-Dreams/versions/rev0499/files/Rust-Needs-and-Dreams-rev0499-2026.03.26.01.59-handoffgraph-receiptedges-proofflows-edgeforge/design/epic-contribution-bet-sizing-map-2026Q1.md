# Design: Epic contribution bet-sizing map (2026Q1)

## Goal
The archive now has:
- a broad ladder for what matters most;
- comparative scorecards for worthy contributions;
- a delivery matrix for what each strong candidate should ship;
- an incubation map for what vehicle each candidate should start in; and
- a proof-burden map for what each candidate must prove before it deserves widening.

What it still lacked was one sharper cross-seam answer to a different practical question:

> once we know a contribution is worthy, **what size and kind of bet is honest**? What can a two-person team really ship, what needs a staffed bridge, what requires a vendor or maintainer coalition, and what should be funded upstream instead of launched as a new product?

This note is the archive's answer to that question.
It does **not** rerank the broad ladder.
It does **not** promote a new frontier.
It does **not** replace seam-local blueprints.
It explains which worthy contributions belong in which **capital band**, what kind of **staffing and runway** they need, what their first **fundable shape** should be, and which promising ideas should be **funded upstream instead of productized sideways**.

Read with:
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
The public Rust picture is no longer just telling us **what hurts**.
It is also telling us something about **what kind of support vehicle and capital posture can honestly move each class of problem**.

The January 2026 program-management update says the annual goals process now sits inside longer-lived roadmaps and application areas, and that those layers are meant to help focus industry funding. It also says teams are explicitly being asked to look at champions and capacity before goals are accepted. That means “worthy” is already entangled with real staffing and sponsor fit.
https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/

The project-goals owner guidance is even blunter: a goal needs owners to be fully accepted, and goals without owners can only be provisional. That means owner realism is not a repo preference; it is now part of Rust's own execution grammar.
https://rust-lang.github.io/rust-project-goals/about/owners.html

The Rust Foundation's 2026–2028 strategy explicitly names **stable infrastructure**, **sustainable maintenance**, and **adoption & innovation** as distinct pillars. That is a strong clue that the archive should stop treating every worthy contribution as if it wanted the same kind of funding or the same institutional backing.
https://rustfoundation.org/strategic-plan/

The Rust Foundation Maintainers Fund announcement says the Fund is meant to provide reliable, transparent, long-term support for maintainers and to direct support toward high-impact priorities in collaboration with Rust leadership. The December 2025 program-management update also says the Foundation plans to give the Project a total of $650k USD for 2026, supporting travel, compiler-ops, program management, and leaving room for experiments and maintainer support. That means the ecosystem now has real middle layers between “one volunteer” and “launch a startup”.
https://rustfoundation.org/media/announcing-the-rust-foundation-maintainers-fund/
https://blog.rust-lang.org/inside-rust/2025/12/19/program-management-update--end-of-2025/

The Rust Innovation Lab is another important signal: it exists to provide governance, legal, networking, marketing, and administration for funded Rust-based open source projects while leaving technical direction with the maintainers. That means the ecosystem now has a real keystone-incubation vehicle for some projects, but it also implies that not every worthy seam should be pushed into a lab-shaped home.
https://blog.rust-lang.org/2025/09/03/welcoming-the-rust-innovation-lab/

Cargo's current posture also matters. The 1.94 development-cycle post explicitly says Cargo cannot be everything to everyone because of its compatibility guarantees, and that plugins play an important part of the Cargo ecosystem. That is powerful evidence that some worthy contributions should remain bounded companion tools or bridges instead of trying to merge into Cargo or replace it.
https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

On the pain side, the evidence remains asymmetric. The compiler-performance survey says build pain is broad, with incremental rebuilds as the most common complaint, roughly 45% of former users citing long compile times as one reason they stopped using Rust, and 55% of respondents waiting more than ten seconds for a rebuild. The build-analysis goal then says Cargo still does not persist prior-build data beyond a few limited cases and is only now moving toward recorded rebuild reasons and timing history. That combination makes Build-State Evidence unusually ripe for a modest but high-leverage first build.
https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html

By contrast, the debugging survey frames “truly stellar” debugging as support across multiple debuggers, multiple operating systems, high-quality visualizers, first-class async support, and Rust-expression evaluation, while also warning that the experience can regress as debuggers and internal representations change. That is not a two-person sidecar problem; it is a cross-tool acceptance problem.
https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

The safety-critical writeup is similar. It says Rust is already deployed in real regulated systems, but that ecosystem support thins out as criticality rises, and recommends shared work on dependency lifecycle patterns, safety-case-friendly async requirements, and interop guidance. That is evidence for a consortium-grade commons, not an isolated crate.
https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

Finally, the funding page for Rust contributors makes it easier for individuals and small companies to sponsor people directly. That matters because the smallest honest bet is often not “start a new repo”, but “fund the maintainer or upstream owner whose work unblocks the ecosystem”.
https://blog.rust-lang.org/2025/12/08/making-it-easier-to-sponsor-rust-contributors/

The missing layer is therefore not another rank rewrite.
It is a **bet-sizing map**.

## Headline answer
The archive should now assume:

> not every worthy Rust gap should become the same size of project.
> Some gaps want direct maintainer sponsorship, some want a small companion build, some want a staffed bridge or commons, some want a consortium, and some want upstream sponsorship or keystone incubation rather than a new product at all.

That means future portfolio work must keep these distinct:
- **importance** — how strategically worthy the seam is;
- **delivery shape** — what it should ship;
- **incubation vehicle** — where it should start;
- **proof burden** — what it must prove;
- **bet size** — how much capital, staffing, and runway it honestly needs;
- **funding fit** — what kind of sponsor or operator should carry it; and
- **wrong financial shape** — what kind of “support” would distort or overbuild it.

## The five capital bands

### 1) Direct maintainer / upstream sponsorship lane
Best for work whose highest-leverage move is to strengthen the people already carrying a critical upstream lane.

What it looks like:
- direct contributor sponsorship;
- maintainer-fund support;
- project-priorities support;
- narrow grants for a specific upstream task family;
- no new public-facing product requirement.

Good signs:
- there is already a clear owner or team;
- the missing thing is continuity, review capacity, or sustained implementation time;
- the work is tightly coupled to upstream internals or governance.

Typical fits:
- upstream build-analysis progress;
- toolchain or compiler maintenance work;
- debugger visualizer upkeep inside existing toolchains;
- substrate work where a sidecar product would add noise.

Wrong shape:
- spinning up a new startup or giant side platform when the real need is maintainer time.

### 2) Bootstrap companion build
Best for work that a one- to two-maintainer team can ship as an artifact-first companion layer inside one or two quarters.

What it looks like:
- local-first or CI-importable outputs;
- useful without a hosted backend;
- bounded scope and explicit anti-goals;
- obvious fit as a plugin, report layer, or reviewable pack family.

Good signs:
- the seam has strong imported substrate already;
- the first proof lane can be narrow and repeated;
- the v0 can stay honest without pretending to be universal.

Typical fits:
- **Build-State Evidence** v0;
- narrow **Tooling Contract** or **Compatibility Claims** packs;
- a carefully bounded **Semantic Context** import lane;
- narrow verification or report layers that reuse current Cargo/docs.rs surfaces.

Wrong shape:
- requiring a service, marketplace, daemon, or ecosystem control plane before the seam is even useful.

### 3) Focused funded bridge or commons
Best for work that is still bounded, but now needs a small staffed team, explicit renewal work, or operator integration to remain useful.

What it looks like:
- two to four people or equivalent funded time;
- multiple pilot lanes;
- support or review handoffs;
- renewal, policy, or curation work that is central rather than incidental.

Good signs:
- the seam crosses from raw evidence into routing, review, or operator behavior;
- one maintainer cannot realistically keep the lane current alone;
- the value depends on repeated renewal or integration with a live service boundary.

Typical fits:
- **Package Intake Gateway**;
- **Adoption Navigation + Ecosystem Atlas** once the evidence spine exists;
- wider **Tooling Contract** import/reference work;
- some compatibility-routing or release-bridge layers.

Wrong shape:
- pretending the work can stay volunteer-only when it requires sustained operator judgment, editorial renewal, or security-boundary upkeep.

### 4) Consortium / interoperability program
Best for work whose proof burden requires cross-vendor tuples, shared fixtures, mixed ownership, or repeated acceptance receipts across organizations.

What it looks like:
- multiple participating organizations or tool owners;
- shared corpora, device labs, fixture suites, or acceptance matrices;
- issue-routing and regression receipts that no one vendor can honestly bless alone.

Good signs:
- the seam depends on debugger × OS × runtime × tool-version tuples;
- or on cross-language / cross-regulation coordination;
- or on upstream teams and downstream operators making shared commitments.

Typical fits:
- **Feedback Loop / Debuggability Acceptance**;
- some interop or async qualification lanes;
- acceptance programs that cannot be proven in one stack.

Wrong shape:
- a two-person product team claiming to “solve Rust debugging” from one IDE or one debugger.

### 5) Keystone institution or upstream substrate program
Best for work whose honest path is either long-lived institution-backed incubation or direct sponsorship of upstream substrate and stabilization work.

What it looks like:
- foundation or lab support;
- multi-year horizon;
- shared governance or maintainer-led institutional support;
- or deliberate upstream sponsorship where the right artifact is progress in Cargo, rustc, docs, or platform support itself.

Good signs:
- the seam is mostly substrate, stabilization, or standards/evidence work;
- there is no honest standalone product boundary yet;
- or the work needs governance, legal, and continuity support beyond engineering.

Typical fits:
- **Safety-Critical Readiness Commons**;
- **StableMIR / rustc_public**-adjacent substrate work;
- **build-std**;
- **relink-don't-rebuild**;
- **Rust-for-Linux stable tooling**;
- some keystone security or interop projects.

Wrong shape:
- forcing substrate or readiness-program work into a generic SaaS or dashboard story because it sounds easier to pitch.

## Mapping the strongest current contributions to honest bet sizes

### 1) Build-State Evidence
**Best current band:** bootstrap companion build  
**Possible later graduation:** focused funded bridge

Why:
- the pain is broad and current;
- the proving grounds are concrete now;
- Cargo's recorded-build-data direction gives it a real imported substrate;
- and the first artifact family can be local-first, reviewable, and useful without service dependency.

What a worthy first bet looks like in practice:
- one or two maintainers;
- one or two real workspaces plus one CI lane;
- canonical packs, `explain`, `diff`, and `doctor` flows;
- explicit unsupported or partial outputs.

What should be refused:
- turning the first build into remote-cache theater, an enterprise control plane, or a giant hosted analytics product.

### 2) Feedback Loop / Debuggability Acceptance
**Best current band:** consortium / interoperability program

Why:
- the proof burden is tuple acceptance, not just feature completeness;
- the desired capability bar spans multiple debuggers, operating systems, async workflows, and expression evaluation;
- and the experience can regress as debugger versions and internal representations change.

What a worthy first bet looks like in practice:
- a narrow but explicit debugger-tuple corpus;
- shared receipts for accepted / partial / unsupported / regressed states;
- one visualizer corpus and one async track;
- issue-routing artifacts that upstream maintainers can use.

What should be refused:
- a single-editor plugin or one blessed debugger story presented as ecosystem completion.

### 3) Adoption Navigation + Ecosystem Atlas
**Best current band:** focused funded bridge or commons

Why:
- the work is editorial and renewal-heavy by design;
- its value comes from bounded guidance staying current;
- and it becomes much stronger only after earlier evidence layers exist.

What a worthy first bet looks like in practice:
- a small renewal team or equivalent recurring funded time;
- conservative lane cards rather than giant “best crates” portals;
- visible freshness, source packs, and local-fit caveats;
- receipts showing what changed between review dates.

What should be refused:
- score portals, popularity dashboards, or LLM-curation without explicit renewal and scope.

### 4) Package Intake Gateway
**Best current band:** focused funded bridge or commons

Why:
- the seam lives at a live service and security boundary;
- it depends on fail-closed policy, route, and extraction truth;
- and crates.io plus Cargo changes keep shifting the operational surface.

What a worthy first bet looks like in practice:
- a small staffed operator-shaped team;
- route and payload capture;
- staging/extraction receipts;
- explicit handoffs into review or policy systems;
- no dependence on generic trust scores.

What should be refused:
- turning package intake into another recommendation portal or reputation marketplace.

### 5) Safety-Critical Readiness Commons
**Best current band:** keystone institution or consortium-grade program

Why:
- the work is shared-readiness infrastructure, not one library;
- the open recommendations are consortium-shaped: dependency lifecycle patterns, async-runtime requirements, interop guidance, and target-focused readiness checklists;
- and the hardest missing asset is durable shared ownership.

What a worthy first bet looks like in practice:
- consortium and foundation-backed coordination;
- shared receipts, checklists, and profile documents;
- explicit owner commitments for maintenance and qualification;
- interop and async tracks treated as first-class, not “later”.

What should be refused:
- selling one technical demo or one certified crate as if it solved the readiness problem.

### 6) Tooling Contract, Compatibility Claims, and narrow Semantic Context work
**Best current band:** bootstrap companion build, sometimes graduating to focused funded bridge

Why:
- the first wins are artifact and import-layer wins;
- the sources are already machine-usable enough to support bounded first builds;
- but wider adoption can require recurring compatibility and adapter upkeep.

What a worthy first bet looks like in practice:
- artifact-first, import-first, local-first packs;
- visible lossiness and format caveats;
- at least one external consumer reusing the same output.

What should be refused:
- daemons, portals, or synthetic all-in-one product shells before the reference layer is honest.

### 7) StableMIR, build-std, relink-don't-rebuild, Rust-for-Linux stable tooling, and similar substrate bets
**Best current band:** keystone institution or upstream substrate program

Why:
- these are roadmap substrates or stabilization programs;
- the main leverage comes from upstream progress itself;
- and the wrong move is often to wrap them in a fake public platform before the substrate stabilizes.

What a worthy first bet looks like in practice:
- upstream sponsorship, implementation time, coordination, and stabilization support;
- companion experimentation only where it shortens the path to upstream learning.

What should be refused:
- treating substrate motion as if it already wants a consumer-facing standalone company or dashboard.

## The practical portfolio answer under real constraints
If the available capital is very small, the archive should first ask whether the best move is to **sponsor a maintainer or upstream owner** instead of building anything new.

If a serious but small team wants one broad first build, it should still choose **Build-State Evidence**.
That remains the strongest bootstrapable bet.

If the team is operator- or security-shaped and already sits on a live review boundary, **Package Intake Gateway** is the strongest focused funded bridge.

If the team is editorial/defaults-shaped and already has evidence imports to lean on, **Adoption Navigation** is the strongest focused funded commons.

If the available backers are multiple vendors, debugger owners, platform owners, or regulated adopters, the honest targets are **Feedback Loop / Debuggability Acceptance** and **Safety-Critical Readiness Commons**, because both need coalition proof and recurring shared maintenance.

If the sponsor's main goal is to improve Rust itself rather than to own a downstream product boundary, the archive should prefer **upstream sponsorship** of substrate lanes such as build analysis, build-std, StableMIR-adjacent work, relink-don't-rebuild, or Rust-for-Linux tooling.

## What this changes in the archive
Future comparative answers should now name, for each strong candidate:
- its **best current capital band**;
- the **smallest honest first team and runway**;
- the **most likely sponsor or operator fit**;
- the **most dangerous overbuild shape**;
- and whether the next best move is **fund a maintainer**, **ship a companion tool**, **staff a bridge**, **form a consortium**, or **sponsor upstream**.

That is the new discipline.
The archive should stop acting as if every strategically worthy Rust contribution wants the same kind of bet.
