## Execution addendum (rev0445)
For questions about **what this seam should actually ship now**, read `design/workspace-environment-execution-blueprint-2026Q1.md` immediately after this note.

Interpretation rule:
- this contract note still explains why the seam matters and what truths it must keep separate;
- the new execution blueprint now answers the narrower question of what the worthy contribution should actually build first in theory and practice;
- and future revisions should keep subject/discovery, intent, realization, secret posture, observation, and consumer handoff distinct rather than re-flattening them into generic setup prose.

# Design: Workspace environment contract 2026Q1 (`cargo workenv`, `workenv-pack/v0`)

## Goal
Promote **workspace environment truth** into a first-class Rust ecosystem contract layer.

The worthy contribution here is **not** another setup guide, another one-true dev shell, another remote-dev platform, or another machine-mutation bot.
It is the missing reviewable layer that says:

**which workspace subject is being described, which toolchain/native/service/editor/credential requirements are declared, how host/container/Nix/CI/remote lanes realize them, what was actually observed, which local or parent-directory overrides materially changed the result, and what humans / editors / CI / agents may safely import next.**

Read this together with:
- [`design/workspace-environment-stack.md`](./workspace-environment-stack.md)
- [`design/workspace-environment-bundle.md`](./workspace-environment-bundle.md)
- [`design/tooling-contract-stack.md`](./tooling-contract-stack.md)
- [`design/toolchain-productization-stack.md`](./toolchain-productization-stack.md)
- [`design/native-dependency-kit.md`](./native-dependency-kit.md)
- [`design/runtime-settings-kit.md`](./runtime-settings-kit.md)
- [`design/credentials-kit.md`](./credentials-kit.md)
- [`proposals/epic-workspace-environment-stack.md`](../proposals/epic-workspace-environment-stack.md)
- [`gaps/workspace-environments-onboarding-and-agent-safe-dev-contracts.md`](../gaps/workspace-environments-onboarding-and-agent-safe-dev-contracts.md)

## Why this seam matters now
Fresh official signals make this frontier much more concrete than it looked when the archive first named it.

- The 2025 State of Rust survey says resource usage remains a major productivity problem, online documentation remains the preferred canonical reference, and editors with agentic support are rising. That means environment truth now has to survive both human onboarding and machine-mediated consumption.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo’s configuration model is explicitly hierarchical: it probes `.cargo/config.toml` files in the current directory and parent directories, merges them, and gives deeper directories precedence. That means setup truth is already partly a discovery/precedence problem rather than merely a manifest problem.
  https://doc.rust-lang.org/cargo/reference/config.html
- Cargo workspace discovery also walks parent directories, changes package-selection defaults depending on whether you are in a member or workspace root, and allows `package.workspace` to override auto-discovery. That means “which workspace am I in?” is already part of runtime environment truth.
  https://doc.rust-lang.org/cargo/reference/workspaces.html
- rustup override selection also walks the directory tree, and `rust-toolchain.toml` can declare channel, components, targets, and profile. That makes toolchain choice project-facing, but still only one slice of environment truth.
  https://rust-lang.github.io/rustup/overrides.html
- Cargo 1.94 explicitly says broken or nightly-only parent `Cargo.toml` and `.cargo/config.toml` files can fail unrelated builds, and it discusses broader improvements to workspace/config discovery. That is a strong signal that the workspace-environment subject boundary is still under-specified for real users.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- rust-analyzer already carries its own override commands, invocation strategies, extra args/env, linked-workspace behavior, and dedicated `targetDir` tradeoffs. That is concrete evidence that editor reality and Cargo reality still need an honest shared handoff layer.
  https://rust-analyzer.github.io/book/configuration.html
- The Development Container Specification exists specifically to describe development-container metadata and make environments easy to use, create, and recreate, while Nix flakes default to pure mode and promote reproducible environments. Those are real realization substrates, but they are intentionally generic rather than a Rust-specific review layer.
  https://devcontainers.github.io/implementors/spec/
  https://nix.dev/concepts/flakes.html
- The Rust Foundation’s 2026–2028 strategy explicitly couples **Stable Infrastructure**, **Sustainable Maintenance**, and **Adoption & Innovation**. Workspace environment truth sits directly in that overlap because bad environment handoffs waste maintainer time while also slowing adoption.
  https://rustfoundation.org/strategic-plan/

Taken together, those signals say Rust is getting stronger at the leaves — config, workspace discovery, toolchain pinning, editor overrides, container substrates — but still lacks one honest **workspace environment contract**.

## What changed in the archive’s understanding
The archive already had the ingredients for a workspace-environment story.
What it did **not** yet have was a clear statement that this is now the strongest next **environment / handoff-shaping** move rather than a background Tier-A note or a bag of setup-adjacent documents.

