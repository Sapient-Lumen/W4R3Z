# Design: Native Edge execution blueprint (2026 Q1)

## Goal
Turn the archive's active **specialist frontier** into a sharper **buildable program**.

The missing contribution is not another binding generator, another `-sys` helper, another `pkg-config` wrapper, another `build.rs` cookbook, or another universal interop framework.
It is a disciplined companion layer that lets Rust teams carry **reviewed native-edge subject truth** across Rust↔C/C++ boundaries, provider/link decisions, host-vs-target context, and foreign-build handoff.

Read this note when the question is narrower than the frontier promotion itself:

> if a serious team builds the archive's Native Edge answer, what exact artifact families, commands, pilot lanes, and anti-goals should it have in theory and practice?

## Why this note is needed now
The archive already promoted **Native Edge Contract** as the strongest specialist frontier.
What it still lacked was the same execution-grade answer it now has for Build-State, Semantic Context, Package Intake, Migration/Public API, and Adoption Navigation.

That missing execution answer matters more now because the official and primary-project signals have gotten sharper:
- the accepted 2025H1 goal **Evaluate approaches for seamless interop between C++ and Rust** says Rust should seriously consider what it takes to enable adoption in projects that must use **large, rich C++ APIs**;
- the 2025H2 **C++/Rust Interop Problem Space Mapping** effort says there are **billions of lines of C++** representing enormous value and that full rewrites are not the practical near-term answer;
- the July 2025 goals update says Rust should evolve toward a **first-class C++ interop story**, while also stressing that different groups need different interop lanes;
- the January 2026 program-management update makes **Cross-language interop** an explicit application area for industry funding and also highlights live CPython collaboration topics like std-linking, linker-argument splits, and introducing Rust into large C codebases;
- the January 2026 safety-critical writeup says many teams will integrate Rust into existing C and C++ systems and carry that boundary for years, and explicitly recommends treating interop as part of the safety story;
- Cargo's own docs still show why this remains a compositional rather than solved problem: build scripts own native probing/building, `links` is limited to one package per value with metadata passed only to immediate dependents, host-vs-target behavior is still confusing enough to need `target-applies-to-host` and `host-config`, and build-script overrides exist precisely because some native lanes need structured facts without running the original script;
- and the live tool families are serious but non-equivalent: CXX focuses on a safe common Rust/C++ regime, `autocxx` targets large existing C++ codebases, `bindgen` still depends on `libclang`, and Corrosion proves foreign-build handoff is real but still leaves many boundary/provider choices to users.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h1/seamless-rust-cpp.html
- https://rust-lang.github.io/rust-project-goals/2025h2/interop-problem-map.html
- https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://doc.rust-lang.org/cargo/reference/build-scripts.html
- https://doc.rust-lang.org/cargo/reference/config.html
- https://doc.rust-lang.org/cargo/reference/unstable.html
- https://cxx.rs/
- https://google.github.io/autocxx/
- https://rust-lang.github.io/rust-bindgen/requirements.html
- https://corrosion-rs.github.io/corrosion/usage.html
- https://corrosion-rs.github.io/corrosion/ffi_bindings.html

## Headline answer
If one serious team wants to build the archive's strongest specialist frontier, the answer should now be:

> Build a **Native Edge reference layer** that imports boundary artifacts, provider/link artifacts, host-vs-target/toolchain context, and foreign-build handoff notes into one reviewable subject; preserves those truths as distinct layers; and emits renewable briefs, packs, diffs, and handoffs for C/C++ integrators, release/support/audit consumers, and adjacent Rust tools.

That answer is deliberately narrower than “solve interop”.
It is also deliberately stronger than “pick the best FFI tool”.

## What this contribution should be in theory

### Core thesis
A native-edge system becomes ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what exact mixed-language or native-provider subject is under review;**
2. **what exact boundary artifacts were imported and how they were generated;**
3. **what exact provider, link, and search-path decisions shaped the build;**
4. **what host-vs-target, linker, SDK, runtime, or build-script context mattered;**
5. **what foreign build system or downstream consumer is expected to ingest the result;**
6. **what downstream conclusions are justified, and until when.**

If a project cannot answer those questions without reading `build.rs`, generated headers, CMake glue, local toolchain setup, and tribal-memory issue threads, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable native-edge review and handoff**.

It should include:
- exact subject capture;
- imported boundary truth;
- imported provider/link truth;
- explicit host/target/toolchain and foreign-build context;
- bounded release / support / audit / atlas handoffs.

