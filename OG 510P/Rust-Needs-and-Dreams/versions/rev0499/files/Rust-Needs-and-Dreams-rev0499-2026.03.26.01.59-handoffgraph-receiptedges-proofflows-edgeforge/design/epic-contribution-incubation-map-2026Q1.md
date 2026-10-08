# Design: Epic contribution incubation map (2026Q1)

## Goal
The archive now has:
- a broad ladder for what matters most;
- scorecards that separate first-build value from urgency and multiplier value;
- a delivery matrix for what each strong candidate should ship and who should roughly own it; and
- seam-local execution blueprints for many of the most serious candidates.

What it still lacked was one sharper answer to a different practical question:

> once we know a contribution is worthy, **what kind of incubation vehicle should it actually start in so it can land without being distorted by the wrong ownership, funding, or governance shape?**

This note is the archive's answer to that question.
It does **not** rerank the broad ladder.
It does **not** promote a new frontier.
It explains which worthy contributions should begin as:
- upstream-adjacent companion projects,
- acceptance consortia,
- editorial/defaults commons,
- operational bridges,
- foundation- or lab-backed keystone incubations,
- long-horizon roadmap substrates,
- or consortium-grade readiness programs.

Read with:
- `design/epic-contribution-delivery-matrix-2026Q1.md`
- `design/epic-contribution-scorecards-2026Q1.md`
- `design/territory-priority-refresh-2026Q1.md`
- `design/portfolio-contribution-shapes-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/tooling-contract-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- `design/semantic-context-execution-blueprint-2026Q1.md`
- `design/maintainer-reality-keystone-stewardship-execution-blueprint-2026Q1.md`

## Why this note is needed now
The current public Rust picture keeps saying something the archive should take more literally: **many of the worthiest Rust contributions are failing, stalling, or being mis-scoped because they start in the wrong institutional container**.

The program-management update says the project now thinks in **roadmaps** and **application areas** because many important efforts do not fit a six-month or even one-year box, and because this framing is meant to help focus outside funding.
https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/

The Rust Foundation's 2026–2028 strategy says the next chapter is explicitly about **stable infrastructure**, **sustainable maintenance**, and **adoption & innovation** rather than about only backing isolated feature work.
https://rustfoundation.org/strategic-plan/

The Rust Innovation Lab now provides a concrete support vehicle for keystone Rust projects while keeping technical direction with maintainers, which is direct evidence that “important Rust thing” and “ordinary crate maintained in spare time” are no longer the only two organizational shapes.
https://blog.rust-lang.org/2025/09/03/welcoming-the-rust-innovation-lab/

At the same time, official project goals keep showing that many of Rust's highest-leverage improvements land first as **focused compatible experiments** rather than as giant platform rewrites:
- Cargo plumbing was explicitly framed as a third-party subcommand experiment.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo build analysis is framed as unstable `cargo report` surfaces and recorded metadata across invocations.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- build-dir layout work is framed as reworking internal layout so finer-grained caching and shared-cache use become possible, not as a universal build control plane.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Cranelift is framed as a production-ready local-development backend, not as “replace rustc.”
  https://rust-lang.github.io/rust-project-goals/2025h2/production-ready-cranelift.html
- `relink-don't-rebuild` is framed as a narrow compile/rebuild optimization substrate, not a new package manager.
  https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html

The industrial side tells the same story from a different angle.
Rust-for-Linux stable-tooling work and `build-std` both show that some of the most valuable ecosystem contributions are really **stabilization and integration programs** around toolchain boundaries, not “another library.”
https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html

And the security/operations side keeps warning against romanticizing purely local or purely advisory fixes.
The March 2026 Cargo advisory, the crates.io malicious-notification policy update, and sandboxed build-scripts work all point toward operational bridges, policy surfaces, and safer default execution posture — not just better dashboards or better vibes.
https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html

So the archive now needs an **incubation map** that says, seam by seam, not just what is worthy, but **what organizational starting shape gives it the best chance of landing honestly**.

## Core rule
The archive should now assume:

> many worthy Rust contributions fail when started in the wrong vehicle.
> A great **report layer** dies inside a giant platform pitch.
> A real **acceptance problem** dies when framed as one team's plugin.
> A serious **operational bridge** dies when framed as a generic portal.
> A true **readiness program** dies when framed as one crate.
> And a delicate **upstream-facing substrate** dies when forced to promise user-facing completeness too early.

That means future revisions must keep these truths separate:
- the **seam**;
- the **artifact family**;
- the **incubation vehicle**;
- the **funding/staffing posture**;
- the **exit path**;
- and the **wrong starting vehicle** that would likely deform the work.

## The incubation vehicles

