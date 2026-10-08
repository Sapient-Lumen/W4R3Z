## Execution addendum (rev0445)
For questions about **what this epic should actually ship first rather than merely propose**, read `design/workspace-environment-execution-blueprint-2026Q1.md` immediately after this note.

Interpretation rule:
- the proposal still names the worthy seam and candidate CLI shape;
- the new execution blueprint now answers the narrower question of feature ranking, pilot lanes, and anti-goals;
- and future proposal changes should stay aligned with the blueprint's subject/discovery, intent, realization, secret posture, observation, and consumer-handoff separation rules.

# Epic Proposal: Workspace Environment Stack / Workspace Environment Contract (`cargo workenv` + `workenv-pack/v0`)

## Why this is worthy
Rust workspaces increasingly behave like products for humans, CI systems, editors, and agents long before they produce a final binary.

But the ecosystem still has no single honest handoff for **workspace environment truth**.

That means contributors and automation still reconstruct setup from:
- `rust-toolchain.toml` and rustup override state,
- `.cargo/config.toml` files across the directory tree,
- rust-analyzer override commands and extra environment variables,
- Nix shells or flakes,
- Dev Container lifecycle commands,
- native SDK / linker / service bootstrap notes,
- credential setup snippets,
- and stale README prose.

The missing contribution is a thin portable layer above those pieces, not another replacement for them.

The 2026Q1 sharpening is that this should be treated explicitly as a **workspace environment contract**: a reviewable handoff layer for humans, editors, CI systems, and agents.

## Proposal
Define a **Workspace Environment Stack** with:
- a reference aggregation CLI, `cargo workenv`;
- a thin linked bundle, `workenv-pack/v0`;
- imported evidence from:
  - Tooling Contract artifacts for discovery / scope truth,
  - Toolchain Productization artifacts for toolchain / target truth,
  - Native Dependency artifacts for provider / link truth,
  - Runtime Settings artifacts for config/env/source truth,
  - Credentials artifacts for secret-handle posture;
- stable handoff and diff artifacts:
  - `workenv-subject/v0`
  - `workenv-intent/v0`
  - `workenv-secret-profile/v0`
  - `workenv-realization-report/v0`
  - `workenv-observation-report/v0`
  - `workenv-handoff/v0`
  - `workenv-diff-report/v0`

## Reference CLI shape
- `cargo workenv export`
  - emit `workenv-subject/v0` + `workenv-intent/v0` for one selected repo/workspace subject
- `cargo workenv observe`
  - emit `workenv-observation-report/v0` from imported toolchain/native/settings/editor/service checks
- `cargo workenv realize --kind <host|devcontainer|nix|ci|remote>`
  - emit `workenv-realization-report/v0` describing one environment substrate without pretending it is the only truth
- `cargo workenv handoff --for <human|editor|ci|agent>`
  - emit `workenv-handoff/v0`
- `cargo workenv diff --against <ref|pack|path>`
  - emit `workenv-diff-report/v0`
- `cargo workenv pack`
  - produce `workenv-pack/v0`
- `cargo workenv verify-pack <path>`
  - verify schema versions, checksums, redaction policy, and imported-attachment integrity

This should stay a **thin composition layer**.
It should not replace rustup, Cargo, Dev Containers, Nix, task runners, or secret managers.

## What `workenv-pack/v0` should contain
- `manifest.json`
- `workenv-subject.json`
- `workenv-intent.json`
- optional `workenv-secret-profile.json`
- one or more `workenv-realization-report.json`
- one or more `workenv-observation-report.json`
- optional `workenv-handoff-*.json`
- optional `workenv-import-handoff.json`
- optional `workenv-diff-report.json`
- imported tooling / toolchain / native / settings / credential attachments or pointers
- checksums, provenance, and generator identity

## Design principles
- **Workspace environment is product surface, not just setup prose.**
- **Discovery, intent, realization, observation, and handoff remain distinct truths.**
- **Secrets are posture and handles, not archived values.**
- **Multiple realization substrates are valid; none becomes the one true environment.**
- **Agent/editor/CI handoffs must be bounded and redacted by design.**
- **Imports over reinvention.**

## Early implementation order
1. repo subject + intent export
2. host-shell observation lane
3. Dev Container / Nix realization lanes
4. editor / CI / agent handoff lanes
5. support / onboarding / archaeology consumers

## Non-goals
- another workspace manager;
- a universal secret vault;
- a forced Nix or Dev Container migration;
- a hidden machine-mutation tool;
- a fake “dev environment works” badge.

## Success bar
This becomes worthy when a team can answer:
- which workspace/root/scope the environment is actually about;
- which toolchain, native, service, editor, and credential assumptions are declared;
- how host, container, Nix, CI, or remote lanes realize those assumptions;
- what was actually observed versus merely intended;
- what changed between two environment states;
- and what a contributor, editor, CI system, or assistant may safely import next,

without scraping shell history, overreading README prose, or exposing raw secrets.

## Read this with
- `gaps/workspace-environments-onboarding-and-agent-safe-dev-contracts.md`
- `design/workspace-environment-stack.md`
- `design/tooling-contract-stack.md`
- `design/toolchain-productization-stack.md`
- `design/native-dependency-kit.md`
- `design/runtime-settings-kit.md`
- `design/credentials-kit.md`

## References (signals)
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo 1.94 dev-cycle note:
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo config reference:
  https://doc.rust-lang.org/cargo/reference/config.html
- rustup overrides:
  https://rust-lang.github.io/rustup/overrides.html
- rust-analyzer configuration:
  https://rust-analyzer.github.io/book/configuration.html
- Dev Container specification:
  https://containers.dev/implementors/spec/
- Nix flakes:
  https://nix.dev/concepts/flakes.html
- Rust Foundation strategic plan:
  https://rustfoundation.org/strategic-plan/
