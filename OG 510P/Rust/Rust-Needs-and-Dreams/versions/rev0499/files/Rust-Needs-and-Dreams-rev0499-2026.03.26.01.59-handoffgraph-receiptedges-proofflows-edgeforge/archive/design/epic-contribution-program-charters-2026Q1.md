# Design: Epic contribution program charters (2026 Q1)

## Goal
The archive already has strong answers to four big questions:
- which Rust ecosystem gaps rank highest;
- what practical build shape they should take;
- how those answers fold into a smaller number of macro-programs; and
- what each top program must actually contain as a minimum viable reference architecture.

What it still lacked was one sharper answer to a different repo-construction question:

> once the strongest programs are specified, **what launch charter makes them real enough to start, survive, and widen honestly** — where should they live, who should own them, which pilot partners should prove them, what maintenance envelope should exist, which narrow upstream asks are justified, and when should they be folded or killed?

This note is a **launch-charter / owner-shape / proving-partner / maintenance-envelope** pass.
It does **not** rerank the broad ladder.
It does **not** promote a new frontier.
It exists to keep the repo from stopping at good technical designs with vague institutional stories.

Read with:
- `design/epic-contribution-reference-architectures-2026Q1.md`
- `design/epic-contribution-program-stack-2026Q1.md`
- `design/practical-epic-contribution-briefs-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/epic-contribution-decision-rights-map-2026Q1.md`
- `design/epic-contribution-support-bundle-map-2026Q1.md`
- `design/epic-contribution-renewal-burden-map-2026Q1.md`
- `meta/PROGRAM_SPEC_DEEPENING_PROTOCOL.md`
- `meta/PROGRAM_CHARTER_PROTOCOL.md`

## Why this pass is merited now
The public Rust signals keep reinforcing that worthy work becomes real only when it has an owner, review path, and maintenance story.

Signals that matter here:
- The March 2026 challenges writeup still concentrates pain around **async difficulty**, **crate choice/trust**, **embedded constraints**, **safety-critical tooling maturity**, and **GUI compile-loop tax** rather than one missing universal framework. That says the repo should charter a small number of serious programs instead of another field of speculative products.  
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says **resource usage** remains a major productivity limit, **debugging** remains a meaningful pain point, and online docs remain canonical while editor/LLM mediation rises. That reinforces that any consumer-facing widener must carry explicit renewal and canon boundaries.  
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2026 goals overview describes goals as a **contract**: contributors propose goals, teams accept them, champions mentor the owners, and new goals should only be added when required resources are already known. The first-look post is even more explicit that a team champion is expected to meet with the owner regularly, while the task-owner guidance says goals without owners can only be accepted provisionally. That is almost a direct charter template for worthy ecosystem programs.  
  https://rust-lang.github.io/rust-project-goals/2026/  
  https://blog.rust-lang.org/inside-rust/2026/02/03/first-look-at-2026-project-goals/  
  https://rust-lang.github.io/rust-project-goals/about/owners.html
- Cargo’s external-tools chapter still says the supported third-party lanes are `cargo metadata`, `--message-format=json`, and custom subcommands. That means many worthy contributions should still begin as **companion-first** layers with narrow upstream asks, not as “merge the whole thing into Cargo” demands.  
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- The maintenance writeup says maintenance is hard to plan, often low-status, and has a **multiplicative effect** because maintainers unblock and review the work of others. That raises the bar for any proposed program that has no named maintenance envelope.  
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- The Rust Foundation strategy for 2026–2028 explicitly centers **Stable Infrastructure**, **Sustainable Maintenance**, and **Adoption & Innovation**. That is a good reminder that the right programs often need mixed support forms: local builders, maintainers, and institutional backing, not one monolithic product owner.  
  https://rustfoundation.org/strategic-plan/
- The sponsorship post and related maintainer-fund work make clear that Rust increasingly has **plural funding lanes**: direct contributor sponsorship, maintainer funds, and Foundation-backed support. That means a charter should say what support form it actually needs instead of vaguely gesturing at “funding”.  
  https://blog.rust-lang.org/2025/12/08/making-it-easier-to-sponsor-rust-contributors/
- The safety-critical writeup is the strongest practical lesson of all: the FLS found a durable home because companies invested and the Rust Project could collaborate, while MC/DC work stalled when there was no sustained owner. The post explicitly recommends shared ownership of requirements with implementation and maintenance done by parties that have a vested interest.  
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

Taken together, the missing layer is:
**not just what to build, but what honest launch charter each serious program needs.**

