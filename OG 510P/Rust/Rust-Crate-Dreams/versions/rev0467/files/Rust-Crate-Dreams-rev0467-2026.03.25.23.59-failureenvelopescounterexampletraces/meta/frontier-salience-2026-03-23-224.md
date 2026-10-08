# Frontier salience 224 — broad rerank after survey pain, official goals, docs.rs constraints, and registry trust surfaces

This pass re-read the archive as a **portfolio**, not as a hunt for one more clever missing crate.
The question was not “what idea could be added next?”
It was “which proposed crates would most materially improve the Rust ecosystem if they actually existed and were good?”

## Fresh ecosystem signals that matter

### 1. Compile/iteration pain is still central
The 2025 State of Rust results still list resource usage / slow compile times among the major pain points, and the 2025 compiler performance survey says build performance limits productivity, with many respondents still waiting more than ten seconds for rebuilds.
The same survey explicitly calls out unnecessary workspace rebuilds, slow linking, and Cargo / rust-analyzer blocking each other.

Sources:
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/inside-rust/2026/02/06/2025-Rust-Compiler-Performance-Survey-Results/

### 2. The official roadmap is already moving toward build introspection and workflow support
Recent Rust project goals explicitly include Cargo build analysis, build-dir layout reform, relink-don't-rebuild, production-ready Cranelift for local development, build-std improvements, sandboxed build scripts, public/private dependencies, SBOM precursor work, MC/DC, safety-critical lints, and FLS/spec upkeep.
That means the archive should favor crates that **turn these moving parts into reviewable user-facing support layers**.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h2/
- https://rust-lang.github.io/rust-project-goals/2026h1/

### 3. Async remains a live difficulty, but the missing value is often semantic honesty rather than another runtime helper
The latest Rust challenges write-up still names async complexity as a real pain for network developers.
That pushes concurrency-support and runtime-assurance ideas upward, but only when they publish crisp evidence about behavior rather than adding another abstraction shell.

Source:
- https://blog.rust-lang.org/2026/03/20/rust-challenges/

### 4. Documentation, provenance, and answerability matter more as people ask tools for help
The State of Rust results still say online documentation is the preferred canonical reference surface.
At the same time, docs.rs remains a resource-constrained, target-sensitive builder with explicit metadata knobs and limits.
That makes **pinned, cited, target-aware knowledge export** much more valuable than generic “crate chatbot” ideas.

Sources:
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://blog.rust-lang.org/2025/05/23/docsrs-default-targets/

### 5. Registry trust surfaces improved, but decision help is still missing
crates.io now exposes Security-tab facts, which is important, but that surface intentionally does not collapse security posture into a one-number crate choice answer.
The missing ecosystem contribution is still the layer that helps other people make and replay dependency decisions with explicit trade-offs.

Sources:
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://alpha-omega.dev/blog/rust-security-at-a-glance-crates.io-security-tab/

## Ranking: the most ecosystem-worthy missing crates right now

## 1. P-0537 Compile Iteration Feedback Kit

### Why it ranks here
This lane aligns directly with one of the ecosystem’s most repeated pains and with active official work on build analysis, shared build caches, relinking, and faster dev-oriented codegen.
It has unusually broad reach: app teams, game teams, embedded teams, CLI authors, IDE users, CI triagers, and compiler-adjacent tooling all feel the cost of iteration opacity.

### What it should provide other people
- `build-change-basis.receipt.json` — what actually changed between two builds.
- `rebuild-reason.report.json` — why each crate/unit rebuilt.
- `cache-contention.report.json` — whether workspace locking, analyzer access, or cache layout caused avoidable waiting.
- `iteration-outcome.report.json` — whether the developer got hotpatch, relink, rebuild, or restart.
- `action-plan.report.json` — concrete interventions, ranked by likely effect.
- portable bundle manifests for comparing multiple runs across time.

### Why it would be epic
It would turn build pain from “I waited again” into something other teams can inspect, diff, and fix.
That is a cross-cutting ecosystem service, not a niche helper.

## 2. P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit

### Why it ranks here
The ecosystem has many crates, increasingly visible security/trust signals, and many cases where the real pain is not writing code but **choosing the right dependency set without regret**.
Pathfinder is the receiver-facing missing layer between crates.io surfaces and concrete adoption decisions.

### What it should provide other people
- candidate corpus capture,
- inclusion / exclusion receipts,
- starter-set manifests,
- re-entry policies for previously excluded crates,
- decision timeboxes and replay packs,
- explicit “why this won over that” bundles portable into design review or procurement-like review.

### Why it would be epic
A good pathfinder crate reduces duplicated research across thousands of teams and makes dependency choice auditable instead of folkloric.

## 3. P-0535 Dependency Lifecycle Transition Kit

### Why it ranks here
Rust’s supply-chain and policy story is getting richer, but teams still lack a practical layer for moving from “this dependency is currently in the graph” to “we can replace, fork, pin, phase out, or re-resolve it safely.”
This sits right next to public/private dependency boundaries, SBOM work, and evolving stewardship/security signals.

### What it should provide other people
- current-lock selection anchors,
- clean-resolve risk reports,
- override provenance receipts,
- source-parity / fork-drift reports,
- off-ramp recipe bundles,
- local architectural placement records showing where a dependency actually matters.

### Why it would be epic
This is one of the strongest missing “operations of dependencies” layers in Rust today.
It helps real teams leave bad states instead of merely diagnosing them.

## 4. P-0536 Crate Knowledge Pack Kit

### Why it ranks here
The ecosystem increasingly needs artifacts that help humans and tools answer crate questions without hallucinating or flattening target/version/build differences.
Because docs.rs has limits and defaults, the valuable thing is not “chat over docs” but **pinned, cited, answerability-aware knowledge export**.