### 1) Upstream-adjacent companion project
Best when the missing thing is a **portable evidence / report / protocol / adapter layer** that needs rapid iteration, real proving grounds, and eventual upstream influence without premature stability promises.

Typical properties:
- starts outside core Cargo/rustc release trains;
- imports first-party surfaces rather than replacing them;
- proves schemas, adapters, and UX on real workspaces;
- can upstream pieces later, but does not need full upstream blessing to begin.

Good fits:
- **Build-State Evidence**
- **Tooling Contract**
- parts of **Compatibility Claims**
- parts of **Package Intake Gateway**

Bad fit for:
- broad editorial/defaults guidance,
- multi-debugger acceptance governance,
- consortium-grade readiness programs.

### 2) Acceptance consortium / interop working set
Best when the missing thing is a **cross-tool / cross-OS / cross-runtime capability matrix** where no single upstream or vendor can honestly certify the whole experience alone.

Typical properties:
- shared test corpus and accepted tuples;
- issue-routing and regression receipts across multiple upstreams;
- explicit unsupported/partial/regressed states;
- value comes from keeping the matrix honest, not from owning every implementation.

Good fit:
- **Feedback Loop / Debuggability Acceptance**

Bad fit for:
- recommendation portals,
- monolithic debugger forks,
- private IDE-only features.

### 3) Editorial atlas / defaults commons
Best when the missing thing is **bounded recommendation and renewal discipline** rather than one executable substrate.

Typical properties:
- conservative scenario cards;
- imported evidence, not score theater;
- recurring renewal receipts;
- tight consumer routing and explicit uncertainty.

Good fit:
- **Adoption Navigation + Ecosystem Atlas**

Bad fit for:
- operational incident response,
- low-level compiler or Cargo substrate work,
- institution-heavy certification programs.

### 4) Operational bridge / security-service companion
Best when the missing thing sits at a live **registry, package, execution, or policy boundary** and must survive incidents, escalation, and operator review.

Typical properties:
- reviewable receipts and route facts;
- policy and enforcement hooks;
- explicit alternate-registry or deployment posture;
- security-team and operator involvement from the start.

Good fit:
- **Package Intake Gateway**
- future build-script capability or sandbox-routing layers

Bad fit for:
- generic trust portals,
- academic-only prototypes,
- consumer guidance sites pretending to improve intake safety.

### 5) Foundation- or lab-backed keystone incubation
Best when the thing is already **critical infrastructure with real industry dependence** and the main missing resource is continuity, governance, staffing, and operational support rather than conceptual clarity.

Typical properties:
- maintainers retain technical direction;
- the host organization supplies governance, legal, staffing, operational, or fundraising support;
- success is measured by continuity and real-world reliability, not just feature velocity.

Good fit:
- keystone ecosystem services or libraries
- some later-stage operational bridges if they become shared infrastructure

Bad fit for:
- early design notes that still lack artifact clarity,
- recommendation layers,
- one-team experiments that have not proven broad demand.

### 6) Long-horizon roadmap substrate
Best when the missing thing is an **enabling primitive or stabilization program** whose value appears indirectly through later tools, industrial support, or local-development speed.

Typical properties:
- compiler/toolchain or platform-adjacent work;
- multi-release or multi-year horizon;
- narrower user-visible story at first;
- enormous multiplier value if it lands.

Good fit:
- **Semantic Context / StableMIR-adjacent work**
- **Cranelift local-dev backend** as a focused acceleration lane
- **build-std** and **Rust-for-Linux stable tooling** as industrial boundary programs
- `relink-don't-rebuild` and similar rebuild substrates

Bad fit for:
- claims that a user-facing ecosystem epic is already complete,
- one-shot hackathon productization,
- hosted-service pitches.

### 7) Consortium-grade readiness commons
Best when the missing thing is a **shared adoption threshold** involving policy, evidence, checklists, tool qualification, dependency lifecycle, or cross-organization commitment.

Typical properties:
- multiple institutions must agree on what counts as readiness;
- artifact output includes profiles, checklists, evidence bundles, and renewal receipts;
- maintenance cost is part of the product;
- one crate cannot honestly deliver the whole seam.

Good fit:
- **Safety-Critical Readiness Commons**

Bad fit for:
- certification theater,
- “foundation blessed” marketing,
- one vendor's gated platform.

## Mapping the current top candidates to the right vehicles

### 1) Build-State Evidence
**Right starting vehicle:** upstream-adjacent companion project  
**Why:** the Cargo plumbing and build-analysis work both point toward portable recorded facts, explainability, and local reports, while build-dir-layout work keeps proving that ecosystem users are leaning on internal details because the right surfaced facts are still missing.

