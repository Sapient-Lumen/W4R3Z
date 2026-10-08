## Execution addendum (rev0445)
For questions about **what the stack should actually become as a buildable contribution**, read `design/workspace-environment-execution-blueprint-2026Q1.md` immediately after this note.

Interpretation rule:
- this stack note still explains the imported truth families beneath the seam;
- the new execution blueprint now answers the narrower question of what the workspace-environment layer should actually ship first;
- and future revisions should keep the imported stacks distinct from the portable environment layer above them.

# Design: Workspace Environment Stack (Toolchain Productization + Native Dependency + Runtime Settings + Credentials + Tooling Contract)

## Goal
Treat **Rust workspace environments** as a first-class ecosystem seam.

Read this together with:
- [`design/workspace-environment-contract-2026Q1.md`](./workspace-environment-contract-2026Q1.md)
- [`design/workspace-environment-bundle.md`](./workspace-environment-bundle.md)

The ecosystem does not just need more setup scripts, better dotfiles, or one more opinionated dev shell. It needs a coherent contract story for:
- **subject** — which repo/workspace and discovery boundary the environment describes;
- **intent** — which toolchain/native/service/editor/credential assumptions are declared;
- **realization** — how a host shell, devcontainer, Nix flake, CI image, or remote workspace realizes those assumptions;
- **observation** — what was actually present and working on a given run or machine;
- **handoff** — what a contributor, editor, CI system, or assistant may safely import next.

The proposal-layer candidate for that seam should therefore be a thin `cargo workenv` / `workenv-pack/v0` composition layer that links existing artifacts instead of replacing them.

## Why this seam matters now
Official and ecosystem signals are unusually aligned:
- The 2025 State of Rust survey says online docs remain the preferred canonical reference while LLM tooling is increasingly part of how people learn Rust, and it separately notes editors with agentic support are on the rise. That means setup truth now needs bounded machine-readable handoff, not only prose.  
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The same survey still reports resource usage and debugging as important productivity problems. That is a reminder that local developer-loop reality remains a strategic pain surface.  
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo’s config model is explicitly hierarchical and merges settings discovered from the current directory up through parent directories to `$CARGO_HOME`, which means environment behavior is already partly a discovery problem rather than only a manifest problem.  
  https://doc.rust-lang.org/cargo/reference/config.html
- rustup’s override model also walks the directory tree, and `rust-toolchain.toml` can declare channel, components, targets, and profile. That means toolchain selection is project-facing, but still not the whole environment story.  
  https://rust-lang.github.io/rustup/overrides.html
- Cargo 1.94 is actively discussing workspace and configuration discovery because broken parent manifests or `.cargo/config.toml` files can poison unrelated builds. That is a strong signal that repo/environment subject boundaries need to become more explicit.  
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- rust-analyzer already exposes override commands, extra args, extra env, feature/target control, and linked-workspace behavior. That is concrete evidence that editor reality and build reality still need an honest shared contract.  
  https://rust-analyzer.github.io/book/configuration.html
- Dev Containers and Nix both show that reproducible realization substrates are real and useful, but they are intentionally generic. Rust still lacks the thin Rust-specific review layer above them.  
  https://containers.dev/implementors/spec/  
  https://nix.dev/concepts/flakes.html
- The Rust Foundation’s 2026–2028 strategy elevates Stable Infrastructure, Sustainable Maintenance, and Adoption & Innovation together. Workspace-environment truth sits directly in that overlap.  
  https://rustfoundation.org/strategic-plan/

## References (signals)
- 2025 State of Rust survey: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo 1.94 dev-cycle note: https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo config reference: https://doc.rust-lang.org/cargo/reference/config.html
- rustup overrides: https://rust-lang.github.io/rustup/overrides.html
- rust-analyzer configuration: https://rust-analyzer.github.io/book/configuration.html
- Dev Container specification: https://containers.dev/implementors/spec/
- Nix flakes: https://nix.dev/concepts/flakes.html
- Rust Foundation strategic plan: https://rustfoundation.org/strategic-plan/

## Current archive decision
The right contribution is **not**:
- a universal Rust dev environment manager,
- a forced move to Dev Containers or Nix,
- a secret-distribution system,
- another README-driven setup helper,
- or a workspace bot that silently mutates local machines.

It is a stack with explicit boundaries:
- [`design/tooling-contract-stack.md`](./tooling-contract-stack.md) owns workspace discovery, config roots, package-selection scope, graph/plan truth, and build-evidence imports.
- [`design/toolchain-productization-stack.md`](./toolchain-productization-stack.md) owns toolchain / stdlib / target / activation truth.
- [`design/native-dependency-kit.md`](./native-dependency-kit.md) owns provider selection, link plans, and external dependency posture.
- [`design/runtime-settings-kit.md`](./runtime-settings-kit.md) owns config/env/default/source/reload truth.
- [`design/credentials-kit.md`](./credentials-kit.md) owns secret-handle and credential-source posture.
- A new **Workspace Environment Stack** should own the thin handoff layer above them.

