# Design: Epic contribution boundary map (2026Q1)

## Goal
The archive now has:
- a broad ladder for what matters most;
- scorecards for comparing already-worthy contributions;
- a delivery matrix for what each candidate should ship;
- an incubation map for what vehicle each candidate should start in;
- a proof-burden map for what each candidate must prove;
- a bet-sizing map for what capital band each candidate honestly needs;
- a compounding map for what unlocks later work;
- a support-bundle map for what each candidate should ask from the ecosystem;
- a renewal-burden map for what it costs to keep each one honest after launch; and
- a distortion-risk map for how the best ideas most easily go wrong while still looking successful.

What it still lacked was one sharper cross-seam answer to a different practical question:

> once we know a contribution is worthy, **where should its value actually live?**
> What should stay a companion tool, checker, atlas, or commons? What deserves narrow upstream hooks or stabilized machine-facing surfaces? What is really an upstream substrate or stabilization program from the start? And what only looks “official” because we have not separated boundary fit from importance?

This note is the archive's answer to that question.
It does **not** rerank the broad ladder.
It does **not** demote companion work as second-class.
It does **not** say “keep everything out of Cargo” or “merge everything into Cargo”.
It explains which worthy contributions belong **outside upstream**, which need **narrow upstream asks**, which are truly **upstream substrate programs**, and what first shipped artifacts look like in theory and practice.

