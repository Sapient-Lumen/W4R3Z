# Design: Epic contribution delivery matrix (2026Q1)

## Goal
The archive already has:
- a broad ladder;
- execution blueprints for many individual seams;
- a contribution-shape atlas;
- sequencing guidance;
- and scorecards that separate broad first-build value from urgency, multiplier value, and program shape.

What it still lacked was one sharper cross-seam answer to a practical question:

> once we already believe several Rust ecosystem contributions are worthy, what should each one actually look like as a **delivered thing** — who should own it, what should ship first, what proving grounds should it survive, and what seductive wrong shape should be refused early?

This note is the archive's answer to that question.
It does **not** rerank the broad ladder.
It does **not** promote a new frontier.
It turns the strongest candidates into a more operational **delivery matrix**.

Read with:
- `design/epic-contribution-scorecards-2026Q1.md`
- `design/territory-priority-refresh-2026Q1.md`
- `design/portfolio-contribution-shapes-2026Q1.md`
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
The current public Rust picture keeps saying two things at once.
First, the recurring pain is broad and stubborn: compile/resource taxes, debugging friction, tacit knowledge, async complexity, and domain-specific maturity gaps remain visible in both the March 2026 challenges writeup and the 2025 State of Rust survey results.
https://blog.rust-lang.org/2026/03/20/rust-challenges/
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Second, the most promising substrates are becoming more machine-usable in very particular shapes.
Cargo build analysis is explicitly a record-and-report effort with unstable `cargo report` surfaces and evolving schemas; Cargo's 1.93 and 1.94 development updates keep structured logging, report commands, build-dir layout, target-dir locking, and workspace/config discovery in motion; docs.rs now hosts rustdoc JSON but explicitly warns consumers to check `format_version` and historical availability; and the `cargo-semver-checks` goal keeps showing how far precise public-boundary reasoning depends on better imported semantic facts instead of one-off heuristics.
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
https://docs.rs/about/rustdoc-json
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html

That combination creates a new archive failure mode: even when the ranking is right, future revisions can still choose the wrong **delivery shape** or the wrong **owner shape**.
That is especially risky now because the Rust Project and Foundation are increasingly talking in roadmap, application-area, and support-capacity terms rather than only in crate/tool terms. The program-management update says roadmaps and application areas are intended to help focus industry funding; the Rust Foundation's 2026–2028 strategy explicitly pairs stable infrastructure, sustainable maintenance, adoption, and community support; the Rust Innovation Lab exists to support funded Rust projects without taking technical direction away from maintainers; and the maintenance writeup makes explicit that contributor unblocking, review, and maintenance capacity are real limiting resources.
https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
https://rustfoundation.org/strategic-plan/
https://blog.rust-lang.org/2025/09/03/welcoming-the-rust-innovation-lab/
https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/

So the archive needs a note that says, seam by seam, not just **what matters**, but **what should be built, by whom, and in what first shape**.

## Headline answer
The strongest current delivery rule is:

> the best Rust ecosystem epics are usually **import-first evidence / reference / report layers with explicit proving grounds**, while the biggest program seams are usually **institution-shaped readiness commons** rather than one crate or dashboard.

In practice, that means:
- **Build-State Evidence** should still be built first, and it should still look like an evidence collector + report layer + diff/doctor surface.
- **Feedback Loop / Debuggability Acceptance** should be built second, and it should look like an acceptance corpus + export bundle + debugger-tuple review layer, not one debugger fork.
- **Adoption Navigation** should stay a reviewable atlas / defaults / renewal system, not a generic crate-score portal.
- **Tooling Contract**, **Semantic Context**, and **Compatibility Claims** are best treated as machine-facing reference layers with bounded imports.
- **Package Intake Gateway** is an urgent operational bridge whose first victory is reviewable route/extraction/resolution receipts, not a giant hosted trust platform.
- **Safety-Critical Readiness Commons** is real, but it is only honest as a consortium / readiness program with shared ownership and maintenance commitments.

## The delivery matrix

