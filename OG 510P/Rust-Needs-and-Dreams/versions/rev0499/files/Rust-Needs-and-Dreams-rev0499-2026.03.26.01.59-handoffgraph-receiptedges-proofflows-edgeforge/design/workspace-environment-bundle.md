## Execution addendum (rev0445)
For questions about **what the bundle should actually ship first as a real project**, read `design/workspace-environment-execution-blueprint-2026Q1.md` immediately after this note.

Interpretation rule:
- this bundle note still explains the composition boundary;
- the new execution blueprint now answers the narrower question of what the worthy contribution should actually build, prove, and refuse;
- and future revisions should keep subject/discovery, intent, realization, observation, and handoff distinct rather than silently turning one substrate or one local success into the whole bundle.

# Design: Workspace Environment Bundle

## Thesis
Rust workspace-environment truth is now too important to stay smeared across `rust-toolchain.toml`, `.cargo/config.toml`, rust-analyzer settings, devcontainer metadata, Nix files, CI bootstrap scripts, and README prose.

The missing contribution is not another environment manager.
It is a thin portable bundle that keeps five truths separate:
- **workspace subject** — which repo/workspace/discovery boundary is being described;
- **declared intent** — which toolchain/native/service/editor/credential requirements are claimed;
- **realization** — how a host shell, Dev Container, Nix shell/flake, CI image, or remote workspace realizes those requirements;
- **observation** — what was actually present and working on one machine or run;
- **handoff** — what a human, editor, CI system, or assistant may safely import next.

## Why this bundle now matters
Fresh official signals are unusually aligned:
- The 2025 State of Rust survey says online docs remain the preferred canonical reference while editors with agentic support are rising and resource usage/debugging remain important productivity problems.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo config is hierarchical and is discovered from the current directory through parent directories, which means environment behavior is already partly a discovery problem rather than only a manifest problem.
  https://doc.rust-lang.org/cargo/reference/config.html
- Cargo workspace discovery also walks parent directories for `[workspace]`, and package selection defaults differ depending on whether you are in a member directory or a workspace root.
  https://doc.rust-lang.org/cargo/reference/workspaces.html
- rustup toolchain files can pin channel, date, components, targets, and profile, while `path` toolchains have different semantics. Toolchain choice is therefore project-facing but still only one slice of environment truth.
  https://rust-lang.github.io/rustup/overrides.html
- Cargo 1.94 says broken parent manifests or `.cargo/config.toml` files can poison unrelated builds, which is a strong signal that workspace subject/discovery boundaries need reviewable exports.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- rust-analyzer already runs build scripts / check commands per workspace by default, supports override commands, extra args/env, and linked-workspace behavior. That is concrete evidence that editor reality and build reality still need an honest shared contract.
  https://rust-analyzer.github.io/book/configuration.html
- The Development Container Specification and Nix both provide repeatable environment substrates, but they are substrate-level mechanisms rather than the Rust-specific review layer above them.
  https://containers.dev/implementors/spec/
  https://nix.dev/concepts/flakes.html
- The Rust Foundation’s 2026–2028 strategy explicitly couples stable infrastructure, sustainable maintenance, and adoption growth, which is exactly where workspace-environment truth sits.
  https://rustfoundation.org/strategic-plan/

Together these signals say the next worthy move is not one more setup guide.
It is a **workenv bundle** that can travel between humans and tools without pretending that all realization substrates are identical.

## Bundle members
Treat this as a deliberate bundle composed from existing lower layers:
- **Tooling Contract Stack** owns discovery roots, workspace/config inheritance, package selection, and execution-scope truth.
- **Toolchain Productization Stack** owns toolchain / target / sysroot / activation truth.
- **Native Dependency Kit** owns provider/link/SDK posture.
- **Runtime Settings Kit** owns config/env/default/source/reload truth.
- **Credentials Kit** owns secret-handle and credential-source posture.
- **Workspace Environment Bundle** owns the composition boundary above them.

## Core artifact family

### 1. `workenv-brief/v0`
A concise summary for humans and assistants:
- workspace subject label
- discovery root and scope summary
- selected realization kinds present
- current observation freshness
- mismatch / drift / missing-requirement summary
- redaction posture and review timestamp

### 2. `workenv-subject/v0`
Identity for the thing being described:
- repo/workspace identity
- discovery root and discovery method
- included / excluded workspace scope
- relevant non-Cargo attachments
- local overlay or org overlay refs when present

### 3. `workenv-intent/v0`
What the workspace says it needs:
- toolchain/channel/target/component needs
- native/provider/service requirements
- editor/task/build-system assumptions
- supported realization kinds (`host`, `devcontainer`, `nix`, `ci`, `remote`, `other`)
- required vs optional lanes

### 4. `workenv-secret-profile/v0`
Secret posture without secret capture:
- required handles / classes of secret
- acquisition/source posture (`local`, `ci`, `remote`, `manual`, `unknown`)
- redaction guarantees
- validation posture
- optional vs required secret lanes

### 5. `workenv-realization-report/v0`
One concrete substrate realization:
- imported `workenv-subject/v0`
- realization kind and generator identity
- realized toolchain/native/service/editor attachments
- material overrides or omissions
- portability / host-specific notes