Read with:
- `design/epic-contribution-distortion-risk-map-2026Q1.md`
- `design/epic-contribution-renewal-burden-map-2026Q1.md`
- `design/epic-contribution-support-bundle-map-2026Q1.md`
- `design/epic-contribution-incubation-map-2026Q1.md`
- `design/epic-contribution-proof-burden-map-2026Q1.md`
- `design/epic-contribution-compounding-map-2026Q1.md`
- `design/shared-spine-execution-blueprint-2026Q1.md`
- `design/portfolio-exemplar-federation-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/tooling-contract-execution-blueprint-2026Q1.md`
- `design/compatibility-claims-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- `design/semantic-context-execution-blueprint-2026Q1.md`

## Why this note is needed now
Current Rust signals are no longer just telling us “what is missing”.
They are telling us something stricter:
**several of the best-seeming ecosystem bets only stay honest if they begin outside upstream and ask for narrower hooks, while a smaller set are genuinely upstream substrate/stabilization work from the start.**

Cargo's own external-tools chapter still frames the relationship clearly: Cargo wants simple integration with third-party tools, offers bounded machine-facing surfaces like `cargo metadata`, `--message-format=json`, and custom subcommands, and tells consumers to pass explicit format versions to avoid forward-compatibility hazards.
https://doc.rust-lang.org/cargo/reference/external-tools.html
https://doc.rust-lang.org/cargo/commands/cargo-metadata.html

The Cargo 1.93 and 1.94 development-cycle posts make the boundary lesson even more explicit. Both say Cargo cannot be everything to everyone because of the compatibility guarantees it must uphold, while also showing active work on structured logging, `cargo report`, build-dir layout, custom final-artifact plumbing, and schema questions. That is exactly the pattern the archive needed to name: important ecosystem value often belongs in **companion layers importing bounded upstream surfaces**, not in Cargo becoming one giant product.
https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

The Cargo plumbing goal says the experiment should be a **third-party subcommand** to discover what Cargo should eventually integrate. That is a direct model for boundary-fit thinking: prototype outside, learn on real workflows, and upstream only the narrow parts whose compatibility burden belongs in Cargo.
https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html

Cargo build analysis and build-dir work reinforce the same split from another angle. Recorded build metadata, `cargo report`, and shared-cache/build-dir changes are important, but they are still prototyping and evolving. Tools built on top of them should therefore begin as companion layers that can move faster, attach richer receipts, and be honest about unstable imports while upstream stabilizes only the narrower machine-facing substrate.
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/

StableMIR / `rustc_public` is the opposite kind of signal. The whole point is to publish a more reliable compiler-facing API so tool developers can build on top of Rust without depending on compiler internals. That is not a hosted product idea; it is upstream substrate work that later companion tools should import.
https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
https://blog.rust-lang.org/2025/08/05/july-project-goals-update/

`build-std` and Rust-for-Linux tooling are another opposite-case signal. Their value is precisely about what Cargo/rustc and the standard library themselves must make stable or first-class: rebuilding std/core, ABI-affecting flags, hardening/sanitizer support, metadata for other build systems, and support for low-level projects that need stable, reusable foundations. Those are not ecosystem “apps”; they are upstream/stabilization programs.
https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
https://blog.rust-lang.org/2025/08/05/july-project-goals-update/

The `cargo-semver-checks` trajectory adds one more lesson: some strong companion checkers may eventually deserve partial upstream integration, but only after they have paid a very high proof burden and reduced false-positive/false-negative risk enough for Cargo's compatibility posture.
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html

The missing layer is therefore not another ranking rewrite.
It is a **boundary-fit map**.

## Headline answer
The archive should now assume:

> a worthy Rust contribution needs an explicit **residency claim**:
> **companion-first**, **companion with narrow upstream asks**, **consortium/editorial commons**, **operator bridge**, or **upstream substrate/stabilization program**.
> If the archive cannot say where the value should live and why, it is still reasoning at the wrong level.

Companion-first does **not** mean unimportant.
Upstream does **not** mean “more real”.
The right question is:
**where can the contribution stay honest while paying the smallest compatibility and maintenance burden consistent with its goals?**

## The five boundary families

### 1) Companion-first evidence or contract layer
Use this when the contribution needs to:
- iterate quickly on artifact families, exemplar packs, policy overlays, or opinionated reports;
- combine several upstream inputs that move at different cadences;
- say “unsupported”, “stale”, or “manual review required” without being forced into core-tool UX simplicity;
- or prove demand before any compatibility guarantee should be upstreamed.

Typical shape:
- CLI + schema family + fixture corpus + validator + exemplar packs.

Wrong shape:
- demanding that Cargo/rustc/docs.rs absorb the whole workflow immediately.

### 2) Companion layer with narrow upstream asks
Use this when the value mostly lives outside upstream, but upstream must expose one or two cleaner surfaces so the companion layer stops scraping, inferring, or relying on internals.

Typical asks:
- stable identifiers;
- explicit versioned machine-facing schemas;
- better report/plumbing commands;
- support for carrying metadata or receipts through existing workflows.

Wrong shape:
- “merge the whole product into Cargo”.

### 3) Consortium or editorial commons above upstreams
Use this when the value is mostly in coordination, acceptance matrices, checklists, curated defaults, or maintained guidance across several tools/targets/organizations.

Typical shape:
- editorial atlas, acceptance corpus, conformance matrix, readiness commons, or consortium pack set.

Wrong shape:
- pretending the right answer is one official plugin or one upstream command.

### 4) Operator / boundary bridge
Use this when the contribution sits at a live operational seam: registry intake, provenance routing, incident response, extraction boundaries, mirror posture, policy controls, or local-vs-public decision routing.

Typical shape:
- bridge tool or service with strong receipts and fail-closed behavior.

Wrong shape:
- trust-score portal or generalized “supply chain dashboard”.

### 5) Upstream substrate or stabilization program
Use this when the core value is *not* orchestration around upstream, but a more reliable upstream contract itself.

Typical shape:
- stabilized flag family;
- compiler/Cargo/library API or protocol;
- first-class metadata extraction path;
- or a language/toolchain feature whose absence forces entire classes of ecosystem work into hacks.

Wrong shape:
- wrapping the unstable gap in a polished companion product and calling the problem solved.

## Boundary-adjusted ranking of the strongest contributions
This is **not** a broad-importance rerank.
It is a “where should this live first?” ranking.

### 1) Build-State Evidence
**Residency:** companion-first with narrow upstream asks.

Why:
- the pain is broad and recurring;
- Cargo is actively building machine-usable inputs (`cargo report`, build-analysis, build-dir work);
- but those inputs are still evolving and not yet the whole answer.

What a worthy contribution should look like:
- a companion evidence kit that imports Cargo run/session/timing/rebuild signals where available;
- lineaged packs and diffs over exemplar workspaces;
- local and CI receipts that can say exactly what was observed, from which Cargo surfaces, on which build tuple;
- strong fallback / unsupported states when the needed surfaces are absent.

Upstream asks:
- stable identities and report semantics where justified;
- bounded machine-facing schema commitments for the pieces Cargo wants to support long-term;
- fewer reasons for tools to touch build-dir internals.

Wrong shape to refuse:
- “just put a build dashboard in Cargo”;
- anything that treats `target/` archaeology as the canon.

### 2) Feedback Loop / Debuggability Acceptance
**Residency:** consortium-style acceptance commons with narrow upstream asks.

Why:
- the problem spans debugger implementations, operating systems, IDEs, async runtimes, and compiler-generated debug info;
- acceptance is inherently cross-tool and cross-tuple;
- one plugin or one debugger integration cannot honestly stand in for the whole seam.

What a worthy contribution should look like:
- acceptance fixtures, async/visualizer tuples, and issue-routing packs across debugger families;
- an exemplar-backed acceptance matrix with explicit unsupported states;
- thin adapters for debuggers and IDEs, not one giant debugger replacement.

Upstream asks:
- better debug-info fidelity where Rust owns it;
- clearer hooks for async/task state visualization;
- compiler/runtime receipts that make failures classifiable.

Wrong shape to refuse:
- a single extension that demos well on one tuple and claims Rust debugging is solved.

### 3) Adoption Navigation + Ecosystem Atlas
**Residency:** external editorial/default commons with narrow metadata asks upstream.

Why:
- the value is in curation, decision briefs, maintained defaults, and slice-aware comparisons;
- upstream docs should remain authoritative for their own subjects, but not become a universal product-choice engine.

What a worthy contribution should look like:
- canonical-question briefs tied to maintained sources and exemplar profiles;
- explicit freshness and local-fit markers;
- exportable assistant slices that stay weaker than canon.

Upstream asks:
- better machine-usable docs metadata, support declarations, target metadata, or feature annotations where missing.

Wrong shape to refuse:
- “official Rust stack leaderboard”;
- recommendation pages whose summaries outrun source freshness.

### 4) Tooling Contract
**Residency:** companion protocol/contract kit with selective upstream plumbing asks.

Why:
- the value is in keeping discovery, manifest import, plan/execution, reports, and consumer handoff visibly separate;
- Cargo's own plumbing goal explicitly wants this experimentation outside Cargo first.

What a worthy contribution should look like:
- contract kit + adapters over Cargo plumbing/report/metadata lanes;
- bounded shared vocabulary and compatibility gates;
- fixture corpus proving where contracts hold or degrade.

Upstream asks:
- locate/read/report primitives that are versioned and bounded;
- better documented machine surfaces where Cargo already wants to support them.

Wrong shape to refuse:
- a Cargo replacement or giant workflow manager.

### 5) Compatibility Claims
**Residency:** companion checker/import layer with possible later partial upstream merge.

Why:
- the checker must combine several weak or partial inputs, sometimes including witness compilation;
- false positives and false negatives are too costly for casual upstreaming;
- but specific publish-time lanes may later deserve upstream hooks.

What a worthy contribution should look like:
- precise claim classes, witness programs when needed, versioned reports, and explicit “inconclusive” states;
- import from rustdoc JSON, StableMIR / `rustc_public`, and compiler/Cargo lanes where appropriate.

Upstream asks:
- stronger public-API and implied-bound information where rustdoc JSON is too weak;
- narrow Cargo hooks only after proof burden is paid.

Wrong shape to refuse:
- “Cargo should just tell you if your release is semver-safe” before the evidence is strong enough.

### 6) Package Intake Gateway
**Residency:** operator/security bridge with narrow upstream route/provenance asks.

Why:
- this seam sits at a live operational boundary involving crates.io posture, alternate registries, extraction behavior, and local policy;
- the right answer needs bridge behavior, receipts, route awareness, and fail-closed modes more than broad upstream UX.

What a worthy contribution should look like:
- intake route packs, extraction receipts, policy gates, and operator-facing decision outputs;
- sharp distinction between public-registry facts, local policy, alternate-registry posture, and verified versus hinted provenance.

Upstream asks:
- cleaner registry/route metadata and safer provenance/intake primitives where Cargo or crates.io can provide them.

Wrong shape to refuse:
- generic trust-score portal or “crate safety number”.

### 7) Safety-Critical Readiness Commons
**Residency:** consortium/institutional commons above upstream.

Why:
- the value is in readiness slices, maintained checklists, dependency-lifecycle discipline, evidence import, and shared program legitimacy across organizations;
- no single upstream team or one crate can honestly own the whole readiness story.

What a worthy contribution should look like:
- shared readiness profiles, authority-linked checklists, exemplar evidence imports, and named stewardship commitments.

Upstream asks:
- better substrate support where needed, but not “merge the safety commons into Rust itself”.

Wrong shape to refuse:
- one technical demo dressed up as a safety program.

### 8) Shared Spine / Semantic Context
**Residency:** companion stage-0 protocol and reference layer, importing upstream substrates.

Why:
- these are portfolio glue and bounded semantic/import layers;
- their job is to connect canon, lineage, and consumer handoff across later contributions.

What a worthy contribution should look like:
- shared envelope, lineage receipts, fixture packs, and bounded semantic-query layers;
- import from StableMIR / `rustc_public`, rustdoc JSON, Cargo reports, and other first-party surfaces.

Wrong shape to refuse:
- hosted mega-platform or LLM memory canon.

### 9) StableMIR / `rustc_public`, `build-std`, Rust-for-Linux stable tooling
**Residency:** upstream substrate/stabilization programs.

Why:
- the value here is a more reliable upstream contract itself;
- companion tooling can consume these, but cannot substitute for them.

What worthy contribution means here:
- RFC / MCP / stabilization work;
- public API publication and SemVer discipline;
- stable metadata extraction and low-level toolchain support.

Wrong shape to refuse:
- pretending a wrapper or hosted service solves the missing compiler/Cargo/library contract.

## Graduation rule: when should companion work move upstream?
The archive should now prefer this rule:

A companion layer should only seek upstream migration when **all** of these become true:
1. **bounded question** — the upstream ask is crisp and narrow;
2. **repeated demand** — many users need the same surface, not just one policy overlay;
3. **compatibility fit** — the long-term stability burden belongs in the upstream tool;
4. **proof paid** — exemplar packs and real users show the shape is correct;
5. **residue known** — the remaining opinionated/editorial/consortium pieces can still live outside.

If any of those fail, upstream should usually expose a narrower primitive and let the companion layer keep the rest.

## First-practice framework for future proposals
When evaluating a new “worthy contribution”, ask these in order:

### Question 1 — is the core value a new upstream truth, or orchestration around several truths?
- **new upstream truth** → substrate/stabilization candidate;
- **orchestration around several truths** → companion or commons candidate.

### Question 2 — does the contribution need to move faster than upstream compatibility allows?
- if yes, default companion-first.

### Question 3 — does it mostly coordinate several tools, organizations, or tuples?
- if yes, default consortium/editorial commons or operator bridge.

### Question 4 — can the first useful shipped artifact be a validator, corpus, adapter, or report?
- if yes, companion-first is probably honest.

### Question 5 — what is the narrowest upstream ask that would make the contribution more truthful?
- ask for that, not for product annexation.

## What this means for the repo itself
The archive should now stop talking as if “more official” is automatically better.
Future revisions should say explicitly:
- **where the value lives first**;
- **what narrow upstream hooks are wanted**;
- **what must never be upstreamed whole**;
- and **what artifact still has value if the upstream ask takes years**.

That shift also strengthens archive hygiene.
It gives future LLM/archive edits a way to avoid one recurring confusion:
mistaking a contribution's **importance** for an argument that Cargo or rustc should directly absorb it.

## Concrete design consequences for a future builder
If a small serious team wanted to build one portfolio-aware thing next:
- build a **companion-first evidence or contract layer** that imports current Cargo/compiler/docs.rs surfaces honestly;
- keep the first artifacts lineaged, replayable, and exemplar-backed;
- ask upstream only for the narrow machine-facing gaps that make the companion layer less scrappy;
- and explicitly refuse the temptation to become the Cargo replacement, the official recommendation portal, or the universal trust dashboard.

That remains the archive's strongest outside-the-box but plausible posture:
**thinner companions, sharper upstream asks, fewer fake platform empires.**
