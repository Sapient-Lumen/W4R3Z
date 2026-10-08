# Design: ScriptKit (`cargo scriptkit`, `script-pack/v0`)

## Goal
Make Rust single-file packages **shareable, reproducible, and governable** without pretending they are full Cargo projects or disposable temp files.

ScriptKit should sit **between** upstream cargo-script support and downstream consumers.
It is not trying to replace Cargo’s implementation.
It is trying to define the missing **script-truth layer** so one-file Rust programs can be:
- run locally with predictable cache/lock behavior,
- attached to issues as real repro subjects,
- committed inside repos without discovery/workspace ambiguity,
- imported by editors and CI without subject drift,
- and checked by policy, supply-chain, or support tooling when needed.

## What changed since the earlier archive version
The old archive version treated ScriptKit mostly as a workflow layer on top of cargo-script.
Current Cargo signals are stronger and more specific than that:
- single-file packages now have documented unstable semantics;
- the default target dir and lockfile location are explicitly defined;
- workspace auto-discovery is intentionally disabled for now;
- shebang / editor / output UX still has visible open edges;
- and the feature is close enough to stabilization that **import discipline** matters more than a new runner.

So ScriptKit should now be evaluated less as “better scripting ergonomics” and more as **portable one-file package truth**.

## References (signals)
- 2026 flagship goal: stabilize cargo-script.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo unstable-features docs: single-file packages, embedded frontmatter, defaulted fields, disallowed fields, hashed target dir, target-dir lockfile, and manifest-command behavior.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- January 2026 program-management update: cargo-script is highly anticipated and especially good for minimal reproducers and prototypes.
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- December 2025 goals update: frontmatter work landed but rustdoc/doctest handling remained a blocker.
  https://blog.rust-lang.org/2026/01/05/project-goals-2025-december-update/
- Cargo 1.94: workspace/config discovery remains active design work and cargo-script is starting with workspace auto-discovery disabled.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- rust-analyzer still has an open shebang support issue.
  https://github.com/rust-lang/rust-analyzer/issues/15318
- Cargo still has active UX polish questions such as suppressing Cargo noise on no-change script runs.
  https://github.com/rust-lang/cargo/issues/16388

## Working thesis
A worthy ecosystem contribution here should make it possible to answer all of these cleanly:
- What exactly is the script subject?
- Which manifest fields were explicit and which were inferred by Cargo?
- Where does the lock/cached build state live, and how persistent is it?
- Is the script intentionally standalone or intentionally repo-governed?
- Can editors and CI point to the same subject id and the same diagnostics paths?
- If the script triggers proc macros or build scripts, can that complexity remain visible?

## Core UX: `cargo scriptkit`
### `cargo scriptkit report <file.rs>`
Produce a script-subject / frontmatter / lane report without changing policy.

Should explain:
- inferred package name / edition
- frontmatter parse status
- lockfile and target-dir posture
- standalone vs repo-governed lane
- known consumer gaps

### `cargo scriptkit run <file.rs>`
Run the script while preserving subject identity.

Should report:
- invocation mode (`cargo <file.rs>`, direct shebang, or `--manifest-path`)
- whether dependencies were fetched
- where build artifacts and lock material live
- whether this was a no-change rerun
- optional import links to build-state artifacts

### `cargo scriptkit pack <file.rs>`
Bundle enough truth for sharing and review.

Should include:
- script bytes or digest
- subject/frontmatter/lane reports
- toolchain pin or explicit unpinned state
- lock material or explicit `UNLOCKED`
- optional consumer-import report
- optional policy / SBOM / safety attachments

### `cargo scriptkit verify <pack>`
Reproduce and check the packed script lane.

Should verify:
- subject identity
- frontmatter interpretation
- lock/toolchain expectations
- imported consumer notes
- reason-coded mismatches

### `cargo scriptkit import-check <file.rs>`
Test how non-Cargo consumers see the script.

Should report:
- editor recognition
- shebang handling
- diagnostics path fidelity
- CI runner identity match
- explicit partial-support notes

## Shared artifacts
### `script-subject/v0`
Canonical identity for the script subject:
- content digest
- origin / path hint
- shebang presence
- explicit vs derived package name
- explicit vs defaulted edition
- invocation mode

### `script-frontmatter-report/v0`
What Cargo parsed:
- raw frontmatter digest
- explicit fields
- inferred defaults
- disallowed-field findings
- warnings / normalization notes
- rustdoc/doctest compatibility posture

### `script-lane-profile/v0`
Execution/discovery context:
- target-dir / build-dir posture
- lockfile location
- offline/online expectation
- workspace discovery posture
- config-layer assumptions
- repo-committed vs ephemeral status

### `script-run-report/v0`
Observed execution:
- resolution/build/run outcomes
- dependency fetches
- compile-time imports when visible
- rerun posture
- output-mode expectation
- optional links to build-state / compile-time packs

### `script-consumer-import-report/v0`
How editors/CI imported the same subject:
- subject-id matches or mismatches
- path/rendering fidelity
- support level
- lossiness notes

### `script-pack/v0`
Portable bundle combining the above.

## Integration points
### Compile-Time Surface Stack
ScriptKit is still an adjacent lane to the compile-time stack, not its authority center.
But if a script pulls proc macros or build scripts, ScriptKit should link to compile-time evidence instead of hiding those imports.

### Repo Composition Stack
A script committed under `scripts/*.rs` should not inherit repo/workspace/config behavior by folklore.
ScriptKit should make standalone-vs-repo-governed posture explicit and future-proof any later workspace opt-in.

### Policy / Trust / SBOM / Lifecycle
Policy consumers should be able to require:
- a present `script-pack/v0`,
- explicit lock posture,
- explicit online/offline expectation,
- or imported SBOM/safety evidence for important repo scripts.

### Build-State Evidence Stack
ScriptKit should not reinvent build diagnosis.
Instead it should be able to attach build-state imports so a one-file repro can also carry rebuild/block/reuse truth when needed.

## Ranked execution posture
Treat [`design/scriptkit-pilot-program.md`](./scriptkit-pilot-program.md) as the execution anchor.
The right rollout is now:
1. minimal bug repro lane,
2. shebang utility lane,
3. in-repo automation lane,
4. editor + CI import lane,
5. workspace opt-in + policy lane.

That order matters because the archive should win **portable one-file truth** before dreaming about publication, giant script registries, or a generalized “Rust shell scripts” brand.

## Non-goals
- Replacing Cargo’s built-in single-file package support
- Inventing a new scripting language
- Treating scripts as a hidden exception to compile-time governance
- Assuming workspace support should arrive before standalone subject truth is stable
- Collapsing local UX, editor support, and policy semantics into one generic success bit

## Archive decision
ScriptKit should now be treated as the **script-truth seam** between compile-time governance, repo composition, and lightweight sharing/repro.
The worthy contribution is not “Cargo but shorter”.
It is **one-file package truth that humans and tools can share without guessing**.