The new reading is:
- [`design/tooling-contract-stack.md`](./tooling-contract-stack.md) owns workspace discovery, config inheritance, package-selection scope, graph/plan truth, and build-evidence imports;
- [`design/toolchain-productization-stack.md`](./toolchain-productization-stack.md) owns toolchain / stdlib / target / activation truth;
- [`design/native-dependency-kit.md`](./native-dependency-kit.md) owns provider selection, linker/SDK posture, and external dependency reality;
- [`design/runtime-settings-kit.md`](./runtime-settings-kit.md) owns config/env/default/source/reload truth;
- [`design/credentials-kit.md`](./credentials-kit.md) owns secret-handle and credential-source posture;
- **Workspace Environment Contract** is the thin composition layer that keeps those truths separate while making them reviewable and diffable together.

That is a stronger and more buildable claim than “setup matters” or “onboarding is hard” in the abstract.

## The missing distinction
A worthy contribution here must keep at least six truths explicit.

### 1) Subject / discovery truth
- repo or workspace identity
- discovery root and discovery method
- included / excluded package scope
- non-Cargo attachments in scope
- parent-directory effects that materially changed interpretation

### 2) Declared intent truth
- required toolchain / channel / targets / components
- native SDK / linker / provider requirements
- local services / emulators / side processes
- editor and task assumptions
- required vs optional realization lanes

### 3) Realization truth
- host-shell realization
- Dev Container realization
- Nix realization
- CI realization
- remote-workspace realization
- explicit omissions or substitutions in each lane

### 4) Secret / credential posture truth
- required secret handles or credential classes
- acquisition source (`local`, `ci`, `oidc`, `cloud-profile`, `prompt`, `unknown`)
- redaction and non-serialization posture
- validation posture
- optional vs required secret lanes

### 5) Observation / drift truth
- what one machine or run actually observed
- active overrides from parent directories, local files, or editor configuration
- what mismatched, drifted, or remained unavailable
- what is reproducible versus local-only
- what checks were executed, skipped, or unsupported

### 6) Consumer handoff truth
- contributor/onboarding summary
- editor summary
- CI summary
- support/archaeology summary
- bounded `agent` summary
- explicit forbidden conclusions for each consumer class

## What a worthy contribution would look like in theory and practice
In theory, the right contribution is a thin contract layer:
- narrow enough to stay honest;
- structured enough to survive real editors, CI, remote workspaces, and agent consumers;
- and modest enough to avoid becoming the one true environment platform.

In practice, the worthy contribution looks like:
- a reference companion CLI, `cargo workenv`;
- one attachable bundle family, `workenv-pack/v0`;
- imports from Tooling Contract, Toolchain Productization, Native Dependency, Runtime Settings, and Credentials rather than schema imperialism;
- explicit reason-coded diffs between declared intent, one realization, and one observation lane;
- and bounded renderers for human, editor, CI, support, and agent consumers.

The MVP should be able to answer:
- which workspace/root/scope this environment actually describes,
- which requirements are declared versus merely observed,
- how host/container/Nix/CI/remote lanes differ,
- which parent or local overrides changed the effective environment,
- which secrets are required only as posture rather than captured values,
- and what each downstream consumer may safely import next.

That is already a major ecosystem improvement over today’s combination of README prose, shell history, editor-local settings, CI YAML, and maintainer memory.

## Ranked execution order
### 1) Subject + intent export lane
Prove:
- one real subject can export `workenv-subject/v0` and `workenv-intent/v0`;
- discovery roots and package-selection assumptions stay explicit;
- and local Cargo/rustup precedence does not get flattened into one fake “repo config”.

### 2) Host observation lane
Prove:
- one real subject can export `workenv-observation-report/v0` for a host machine;
- parent-directory config and rustup override effects remain visible;
- and local-only drift does not silently widen into cross-lane truth.

### 3) Realization lane comparison
Prove:
- one real subject can compare host, Dev Container, or Nix realizations without claiming they are identical;
- omissions and substitutions remain explicit;
- and realization reports stay distinct from observations.

### 4) Secret posture + bounded handoff lane
Prove:
- one real subject can export a redacted secret profile;
- `human`, `editor`, `ci`, and `agent` handoffs remain different products;
- and the `agent` lane can stay useful without exposing raw credentials or hidden local files.

### 5) Support / archaeology lane
Prove:
- one environment diff can explain “what changed since the last working setup”;
- support consumers can import that diff without replaying shell history;
- and archaeology remains bounded rather than turning into a universal infra database.

## What not to build
Do **not** build:
- a universal Rust environment manager;
- a forced migration to Nix or Dev Containers;
- a secret vault or `.env` synchronizer;
- a hidden machine-mutation bot;
- or a hosted remote-dev empire marketed as the solution to setup.

The point is a **reviewable contract layer**, not a new control tower.

## Archive consequence
The archive should now treat **Workspace Environment Contract** as the clearest next **environment / handoff-shaping** move beneath:
- Workspace Environment Stack,
- Workspace Environment Bundle,
- Tooling Contract,
- Toolchain Productization,
- Native Dependency,
- Runtime Settings,
- and Credentials.

That does **not** make it the broad new #1 ecosystem need.
It does mean the repo now has enough substrate to say a concrete, worthy, machine-usable thing about this frontier.