### 1) Build-State Evidence
**Portfolio role:** broad first build  
**Best owner shape:** Cargo-adjacent tool team or funded lab that stays import-first and compatible with upstream Cargo motion.  
**Why this shape fits:** Cargo's build-analysis goal, 1.93 structured logging, 1.94 report work, and build-dir-layout work all point toward recorded build facts, explainability, and local report surfaces rather than a replacement build system.
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html

**What v0 should ship:**
- one canonical `build-state-pack/v0` family;
- import lanes for Cargo-native timings, rebuild reasons, invocation metadata, and bounded environment facts;
- `explain`, `diff`, and `doctor` commands;
- explicit partiality / unsupported fields;
- lineage receipts that downstream CI, support, IDE, and assistant consumers can import.

**What v1 should add:**
- better resource/capacity evidence;
- stable adapter guidance for editor/build contention;
- multi-run comparison and renewal receipts;
- proving-ground packs for large workspaces and CI/local divergence.

**What counts as success:** a developer can answer “what rebuilt, why, how expensive was it, and what should I inspect next?” after the fact instead of only during a lucky terminal session.

**Refuse early:**
- remote cache empires sold as the whole answer;
- target-dir/build-dir scraping as primary truth;
- one hosted build-health dashboard pretending to replace local evidence.

### 2) Feedback Loop / Debuggability Acceptance
**Portfolio role:** second serious build  
**Best owner shape:** debugger-interop working set with funded maintainers and explicit debugger / OS / runtime acceptance lanes.  
**Why this shape fits:** the debugging survey frames the problem as missing support across debugger tuples, visualizers, async workflows, and Rust-expression evaluation — a compatibility-and-acceptance problem, not just an IDE plugin problem.
https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

**What v0 should ship:**
- one `feedback-loop-pack/v0` family;
- explicit debugger-tuple acceptance profiles;
- visualizer and expression-evaluation acceptance corpus;
- import hooks from build-state artifacts rather than disconnected session lore;
- export bundles for issue filing, docs, and support.

**What v1 should add:**
- async-debug acceptance lanes on one real runtime family;
- split-debug / symbol / visualizer posture across major OS tuples;
- renewal receipts for regressions and unresolved gaps.

**What counts as success:** maintainers can say “this debugger/OS/toolchain/runtime lane is accepted, partial, unsupported, or regressed” with receipts instead of forum folklore.

**Refuse early:**
- “just bless one debugger”;
- IDE-only integrations with no portable truth export;
- a new debugger fork sold as the entire ecosystem answer.

### 3) Adoption Navigation + Ecosystem Atlas
**Portfolio role:** first consumer-facing widening  
**Best owner shape:** neutral atlas/defaults team with strong renewal discipline and explicit consumer-routing limits.  
**Why this shape fits:** the challenges writeup and survey both keep naming tacit knowledge and choice paralysis, while docs remain canonical and editor/LLM mediation is rising. That argues for reviewable defaults and renewal receipts, not algorithmic ranking theater.
https://blog.rust-lang.org/2026/03/20/rust-challenges/
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

**What v0 should ship:**
- lane-default cards for a small set of product/repo scenarios;
- imported canon/evidence/default-fit packs;
- renewal receipts and bounded briefs;
- explicit “unknown / manual-review-required” posture.

**What v1 should add:**
- stronger persona/question records;
- more proving-ground anchors;
- migration notes when defaults change;
- narrow consumer views for docs, support, and assistants.

**What counts as success:** a new or returning Rust team can choose a conservative default stack for a known scenario without having to reverse-engineer Reddit, GitHub stars, or stale blog posts.

**Refuse early:**
- generic crate-score sites;
- framework winner-hunting;
- opaque recommendation engines with no renewal or evidence lineage.

### 4) Tooling Contract
**Portfolio role:** hidden multiplier / machine-facing substrate  
**Best owner shape:** Cargo-adjacent reference-layer effort with tight adapter corpus and lossiness accounting.  
**Why this shape fits:** Cargo explicitly says it cannot be everything to everyone, while plugins matter; build-analysis and report surfaces are emerging; and machine-facing consumers keep needing scope/plan/evidence truth without scraping internals.
https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html

