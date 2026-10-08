# Design: Workspace Environment execution blueprint (2026 Q1)

## Goal
Turn the archive's repeatedly named **workspace environment / realization / observation / handoff** seam into a sharper **buildable program**.

The missing contribution is not another universal environment manager, another secret vault, another remote-dev control plane, or another setup README generator.
It is a disciplined companion layer that makes Rust's **workspace subject/discovery -> declared intent -> realization -> observation -> redacted handoff** story reviewable across local hosts, Dev Containers, Nix, CI, remote workspaces, onboarding, support, and later editor/agent consumers.

Read this note when the question is narrower than the broad ladder:

> if a serious Rust team wants to build the archive's workspace-environment contribution, what should that project actually ship in theory and practice?

Read with:
- `design/workspace-environment-contract-2026Q1.md`
- `design/workspace-environment-stack.md`
- `design/workspace-environment-bundle.md`
- `design/tooling-contract-stack.md`
- `design/toolchain-productization-stack.md`
- `design/native-dependency-kit.md`
- `design/runtime-settings-kit.md`
- `design/credentials-kit.md`
- `proposals/epic-workspace-environment-stack.md`

## Why this note is needed now
The archive already knew that **Workspace Environment** mattered.
What it still lacked was a crisper answer to **what the missing contribution should look like**.

Fresh ecosystem signals sharpen that answer:
- Cargo's config reference still says configuration is hierarchical and is probed from the current directory up through parent directories. That means environment behavior is already partly a discovery and precedence problem rather than only a manifest problem.
  https://doc.rust-lang.org/cargo/reference/config.html
- Cargo's workspace reference still says Cargo auto-searches parent directories for `[workspace]`, and package-selection defaults change depending on whether the current directory is a member or the workspace root. That means “what workspace is this command really talking about?” is an active part of environment truth.
  https://doc.rust-lang.org/cargo/reference/workspaces.html
- rustup's overrides reference still says toolchain choice is resolved by an explicit precedence order, directory overrides and `rust-toolchain.toml` are chosen by proximity while walking up the directory tree, and toolchain files can pin channel/date/components/targets/profile while `path` toolchains have different semantics. That means toolchain selection is project-facing, but still only one slice of environment truth.
  https://rust-lang.github.io/rustup/overrides.html
- The Cargo 1.94 development-cycle note still says broken parent `Cargo.toml` or `.cargo/config.toml` files can fail unrelated builds and that broader workspace/config discovery improvements are being tracked. That is direct evidence that workspace subject boundaries and discovery effects are still painful in real life.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- rust-analyzer's configuration still exposes per-workspace invocation strategy, override commands, extra args/env, linked-workspace behavior, and workspace-root working-directory assumptions. That is concrete evidence that editor reality and Cargo reality still need an honest shared handoff layer.
  https://rust-analyzer.github.io/book/configuration.html
- The Development Container Specification still defines a repeatable development environment with structured metadata, and it explicitly distinguishes development environments from production containers. Nix flakes still provide a standard-structure entrypoint aimed at sharing Nix code and same-version builds, while remaining an experimental feature. Those are real realization substrates, but not a Rust-specific review layer above them.
  https://containers.dev/implementors/spec/
  https://nix.dev/concepts/flakes.html
- The 2025 State of Rust survey still says resource usage remains a major productivity problem, docs remain the preferred canonical reference, and editors with agentic support are rising. That means setup truth increasingly has to survive both human onboarding and machine-mediated consumption.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Taken together, those signals say the archive should stop treating workspace-environment work as only a stack or bundle.
It should describe a real contribution shape.

## Headline answer
If one serious team wants to build the archive's clearest environment / handoff contribution, the answer should now be:

> Build a **Workspace Environment layer** that records workspace subject/discovery, declared intent, one or more realization reports, one or more observations, redacted secret posture, and bounded handoffs for humans, editors, CI, support, and agents.

That answer is deliberately narrower than “solve onboarding and remote development forever”.
It is also deliberately stronger than “export a devcontainer” or “bless one flake”.

## What this contribution should be in theory

### Core thesis
A workspace-environment system becomes ecosystem infrastructure when one portable pack can answer all of these honestly:
1. **what exact workspace subject is being described;**
2. **what that subject declares it needs;**
3. **how one substrate realizes those needs;**
4. **what one machine or run actually observed;**
5. **what secret/credential posture mattered without exposing raw values;**
6. **what downstream consumers may conclude without replaying local setup folklore.**