It should not become:
- a universal Rust ABI project;
- a universal C++ bridge;
- a universal native package manager;
- a replacement build system;
- or a fake one-number “interop readiness” score.

### Separation rule
The contribution must preserve at least six distinct truth classes:
- **subject truth** — which crate/workspace/revision/lane/platform set is actually under review;
- **boundary truth** — what symbols, types, ownership/lifetime/layout claims, and generated artifacts define the language boundary;
- **provider/link truth** — what native dependency provider, fallback, link mode, search paths, and reason-coded decisions actually won;
- **context truth** — what host-vs-target split, linker choice, SDK/sysroot/runtime details, build-script assumptions, and toolchain quirks shaped the result;
- **handoff truth** — what a CMake/Bazel/Buck/Nix/distro/manual consumer is expected to ingest or reconstruct;
- **brief / consumer truth** — what release, support, safety, audit, or guidance consumers may honestly conclude.

This is the most important theory/practice guardrail in the whole design.
Without it, every interop result becomes one giant folklore blob.

### Composition rule
A worthy v0 should **compose imported artifacts** instead of replacing them.

It should import, not erase:
- `ffi-pack/v0`
- `native-pack/v0`
- optional build-interop exports
- optional cross-toolchain / support / release / safety attachments
- optional package-intake facts when provider payloads arrived through a notable intake route

And then it should emit one thinner **native-edge family** above those imports.

### Pressure rule
The execution design should reflect present-day Rust reality, not an imagined finished interop future.
That means treating these as first-class pressures instead of edge cases:
- build scripts are still how Cargo integrates native probing/building and their outputs/order matter;
- `links` and `DEP_<links>_*` metadata prove there is a principled native-dependency lane, but not yet a full subject-level handoff;
- build-script overrides prove some teams need structured imported facts without re-running upstream probing;
- host artifacts versus target artifacts are still tricky enough that Cargo documents unstable `target-applies-to-host` and `host-config` behavior;
- unwinding and ABI choices remain explicit correctness surfaces, not background details;
- platform/runtime shifts such as musl 1.2.5 updates, Emscripten exception-model changes, and Windows runtime mismatches in mixed builds show that “it linked once” is not durable truth.