**What v0 should ship:**
- one `tooling-pack/v0` family;
- discovery/scope, graph/plan, execution/evidence, and adapter-lossiness sections;
- import adapters for Cargo-native surfaces plus selected outer-build/editor routes;
- explicit consumer-handoff boundaries.

**What v1 should add:**
- better workspace/config discovery routing;
- more stable adapter corpus;
- comparison receipts that preserve unknowns instead of collapsing them.

**What counts as success:** IDEs, CI, docs, assistants, and outer-build tools can import one honest pack instead of each inventing a private approximation of the workspace.

**Refuse early:**
- Cargo daemon dreams;
- BSP-only answers;
- monorepo-control-plane fantasies.

### 5) Semantic Context
**Portfolio role:** hidden multiplier / semantic substrate  
**Best owner shape:** reference-layer effort that imports rustdoc JSON, docs.rs availability, and future compiler-facing stable surfaces without pretending those inputs are already uniform or fully stable.  
**Why this shape fits:** docs.rs now hosts rustdoc JSON with explicit `format_version` and availability caveats; `cargo-semver-checks` shows why cross-crate and type-precise reasoning needs richer imported semantics; and StableMIR / `rustc_public` progress validates compiler-facing substrate work as a multiplier.
https://docs.rs/about/rustdoc-json
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
https://blog.rust-lang.org/2025/08/05/july-project-goals-update/

**What v0 should ship:**
- one `semantic-context-pack/v0` family;
- exact subject capture and freshness/version metadata;
- bounded query and compare artifacts;
- explicit partiality around missing cross-crate or format-sensitive facts.

**What v1 should add:**
- better cross-crate resolution;
- more type-precise imported lanes;
- stronger compatibility with downstream semver and docs consumers.

**What counts as success:** downstream tools can ask precise, bounded semantic questions without each becoming their own rustdoc/rustc archaeology project.

**Refuse early:**
- universal knowledge-graph rhetoric;
- assistant-memory blobs;
- claims that one nightly-only input already settles all semantics.

### 6) Compatibility Claims
**Portfolio role:** claim-routing layer  
**Best owner shape:** reference layer that imports evidence from support, debugger, public-API, and toolchain lanes and emits bounded support verdicts.  
**Why this shape fits:** this seam becomes strongest when it is narrower than a giant support portal and more compositional than a single MSRV or target matrix.

**What v0 should ship:**
- one `compatibility-pack/v0` family;
- claim-family routing with explicit evidence imports;
- drift and reclassification receipts;
- consumer handoff to docs, release, support, and policy surfaces.

**What v1 should add:**
- richer imported support-envelope and acceptance lanes;
- better public-boundary and debugger compatibility joins;
- clearer re-check triggers.

**What counts as success:** a maintainer can make a bounded compatibility claim and show what evidence family supports it.

**Refuse early:**
- badge systems;
- giant matrix portals;
- one-field proxies pretending to define the whole claim.

### 7) Package Intake Gateway
**Portfolio role:** urgent operational bridge  
**Best owner shape:** security/registry-adjacent review layer with fail-closed receipts and narrow policy handoffs.  
**Why this shape fits:** crates.io keeps strengthening service-side signals, and the March 2026 Cargo advisory showed that public-registry mitigation and alternate-registry reality can differ sharply. The first honest win is better intake evidence and routing, not a universal trust oracle.
https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
https://blog.rust-lang.org/2026/03/21/cve-2026-33056/

**What v0 should ship:**
- one `package-intake-pack/v0` family;
- route, payload, extraction, and resolution receipts;
- explicit alternate-registry / mirror / stale-data posture;
- policy-review handoff bundles.

**What v1 should add:**
- stronger registry- and mirror-aware routing;
- richer attachment lanes for advisories and publisher/source identity imports;
- better renewal receipts after advisories or policy shifts.