## Headline answer
A worthy Rust ecosystem contribution should now usually be described with **two layers**, not one:
1. a **reference architecture** that says what is in the box; and
2. a **program charter** that says how the box becomes real.

For the top-band macro-programs, a healthy charter should answer eight practical questions:
1. **Residency** — where does the first real implementation live?
2. **Owner shape** — who is actually on point for shipping and renewal?
3. **Pilot-partner profile** — which proving partners make the first results believable?
4. **First shipset** — what v0 artifact bundle is actually shipped?
5. **Maintenance envelope** — what recurring care is assumed before widening?
6. **Narrow upstream asks** — what minimal upstream collaboration is justified after proof appears?
7. **Graduation / fold / kill rules** — what makes the program widen, fold under another layer, or stop?
8. **Wrong launch pattern to refuse** — what seductive organizational shape should be rejected early?

The broad ordering is unchanged.
What changes is that the strongest programs now have a more honest answer to **who should build them, with whom, and under what constraints**.

## Cross-program charter rules

### 1) Default to companion-first unless the seam is inherently coalition-grade
The Cargo tool story, the goal process, and the archive’s own boundary-fit work all point the same way:
start outside the core unless the value is fundamentally consortium-, policy-, or standards-shaped.

### 2) Charter an owner, not “the community”
A worthy program may have many participants, but it still needs a real owner shape:
- one technical lead plus one adjacent champion;
- one small steward pair;
- one operator-plus-maintainer pair; or
- one consortium with named company maintainers and a Rust Project liaison.

“Someone in the community will keep it fresh” is not a charter.

### 3) Pick pilot partners that match the proving grounds
The proving ground should decide the pilot partner:
- large-workspace users for build-state evidence;
- debugger/runtime/editor combinations for debug acceptance;
- maintainers plus end users for defaults/navigation;
- security/operator teams for intake review;
- companies and standards-heavy practitioners for safety-critical readiness.

### 4) Separate initial shipset from later upstream asks
The charter should say what can ship locally now and what only becomes worth asking upstream for after proof exists.
A healthy charter asks upstream for a **primitive, hook, or review lane**, not for ownership of the whole product fantasy.

### 5) Maintenance is part of the design, not a post-launch footnote
If the program assumes tuple-matrix reruns, editorial renewals, incident replays, or long-lived readiness profiles, that must be named before launch.

### 6) Funding lanes should stay plural
A charter should say whether it mainly wants:
- direct maintainer sponsorship,
- a bootstrap companion build,
- a focused bridge/common grant,
- operator/vendor participation,
- or consortium / Foundation-style convening.

Do not collapse all of those into one generic “needs funding”.

## Program 1 — Evidence Spine / Build-State Evidence launch charter
**Portfolio role:** strongest first build  
**Best initial residency:** companion-first Cargo-adjacent repo with a `cargo report`-shaped CLI and reviewable pack schemas

### Residency
The first implementation should live as a **companion-first tool and schema family**, not as a Cargo-core takeover.
That matches Cargo’s external-tools contract and the still-emerging build-analysis and build-dir-layout work.

### Owner shape
- one technical lead for the pack/report family;
- one Cargo-adjacent champion or reviewer who understands the import surfaces;
- one workspace-scale pilot maintainer;
- one CI-heavy pilot maintainer.

This is a **small owner set with adjacent upstream dialogue**, not a consortium.

### Pilot-partner profile
Start with proving partners that make the evidence honest:
- one large workspace with incremental rebuild pain;
- one CI-heavy project where rerun/diff receipts matter;
- one native-dependency or build-script-heavy project;
- one editor/tooling partner for lock-contention or shared-cache pressure.

### First shipset
- `build-state-pack/v0`
- one diff flow
- one doctor flow
- one exemplar bundle with warm-build, rebuild-reason, and contention cases
- one short issue/support handoff format

### Maintenance envelope
- schema versioning for the pack family;
- explicit lossiness notes when adapter imports change;
- routine reruns against exemplar workspaces;
- release-cadence review for import compatibility.

### Narrow upstream asks
Only after local value is clear:
- cleaner access to build-analysis identifiers or report hooks;
- narrowly declared build-dir/shared-cache facts when documented;
- import-stability feedback, not full ownership transfer.

### Graduation / fold / kill rules
Graduate when:
- three materially different pilot environments can produce honest packs;
- diff/doctor flows survive both local and CI contexts;
- adapter lossiness stays explicit.

