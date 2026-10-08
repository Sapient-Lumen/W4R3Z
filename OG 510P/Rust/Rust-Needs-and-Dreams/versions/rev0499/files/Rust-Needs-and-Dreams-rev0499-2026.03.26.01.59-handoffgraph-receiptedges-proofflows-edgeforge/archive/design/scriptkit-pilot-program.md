# Design: ScriptKit Pilot Program (`cargo scriptkit pilot`, `script-pilot-pack/v0`)

## Goal
Turn single-file packages into a **reviewable execution lane** instead of leaving them as “Cargo can run this now”.

The missing contribution is not another script runner.
Cargo is already making single-file packages real.
The missing contribution is the **script-truth layer** above that reality:
- what the script subject is,
- which manifest fields were explicit vs defaulted,
- where the lock/cache state lives,
- how discovery/workspace posture works,
- how editors and CI should identify the same subject,
- and which policy or evidence consumers can import the result without guessing.

## References (signals)
- Rust’s 2026 flagships explicitly include stabilizing **cargo-script**.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo’s unstable-features docs now define **single-file packages** with embedded frontmatter, defaulted `package.name` / `package.edition`, disallowed fields, a hashed `$CARGO_HOME/target/<hash>` target dir, a lockfile in `CARGO_TARGET_DIR`, and direct `cargo <file.rs>` manifest-command behavior.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- The January 2026 program-management update calls cargo-script one of the most anticipated features, shows the nightly shebang flow, and explicitly says single-file scripts are valuable for quick prototypes and minimal bug reproducers.
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- The December 2025 project-goals update says cargo-script gained frontmatter-format work, but still had blockers around frontmatter handling in rustdoc doctests.
  https://blog.rust-lang.org/2026/01/05/project-goals-2025-december-update/
- Cargo 1.94 says workspace/config discovery remains an active design problem and explicitly notes that cargo-script is starting with **workspace auto-discovery disabled**.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- rust-analyzer still has an open issue for shebang / single-file package support.
  https://github.com/rust-lang/rust-analyzer/issues/15318
- Cargo also still has UX polish gaps such as no-change runs printing Cargo noise instead of only script output.
  https://github.com/rust-lang/cargo/issues/16388

## Why this needs its own execution layer
The archive already had a good instinct: single-file Rust should not be an ungoverned exception to the compile-time story.
But the old ScriptKit design was still too close to “add a convenient workflow around cargo-script”.

Current Cargo signals make a narrower and stronger claim possible:
> A worthy ecosystem contribution would make single-file packages **portable, inspectable, and importable** across local runs, issue repros, repo automation, editor sessions, and CI.

Without that layer, three bad outcomes are likely:
1. **script folklore** — people share one-file repros without enough lock/toolchain/discovery truth to rerun them cleanly;
2. **editor drift** — Cargo, rust-analyzer, and CI identify or cache the script differently;
3. **policy drift** — scripts become a hidden side entrance for dependencies, build scripts, or odd workspace/config interactions.

## Design principles
1. **Treat the script as a subject, not as an anonymous temp package.**
2. **Keep explicit frontmatter distinct from inferred defaults.**
3. **Preserve discovery posture.** “Not in a workspace” and “explicitly opted into a workspace” are different truths.
4. **Separate local execution UX from imported evidence.** A pleasant `cargo file.rs` experience is not the same thing as a reusable report.
5. **Keep compile-time imports explicit.** If a script pulls build scripts or proc macros, that should remain visible.
6. **Prefer issue-repro and repo-automation pilots before wider packaging dreams.**
7. **Allow honest partial outcomes.** Scripts are a great place for `UNPINNED`, `EDITOR_PARTIAL`, and `INCONCLUSIVE` states.

## Shared artifact posture
### 1) `script-subject/v0`
The canonical identity of the script lane.

Should record:
- content hash
- path / origin hint
- shebang presence
- explicit name vs derived file-stem name
- explicit edition vs defaulted edition
- whether the script was executed directly, via `cargo <file.rs>`, or via `--manifest-path`

### 2) `script-frontmatter-report/v0`
What Cargo actually interpreted.

Should record:
- embedded-frontmatter presence
- raw frontmatter digest
- explicit manifest fields
- inferred/defaulted fields
- disallowed-field findings
- frontmatter parse or normalization warnings
- rustdoc/doctest compatibility posture when relevant

### 3) `script-lane-profile/v0`
How the script relates to its environment.

Should record:
- target-dir / build-dir posture
- lockfile location and persistence posture
- offline/online expectation
- workspace discovery posture (`disabled`, `explicit-opt-in`, `unknown-future`)
- config-layer assumptions
- host/target posture
- whether the script is expected to be ephemeral, attached to an issue, or committed in-repo