**What the first year should look like in practice:**
- a third-party-first `build-state-pack/v0` family;
- adapters for current Cargo report/timing/build inputs;
- `explain`, `diff`, and `doctor` flows on real workspaces;
- proving grounds that stress incremental rebuild churn, editor contention, and CI/local divergence;
- an explicit import-to-upstream story, not a full replacement-Cargo story.

**Best staffing posture:** 3–5 people with Cargo fluency plus proving-ground operators.

**Likely exit path:** selected schemas, import lanes, or UX ideas inform upstream Cargo surfaces; some remains a companion layer.

**Wrong starting vehicle:** a remote-cache company story, a giant monorepo platform, or a hosted build-health portal.

### 2) Feedback Loop / Debuggability Acceptance
**Right starting vehicle:** acceptance consortium / interop working set  
**Why:** the debugging survey is explicit that “truly stellar” support means debugger tuples, visualizers, async debugging, and expression evaluation across multiple debuggers and operating systems. That is not one team's plugin backlog.

**What the first year should look like in practice:**
- a shared acceptance corpus and tuple matrix;
- explicit `accepted / partial / unsupported / regressed` receipts;
- debugger-visualizer and async-debug tracks;
- portable export bundles for issue filing and docs;
- one runtime family proven deeply before widening.

**Best staffing posture:** 1–2 full-time coordinators plus debugger/runtime maintainers and upstream liaisons.

**Likely exit path:** accepted tuples become boring and durable; the corpus remains the living boundary.

**Wrong starting vehicle:** an IDE-only feature sprint, one blessed debugger, or a new debugger fork sold as the ecosystem answer.

### 3) Adoption Navigation + Ecosystem Atlas
**Right starting vehicle:** editorial atlas / defaults commons  
**Why:** the challenges writeup and State of Rust survey both keep naming choice paralysis and tacit knowledge, while docs remain canonical and editor/LLM mediation rises. That means the missing thing is a disciplined recommendation commons, not a scoring engine.

**What the first year should look like in practice:**
- 3–5 conservative scenario cards with renewal SLAs;
- imported evidence from build, maintenance, compatibility, and learning seams;
- bounded brief formats for humans and assistant consumers;
- explicit unknown/manual-review-needed posture.

**Best staffing posture:** 2–4 editors/operators with strong renewal discipline, not one “AI recommender” owner.

**Likely exit path:** a trusted defaults corpus that other tools import rather than a giant portal that must own the whole ecosystem.

**Wrong starting vehicle:** global crate rankings, leaderboard portals, or assistant memory canon.

### 4) Tooling Contract
**Right starting vehicle:** upstream-adjacent companion project with strong standards discipline  
**Why:** Cargo keeps exposing partial machine-facing surfaces while still warning that build-dir internals are unstable. The missing thing is a disciplined discovery → scope → graph → evidence → lossiness contract that can be proven on real consumers.

**What the first year should look like in practice:**
- one `tooling-contract-pack/v0` family;
- Cargo, rust-analyzer, CI, and outer-build adapters;
- explicit lossiness receipts and compatibility notes;
- narrow proving grounds with one outer build system and one editor path.

**Best staffing posture:** 2–4 people with Cargo + editor/build-system literacy.

**Likely exit path:** some schema lanes become de facto or de jure standards; the archive keeps the lossiness language honest.

**Wrong starting vehicle:** Cargo daemon dreams, BSP-only declarations, or universal platform productization.

### 5) Package Intake Gateway
**Right starting vehicle:** operational bridge / security-service companion  
**Why:** recent Cargo and crates.io security posture shows this seam lives at a live policy and extraction boundary. It is too operational to be “just another crate” and too narrow to become a fake total-ranking winner.

**What the first year should look like in practice:**
- route/extraction/resolution receipts;
- alternate-registry and offline posture made explicit;
- package review and escalation hooks;
- optional capability-routing evidence for build scripts and other compile-time execution surfaces.

**Best staffing posture:** security-savvy maintainers plus registry/operator participation.

**Likely exit path:** some checks or receipts upstream into registry/Cargo flows; the rest stays a bridge and review layer.

**Wrong starting vehicle:** trust score portals, “safe crates marketplace” theater, or policy-only docs with no receipts.

### 6) Safety-Critical Readiness Commons
**Right starting vehicle:** consortium-grade readiness program  
**Why:** the 2026 flagships page and the safety-critical writeup both say the missing work includes certified tooling, evidence, unsafe documentation, lints, FLS cadence, dependency-lifecycle patterns, async qualification, and interop evidence. That is a readiness commons, not one package.

