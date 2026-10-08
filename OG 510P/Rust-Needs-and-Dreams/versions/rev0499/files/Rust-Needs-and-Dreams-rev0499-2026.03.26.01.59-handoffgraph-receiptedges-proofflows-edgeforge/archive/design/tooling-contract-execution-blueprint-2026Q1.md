# Design: Tooling Contract execution blueprint 2026Q1

## Why this note exists now
The archive already had the right ingredients for **Tooling Contract**:
- `design/tooling-contract-stack.md`
- `design/tooling-contract-pilot-program.md`
- `proposals/epic-tooling-contract-stack.md`
- `design/repo-composition-stack.md`
- `design/build-interop-kit.md`
- `design/build-state-evidence-stack.md`
- `design/workspace-environment-execution-blueprint-2026Q1.md`
- `design/cargo-artifact-contract-execution-blueprint-2026Q1.md`

What it still lacked was the same thing Build-State Evidence, Feedback Loop, Cargo Artifact Contract, Workspace Environment, Reviewable Edit, Public API, Benchmark Evidence, Defect Escalation, Observability, Release Truth, and Compatibility Claims now have:

> one direct answer to **what the worthy contribution should actually ship in theory and practice**.

That absence matters because the current ecosystem pressure is no longer only “Cargo needs more plumbing” or “tools should stop scraping `target/`”.
It is that serious Rust teams increasingly need one honest machine-facing answer to:
- what Cargo discovered,
- what workspace and package scope was actually selected,
- what graph and plan were intended,
- what execution and rebuild evidence actually occurred,
- what parts came from stable surfaces versus experimental imports,
- what adapter lossiness remained,
- and what later IDE / CI / outer-build / docs / release / support / assistant consumers may honestly conclude.

The archive should therefore stop treating Tooling Contract as only a synthesis stack.
It should describe a real contribution shape.

## Fresh signals that force the seam into focus
Primary sources now line up around the same missing middle:
- Rust’s 2026 flagships explicitly keep **integrate Cargo into larger build systems** inside the active “Building blocks” agenda. That is a direct signal that machine-facing Cargo contracts are strategic infrastructure rather than optional polish.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo’s accepted plumbing goal still says current programmatic surfaces are too porcelain-oriented, that `cargo metadata` excludes feature resolution, and that builds decompose into explicit phases from project discovery through final-artifact staging.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo’s stable external-tools docs still center on only three broad integration lanes — `cargo metadata`, `--message-format=json`, and custom subcommands. Those are valuable, but they still do not form one coherent discovery → scope → plan → execute → handoff story.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo metadata itself remains versioned and future-evolving, which is good for a stable import lane but also a reminder that one metadata dump is not the whole tooling story.
  https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo’s build-cache docs now explicitly separate final artifacts in `target-dir` from intermediate build artifacts in `build-dir`, while saying the build-dir layout is internal and subject to change. The March 2026 testing call is even more direct: many projects still rely on unspecified details because Cargo lacks the right features.
  https://doc.rust-lang.org/cargo/reference/build-cache.html
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo’s unstable surface still treats `--unit-graph` as internal-graph JSON and build analysis as recorded metrics queried later, which means the missing contribution should import those surfaces honestly instead of pretending they already solve the whole contract problem.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo 1.94 kept structured logging, `cargo report rebuild`, `cargo report sessions`, and workspace/config discovery active, while also reiterating that Cargo cannot be everything to everyone and that plugins matter.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- rust-analyzer still exposes `cargo.targetDir` specifically to avoid lock contention from its own `cargo check` / build-script / proc-macro activity, at the cost of duplicating artifacts; it also documents override commands and `{label}` interpolation for non-Cargo build systems. That is unusually concrete evidence that external tools still need a better shared contract with Cargo.
  https://rust-analyzer.github.io/book/configuration.html

Taken together, those signals say the missing contribution is not another Cargo wrapper and not a giant build-control plane.
It is a **reviewable tooling-contract layer**.

## Headline answer
If one serious team wants to build the archive’s clearest remaining machine-facing Cargo composition contribution, the answer should now be:

> Build a **Tooling Contract reference layer** that links discovery and package-selection truth, graph/plan truth, execution/build-state evidence, stability posture, adapter lossiness, and bounded consumer handoffs; emit reusable reports and packs; and prove the shape across IDE, CI, outer-build, docs, release, support, and assistant consumers without collapsing them into one universal protocol.