## What a worthy contribution would look like in practice
### 1) Start from intent and realization, not from one substrate
A credible environment contract must preserve the difference between:
- what the workspace *declares* it needs,
- how one substrate *realizes* that need,
- what was actually *observed* on one machine or run,
- and what downstream consumers may conclude.

That means the stack should import Dev Container, Nix, shell-task, CI-image, or remote-workspace facts without forcing them into one fake universal runtime.

### 2) Keep discovery / scope explicit
The contract must say:
- which repo/workspace root it covers,
- how that root was discovered,
- which packages or non-Cargo attachments are in scope,
- and what parent-directory or editor assumptions materially change interpretation.

Without that, contributors and tools keep claiming to represent “the workspace” while meaning different things.

### 3) Keep secrets as posture, not raw values
A serious workspace-environment contribution should describe:
- whether a secret is required,
- what kind of source supplies it,
- whether it is optional or mandatory,
- and what validation happened,

without turning `workenv-pack/v0` into a vault dump or `.env` archive.

### 4) Prefer bounded handoff artifacts
The stack should help:
- new contributors,
- maintainers doing support/onboarding,
- CI systems,
- editor integrations,
- remote-dev hosts,
- and assistants/agents.

It should therefore emit bounded handoff artifacts rather than expect each consumer to scrape shell commands or infer setup from failed builds.

## Suggested artifact family
A good epic candidate should add only a small composition family above imported artifacts:
- `workenv-subject/v0`
- `workenv-intent/v0`
- `workenv-secret-profile/v0`
- `workenv-realization-report/v0`
- `workenv-observation-report/v0`
- `workenv-handoff/v0`
- `workenv-diff-report/v0`
- `workenv-pack/v0`

### `workenv-subject/v0`
Defines:
- repo/workspace identity,
- discovery root,
- included/excluded scope,
- relevant non-Cargo attachments.

### `workenv-intent/v0`
Declares:
- toolchain/target/component needs,
- native/provider/service requirements,
- editor/task assumptions,
- optional vs required lanes,
- supported realization kinds.

### `workenv-secret-profile/v0`
Declares:
- secret handles and acquisition posture,
- local-vs-CI-vs-remote credential lanes,
- non-serializable/value-redacted fields,
- validation posture.

### `workenv-realization-report/v0`
Explains one concrete realization:
- host shell,
- Dev Container,
- Nix,
- CI image,
- remote workspace,
- or other.

It should record what was provisioned or attached, not pretend that all realizations are equivalent.

### `workenv-observation-report/v0`
Records what a run or machine actually saw:
- active toolchain/config/editor/native/service posture,
- mismatches and missing pieces,
- local-only facts,
- validation checks.

### `workenv-handoff/v0`
A bounded consumer summary for:
- `human`
- `editor`
- `ci`
- `agent`

The `agent` lane should stay capability-bounded and redacted by default.

### `workenv-pack/v0`
Thin bundle linking:
- the subject,
- declared intent,
- secret posture,
- realization reports,
- observation reports,
- imported toolchain/native/settings/credential/tooling attachments,
- checksums, provenance, and generator identity.

## Shared success criteria
A strong workspace-environment contribution should let a reviewer answer six questions quickly:
1. Which repo/workspace does this environment actually describe?
2. Which requirements are declared versus merely observed?
3. How is the environment realized on host/devcontainer/Nix/CI/remote lanes?
4. Which secrets or credentials are required, and only at what posture level?
5. What mismatched, drifted, or remained optional?
6. What may a contributor, editor, CI system, or assistant safely import next?

If the stack cannot answer those six questions, it is not yet ecosystem infrastructure.

## Ranked opportunity inside this stack
1. **workspace subject + intent truth**
2. **host vs container vs Nix realization truth**
3. **secret / credential posture and validation truth**
4. **editor / CI / agent handoff consumers**
5. **support / onboarding / archaeology consumers**

That order matters. The archive should not jump straight to a universal remote-dev platform.

## Boundaries / non-goals
- not a replacement for rustup,
- not a replacement for Cargo,
- not a replacement for Dev Containers or Nix,
- not a replacement for secret managers,
- not a replacement for task runners,
- not a justification for opaque machine mutation.

## Why this is an ecosystem contribution, not just onboarding polish
This seam affects many kinds of Rust users at once:
- maintainers lose time re-explaining setup,
- contributors hit hidden native/editor/config assumptions,
- CI diverges from local machines,
- agents and automation guess wrong about setup and scope,
- larger organizations need a handoff artifact that survives turnover.

A real Workspace Environment Stack would reduce that friction without requiring one giant platform vendor or one blessed substrate.

See also [`proposals/epic-workspace-environment-stack.md`](../proposals/epic-workspace-environment-stack.md) for the proposal-layer framing of this seam as a concrete ecosystem contribution rather than only a synthesis note.
