# Design: Epic contribution handoff graph (2026 Q1)

## Goal
The archive already knows:
- which Rust ecosystem seams rank highest;
- what the first believable wedges are;
- what repeated decision journeys they should compose inside; and
- what exact first shipsets the current kernelized seams should take.

What it still lacked was one compact answer to a narrower implementation question:

> once the strongest seams already have shipsets, **what exact artifacts should move between them, what stable versus unstable surfaces are allowed to carry those artifacts, and what fake all-in-one product shape should still be refused?**

This note is the archive's answer to that question.
It does **not** rerank the broad ladder.
It does **not** promote a new frontier.
It adds a **handoff graph / receipt-edge ledger** so future revisions can say how the best small-team repos should exchange facts, review packets, and readiness receipts without improvising a giant platform.

Read with:
- `design/epic-contribution-kernel-shipset-ledger-2026Q1.md`
- `design/epic-contribution-decision-journeys-2026Q1.md`
- `design/epic-contribution-launch-wedges-2026Q1.md`
- `meta/HANDOFF_GRAPH_PROTOCOL.md`
- `ledgers/top-band-handoff-graph-v0/handoffs.json`
- `ledgers/top-band-kernel-shipsets-v0/shipsets.json`

## Why this pass is merited now
The live Rust picture keeps rewarding **explicit handoffs between narrow tools** over one magical control plane.

Cargo's external-tools reference still centers three public integration lanes for third-party tooling: `cargo metadata`, `--message-format=json`, and custom subcommands. It also says the `cargo metadata` format is stable and versioned when called with an explicit `--format-version`. That is a strong signal that worthy ecosystem products should compose through documented artifact lanes rather than through Cargo-as-a-library fantasies.  
https://doc.rust-lang.org/cargo/reference/external-tools.html

Cargo build analysis is still prototype-stage: the goal is to record build metadata across invocations and add unstable `cargo report` subcommands for rebuild explanations and timing history. That means the archive needs one place to say which handoffs may consume those facts, and how they must preserve unstable-versus-stable posture instead of laundering prototype state into fake permanence.  
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html

The March 2026 build-dir-layout testing call makes the same composition pressure very concrete. The post says the build-dir layout is internal-only, yet many projects still rely on unspecified details because features are missing; it explicitly asks people to run tests, release processes, and anything else touching build-dir or target-dir against the new layout. That is exactly a handoff problem: build facts, path receipts, and migration caveats need an endorsed route into downstream tools instead of repeated ad hoc scraping.  
https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/

Registry and release-boundary work is also increasingly handoff-shaped. The crates.io January 2026 update added GitLab support for Trusted Publishing, Trusted Publishing only mode, blocked risky GitHub Actions triggers, and a `pubtime` field in the index. The March 2026 Cargo security advisory says crates.io deployed a preventative change on March 13 and audited all published crates for this incident class. Those are real service truths, but they still need local review kits and route-specific receipts rather than one universal trust badge.  
https://blog.rust-lang.org/2026/01/21/crates-io-development-update/  
https://blog.rust-lang.org/2026/03/21/cve-2026-33056/

The March 2026 Project Director update adds another important ingredient: `cargo-capslock` now exists for static and runtime capability analysis, the vulnerability-surfacing-to-crates.io RFC has been accepted, and the Foundation is discussing an End User Group aimed at stronger reciprocal relationships with industrial users and tooling innovation. That is a strong cue that some of the missing value in Rust is now about how service truth, capability receipts, and local review artifacts travel together.  
https://blog.rust-lang.org/inside-rust/2026/03/25/project-director-update/

The release-boundary path also keeps getting more explicit. The `cargo-semver-checks` goal says the cargo team wants integration into the `cargo publish` workflow, potentially default-on with an override flag, and the current approach includes witness-program generation compiled with `cargo check`. The goal also says rustdoc JSON currently lacks some precise information that the tool needs. docs.rs in turn says hosted rustdoc JSON is programmatic but caveat-heavy: consumers must inspect `format_version`, old releases may not yet have downloads, and redirect targets may briefly not exist. That is exactly the kind of caveated handoff the archive should make explicit.  
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html  
https://docs.rs/about/rustdoc-json

The libtest JSON goal reinforces the same point from the test side. It says Cargo could benefit from programmatic test output, and that shifting responsibilities from the test harness to the runner enables stronger experiments and custom runners like `cargo nextest`. That means test and debug flows need explicit receipt edges rather than prose-only “integration later” promises.  
https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html

