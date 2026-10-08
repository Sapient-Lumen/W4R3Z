# Epic Proposal: Workspace Environment Bundle (`cargo workenv` + `workenv-pack/v0`)

## One-sentence pitch
Make Rust workspace setup and day-2 environment truth boring by standardizing a portable **subject → intent → realization → observation → handoff** bundle instead of leaving onboarding, editor/CI alignment, and local override archaeology scattered across config files, substrate metadata, and README prose.

## Deliverables
- `cargo workenv` reference tool
- schemas:
  - `workenv-brief/v0`
  - `workenv-subject/v0`
  - `workenv-intent/v0`
  - `workenv-secret-profile/v0`
  - `workenv-realization-report/v0`
  - `workenv-observation-report/v0`
  - `workenv-handoff/v0`
  - `workenv-diff-report/v0`
  - `workenv-pack/v0`
  - `workenv-import-handoff/v0`
- adapters/importers for:
  - tooling-contract artifacts
  - toolchain-product artifacts
  - native-dependency artifacts
  - runtime-settings artifacts
  - credentials artifacts
  - selected devcontainer / Nix / CI substrate metadata
- docs:
  - subject and discovery-boundary recipe
  - host observation recipe
  - devcontainer or Nix realization recipe
  - secret posture and redaction guide
  - human/editor/CI handoff guide

## Why now (signals)
- The 2025 State of Rust survey says online docs remain canonical, editors with agentic support are rising, and resource usage/debugging remain significant productivity problems; environment truth now needs machine-usable handoffs, not only prose.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo config discovery is hierarchical from the current directory through parent directories, so environment behavior already depends on discovery boundaries rather than only local files.
  https://doc.rust-lang.org/cargo/reference/config.html
- Cargo workspace discovery also walks parent directories for `[workspace]`, and default package selection differs between workspace roots and member directories.
  https://doc.rust-lang.org/cargo/reference/workspaces.html
- rustup toolchain files can pin channel/date/components/targets/profile, while `path` toolchains have different semantics. Toolchain selection is important, but it is not the whole environment.
  https://rust-lang.github.io/rustup/overrides.html
- Cargo 1.94 says broken parent manifests or `.cargo/config.toml` files can poison unrelated builds, which makes explicit subject/discovery export a live need instead of an academic nicety.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- rust-analyzer already runs per-workspace commands by default and supports override commands, extra args/env, and linked-workspace behavior, which shows editor reality is materially configurable and should not stay hidden.
  https://rust-analyzer.github.io/book/configuration.html
- Dev Containers and Nix are real reproducible substrates, but they are substrate-level mechanisms rather than the Rust-specific review layer above them.
  https://containers.dev/implementors/spec/
  https://nix.dev/concepts/flakes.html
- The Rust Foundation’s 2026–2028 strategy couples stable infrastructure, sustainable maintenance, and adoption growth, which makes portable environment truth a strategically well-timed companion-tool category.
  https://rustfoundation.org/strategic-plan/
- The archive’s Epic Contribution Ladder 2026 already ranks Workspace Environment in the top buildable band; this proposal specifies the MVP artifact family clearly enough to start building.
  ../design/epic-contribution-ladder-2026.md

## Non-goals
- replacing Cargo, rustup, Dev Containers, Nix, CI systems, or editors;
- shipping a secret vault;
- forcing one substrate as the one true Rust environment;
- mutating local machines behind a “setup succeeded” abstraction;
- turning environment review into a hosted remote-dev platform.

## Strategic value
This deserves promotion because it gives the archive a **workspace-environment composition point**.
With it:
- onboarding/support can import one bounded workenv pack instead of rediscovering setup from prose;
- editors and CI can consume explicit handoffs rather than reproducing implicit local state;
- bootstrap and prototype-elevation flows can hand off into a sustained environment surface cleanly;
- institutional overlays can express local deviations over a stable public workenv boundary;
- future agent workflows can import a redacted, capability-bounded environment view instead of guessing from repository text.

The prize is not another environment manager.
The prize is a reviewable workspace-environment boundary that other tools can import.

## Proposed shape
Ship a narrowly scoped bundle layer:
1. export one explicit `workenv-subject/v0` and `workenv-intent/v0`;
2. record one host observation lane as `workenv-observation-report/v0`;
3. record one substrate realization lane (`devcontainer` or `nix`) as `workenv-realization-report/v0`;
4. export one redacted `workenv-secret-profile/v0` with validation posture but no secret values;
5. emit one bounded `workenv-handoff/v0` for `human`, `editor`, or `ci`;
6. provide `workenv-diff-report/v0` and `workenv-pack/v0` once the base lanes exist.

## Critical design bet
The critical bet is that **workspace environment truth should stop at declared intent, realized substrate, observed posture, and bounded handoff**.
That means:
- discovery roots and scope are explicit,
- realization kinds stay distinct,
- local overrides and mismatch stay visible,
- secrets remain posture not payload,
- downstream handoffs are explicit,
- but bootstrapping, package admission, release policy, remote-dev hosting, and secret management stay outside the bundle.

Without that boundary, the contribution either stays too weak to matter or bloats into a fake universal workspace platform.

## Milestones
1. **v0 subject + intent lane**
   - `workenv-brief` / `workenv-subject` / `workenv-intent`
   - import selected tooling/toolchain/native/settings facts
2. **v0.2 observation lane**
   - `workenv-observation-report`
   - preserve discovered parent-config and local-override posture explicitly
3. **v0.3 realization lane**
   - `workenv-realization-report`
   - prove one `devcontainer` or `nix` lane without flattening it into intent
4. **v0.4 secret posture lane**
   - `workenv-secret-profile`
   - prove validation/redaction boundaries
5. **v1 handoff + pack lane**
   - `workenv-handoff` / `workenv-pack` / `workenv-import-handoff`
   - support onboarding/editor/CI/agent consumers without overclaiming authority

## Execution order
Use [`design/workspace-environment-bundle.md`](../design/workspace-environment-bundle.md) as the top-level bundle definition.
Then roll out beneath it in this order:
1. [`design/tooling-contract-stack.md`](../design/tooling-contract-stack.md)
2. [`design/toolchain-productization-stack.md`](../design/toolchain-productization-stack.md)
3. [`design/native-dependency-kit.md`](../design/native-dependency-kit.md)
4. [`design/runtime-settings-kit.md`](../design/runtime-settings-kit.md)
5. [`design/credentials-kit.md`](../design/credentials-kit.md)
6. bounded consumers in bootstrap/onboarding/editor/CI/agent lanes

## Success metrics
- humans can reconstruct declared and observed workspace environment truth from one pack;
- local discovery/config/override effects are reviewable instead of folklore;
- host, devcontainer, Nix, CI, and remote lanes remain visibly distinct;
- secrets are represented as posture and validation, not archived values;
- editor/CI/agent consumers can import bounded handoffs without scraping setup prose or local shells;
- the ecosystem gets one explainable workenv seam instead of many substrate-specific setup islands.