Fold or kill when:
- the project drifts into cache-control or hosted-scoreboard theater;
- build-state truth depends on undocumented target-dir archaeology;
- upstream lands an equivalent surface and the companion layer adds no longer-distinct review value.

### Wrong launch pattern to refuse
- “universal build daemon”
- “shared cache product”
- “hosted build intelligence portal”
- any launch plan that makes provenance weaker than the pack itself

## Program 2 — Feedback / Debug Acceptance Commons launch charter
**Portfolio role:** strongest second build  
**Best initial residency:** cross-tool acceptance commons with portable session/export artifacts

### Residency
The first real home should be a **neutral corpus-and-export commons**, not one debugger fork or one IDE integration.

### Owner shape
- one technical lead for the acceptance corpus and session export format;
- one debugger champion from a major debugger family;
- one async/runtime liaison;
- one downstream issue/support/export consumer.

This is a **cross-tool steward group**, but still smaller than a full consortium.

### Pilot-partner profile
- one LLDB tuple family;
- one GDB tuple family;
- one Windows debugger tuple family;
- at least one async runtime scenario, preferably Tokio-first;
- one editor or issue-routing consumer for session exports.

### First shipset
- tuple manifest format
- async-debug fixture corpus
- visualizer corpus
- session export pack
- re-import path into issue/support context
- a plainly lossy unsupported-state vocabulary

### Maintenance envelope
- tuple reruns on debugger and toolchain updates;
- explicit unsupported/degraded states instead of stale green cells;
- fixture refresh when major debugger/runtime capabilities change.

### Narrow upstream asks
Only after proof exists:
- debugger- or runtime-specific metadata hooks;
- issue-template or editor attachment conventions;
- narrow capability descriptors, not “please merge our entire acceptance stack”.

### Graduation / fold / kill rules
Graduate when:
- session exports roundtrip across more than one debugger family;
- tuple identity stays intact;
- async unsupported states are preserved honestly.

Fold or kill when:
- the program becomes “one debugger product page”;
- session export is replaced by screenshots or prose;
- the corpus stops recording degraded states.

### Wrong launch pattern to refuse
- one debugger fork sold as ecosystem closure
- IDE-only magic with no durable export
- single-demo-tuple theater

## Program 3 — Navigation / Defaults / Claims Commons launch charter
**Portfolio role:** strongest widener once stronger evidence exists  
**Best initial residency:** editorial corpus with renewable lane cards, default stacks, and claims packs

### Residency
This should begin as a **reviewable editorial corpus**, not as a ranking portal.
Its home is closer to a renewable reference project than to a marketplace.

### Owner shape
- one editorial steward;
- one maintainer-review network for selected lanes;
- one evidence-import steward who keeps claims weaker than canon;
- optional consumer-facing documentation/editor partners later.

### Pilot-partner profile
- one internal CLI lane;
- one HTTP service lane;
- one publishable library or SDK lane;
- participating maintainers willing to review lane cards and defaults.

### First shipset
- a very small lane-card starter set
- conservative defaults for those lanes
- renewal receipts
- claims-pack template
- one consumer-routing example that stays visibly weaker than maintainer-authored canon

### Maintenance envelope
- explicit renewal windows;
- expiry states for stale cards;
- contributor review rules that distinguish imported fact from editorial recommendation.

### Narrow upstream asks
Later, and only if deserved:
- docs.rs or crates.io cross-link hooks;
- standard places to point from consumer tooling into canonical lane cards.

### Graduation / fold / kill rules
Graduate when:
- the corpus proves it can renew itself without pretending to be universal;
- maintainers actually review the claims in a few lanes;
- consumer slices remain visibly derived.

Fold or kill when:
- it becomes a popularity contest;
- renewal receipts are not maintained;
- it starts replacing maintainer docs rather than routing to them.

### Wrong launch pattern to refuse
- “best crates” leaderboard
- trust-score portal
- assistant-memory canon
- badge systems that flatten support truth

## Program 4 — Package Intake + Release Boundary Review launch charter
**Portfolio role:** urgent local-first bridge  
**Best initial residency:** local-first command / pack family with security- and operator-adjacent proving grounds

### Residency
The first home should be a **local-first intake review toolchain**, not a centralized reputation service.

### Owner shape
- one technical lead for the intake/replay pack family;
- one security/operator partner;
- one registry or publish-path liaison;
- one enterprise or high-discipline consumer of intake reviews.

This is an **operator bridge**, not a generic community portal.

### Pilot-partner profile
- one internal package intake team;
- one publish-path maintainer;
- one alternate-registry or non-default route case;
- one suspicious-package replay corpus owner.