### 4) `script-run-report/v0`
What actually happened during execution.

Should record:
- resolution outcome
- build/run outcome
- no-change rerun posture
- dependency/download activity
- compile-time imports (proc macros, build scripts) when visible
- output-mode expectations (Cargo noise allowed, script-only expected, unknown)
- optional links to build-state or compile-time packs

### 5) `script-consumer-import-report/v0`
How other tools imported the subject.

Should record:
- editor recognition status
- CI verification status
- subject-id match / mismatch across tools
- diagnostics path rendering posture
- known lossiness (for example: shebang ignored, temp path substituted, unsupported workspace lane)

### 6) `script-pack/v0`
Bundle for sharing and review.

Should contain or point to:
- script bytes or stable digest
- subject report
- frontmatter report
- lane profile
- run report
- optional consumer-import report
- toolchain pin / channel
- lock material or explicit absence marker
- optional policy / SBOM / safety attachments

## Ranked first pilots

### 1) Minimal bug-repro lane
**Why first**
The January 2026 update explicitly says cargo-script shines for minimal bug reproducers.
This is the highest-leverage “one file matters” use case.

**Must prove**
- explicit vs defaulted manifest truth is preserved;
- lock/toolchain posture is attachable enough for another person to rerun;
- Cargo/rustc diagnostics still point to the one file as the subject;
- `script-pack/v0` is better than “paste this in a comment and hope”.

**Primary consumers**
- issue trackers
- compiler / Cargo bug triage
- docs and discussion threads

### 2) Shebang utility lane
**Why second**
Cargo’s manifest-command behavior and shebang flow are part of what makes this feel like scripting rather than mini-project generation.
But current editor support and output UX are still uneven.

**Must prove**
- shebang presence and invocation mode are preserved in the subject report;
- no-change rerun expectations are explicit;
- editor / shell / CI consumers can admit partial support instead of pretending parity;
- scripts without frontmatter still render the edition/default story honestly.

**Primary consumers**
- local shell users
- rust-analyzer / editor integrators
- documentation examples for executable snippets

### 3) In-repo automation lane
**Why third**
This is where script truth meets repo-composition truth.
A `scripts/*.rs` lane is strategically useful, but only if discovery/config/workspace posture is not implicit folklore.

**Must prove**
- workspace auto-discovery disabled vs explicit opt-in remains visible;
- lockfile persistence policy is reviewable;
- config-layer assumptions are attachable;
- scripts importing proc macros / build scripts can point to compile-time evidence instead of hiding that complexity.

**Primary consumers**
- maintainers
- CI and release workflows
- policy / supply-chain reviewers

### 4) Editor + CI import lane
**Why fourth**
Once scripts are shareable, the next failure mode is divergent tool identity.
The same script should not quietly become different temp projects in different consumers.

**Must prove**
- editor and CI can import the same subject id or admit mismatches;
- path/rendering lossiness is visible;
- `script-consumer-import-report/v0` is useful even when support is partial;
- script truth can be consumed without requiring every tool to fully implement Cargo internals.

**Primary consumers**
- rust-analyzer and other editors
- CI runners
- future semantic-context / atlas consumers

### 5) Workspace opt-in + policy lane
**Why fifth**
Cargo is intentionally starting with workspace auto-discovery disabled.
Any future widening needs a reviewable contract first.

**Must prove**
- “standalone script” and “repo-governed script” remain separate lane identities;
- policy consumers can require packs, locks, offline posture, or restricted dependency behavior for committed scripts;
- future workspace support can be additive instead of retroactively changing the meaning of old packs.

**Primary consumers**
- repo governance tools
- policy / trust / release systems
- large mixed-repo workflows

## Immediate archive consequences
Read this file together with:
- [`design/scriptkit.md`](./scriptkit.md)
- [`design/compile-time-surface-pilot-program.md`](./compile-time-surface-pilot-program.md)
- [`design/repo-composition-pilot-program.md`](./repo-composition-pilot-program.md)
- [`design/policy-pilot-program.md`](./policy-pilot-program.md)
- [`design/build-state-evidence-pilot-program.md`](./build-state-evidence-pilot-program.md)
- [`proposals/epic-scriptkit.md`](../proposals/epic-scriptkit.md)

## Archive decision
Future ScriptKit revisions should prefer:
- explicit subject/frontmatter/lane reports over another wrapper command,
- issue-repro and repo-script pilots over vague “Rust as a scripting language” rhetoric,
- consumer import reports over hand-wavy editor claims,
- and honest standalone-vs-workspace distinctions over premature convergence.