### 6. `workenv-observation-report/v0`
What one machine or run actually saw:
- imported `workenv-subject/v0`
- current toolchain/config/editor/native/service posture
- active overrides discovered from parent directories or local files
- missing pieces / mismatch / drift findings
- validation checks executed and skipped

### 7. `workenv-handoff/v0`
A bounded consumer-facing summary for:
- `human`
- `editor`
- `ci`
- `agent`

The `agent` lane must be redacted and capability-bounded by default.

### 8. `workenv-diff-report/v0`
Difference between two workenv states:
- subject-consistency check
- intent drift
- realization drift
- observation drift
- secret-profile posture drift
- bounded consequence summary

### 9. `workenv-pack/v0`
Attachable bundle linking:
- `workenv-brief/v0`
- current `workenv-subject/v0`
- current `workenv-intent/v0`
- optional `workenv-secret-profile/v0`
- one or more realization reports
- one or more observation reports
- optional handoffs and diff reports
- imported tooling/toolchain/native/settings/credential attachments

### 10. `workenv-import-handoff/v0`
Lossy but explicit export for downstream consumers such as:
- onboarding/support
- bootstrap/prototype-elevation
- policy/institutional overlays
- CI/editor integration
- archaeology and environment migration

## Reference UX
A reference implementation could expose:
- `cargo workenv export` — emit `workenv-subject/v0` + `workenv-intent/v0`
- `cargo workenv observe` — emit `workenv-observation-report/v0`
- `cargo workenv realize --kind <host|devcontainer|nix|ci|remote>` — emit `workenv-realization-report/v0`
- `cargo workenv handoff --for <human|editor|ci|agent>` — emit `workenv-handoff/v0`
- `cargo workenv diff <state-a> <state-b>` — emit `workenv-diff-report/v0`
- `cargo workenv pack` — bundle `workenv-pack/v0`

## Theory of change
The critical design move is to keep these truths separate:
- **what workspace this is**,
- **what it claims to need**,
- **how one substrate realizes that claim**,
- **what one machine actually observed**,
- and **what another consumer may safely import**.

That separation matters because current Rust practice often collapses them into one fake story:
- `rust-toolchain.toml` becomes “the whole environment”;
- `.cargo/config.toml` becomes “the intended workspace behavior” even when inherited parent config or local overrides materially change it;
- a devcontainer or flake becomes “the one true setup” even when host or CI lanes are also supported;
- an editor override command becomes “the build system”; or
- a successful local run becomes “proof that onboarding is solved”.

If those truths stay flattened together, the ecosystem will keep producing substrate-specific setup islands instead of one boring portable workenv vocabulary.

## Shared stack role
This bundle should be treated as the archive’s **workspace-environment composition point**.
It is:
- above **Tooling Contract**, **Toolchain Productization**, **Native Dependency**, **Runtime Settings**, and **Credentials**;
- beside **Project Bootstrap**, **Prototype Elevation**, and **Institutional Overlay**;
- upstream of onboarding/support/editor/CI/agent consumers.

## Adjacent boundaries
- **Tooling Contract Stack** still owns discovery roots, package selection, config inheritance, and execution-scope truth.
- **Toolchain Productization Stack** still owns toolchain/sysroot/activation truth.
- **Native Dependency Kit** still owns provider/link/SDK posture.
- **Runtime Settings Kit** still owns config/env/default/source/reload truth.
- **Credentials Kit** still owns secret handles and credential-source posture.
- **Project Bootstrap** still owns starter realization rather than sustained environment truth.
- **Prototype Elevation** still owns small-to-structured promotion rather than full workspace environment description.

## MVP boundary
A worthy first implementation should prove exactly five things:
1. export one explicit workspace subject and declared intent;
2. record one host observation lane without pretending it is the only supported lane;
3. record one substrate realization lane (`devcontainer` or `nix`) as a realization report rather than flattening it into intent;
4. emit one redacted secret profile with validation posture but no raw secret capture;
5. emit one bounded handoff for `human`, `editor`, or `ci` consumers.

That is enough to validate the bundle without becoming a universal environment manager.

## Non-goals
Do **not** turn this into:
- a universal Rust environment manager,
- a replacement for rustup or Cargo,
- a secret vault,
- a forced move to Dev Containers or Nix,
- a hidden machine-mutation bot,
- or a fake “works on my machine” badge.

Also avoid flattening:
- workspace subject and package-selection truth,
- intended requirements and observed reality,
- one realization substrate and all other supported lanes,
- secret posture and secret values,
- editor overrides and canonical build behavior.

## Success criteria
- humans can reconstruct a workspace’s declared environment and current observed posture from one portable pack;
- host, container, Nix, CI, and remote lanes remain visibly distinct;
- local overrides and parent-discovery effects become reviewable instead of folklore;
- editors/CI/agents can import bounded handoffs without scraping README prose or local shell history;
- the ecosystem gets one explainable workspace-environment seam instead of setup truth staying split across config files, editor settings, container metadata, and tribal knowledge.