If a project still needs shell history, editor settings, CI YAML, container metadata, Nix expressions, and README archaeology to reconstruct that story, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable environment review and handoff**.

It should include:
- workspace subject/discovery capture;
- declared intent capture;
- realization reports for bounded substrates;
- observation reports for real host or CI runs;
- redacted secret/credential posture;
- bounded handoffs to human/editor/CI/support/agent consumers.

It should not become:
- a replacement for rustup;
- a replacement for Cargo;
- a universal environment manager;
- a secret vault;
- a remote-dev platform;
- or a hidden machine-mutation bot.

### Separation rule
The contribution must preserve at least six distinct truth classes:
- **subject/discovery truth** — repo/workspace identity, discovery root, scope, and parent-directory effects;
- **declared-intent truth** — toolchain/native/service/editor/credential requirements and optional-vs-required lanes;
- **realization truth** — what one host/devcontainer/Nix/CI/remote lane claims to realize;
- **secret-posture truth** — required handles, acquisition source, validation, and redaction posture without secret capture;
- **observation truth** — what one machine or run actually saw, including drift, missing pieces, and active overrides;
- **consumer truth** — what humans, editors, CI, support, or agents may conclude, with what lossiness.

Without those separations, “it works on my machine” becomes the only environment contract.

### Shape rule
This contribution should begin as a **reference layer + report/pack command + realization/acceptance corpus**.
That means:
- a **reference layer** for subject/discovery, intent, realization, observation, and handoff vocabulary;
- a thin **report/pack command layer** for collecting, diffing, and exporting workspace-environment packs;
- and a **realization/acceptance corpus** that proves the contract across host, Dev Container, Nix, CI, editor, and redacted-agent lanes.

