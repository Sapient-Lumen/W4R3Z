# Design: Runtime Capability Pilot Program (`cargo capability pilot`, `cap-pilot-pack/v0`)

## Goal
Make the **Runtime Capability Kit** executable through a ranked pilot program that proves Rust projects can publish **portable runtime-authority continuity** for a few concrete lanes before widening the claim surface.

The archive already had a strong runtime-capability thesis:
- powers and scopes must be explicit,
- delegation matters,
- analyzer inference matters,
- generated policy is not enacted policy,
- and deny-path evidence matters.

What still needed sharpening was the rollout discipline:
- which capability lanes should go first,
- how much weight different analyzers should carry,
- when generated artifacts are useful,
- and how to record actual enactment without overclaiming.

A worthy contribution here is **not** another sandbox, seccomp generator, or permission DSL.
It is a disciplined rollout that proves Rust teams can attach declared, inferred, generated, enacted, and checked runtime-capability truth without collapsing them.

## References (signals)
- Alpha-Omega funding is supporting a Rust-focused implementation of Capslock.
  https://rustfoundation.org/media/strengthening-rust-security-with-alpha-omega-a-progress-update/
- The January 2026 Project Director update says the Capslock capability analyzer has a functioning prototype.
  https://blog.rust-lang.org/inside-rust/2026/02/09/project-director-update/
- `cargo-capslock` exists as an experimental Rust capability analyzer.
  https://github.com/rustfoundation/cargo-capslock
- `cargo-caps` exists as a second capability-analysis lane focused on emitted linker symbols.
  https://github.com/emilk/cargo-caps
- FOSDEM 2026 material explicitly connects Rust capability analysis to generated seccomp profiles for services.
  https://fosdem.org/2026/schedule/event/QGCFDA-using_capslock_analysis_to_develop_seccomp_filters_for_rust_and_other_services/
- `cap-std`, Wasmtime/WASI, and Tauri already expose materially different capability models with real users today.
  https://docs.rs/cap-std/latest/cap_std/
  https://docs.wasmtime.dev/security.html
  https://v2.tauri.app/security/capabilities/

## Why this needs its own design layer
Without a pilot layer this seam risks four bad outcomes:
1. **declaration theater** — maintainers export polished least-privilege manifests without proving reality;
2. **analysis theater** — analyzer output is mistaken for whole-product truth;
3. **generation theater** — generated seccomp or permission drafts are mistaken for deployment proof;
4. **deployment theater** — one packaging or orchestration receipt is mistaken for universal runtime posture.

## Design principles
1. **Pilot capability lanes, not “application security” in the abstract.**
2. **Keep declaration, inference, generation, enactment, and checked behavior distinct.**
3. **Prefer lanes with real downstream consumers.**
4. **Reward partial but explicit truth.** Unknowns are acceptable; silent flattening is not.
5. **Treat analyzer plurality as a feature, not a bug.** Different analyzers can illuminate different authority shapes.
6. **Raw framework truth stays attachable.**
7. **Promotion requires a reusable handoff into Policy / Dependency Review / release or operations consumers.**

## Artifact family
### 1. `cap-pilot-brief/v0`
Why this capability lane is being piloted.

### 2. `cap-inference-profile/v0`
What inference sources, versions, completeness claims, and disagreement rules are allowed.

### 3. `cap-generation-policy/v0`
How generated enforcement artifacts are handled, including whether they are advisory only.

### 4. `cap-enactment-policy/v0`
What counts as enactment evidence for this pilot.

Should record:
- accepted deployment or packaging receipt kinds
- freshness requirements
- whether enactment evidence must be exact, sampled, or best-effort
- what platform or orchestrator tuples are in scope
- what the pilot is forbidden to conclude from enactment evidence alone

### 5. `cap-consumer-handoff/v0`
How downstream consumers use the pilot output and what they are still forbidden to conclude automatically.

### 6. `cap-pilot-scorecard/v0`
Did the pilot keep declaration, inference, generation, enactment, and checked behavior distinct while delivering real consumer value?

### 7. `cap-pilot-pack/v0`
Bundle for review and reuse.

## Ranked pilots
### 1) Service-binary inference lane
**Why first**
- clearest operational consumer;
- `cargo-capslock` is already being aimed at services;
- produces immediate value before any deployment claim is made.

### 2) Declaration-versus-inference reconciliation lane
**Why second**
- the honesty question is not only “what did the analyzer find?” but “how does that compare to the maintainer claim?”
- `cargo-capslock` and `cargo-caps` can disagree usefully rather than pretending one lane is final.

### 3) Generated-enforcement lane
**Why third**
- seccomp or similar drafts are compelling and risky;
- this lane proves generation can be attached without being mistaken for deployment truth.

### 4) Enactment-continuity lane
**Why fourth**
- once generated artifacts exist, the next missing truth is whether the shipped/deployed subject actually used them;
- this is where `cap-enactment-report/v0` earns its place.

### 5) Framework-attachment lane
**Why fifth**
- after service lanes prove the discipline, the archive should show the same artifact family attaching to Tauri, Wasmtime/WASI, or plugin hosts.

### 6) Policy/release consumer lane
**Why sixth**
- only after the raw lanes are honest should Policy, Dependency Review, release review, or support consumers ingest them.

## Success conditions
A pilot succeeds when it:
- leaves behind reusable artifacts rather than a one-off demo,
- surfaces real least-privilege questions for a concrete consumer,
- preserves analyzer incompleteness honestly,
- avoids treating generated policy as enacted policy,
- avoids treating one deployment receipt as universal truth,
- and makes capability drift easier to review over time.

## What promotion should look like
If the pilot program works, the promoted ecosystem contribution should be:
- a thin `cargo capability` / `cap-pack/v0` layer,
- adapter-heavy rather than framework-owning,
- explicit about analyzer plurality and deployment lossiness,
- and good enough for downstream review without pretending Rust has solved permissions universally.
