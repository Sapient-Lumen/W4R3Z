# Design: Config Set Kit (`cargo configset`, `config-pack/v0`)

## Goal
Define a portable contract for choosing, explaining, running, and diffing bounded Rust configuration matrices so feature/cfg/target/profile selection becomes a reviewable artifact rather than a pile of CI folklore.

This should **not** replace Cargo’s resolver, `cargo-hack`, nextest, coverage tools, or compiler-based prioritizers.
It should make them compose better and make matrix decisions visible.

## References (signals)
- `cargo-hack` already provides powerset / each-feature / grouping / skip controls for CI and continuous testing, which is strong evidence of demand for bounded configuration exploration.
  https://docs.rs/crate/cargo-hack/latest
  https://github.com/taiki-e/cargo-hack
- Cargo’s docs explicitly say `cargo metadata` cannot fully represent feature relationships across dependency kinds, commands, and selected targets under the modern resolver behavior.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo workspaces now make package-selection posture more machine-visible via `default-members` and `workspace_default_members` in `cargo metadata`, which means bounded config selection can import repo-scope truth instead of guessing it.
  https://doc.rust-lang.org/cargo/reference/workspaces.html
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo’s feature and metadata docs show the surface area is real even before targets and cfgs enter the picture.
  https://doc.rust-lang.org/cargo/reference/features.html
  https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Automatic `check-cfg` support exists because cfg correctness across features/targets is already a common failure mode.
  https://blog.rust-lang.org/2024/05/06/check-cfg/
- docs.rs changed its default targets in 2025, which is a reminder that target selection is an ecosystem-facing claim, not just a local CI detail.
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- nextest and cargo-llvm-cov already emit machine-readable outputs, which makes per-config result attachment realistic today.
  https://nexte.st/docs/machine-readable/
  https://docs.rs/crate/nextest-metadata/latest
  https://docs.rs/crate/cargo-llvm-cov/latest
- Cargo 1.94 is adding richer report surfaces (`cargo report timings`, `cargo report rebuild`, `cargo report sessions`), which is exactly the kind of substrate a config-run layer should attach to instead of duplicating.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- RustyEx shows compiler-guided configuration prioritization is now credible prior art, but also reinforces that the archive should standardize outputs rather than lock itself to one ranking algorithm.
  https://arxiv.org/abs/2601.16008

## Core components

### 1) `config-set/v0`
Declares the bounded matrix a team intends to run.

Required ideas:
- subject identity (`workspace`, `commit?`, `lockfile_hash?`, `toolchain?`, `package_selection_basis?`)
- command lane (`check`, `test`, `doc`, `coverage`, `fuzz`, `verify`, or mixed)
- explicit dimensions varied:
  - features / optional deps
  - cfg names/values
  - targets
  - profiles
  - toolchains / channels
- list of concrete config entries
- stable config ids for diffing
- optional workspace/package-selection import (`cwd package`, `default-members`, explicit package list, docs lane, release lane, CI policy)
- human-facing notes and policy tags

Each config entry should be fully specified enough to replay or at least understand:
- feature selection
- cfg selection
- target triple(s)
- profile / command lane
- optional environment or capability requirements
- expected cost class / timeout budget

### 2) `config-analysis-report/v0`
Explains why the chosen matrix exists.

Should record:
- generator / analyzer identity
- inputs and constraints
- ranking or prioritization method (human, heuristic, compiler-guided, policy-driven)
- selected configs + short rationale
- equivalence groups / deduplicated regions
- uncovered or intentionally skipped zones
- invalid combinations or resolver-rejected space
- confidence notes / known blind spots

Design rule: **selection must stay explainable**.
A config set without a justification layer quickly becomes another opaque YAML artifact.

### 3) `config-run-report/v0`
Maps config ids to actual execution outcomes.

Should support:
- status per config (`passed`, `failed`, `skipped`, `not-provisioned`, `timed-out`)
- attached run subjects (nextest run id, coverage output, fuzz pack, verify pack, Cargo report session id)
- artifact pointers
- duration / cost summary
- failure classification
- provenance of who/what executed the run

This is the layer that lets other kits consume one consistent matrix subject.

### 4) `config-pack/v0`
Bundle containing:
- `config-set/v0`
- optional `config-analysis-report/v0`
- optional `config-run-report/v0`
- optional raw attachments / generated CI matrices / tool-specific exports

This is the unit that travels through CI, release review, regression triage, or audit evidence.

### 5) `cargo configset`
Reference UX:
- `cargo configset plan`
- `cargo configset diff`
- `cargo configset run`
- `cargo configset gha`
- `cargo configset pack`

`cargo configset` should begin as an orchestrator / explainer / packer.
It should not try to become a universal CI runner or replace best-of-breed execution tools.

## What the kit should provide to others
- **Workspace Governance Kit:** import `default-members` / package-selection truth so config plans start from the repo scope Cargo actually selected.
- **Feature Kit:** consume explicit chosen feature matrices instead of inventing its own hidden subsets.
- **Coverage Evidence Kit:** report which configs a coverage claim came from.
- **FuzzPack Kit / Formal Verification Kit:** reuse the same selected config ids for expensive assurance lanes.
- **Cross Toolchain Kit / Sysroot Pack Kit:** attach target/toolchain provisioning requirements to configs instead of burying them in docs.
- **Downstream Testing Kit / Public API Kit:** make matrix scope reviewable when semver or revdep claims depend on non-default features or targets.
- **Cargo Report Kit / Perf Labs:** join run costs and rebuild reasons back to explicit config ids.

## Overlap boundaries
- **Not Feature Kit:** Feature Kit explains feature graphs and policy; Config Set Kit records which subsets are actually selected for work.
- **Not Cross Toolchain Kit:** that kit provisions toolchains/sysroots; this kit records when they are needed by chosen configs.
- **Not Downstream Testing Kit:** revdep selection is about *which dependent packages* to test; config selection is about *which build/test environments* to run.
- **Not Cargo’s resolver:** we record and explain outcomes; we do not replace dependency resolution.
- **Not a generic CI service:** this defines artifacts and orchestration seams, not hosted execution.

## Hard problems (explicitly scoped)
1. **The space is multi-axis, not just features**
   - targets, cfg values, profiles, and command lanes all matter.
   - v0 must not collapse everything into a feature-only view.

2. **Perfect selection is impossible**
   - the point is bounded, reviewable choices, not fake completeness.
   - uncovered zones and confidence limits must be first-class.

3. **Metadata is not enough**
   - Cargo docs explicitly warn that metadata cannot represent every feature relationship.
   - designs should allow compiler-guided or tool-specific raw attachments where needed.

4. **Provisioning is uneven across targets**
   - some configs fail because the target/toolchain/sysroot is missing, not because the code is broken.
   - `config-run-report/v0` must distinguish those cases honestly.

5. **Execution outputs already have good native formats**
   - nextest, coverage, fuzzing, and verification tools should keep their own detailed outputs.
   - Config Set Kit should point to them, not flatten them into one fake super-report.

## Minimal adoption path
1. Publish schemas + validators for `config-set/v0` and `config-analysis-report/v0`.
2. Ship `cargo configset plan` and `cargo configset gha` first.
3. Ingest `cargo-hack`-style feature subsets and explicit target/cfg policies.
4. Add adapters for nextest, cargo-llvm-cov, and Cargo report session ids.
5. Add compiler-guided prioritization hooks when tools like RustyEx or future upstream analysis become practical.