It should not begin as a service, platform, or one-true-substrate ecosystem.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo workenv subject`
- `cargo workenv intent`
- `cargo workenv observe`
- `cargo workenv realize --kind <host|devcontainer|nix|ci|remote>`
- `cargo workenv handoff --to <human|editor|ci|support|agent>`
- `cargo workenv diff`
- `cargo workenv pack`

The tool should **import** lower-layer artifacts where possible rather than replace them.

### Public artifact spine

#### Imported/internal families
- tooling/discovery reports from **Tooling Contract**
- toolchain/target reports from **Toolchain Productization**
- native dependency and linker/provider attachments
- runtime settings attachments
- credentials or secret-profile attachments

#### Public review families
- `workenv-brief/v0`
- `workenv-subject/v0`
- `workenv-intent/v0`
- `workenv-secret-profile/v0`
- `workenv-realization-report/v0`
- `workenv-observation-report/v0`
- `workenv-handoff/v0`
- `workenv-diff-report/v0`
- `workenv-pack/v0`

### Minimum schema disciplines
Every public artifact should keep these fields first-class:
- **subject anchors** — repo/workspace identity, discovery root, scope, selected packages, non-Cargo attachments, and local overlay refs;
- **intent anchors** — channel/version/toolchain profile, targets/components, native SDK/provider needs, services, editor/task expectations, required-vs-optional lanes;
- **realization anchors** — substrate kind, generator identity, realized toolchain/native/service/editor attachments, substitutions, omissions, and host-specific notes;
- **secret anchors** — handle names/classes, acquisition source, validation posture, optionality, and redaction guarantees;
- **observation anchors** — what actually ran, active overrides, mismatches, missing pieces, skipped checks, and freshness;
- **consumer limits** — what each handoff consumer may conclude without escalating back to the full pack.

### Commands and what they should emit

#### `cargo workenv subject`
Purpose:
- freeze the workspace subject and discovery boundary;
- emit `workenv-subject/v0`.

Important rule:
- package selection and discovery effects must be explicit; do not let one `Cargo.toml` path or current directory stand in for the subject.

#### `cargo workenv intent`
Purpose:
- emit the declared environment requirements as `workenv-intent/v0`.

Important rule:
- separate declared requirements from observed success; do not silently upgrade README or editor assumptions into canonical intent unless they were named explicitly.

#### `cargo workenv observe`
Purpose:
- collect one host or CI observation and emit `workenv-observation-report/v0`.

Important rule:
- observation is local and time-bound; it must surface active overrides, drift, skipped checks, and unsupported lanes honestly.

#### `cargo workenv realize`
Purpose:
- record one substrate realization as `workenv-realization-report/v0`.

Important rule:
- a realization report is not proof that all substrates behave the same; devcontainer, Nix, host, CI, and remote lanes must remain distinct.

#### `cargo workenv handoff`
Purpose:
- emit smaller consumer handoffs for humans, editors, CI, support, or agents.

Important rule:
- every handoff is lossy and subordinate to the pack; the `agent` lane must stay capability-bounded and redacted by default.

#### `cargo workenv diff`
Purpose:
- compare two workspace-environment packs while preserving the difference between:
  - subject drift,
  - intent drift,
  - realization drift,
  - observation drift,
  - and secret-posture drift.

## Ranked feature set

### P0 — required for a worthy v0
- freeze workspace subject/discovery truth explicitly;
- export declared environment intent explicitly;
- collect at least one host or CI observation lane;
- collect at least one non-host realization lane (`devcontainer` or `nix`) without flattening it into intent;
- emit one redacted secret profile;
- emit one portable pack and one bounded handoff;
- surface `partial`, `drifted`, `redacted`, `lossy`, `unsupported`, and `unknown` honestly.

### P1 — strong near-term extensions
- workspace-root and parent-config poisoning diagnostics;
- editor-specific handoffs that preserve override-command posture;
- CI import lanes and support/archaeology handoffs;
- richer native-SDK/provider attachments;
- diff reports that separate subject drift from observation drift.

### P2 — do later or fold elsewhere
- remote-dev orchestration suites;
- machine mutation or auto-fix flows;
- secret distribution;
- universal environment-hosting services;
- substrate rankings or badges.

## Pilot lanes that best prove the idea

### 1) Parent-discovery / config-precedence lane
Prove:
- that one selected workspace can record parent-directory config and workspace-discovery effects honestly.

### 2) rustup toolchain lane
Prove:
- that override precedence, toolchain-file settings, and path-toolchain semantics can be exported without pretending they define the whole environment.

### 3) Host versus Dev Container or Nix lane
Prove:
- that one subject can compare a host observation with one realized substrate while keeping realization and observation distinct.

### 4) rust-analyzer / CI handoff lane
Prove:
- that editor and CI consumers can import bounded environment truth instead of re-deriving it privately.

### 5) Redacted support / agent lane
Prove:
- that support and agent consumers can receive useful bounded handoffs without leaking secrets or overclaiming local state.

## Dependencies and imports
This blueprint should import rather than replace:
- **Tooling Contract** for discovery and scope truth;
- **Toolchain Productization** for toolchain and target truth;
- **Native Dependency** for SDK/linker/provider posture;
- **Runtime Settings** for config/env/source posture;
- **Credentials** for secret-handle posture;
- **Project Bootstrap** and local overlays as downstream or adjacent consumers.

Read with:
- `design/workspace-environment-contract-2026Q1.md`
- `design/workspace-environment-stack.md`
- `design/workspace-environment-bundle.md`
- `design/tooling-contract-stack.md`
- `design/toolchain-productization-stack.md`
- `design/native-dependency-kit.md`
- `design/runtime-settings-kit.md`
- `design/credentials-kit.md`
- `proposals/epic-workspace-environment-stack.md`

## Anti-goals worth refusing early
Refuse these tempting wrong shapes early:
- “just bless Dev Containers as the contract”;
- “just bless a flake and call the problem solved”;
- “just archive `.env` and shell history”;
- “just build a universal Rust workbench”;
- “just auto-fix the local machine until the tests pass”.

## Ranking / portfolio position
This blueprint does **not** outrank Build-State Evidence.
It also does **not** replace Tooling Contract, Toolchain Productization, Native Dependency, Runtime Settings, or Credentials.

What it does is sharpen one of the archive's repeatedly named next moves:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest under-ranked day-to-day missing middle;
- **Workspace Environment** is now the clearest **environment / realization / observation / handoff execution blueprint**;
- and future onboarding/editor/CI/agent/local-overlay work should import this layer rather than rediscover workspace-environment truth privately.