### First shipset
- extraction/intake review receipt
- quarantine/waiver/replay flow
- release-boundary receipt
- malicious/suspicious package fixture bundle
- one older-Cargo or alternate-registry edge case

### Maintenance envelope
- incident-driven replay additions;
- route-specific caveat refresh;
- explicit distinction between local findings, registry facts, and RustSec imports.

### Narrow upstream asks
Only after local review value is proven:
- better import hooks from publish/package flows;
- better route or provenance facts when services choose to expose them;
- narrow security-surface coordination, not a universal trust oracle.

### Graduation / fold / kill rules
Graduate when:
- replay fixtures teach something before the next incident arrives;
- local review remains primary;
- waiver lineage survives handoff and audit.

Fold or kill when:
- the system drifts into vague package trust scoring;
- route-specific facts become invisible;
- the tool becomes registry-specific while claiming generality.

### Wrong launch pattern to refuse
- global trust-score dashboard
- “AI package reputation” veneer
- registry-branded fix sold as complete intake canon

## Program 5 — Safety-Critical + Institutional Readiness Commons launch charter
**Portfolio role:** stewarded program seam  
**Best initial residency:** consortium/editorial commons with named company owners and Rust Project collaboration

### Residency
This is the clearest case where the first serious home is **program-shaped**.
It should live as a readiness commons with consortium participation and explicit Rust Project touchpoints, not as one crate.

### Owner shape
- one consortium or equivalent multi-company steward lane;
- named maintainers from companies with direct safety-critical needs;
- one Rust Project liaison or champion where upstream interaction is required;
- one editorial owner for readiness profiles and evidence recipes.

### Pilot-partner profile
- one target-readiness checklist effort;
- one dependency-lifecycle / MSRV posture effort;
- one async/runtime requirement profile;
- one interop or qualification-adjacent profile;
- companies willing to help maintain the outputs, not just consume them.

### First shipset
- target-readiness profile(s)
- dependency-lifecycle playbook
- evidence recipe templates
- target/onramp cards
- one narrowly scoped async/runtime requirement profile
- one collaboration note describing which asks belong to companies versus the Rust Project

### Maintenance envelope
- named renewing owners per profile;
- review windows synchronized to release/toolchain reality;
- explicit statements of what is guidance versus project-owned substrate;
- consortium continuity planning.

### Narrow upstream asks
After the commons demonstrates real adoption:
- concrete target-readiness hooks or issue-routing lanes;
- collaboration on MSRV/LTS conventions where justified;
- shared requirements work on things like MC/DC or qualification-relevant surfaces.

### Graduation / fold / kill rules
Graduate when:
- multiple companies actively maintain and use the profiles;
- the commons produces durable readiness outputs rather than only conference interest;
- collaboration with the Rust Project is concrete and bounded.

Fold or kill when:
- the work becomes certification theater with no real owner;
- requirements are exported to the Rust Project without maintainers willing to validate and sustain them;
- “institutional” language outruns actual steward capacity.

### Wrong launch pattern to refuse
- one crate pretending to solve safety-critical readiness
- consultancy slideware with no maintained artifacts
- consortium branding without named company maintainers

## What got folded, refused, and left unchanged

### Folded under stronger parents
- generic “platform” thinking is folded under explicit charter questions;
- vague “someone should fund this” language is folded under owner shape, maintenance envelope, and plural funding lanes;
- vague “upstream should adopt this” language is folded under narrow-upstream-ask discipline.

### Explicitly refused
- hosted-first launches for evidence-heavy seams;
- unnamed-owner launches for maintenance-heavy seams;
- framework or portal dreams for recommendation-heavy seams;
- institutional aura without steward capacity.

### Left unchanged
- the broad ladder is unchanged;
- **Evidence Spine / Build-State Evidence** remains the strongest first build;
- **Feedback / Debug Acceptance Commons** remains the strongest second build;
- **Navigation / Defaults / Claims Commons** remains the strongest widener;
- **Package Intake + Release Boundary Review** remains the urgent bridge;
- **Safety-Critical + Institutional Readiness Commons** remains the clearest stewarded program seam.

## Recommended next repo move
The next good deepening is no longer another broad ranking note.
It is either:
- seam-local charter work for one of the top programs; or
- a small `charters/` family if the repo starts carrying concrete v0 implementation plans.

Until then, future revisions should treat **reference architecture + program charter** as the minimum pair for any serious “worthy epic” answer.

