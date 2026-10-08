# Epic Proposal: Config Set Kit (`cargo configset`, `config-pack/v0`)

## One-sentence pitch
Give Rust a standard way to choose, explain, run, and diff bounded configuration matrices so feature/cfg/target/profile coverage becomes an explicit engineering decision instead of tribal CI lore.

## Deliverables
- `cargo configset` reference tool
- Schemas:
  - `config-set/v0`
  - `config-analysis-report/v0`
  - `config-run-report/v0`
  - `config-pack/v0`
- Adapters / integrations for:
  - `cargo-hack` feature subsets and groupings
  - `check-cfg` / declared cfg expectations
  - nextest machine-readable listings and run identifiers
  - cargo-llvm-cov machine-readable coverage outputs
  - Cargo report session/rebuild/timings ids where available
- Docs:
  - matrix selection and review guide
  - CI integration guide
  - “coverage/verification claims by config” guide

## Why now (signals)
- `cargo-hack` is mature enough that many teams already rely on powersets, grouped features, skips, and CI helpers, which shows the problem is real but still externalized.
  https://docs.rs/crate/cargo-hack/latest
  https://github.com/taiki-e/cargo-hack
- Cargo is explicit that `cargo metadata` cannot fully capture feature relationships under the current resolver model across dependency kinds, commands, and targets, which means the ecosystem still lacks a trustworthy matrix-explanation layer.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Rust’s automatic `check-cfg` work exists because cfg correctness across feature/target combinations is already an ecosystem pain point.
  https://blog.rust-lang.org/2024/05/06/check-cfg/
- docs.rs changing its default targets is a reminder that target selection is user-visible and ecosystem-facing, not just an internal CI concern.
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- nextest and cargo-llvm-cov already provide machine-readable outputs, so the missing layer looks like matrix identity + attachment, not a replacement runner.
  https://nexte.st/docs/machine-readable/
  https://docs.rs/crate/nextest-metadata/latest
  https://docs.rs/crate/cargo-llvm-cov/latest
- Cargo 1.94 is making structured reports more practical (`cargo report timings`, `cargo report rebuild`, `cargo report sessions`), which is the right time to give those reports stable configuration subjects.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- RustyEx provides fresh research evidence that compiler-guided configuration prioritization is now concrete enough to build around.
  https://arxiv.org/abs/2601.16008

## Non-goals
- Exhaustively testing every possible configuration
- Replacing Cargo’s dependency resolver
- Forcing one ranking algorithm for all projects
- Flattening nextest / coverage / fuzz / verify outputs into one fake universal format
- Becoming a hosted CI platform

## Strategic value
This is a worthy contribution because it upgrades configuration choice from **implicit CI glue** into **portable reviewable evidence**.

That unlocks:
- clearer reasoning about which feature/cfg/target combinations a project actually supports,
- more honest coverage and verification claims,
- better reuse across testing, fuzzing, verification, docs, and release review lanes,
- easier diff review when matrix scope changes,
- and a path for compiler-guided or policy-guided prioritizers to interoperate without each inventing a new artifact format.

The archive already has Feature Kit, Coverage Evidence Kit, FuzzPack Kit, Formal Verification Kit, Cross Toolchain Kit, and Cargo Report Kit.
Config Set Kit fills the missing seam between them: one explicit configuration subject that each can attach to.

## Milestones
1. **v0 schemas + validators**
   - publish `config-set/v0` and `config-analysis-report/v0`
   - require uncovered-zone / skipped-space reporting
2. **v0.2 planning + CI export**
   - ship `cargo configset plan`, `diff`, and `gha`
   - ingest `cargo-hack`-style subsets and policy constraints
3. **v0.3 execution attachments**
   - normalize per-config run results into `config-run-report/v0`
   - attach nextest / coverage / Cargo report ids
4. **v1 cross-kit hooks**
   - plug into Coverage Evidence, FuzzPack, Formal Verification, Public API, and Downstream Testing flows
   - support compiler-guided prioritizers as optional analyzers

## Success metrics
- Teams can produce one `config-pack/v0` for a workspace without custom YAML archaeology.
- Coverage, fuzzing, and verification reports can point back to stable config ids.
- PRs can diff matrix scope explicitly instead of hiding it in CI scripts.
- Feature/cfg/target support claims become easier to audit and harder to overstate.