**What counts as success:** dependency reviewers can see what was fetched, from where, under what extraction/resolution assumptions, and what remained unknown.

**Refuse early:**
- hosted trust scores;
- one giant security dashboard;
- “crate quality” theater that hides route and extraction uncertainty.

### 8) Safety-Critical Readiness Commons
**Portfolio role:** consortium / readiness program seam  
**Best owner shape:** industry-backed consortium or foundation-supported readiness program with explicit shared maintenance commitments.  
**Why this shape fits:** the safety-critical writeup is unusually direct that successful work needs companies to define requirements, validate implementations, and commit to maintenance. It cites the FLS as a positive model and MC/DC work as a cautionary tale when ownership is unclear. The Foundation's strategy and the Innovation Lab also make institution-backed support shapes more plausible than they used to be.
https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
https://rustfoundation.org/strategic-plan/
https://blog.rust-lang.org/2025/09/03/welcoming-the-rust-innovation-lab/

**What v0 should ship:**
- readiness checklists and profile definitions;
- dependency-lifecycle and async/runtime qualification playbooks;
- interop and evidence-routing templates;
- explicit owner and renewal commitments.

**What v1 should add:**
- attachable acceptance and qualification receipts;
- sector-specific profile variants;
- clearer import lanes from coverage, toolchain, interop, and compatibility seams.

**What counts as success:** regulated adopters can organize shared requirements and maintenance without asking the core Rust Project to absorb all domain cost alone.

**Refuse early:**
- one crate sold as “certified Rust”;
- marketing-heavy compliance portals;
- technical work with no owner for long-term maintenance.

## What counts as a worthy contribution now
A contribution should count as **worthy** only if it clears most of these bars:
- it addresses a recurring pain cluster that current public Rust signals keep naming;
- it has a delivery shape that matches the problem rather than a fashionable platform instinct;
- it leaves behind reviewable artifacts, not just workflow vibes;
- it has a realistic owner shape and maintenance path;
- and it makes other consumers or later seams better without hiding uncertainty.

A contribution should count as **epic** only when it also does at least one of these:
- creates a reusable evidence or reference layer many later seams can import;
- shifts a stubborn broad workflow tax for a large slice of Rust users;
- or establishes a neutral program/institution shape that lets an underbuilt domain finally sustain itself.

That is why **Build-State Evidence** is still the strongest generic epic, **Feedback Loop / Debuggability Acceptance** is the clearest second epic, and **Safety-Critical Readiness Commons** is an epic only in the consortium/program sense.

## Practical build/fund map
If a serious team can fund or staff only one thing, build **Build-State Evidence**.
If it can fund two things, add **Feedback Loop / Debuggability Acceptance**.
If it is strongest at machine-facing substrate work, prefer **Tooling Contract** or **Semantic Context** over a glossy consumer portal.
If it is operating near registry/security pressure, build **Package Intake Gateway** as a narrow review layer.
If it is a consortium or foundation-backed effort with domain commitments, **Safety-Critical Readiness Commons** is the clearest program seam.
If it is trying to help ordinary teams choose a stack, do **Adoption Navigation** only with renewal receipts and bounded defaults.

## Recommended archive move
Treat this as a **comparative-delivery + meta-hygiene** addition.
Do **not** change the broad ladder.
Do **not** promote a new frontier.

Instead:
- keep **Build-State Evidence** as the strongest broad first build;
- keep **Feedback Loop / Debuggability Acceptance** as the clearest second serious build;
- keep **Adoption Navigation** as the first honest consumer-facing widening;
- keep **Tooling Contract**, **Semantic Context**, and **Compatibility Claims** as machine-facing multipliers or routing layers;
- keep **Package Intake Gateway** as the urgent operational bridge;
- keep **Safety-Critical Readiness Commons** as the clearest institution-shaped program seam;
- and require future “what should we actually build?” syntheses to state **delivery shape**, **owner shape**, **first shipped artifact family**, **proving grounds**, and **refused wrong shape** explicitly.