Finally, the 2025 State of Rust survey and the March 2026 challenges post still point to build/resource pain, crate-choice burden, debugging pain, embedded constraints, and safety-critical maturity gaps. The survey also says online docs remain the preferred canonical reference even as some learning traffic appears to be moving toward LLM tooling. Together, those signals argue for receipt-bearing, inspectable handoffs over conversational or portal-shaped glue.  
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/  
https://blog.rust-lang.org/2026/03/20/rust-challenges/

## Headline answer
A worthy repo should now keep a **handoff graph ledger** for the strongest seams.

A handoff card is a compact answer to:
1. what artifact or fact family is being handed off;
2. who the producer and consumer are;
3. what journey that edge primarily serves;
4. what transformation is allowed in the middle;
5. what stable, unstable, and service-boundary surfaces the edge may rely on;
6. what output receipt should exist after the handoff;
7. what tempting collapse the archive still refuses; and
8. what review cadence should revisit the edge.

The point is not to replace kernel briefs or journeys.
The point is to stop future revisions from saying “these contributions fit together somehow” without naming the actual edge.

## What this layer governs
Use the handoff graph when the repo needs to answer:
- what artifact should move from one top seam into another;
- whether a proposed integration depends on stable, unstable, or service-only truth;
- what bridge modules or adapters belong in the first repo instead of in a later platform;
- which cross-seam edge deserves hardening first; or
- whether a new idea is a missing handoff or just a renamed monolith dream.

Do **not** use this layer to:
- rerank seams;
- promote a whole new worthy-contribution frontier;
- pretend that every adjacent seam needs a direct edge; or
- claim that a passing ledger means the integration is strategically sufficient or semantically complete.

## Current interpretation
The archive's best current receipt edges are:
1. **Cargo raw facts → Build-State Pack**
2. **Build-State Pack → Debug Acceptance Matrix**
3. **Registry/security truth → Intake Review Kit**
4. **Structured API facts → Release-Boundary Review**
5. **Intake + compatibility receipts → Safety Readiness Cards**
6. **Reviewed receipts → Conservative defaults and atlas guidance**

That ordering matters.
The first edge hardens raw facts into reviewable build evidence.
The middle edges turn service truth and machine-readable surfaces into operator decisions.
The later edges prevent navigation and safety work from becoming vibe layers.

## Cross-card rules

### 1) A handoff edge must be narrower than a platform
A handoff card names a producer, a consumer, and the receipt that should travel.
If the card starts inventing its own giant storage, workflow engine, or hosted truth plane, it has widened into the wrong thing.

### 2) Stable, unstable, and service truth must stay visibly distinct
A good edge says whether it depends on:
- stable/versioned CLI or file surfaces,
- unstable prototype surfaces,
- or service-side truth from crates.io or docs.rs.

Do not flatten those into one fake compatibility guarantee.

### 3) Each edge should end in a reviewable receipt
If an edge only produces more hidden state, dashboards, or “insights,” it is incomplete.
The archive should prefer packs, diff notes, waiver receipts, readiness cards, or renewal receipts.

### 4) Handoff cards should compose with shipsets and journeys
A valid edge should point back to the kernel shipset that produces or consumes it and to the decision journey that gives the edge meaning.
If those links are missing, the edge is probably atmospheric.

### 5) Refused collapses are part of the design
Each edge must say what product collapse it resists: scoreboards, portals, universal trust graphs, debugger replacements, or platform glue that pretends every handoff is one database row away.

## Preferred deepen order from this layer
This note does not change the broad ladder, but it sharpens the next practical buildout order:
1. harden **Cargo raw facts → Build-State Pack** first;
2. harden **Registry/security truth → Intake Review Kit** second;
3. harden **Structured API facts → Release-Boundary Review** third;
4. deepen **Build-State Pack → Debug Acceptance Matrix** fourth;
5. keep **Intake + compatibility receipts → Safety Readiness Cards** as the clearest stewardship-heavy bridge; and
6. keep **Reviewed receipts → Conservative defaults** deliberately narrow until renewal burden improves.

## What should still be refused
Do not let this layer become:
- a universal artifact bus,
- a hosted workflow shell for every Rust tool,
- a reason to centralize all proof in Cargo core,
- or a substitute for seam-local contracts, witnesses, fixtures, and source-candor.

The right outcome is smaller and more useful: a repo that can now say **what evidence-bearing edges should exist between its best ideas, and what each edge is allowed to mean in practice**.