**What the first year should look like in practice:**
- narrow pilot profiles;
- readiness checklists and evidence bundles;
- dependency lifecycle and async qualification lanes;
- explicit “what remains outside the commons” boundaries;
- multi-organization maintenance commitments.

**Best staffing posture:** a coordinator plus partner organizations, domain experts, and maintainers.

**Likely exit path:** shared readiness artifacts that real adopters import, with some pieces eventually upstreamed into toolchain/docs/lints.

**Wrong starting vehicle:** certification-badge startup, one vendor platform, or one crate claiming to make Rust “safety-critical ready.”

### 7) Semantic Context / StableMIR-adjacent work
**Right starting vehicle:** long-horizon roadmap substrate  
**Why:** StableMIR progress and compiler-public-surface work validate that semantic import truth is a real multiplier, but still a substrate. The archive should treat it as a serious bet without demanding a full user-facing product story too early.

**What the first year should look like in practice:**
- narrow publication and versioning discipline;
- one or two proving consumers;
- explicit semantic-partiality posture;
- compatibility notes for downstream analysis tools.

**Best staffing posture:** compiler-adjacent specialists with one or two tool consumers.

**Likely exit path:** later tools become radically more honest; the substrate remains partially specialist.

**Wrong starting vehicle:** giant “semantic portal” marketing, or pretending the substrate alone is the ecosystem epic.

## What the current official examples teach

### Cargo plumbing, build analysis, and build-dir work teach “companion first, platform later if ever”
The lesson is not that Rust needs a new mega-build-platform company.
The lesson is that Cargo-native truth becomes more usable when a careful companion layer proves the missing seams on real workspaces before demanding permanence.

### Cranelift teaches “focused acceleration lane”
A worthy contribution can be epic without trying to become the one true backend.
Cranelift's value proposition is sharply bounded: local-development speed for common workflows.
That clarity is a feature, not a limitation.

### Rust-for-Linux and build-std teach “stabilization programs are real ecosystem contributions”
Some of the most valuable work is not a new user-facing tool at all.
It is making Rust survivable at hard industrial boundaries through toolchain, support-envelope, and integration work.
The archive should keep honoring that category.

### Innovation Lab teaches “keystone continuity is now a first-class vehicle”
The ecosystem now has a real support shape for projects that are too important to rely on goodwill alone but should still remain maintainer-led.
That should change how the archive thinks about ownership realism.

### The Cargo advisory and malicious-crate policy teach “security bridges need operators, not just opinion”
Operational seams need route facts, review surfaces, and enforcement posture.
They should not be turned into recommendation theater.

## Current funding / building priority by vehicle
If the archive had to recommend where serious effort should go **next**, by vehicle rather than by only seam, it should say:

1. **Fund first:** one upstream-adjacent companion for **Build-State Evidence**.  
   This is still the broadest first build and the cleanest candidate for a small serious team.

2. **Fund second:** one acceptance consortium for **Feedback Loop / Debuggability Acceptance**.  
   This is the clearest second serious build and the most obvious place where single-owner fantasies fail.

3. **Staff as editorial commons:** **Adoption Navigation + Ecosystem Atlas**.  
   This should widen after the evidence spine proves itself, not before.

4. **Staff as operational bridge:** **Package Intake Gateway**.  
   Operational urgency is real, but the work should stay bridge-shaped.

5. **Sustain as roadmap substrates:** **Tooling Contract**, **Semantic Context / StableMIR**, **Cranelift local-dev backend**, **relink-don't-rebuild**, **build-std**, and **Rust-for-Linux stable tooling**.  
   These are not all “the one next public epic,” but together they strongly shape what later epics can honestly build.

6. **Build as consortium program:** **Safety-Critical Readiness Commons**.  
   This is worthy, rising, and strategically important, but only honest in a multi-party readiness shape.

## Archive decision
The repo should now treat **incubation vehicle** as a first-class comparative layer beside rank, priority type, delivery shape, and owner shape.

That means future revisions should ask, explicitly:
- is this seam best started as a companion project, a consortium, an editorial commons, an operational bridge, a keystone incubation, a roadmap substrate, or a readiness program;
- what staffing/funding posture fits that vehicle;
- what the likely exit path is;
- and which wrong starting vehicle would distort the work.

The top-line answer is:
- **Build-State Evidence** still looks like the best first serious companion build;
- **Feedback Loop / Debuggability Acceptance** still looks like the best next consortium-style acceptance build;
- **Adoption Navigation** still looks like an editorial commons, not a product platform;
- **Package Intake Gateway** still looks like an operator-shaped bridge, not a trust portal;
- **Safety-Critical Readiness Commons** still looks like a consortium program, not a crate;
- and several of Rust's most important long-term wins still look like roadmap substrates and stabilization programs rather than public-facing epics.