That answer is deliberately broader than **Build Interop**.
It is also deliberately narrower than “replace Cargo, rust-analyzer, and every Rust build wrapper with one platform”.

## What this contribution should be in theory

### Core thesis
A tooling-contract system becomes real ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what exact subject is under discussion** — workspace, cwd-rooted invocation, package-selection slice, or consumer-targeted lane;
2. **what discovery and scope facts were used** — manifests, config roots, workspace inheritance, `default-members`, package flags, target/profile/feature slices;
3. **what graph and plan were intended** — package graph, unit graph, dynamic-expansion boundaries, artifact intents, and why exact final commands may still vary;
4. **what execution and evidence facts actually occurred** — sessions, rebuild reasons, blocking, reuse, reports, emitted artifacts, and imported raw attachments;
5. **what stability posture exists** — stable Cargo surface, unstable-but-imported report, tool-specific projection, or lossy adapter;
6. **what downstream consumer may honestly import** — IDE, CI, outer-build, docs, release, support, incident, and assistant consumers should each get bounded summaries rather than freelancing from raw logs;
7. **what remains explicitly out of scope** — e.g. universal build orchestration, stable build-dir internals, or total normalization across every outer build system.

If a project cannot answer those questions without stitching together `cargo metadata`, `--message-format=json`, unstable `--unit-graph`, session logs, rust-analyzer settings, dep-info files, and issue-thread archaeology by hand, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable machine-facing Cargo truth and handoff**.

It should include:
- tooling subject identity;
- discovery and scope truth;
- graph/plan truth;
- execution/evidence truth;
- stability and adapter-lossiness vocabulary;
- consumer-bounded exports and redactions.

It should not become:
- a Cargo daemon;
- a new universal monorepo/workspace manager;
- a frozen copy of Cargo internals;
- a BSP-only bridge;
- or another wrapper that still depends on `target/` folklore while pretending not to.

### Separation rule
A worthy contribution here must preserve at least six distinct truth classes:
- **subject truth** — which workspace / invocation / package-selection slice the record describes;
- **discovery-and-scope truth** — how Cargo found manifests and configs, and what ended up in scope;
- **graph/plan truth** — what Cargo intended to execute and where dynamic expansion remained;
- **execution/evidence truth** — what actually ran, rebuilt, blocked, reused, or emitted;
- **stability / adapter-lossiness truth** — which facts came from stable interfaces, unstable imports, or lossy projections;
- **consumer-handoff truth** — what later consumers may import and what they must not over-claim.

Without that separation, one metadata snapshot, one `rust-project.json`, one report log, one `--message-format=json` stream, or one assistant summary silently becomes “the tooling contract”, and the whole layer stops being honest.

### Shape rule
The primary contribution shape should now be:
- **reference layer + report/pack command + adapter/import corpus**.

Why this shape fits:
- **reference layer** because the seam is really about subject identity, evidence vocabulary, stability posture, and non-collapse rules;
- **report/pack command** because the missing piece is a portable output that teams can diff, attach, and import elsewhere;
- **adapter/import corpus** because the ecosystem already has several partial lanes and the point is to preserve them honestly rather than erase them.

