## Execution addendum (rev0444)
Read `design/distribution-contract-execution-blueprint-2026Q1.md` immediately after this proposal when the question is no longer only “why is this epic worthy?” but “what should it actually ship first?”

Interpretation rule:
- the epic is still valid;
- the sharper answer is now **reference layer + report/pack command + adapter/acceptance corpus** built around release imports, route catalogs, selection/fallback, verification, ownership, and bounded handoffs;
- and the wrong shapes remain installer monopoly, updater empire, or hosted software portal.

# Epic Proposal: Distribution Contract Stack (`cargo distribution-contract` + `distribution-contract-pack/v0`)

## One-sentence pitch
Make Rust software delivery boring by standardizing a portable **consumer-side** contract layer that links release imports, visible install candidates, selection/fallback decisions, verification results, installed-state ownership, and downstream lifecycle/support/policy handoffs without confusing them with producer-side release truth.

## Why now (rev0407 refinement)
The frontier case is stronger now because the ecosystem no longer has just one dominant delivery lane:
- `cargo install` still defaults to source builds and ignores packaged lockfiles unless `--locked` is used;
- Cargo's own team still treats installed-binary updates as plugin territory rather than solved built-in behavior;
- cargo-dist now has explicit build/distribute phases, machine-readable manifests, mirror fallback, and installer-hardening work;
- cargo-binstall openly models prebuilt acquisition as a route/fallback problem;
- and rustup's own channel/component behavior proves that Rust delivery already includes policy-like selection/fallback logic.

That combination makes a thin delivery/acquisition/ownership contract more urgent than another installer-specific wrapper.

## Deliverables
- `cargo distribution-contract` reference composer
- schemas:
  - `distribution-contract-brief/v0`
  - `distribution-contract-diff/v0`
  - `distribution-contract-pack/v0`
  - `distribution-contract-handoff/v0`
- adapters/importers for:
  - `install-pack/v0`
  - `install-receipt/v0`
  - `release-pack/v0`
  - `binpack/v0`
  - `binverify-report/v0`
  - `airgap-pack/v0`
  - package-manager / installer import profiles
- docs:
  - prebuilt-vs-source acquisition recipe
  - mirror / host fallback recipe
  - managed-content / uninstall-ownership guide
  - restricted-network consumer guide
  - support / incident handoff guide

## Why now (signals)
- `cargo install` still manages Cargo’s local set of installed binary crates, builds from source by default, and determines the install root through local Cargo configuration rather than through one universal system-package contract.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
  https://doc.rust-lang.org/book/ch14-04-installing-binaries.html
- Cargo’s own docs are explicit that packaged lockfiles only affect consumers when `--locked` is used, while Cargo’s FAQ explicitly warns that `Cargo.lock` does not affect consumers of a package by default. That means consumer-side install truth can still diverge from package-time and release-time truth in ordinary Rust workflows.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
  https://doc.rust-lang.org/cargo/faq.html
- Cargo team updates still point to missing built-in install/update ergonomics: in the 1.86 development cycle the team highlighted `cargo-install-update` and said built-in support is being tracked in #4101.
  https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/
- Cargo and rustup are actively discussing path ownership and uninstall boundaries: in the 1.90 development-cycle writeup, the teams called out that Rustup can end up deleting user binaries in shared install paths and decided Rustup should only remove content it manages.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- crates.io’s current momentum is still mostly producer-side — GitLab Trusted Publishing, Trusted-Publishing-only mode, blocked risky triggers, and `pubtime` — which strengthens release/package truth without yet telling support or policy consumers what any given machine actually installed.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Rust’s 2026 flagships keep supply-chain work active through public/private dependencies and SBOM support, which raises the value of preserving package → release → install handoffs honestly.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## Non-goals
- replacing OS package managers, rustup, `cargo install`, or package-manager-native flows;
- pretending release truth and install truth are the same event;
- inventing one monopoly installer or one global binary channel for Rust;
- flattening prebuilt verification, source-build fallback, and local-path mutation into one success bit;
- hiding unmanaged or partially managed local files behind “installed successfully”.

## Strategic value
This deserves promotion because it gives the archive the missing **consumer-side composition point**.
With it:
- release-native artifacts can stay canonical upstream while acquisition receipts stay canonical downstream;
- organizations can express channel / mirror / verification / fallback policy without reimplementing installers;
- support and incident tooling can stop reverse-engineering installs from shell logs and screenshots;
- update and uninstall decisions can distinguish **what exists in a path** from **what this tool actually owns**.

The prize is not another installer.
The prize is a durable consumer-side record of **what was visible, what was chosen, what was verified, what was mutated, and who owns it now**.

## Proposed shape
Ship a narrowly scoped stack-level layer:
1. import `install-pack/v0` and `install-receipt/v0` as the canonical leaf acquisition artifacts;
2. import `release-pack/v0`, `binpack/v0`, and `binverify-report/v0` as producer-side evidence, not as substitutes for receipts;
3. preserve visible-catalog truth, refusal reasons, verification outcomes, and source-build lock posture in stack-level diffs;
4. preserve installed-state ownership and managed-content boundaries explicitly;
5. emit bounded handoffs for support / incident / policy / inventory consumers;
6. support online, mirrored, and restricted-network lanes without pretending they are the same environment.

## Critical design bet
The critical bet is that **distribution-contract truth stops at consumer-side acquisition, mutation, and handoff**.
That means:
- producer publication and signatures are imported,
- consumer-visible catalog and selection are first-class,
- verification and fallback remain explicit,
- installed-state ownership is recorded,
- but package admission, producer release authority, trust verdicts, and downstream support conclusions stay in their own layers.

Without that boundary, the stack either stays too weak to matter or bloats into a fake universal package/distribution platform.

## Milestones
1. **v0 stack pack + leaf install lane**
   - `distribution-contract-brief` / `distribution-contract-pack`
   - import `install-pack/v0` + `install-receipt/v0`
2. **v0.2 mirror / fallback lane**
   - preserve candidate ordering and refusal reasons
   - diff host-down vs policy-preferred mirror outcomes
3. **v0.3 ownership / uninstall lane**
   - record manager identity, managed-content scope, and path mutation ownership
   - support update / uninstall planning without overclaiming ownership
4. **v0.4 restricted-network lane**
   - import `airgap-pack/v0`
   - preserve mirror-only / source-only / local-only posture
5. **v1 downstream handoffs**
   - emit support / incident / inventory / policy handoffs
   - support archaeology across time, channel, and host changes

## Execution order
Use [`design/distribution-contract-pilot-program.md`](../design/distribution-contract-pilot-program.md) as the stack-level rollout:
1. single-tool prebuilt-vs-source lane,
2. mirror / host fallback lane,
3. package-manager / install-script import lane,
4. restricted-network consumer lane,
5. support / incident / archaeology consumer lane.

Use [`proposals/epic-consumer-install-kit.md`](./epic-consumer-install-kit.md) as the leaf-level acquisition/tooling epic beneath it.

## Success metrics
- consumers can reconstruct what install candidates were visible and why one was chosen;
- receipts preserve whether a source build used packaged lock truth, recomputed resolution, or a local lock;
- update and uninstall tooling can distinguish managed content from merely co-located binaries;
- support / incident / policy consumers can import the acquisition boundary without re-scraping terminals or CI logs;
- the ecosystem gets one explainable consumer-side acquisition seam instead of scattered installer conventions and path folklore.