### What it should provide other people
- pinned docs/source/material bundles,
- excerpt lineage receipts,
- citation locators,
- item identity witnesses,
- target/build-surface notes,
- answerability and refusal matrices for assistant usage,
- compact exports for downstream search/index/agent tooling.

### Why it would be epic
This would become part of how crates explain themselves to downstream automation without pretending the automation is authoritative.

## 5. P-0538 Concurrency Contract Kit

### Why it ranks here
Async complexity is still a live challenge, and current Rust concurrency surfaces still require users to reconstruct critical semantics from crate-specific prose and folklore.
This proposal has become stronger precisely because it keeps splitting adjacent truths into separate support-contract lanes.

### What it should provide other people
At this point it should provide a portable bundle spanning:
- reentrancy scope,
- fairness/progress class,
- cancellation behavior,
- context legality,
- mobility/affinity,
- driver-liveness,
- delivery memory,
- backlog pressure,
- audience/claim semantics,
- acceptance/evidence,
- order/gaps,
- closure/tail,
- join horizon,
- observer-cursor posture,
- observer-progress isolation.

### Why it would be epic
It would let adopters compare async/concurrency surfaces with honesty instead of half-remembered blog-post lore.

## 6. P-0011 Crate Health Contract Kit

### Why it ranks here
As crates.io trust/security surfaces improve, teams still lack a compact maintainer-authored and import-aware answer to the stewardship question.
This lane has become more important, not less, because more signals now exist and are easy to over-read.

### What it should provide other people
- maintenance-window truth,
- maintenance-coverage truth,
- succession maps,
- support-intent receipts,
- routing-drift diffs,
- imported registry/repo signals kept separate from maintainer promises.

### Why it would be epic
It would give downstream users a better support-risk answer than popularity, last-release age, or vibes.

## 7. P-0440 Projection & Reborrow Semantics Kit

### Why it ranks here
The official 2026 flagship framing around “Beyond the &” makes advanced borrowing/projection ergonomics more important, not less.
A crate here matters when it helps other people use difficult ownership/borrowing patterns safely and predictably rather than merely exposing another clever API trick.

### What it should provide other people
- capability witnesses for supported projection/reborrow patterns,
- diagnostic explanation packs,
- compatibility boundaries,
- recipe fixtures for common container / pin / guard scenarios,
- portability ceilings around nightly/unsafe/toolchain assumptions.

## 8. P-0447 In-Place Initialization Adoption Kit

### Why it ranks here
This remains a high-leverage ergonomics/performance/safety lane around initialization patterns that are powerful but hard to productize for ordinary users.
It is the kind of crate that could move a difficult advanced technique into repeatable ecosystem practice.

### What it should provide other people
- initialization capability contracts,
- drop/partial-init safety witnesses,
- integration recipes for allocators / pin / builders / collections,
- adoption checklists and doctor checks,
- boundaries for when a plain builder or copy path is the better choice.

## 9. P-0532 Async Runtime Assurance Profile Kit

### Why it ranks here
If “Just Add Async” is a flagship theme, then downstream users need clearer capability and topology answers for runtimes and runtime-dependent crates.
This is broader than choosing Tokio vs async-std; it is about deployment truth and guarded capability claims.

### What it should provide other people
- runtime deployment topology receipts,
- capability availability matrices,
- surface guards for APIs that need specific runtime features,
- portability ceilings across local/threaded/embedded/serverless environments,
- bundles other crates can import into their own support contracts.

## 10. P-0484 Toolchain & Target Support Contract Kit

### Why it ranks here
The build-std, Rust-for-Linux, docs.rs target defaults, and safety/toolchain initiatives all reinforce how often users still ask “what does support for this target/toolchain actually mean?”
This crate would make target claims reviewable instead of rhetorical.

### What it should provide other people
- target support receipts,
- exercised-environment records,
- external-prerequisite declarations,
- host-vs-target execution truth,
- `std` / `no_std` / allocator / sanitizer / linker route boundaries,
- imported upstream authority kept separate from local exercise evidence.

## Next wave: very important, but less universally first

### P-0431 Public Dependency Boundary Kit
Essential for the 2026 supply-chain story, but a little narrower than the top ten because many teams can live without first-class public/private boundary receipts until later in adoption maturity.

### P-0125 Cargo SBOM Precursor Workbench Kit
Strategically important and well aligned with official goals, but still somewhat more institutional and pipeline-facing than the top workflow/choice/documentation crates.

### P-0427 Rust Specification Witness Kit
Potentially huge for safety-critical and proof-oriented work, but less universally first-order for ordinary teams than build/choice/docs/runtime lanes.

### P-0433 MC/DC Coverage Workbench Kit
Very important in safety-critical contexts and well aligned with 2026 goals, but not as cross-ecosystem day-one as the top ten.

### P-0175 Trusted Publishing Tooling Kit
Highly important for supply chain, but more deployment/governance-facing than the strongest receiver-facing everyday workflow gaps above.

## What not to over-promote right now

Do not reflexively promote a proposal just because it sounds novel.
A candidate should usually be demoted when it is mostly:

- a thin wrapper over an active upstream initiative,
- a narrow domain/parser/client bridge,
- a single-service integration,
- a better blog post disguised as a crate,
- or an AI shell without strong source-grounded bundles.

## Portfolio rule for future archive passes

When a future pass is tempted to add another proposal, first ask:

1. does it beat the current top ten on ecosystem-wide pain?
2. does it export more reusable artifacts than the current top ten?
3. does it create a genuinely new support-contract seam rather than a one-off feature lane?
4. could the value be captured more effectively by deepening an existing proposal instead?

If the answer is mostly “no,” the archive should deepen, merge, or eliminate instead of append.