Sources:
- https://doc.rust-lang.org/cargo/reference/build-scripts.html
- https://doc.rust-lang.org/cargo/reference/environment-variables.html
- https://doc.rust-lang.org/cargo/reference/config.html
- https://doc.rust-lang.org/cargo/reference/unstable.html
- https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html
- https://doc.rust-lang.org/reference/panic.html
- https://doc.rust-lang.org/beta/releases.html
- https://blog.rust-lang.org/2025/12/05/Updating-musl-1.2.5/
- https://corrosion-rs.github.io/corrosion/common_issues.html

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo native-edge capture`
- `cargo native-edge boundary`
- `cargo native-edge providers`
- `cargo native-edge context`
- `cargo native-edge handoff`
- `cargo native-edge brief`
- `cargo native-edge diff`
- `cargo native-edge pack`

The tool should **import** FFI/provider/build-system surfaces when available rather than pretending it discovered the truth from scratch.

### Public artifact spine

#### Imported families
- `ffi-pack/v0`
- `native-pack/v0`
- optional `build-interop-pack/v0`
- optional `toolchain-pack/v0` or support/release/safety attachments
- optional package-intake or provenance receipts when those materially shaped native inputs

#### Public native-edge families
- `native-edge-subject/v0`
- `native-edge-boundary-report/v0`
- `native-edge-provider-report/v0`
- `native-edge-context-report/v0`
- `native-edge-handoff/v0`
- `native-edge-brief/v0`
- `native-edge-diff-report/v0`
- `native-edge-pack/v0`

### Minimum schema disciplines
Every public artifact should keep these fields first-class:
- **subject identity** — crate/workspace/revision, lane kind, supported host/target tuples, and comparison base;
- **authority posture** — imported from boundary pack, imported from provider pack, observed locally, or derived;
- **generation provenance** — tool family (`bindgen`, `cbindgen`, CXX, `autocxx`, handwritten, provider crate, build-system adapter) and version/command details when available;
- **platform context** — linker, SDK/sysroot, runtime/CRT, unwind assumptions, and build-script vs external-build ownership;
- **freshness anchors** — source revisions, header versions, package versions, tool versions, review timestamp, and renewal triggers;
- **consumer limits** — what release/support/audit/CI/assistant consumers may and may not claim;
- **reason-coded ambiguity** — why a result is partial, provisional, provider-specific, or lane-limited;
- **raw attachments** — generated headers, symbol snapshots, config snippets, `pkg-config` output, Corrosion/CMake fragments, or other captured material when present.

### Commands and what they should emit

#### `cargo native-edge capture`
Purpose:
- define the exact reviewed subject;
- declare lane type (C ABI export, system-library consumer, C++ bridge, external-build handoff, etc.);
- record host/target tuples and comparison base;
- emit `native-edge-subject/v0`.

Important rule:
- if the subject is under-specified, preserve that under-specification explicitly instead of silently assuming one happy-path target or build system.

#### `cargo native-edge boundary`
Purpose:
- import or validate the boundary side of the subject;
- attach generated-artifact provenance, exposed/imported symbol sets, and drift notes;
- emit `native-edge-boundary-report/v0`.

Important rule:
- boundary truth must stay weaker when it is inferred from generated artifacts alone than when it is backed by explicit reviewed manifests.

#### `cargo native-edge providers`
Purpose:
- import or validate provider-choice and link-plan truth;
- attach `links`, `DEP_<links>_*`, `rustc-link-lib`, `rustc-link-search`, provider outputs, and reason-coded fallbacks;
- emit `native-edge-provider-report/v0`.

Important rule:
- provider truth must not be collapsed into boundary truth even when one tool generated both.

#### `cargo native-edge context`
Purpose:
- record host-vs-target split, linker/toolchain context, runtime/CRT assumptions, build-script overrides, and foreign-build ownership;
- emit `native-edge-context-report/v0`.

Important rule:
- context should explain why the lower-layer facts look the way they do; it should not replace them.

#### `cargo native-edge handoff`
Purpose:
- render smaller exports for external build systems or downstream reviewers;
- support targets such as `cmake`, `bazel`, `buck`, `nix`, `distro`, `release`, `support`, `audit`, and `assistant`;
- emit `native-edge-handoff/v0`.

Important rule:
- handoffs must stay explicitly lossy.
A CMake or audit slice is not the canonical pack.

#### `cargo native-edge brief`
Purpose:
- tell a human what lane is under review, what was imported, what went wrong or stayed ambiguous, what consumers may conclude, and when the review expires;
- render the same pack at different depths without inventing new facts.

#### `cargo native-edge diff`
Purpose:
- compare two review points while preserving the distinction between:
  - changed subject/scope,
  - changed boundary surface/provenance,
  - changed provider/link decisions,
  - changed platform/build context,
  - changed foreign-build handoff,
  - and changed downstream claims.

#### `cargo native-edge pack`
Purpose:
- assemble subject, boundary, provider, context, handoff, and brief layers into one reviewable `native-edge-pack/v0`.

## Ranked feature set

### P0 — required for a worthy v0
- explicit subject capture with lane identity;
- importable boundary and provider truth kept separate;
- explicit host/target/toolchain/build ownership reporting;
- one portable handoff for at least one foreign build system;
- one portable brief plus one portable pack;
- diffable renewal / expiration markers;
- honest `partial`, `provider-specific`, `foreign-build-owned`, and `inconclusive` states.

### P1 — strong near-term extensions
- replayable provider and link-plan receipts;
- richer platform-specific context for musl/Apple/Windows/Emscripten style edge cases;
- better release/support/audit slices above the canonical pack;
- compatibility hooks to Build-State, Package Intake, and Migration/Public API work.

### P2 — do later or fold elsewhere
- universal language-interop schemas across every foreign language;
- hosted public “interop scores” portals;
- automatic source rewriting or universal binding generation;
- replacing build systems or provider package managers.

## Pilot lanes that best prove the idea

### 1) Rust `cdylib` / C header export lane
Prove:
- one reviewed subject can carry exported boundary truth and generated-header provenance;
- target-specific linker args and symbol exposure can travel with the pack;
- downstream C/C++ consumers can ingest the result without header/build archaeology.

This lane matters because it is the cleanest proof that subject truth, boundary truth, and foreign-build handoff can stay reviewable.

### 2) System-library consumer / `links` lane
Prove:
- provider truth deserves first-class artifacts rather than being trapped in `build.rs` output;
- `links`, immediate-dependent metadata, and build-script overrides can be represented as structured inputs rather than cargo folklore;
- build-script probing and declarative intent remain visibly different postures.

This lane matters because it captures the dominant `-sys` / provider problem without pretending C++ is the only native-edge story.

### 3) Large existing C++ codebase lane
Prove:
- the system can preserve lane distinctions between CXX-style safe-common bridges and `autocxx`/`bindgen`-style generated boundary work;
- `libclang` / header-shape / target-specific generation pressure can be carried as context instead of buried;
- the subject remains one joined review rather than a pile of generated artifacts.

This lane matters because it addresses the industry pressure that made Native Edge a frontier in the first place.

### 4) Foreign build handoff lane
Prove:
- a CMake-facing consumer can ingest the result without reverse-engineering Cargo state;
- Corrosion-style imported targets, generated bindings, and manual/auto modes can be described as handoff truth rather than magical integration;
- mixed ownership between Cargo and the foreign build remains explicit.

This lane matters because it tests whether the contribution works outside Cargo-centric narratives.

### 5) Platform-friction / mixed-runtime lane
Prove:
- Windows MSVC runtime mismatches, Emscripten unwind settings, musl target shifts, and similar issues can be recorded as context drift rather than one-off lore;
- renewal and diffing actually help when a target/runtime/toolchain moves underneath a stable Rust API surface.

This lane matters because native-edge pain is often not “bad bindings”; it is context drift.

## How this contribution should compose with the rest of the archive

### It strengthens, but does not replace, FFI Boundary
Native Edge should import boundary truth, not redefine it.
`ffi-pack/v0` remains the stronger authority for exact symbol/type/ownership/lifetime claims.

### It strengthens, but does not replace, Native Dependency
Native Edge should import provider and link truth, not absorb it.
`native-pack/v0` remains the stronger authority for provider locks, link plans, and discovery posture.

### It strengthens, but does not replace, Build Interop or Toolchain Productization
Native Edge needs host-vs-target/toolchain/build ownership context, but those remain adjacent seams.
This blueprint should not become a build-system or toolchain empire.

### It strengthens, but does not replace, Package Intake
Where native payloads arrived from and how they were staged may matter, but ingress truth remains its own seam.
Native Edge should import route/provenance receipts when relevant instead of trying to narrate the full intake story itself.

### It strengthens, but does not replace, Build-State Evidence
Build-State answers “what build work happened and why?”
Native Edge answers “what mixed-language/native-adoption subject was reviewed, with which boundary/provider/context/handoff facts?”
They should meet, not merge.

## Failure modes to avoid

### 1) The universal-interop trap
Do not let the project claim it can normalize every language boundary into one perfect schema.
The archive's frontier is specifically about Rust's native edge, especially C and C++ pressure, not every polyglot fantasy at once.

### 2) The generator-winner trap
Do not let one generator or bridge tool silently become the whole theory.
CXX, `autocxx`, `bindgen`, `cbindgen`, handwritten layers, and provider crates express different lanes and should remain comparable rather than collapsed.

### 3) The build-script-folklore trap
Do not settle for “we captured stdout from `build.rs`”.
A worthy layer must separate imported facts, reason-coded choices, and consumer handoffs from raw script logs.

### 4) The Cargo-only trap
Do not call it success if the result only makes sense to the crate author running Cargo locally.
The handoff must travel to at least one serious foreign-build consumer.

### 5) The one-successful-link trap
Do not let one local green build silently become support truth.
Context drift, provider drift, and runtime drift are part of the native-edge story and must remain explicit.

## Why this is the right deepening now
This is the best next increment because it closes the one structural hole the archive still had among its top current answers.
The repo already had concrete execution blueprints for the broad winner, the hidden multiplier, the operational seam, the release/upgrade seam, and the anti-tacit-knowledge frontier.
The active specialist frontier was still sharper as a contract than as a build plan.

This revision fixes that without pretending Native Edge should outrank Build-State Evidence overall.
It says something narrower and more useful:
Native Edge remains the strongest specialist frontier, and now the archive can answer what that frontier should actually ship.

## Ranking impact
The broad portfolio does **not** change:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Adoption Navigation Contract** remains the strongest anti-tacit-knowledge answer;
- **Native Edge Contract** remains the active specialist frontier;
- **Package Intake Gateway** remains the most underappreciated operational seam;
- **Semantic Context Contract** remains the key hidden multiplier.

What changes is execution clarity:
for “what should the active specialist frontier actually build?” questions, the repo should now point here.

## What not to build
Do **not** build:
- a universal FFI abstraction framework;
- a giant score/ranking portal for interop tools;
- a `build.rs` trace warehouse with no review boundary;
- a Cargo replacement for foreign build systems;
- or a one-click “make C++ safe” product pitch.

Build the thinner thing:
- a reviewable subject layer;
- above imported boundary/provider/context truths;
- with honest foreign-build handoff;
- and bounded downstream consumer slices.