Wrong shapes to refuse first:
- one more Cargo wrapper;
- target-dir or build-dir scraper theater;
- BSP-only protocol capture;
- a universal daemon / server mode pitch;
- a hosted build-graph portal;
- or an assistant-facing summary format that cannot point back to source evidence.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo tooling-contract inspect-scope`
- `cargo tooling-contract export-scope`
- `cargo tooling-contract export-plan`
- `cargo tooling-contract import-evidence`
- `cargo tooling-contract adapter-report --for <rust-analyzer|ci|bsp|outer-build|assistant>`
- `cargo tooling-contract handoff --to <ide|ci|outer-build|docs|release|support|assistant>`
- `cargo tooling-contract pack`
- `cargo tooling-contract doctor`

The tool should **import** Repo Composition, Build Interop, Build-State Evidence, Cargo report outputs, and selected rust-analyzer or wrapper facts where possible rather than replacing them.

### Public artifact spine
A credible public artifact family would keep the current stack ideas but make the review spine explicit:
- `tooling-subject/v0`
- `tooling-scope-report/v0`
- `tooling-plan-register/v0`
- `tooling-evidence-register/v0`
- `tooling-adapter-report/v0`
- `tooling-consumer-handoff/v0`
- `tooling-contract-pack/v0`

The pack should import, not replace:
- `workspace-report/v0` and `config-set/v0` attachments;
- `workspace-graph/v0` and `build-plan/v0` attachments;
- `cargo-events/v0` and build-state/report imports;
- raw pointers to `cargo metadata`, `--unit-graph`, report JSONL logs, dep-info files, rust-analyzer discovery output, or outer-build labels where present.

### First proving lanes
A credible rollout should rank proving lanes instead of pretending every consumer lands at once.

#### Lane 1 — discovery and package-selection lane
Start where disagreement is cheapest to explain and most expensive to ignore.

What to prove:
- one invocation can freeze what Cargo discovered and why;
- config and manifest roots stay explicit;
- workspace inheritance, `default-members`, cwd effects, and explicit package flags stay visible;
- later consumers stop saying “the repo” when they really mean different scopes.

#### Lane 2 — graph and plan lane
Only after scope is fixed should the tool export build intent.

What to prove:
- package graph and unit graph stay visibly distinct when needed;
- feature resolution posture and dynamic expansion boundaries remain attached;
- artifact intent is visible without pretending final shell commands are frozen;
- plan imports can coexist with non-Cargo labels instead of flattening them.

#### Lane 3 — execution and build-state import lane
Only after scope and plan are honest should live evidence be imported.

What to prove:
- sessions, rebuild reasons, blocking, reuse, and report imports stay linked to the earlier subject;
- stable-vs-unstable posture is explicit;
- raw attachments remain accessible for audit;
- build-state evidence can enrich the contract without becoming the whole contract.

#### Lane 4 — IDE and outer-build adapter lane
This is where the contribution proves it is useful beyond Cargo theory.

What to prove:
- rust-analyzer projections can attach explicit lossiness notes;
- non-Cargo build labels can coexist with Cargo package IDs;
- CI and wrapper tools can import the same scope/plan/evidence story;
- adapters no longer need to hide duplicated artifacts, lock-contention workarounds, or projected labels behind folklore.

#### Lane 5 — docs / release / support / assistant handoff lane
Only after the machine-facing spine is credible should broader consumers be allowed in.

What to prove:
- docs/release/support/assistant consumers get bounded summaries instead of raw build logs;
- consumer claims remain linked to the canonical pack;
- out-of-scope conclusions remain explicit;
- later archive summaries remain derived rather than silently canonical.

## Why this sits above adjacent seams instead of replacing them
This contribution is only honest if it keeps its imported owners separate:
- **Repo Composition** owns discovery roots, config layers, workspace inheritance, and package-selection posture;
- **Build Interop** owns workspace graphs, plans, events, and adapter posture;
- **Build-State Evidence** owns rebuild reasons, cache/reuse/block truth, and diagnostic imports;
- **Workspace Environment** owns declared intent, realization, secret posture, and observation around the machine context;
- **Cargo Artifact Contract** owns final-output identity and sidecar continuity.

Tooling Contract should compose those truths, not overwrite them.

## Ranking effect inside the archive
This revision does **not** change the broad shortlist.

It does change the archive’s practical interpretation:
- **Build-State Evidence** still remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** still remains the clearest under-ranked missing middle in the daily loop;
- **Tooling Contract** should now be treated as the clearest current **machine-facing Cargo composition / scope-plan-evidence / adapter-lossiness execution blueprint**;
- and future repo-composition, build-interop, rust-analyzer, CI, outer-build, and assistant-handoff work should route through this execution blueprint instead of rediscovering the boundary privately.

## Default build recommendation
If someone asked what to actually fund or build first in this seam, the archive should now answer:
1. one honest `tooling-contract-pack/v0` and doctor/verify flow;
2. discovery and scope receipts first;
3. graph/plan registers second;
4. imported report/build-state evidence third;
5. rust-analyzer / CI / outer-build adapter reports fourth;
6. docs / release / support / assistant handoffs last.

That order is more realistic than trying to standardize one universal build protocol in a single move.
