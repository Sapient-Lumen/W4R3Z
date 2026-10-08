# Design: Airgap Kit (`cargo airgap`, `airgap-pack/v0`)

## Goal
Define a portable bootstrapping and validation boundary for Rust in airgapped and restricted-network environments so Cargo, rustup, mirrors, vendor/local-registry workflows, and CI policy tooling can exchange one reviewable set of artifacts.

This should **not** replace Cargo’s offline flags, source replacement, alternate registries, `cargo vendor`, rustup mirror variables, ROMT, or Panamax. It should make them easier to combine coherently and audit.

Current posture in the archive: **frontier-edge candidate with ranked pilot discipline**. Treat this design together with [`design/airgap-pilot-program.md`](./airgap-pilot-program.md) so the archive proves restricted-network Rust on concrete lanes instead of leaving “offline support” as one vague aspiration.

## References (signals)
- Cargo documents `cargo fetch` as the way to make dependencies locally available so later Cargo commands can run offline.
  https://doc.rust-lang.org/cargo/commands/cargo-fetch.html
- Cargo’s FAQ documents `--offline` / `--frozen` and points users toward vendoring/source replacement, and also warns that `Cargo.lock` does not protect consumers like `cargo install` unless `--locked` is used.
  https://doc.rust-lang.org/cargo/faq.html
- Cargo source replacement explicitly supports mirroring, local registries, and vendoring, and requires replacements to be exact copies.
  https://doc.rust-lang.org/cargo/reference/source-replacement.html
- Cargo’s source replacement docs also say the primary helper for local registries is `cargo-local-registry`, installed via `cargo install`.
  https://doc.rust-lang.org/cargo/reference/source-replacement.html
- Cargo registries support both `git` and `sparse` protocols, with sparse fetching only relevant metadata files.
  https://doc.rust-lang.org/cargo/reference/registries.html
- Rust release notes record that sparse registry support for crates.io was stabilized.
  https://doc.rust-lang.org/beta/releases.html
- `cargo install` is explicitly system/user-level and ignores local project config discovery unless installing with `--path`.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
- rustup documents `RUSTUP_DIST_SERVER` and `RUSTUP_UPDATE_ROOT` for local mirrors.
  https://rust-lang.github.io/rustup/environment-variables.html
- Rust’s crates.io mirroring goal explicitly targets secure local mirrors for restrictive firewalls, poor connectivity, and CI usage.
  https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
- crates.io’s January 2026 development update added Trusted Publishing Only Mode and other publish-side hardening. That is complementary, but it does not solve consumer-side mirror/install/offline truth.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- ROMT and Panamax already demonstrate that teams need mirrored rustup + crates.io workflows today.
  https://github.com/drmikehenry/romt
  https://github.com/panamax-rs/panamax

## Core components

### 1) `airgap-profile/v0`
A human-reviewed declaration of what is allowed in a restricted-network Rust environment:
- operating mode: `strict-airgap`, `restricted-egress`, `mirror-required`
- allowed hosts and protocols
- Cargo source strategy (`vendor`, `local-registry`, `mirror-registry`, mixed)
- registry mappings / replacement rules / sparse vs git expectations
- rustup mirror roots and required toolchains/components
- developer-tool installation policy (`cargo install`, prebuilt binaries, pre-seeded cache, internal packages)
- expected lockfile / frozen requirements
- evidence attachment policy

This is the thing humans review before trusting automation.

### 2) `airgap-lock/v0`
A machine-readable resolved snapshot of the environment assumptions:
- effective registry/index URLs after replacement
- mirror config digests / bundle digests / vendor tree digests
- rustup mirror roots
- required targets/components
- tool provisioning entries and versions
- validator/tool versions
- workspace fingerprint and lockfile fingerprint

Design rule: treat dependency sources, tool installs, and toolchain distribution as separate but linked planes.

### 3) `airgap-check-report/v0`
A portable report for validation runs:
- profile + lock identity
- commands executed (`cargo build`, `cargo test`, `cargo install`, `rustup target add`, etc.)
- pass/fail/skip status per check
- observed network attempts (host, protocol, reason if known)
- cache hit/miss hints when available
- remediation notes and reason codes
- policy outcome for CI gating

This is the explainable evidence artifact.

### 4) `airgap-pack/v0`
Bundle format:
- `airgap-profile/v0`
- `airgap-lock/v0`
- `airgap-check-report/v0`
- generated config snippets / templates
- optional vendor or local-registry metadata attachments
- optional mirror metadata/provenance attachments
- optional tool manifest / bootstrap script attachments

This is the portable thing CI, auditors, and downstream teams can attach or consume.

### 5) `cargo airgap`
Reference UX:
- `cargo airgap init`
- `cargo airgap doctor`
- `cargo airgap check`
- `cargo airgap pack`
- `cargo airgap explain`

Design rule: begin as an adapter/orchestration/report layer. It does not need to replace ROMT or Panamax; it should wrap and validate around them where useful.

## Default policy
- **Profile first:** treat offline/restricted-network intent as a reviewed contract, not a pile of ad-hoc shell snippets.
- **Separate the three planes:** dependency builds, developer-tool installation, and rustup/toolchain provisioning must be modeled independently.
- **Prefer evidence over assumptions:** record actual observed network attempts, not just config text.
- **Allow mirror diversity:** git-index, sparse-index, vendor, local-registry, and mixed strategies should all fit v0.
- **Do not store secrets in the artifact:** record locations and mechanisms, not tokens.

## What the kit should provide to others
Use [`design/airgap-pilot-program.md`](./airgap-pilot-program.md) as the ranked rollout layer: workspace dependency/build lane first, developer-tool install lane second, rustup/toolchain lane third, secure mirror verification lane fourth, integrated restricted-network CI/bootstrap lane fifth.

- **Platform / infra teams:** a reusable restricted-network contract instead of bespoke bootstrap documents.
- **Application teams:** one way to prove their workspace actually builds and installs required tools without unexpected egress.
- **Security / compliance teams:** reviewable allowed-host and source-mapping evidence.
- **Mirror operators:** a portable consumer-facing profile/report boundary around existing mirroring tools.
- **Other archive kits:** a standard way to attach “offline-safe” evidence to release, policy, supply-chain, and CI workflows.

## Overlap boundaries
- **Not Release Pipeline Kit:** release tooling may attach `airgap-pack/v0`, but Airgap Kit is about bootstrapping and validation before release, not packaging releases.
- **Not Policy Kit:** policy decides what is allowed; Airgap Kit proves whether the environment obeyed the restricted-network profile in practice.
- **Not Cross Toolchain Kit:** that kit solves cross-compilation/toolchain provisioning generally; Airgap Kit models mirror/offline constraints around toolchain distribution.
- **Not Signed Binaries Kit:** signed installers and prebuilt tools may participate, but Airgap Kit does not define signature metadata formats.
- **Not Cargo Report Kit:** it may consume Cargo report seams later, but its distinctive value is profile/lock/check semantics for restricted networks.

## Hard problems (explicitly scoped)
1. **`cargo install` is not just another workspace build**
   - it has different configuration discovery and often drives real bootstrap pain.
2. **Mirror topologies differ**
   - vendor trees, local registries, sparse mirrors, git-index mirrors, and full service proxies all matter; v0 must not hard-code one hosted story.
3. **Warm-cache success is not the same as offline correctness**
   - the check/report layer must distinguish accidental cache hits from policy-compliant source resolution.
4. **rustup and Cargo are distinct clients**
   - the profile must model both or it will keep producing false confidence.
5. **Secrets and enterprise auth are real, but not portable**
   - v0 should record auth modes and attachment points, not bake credentials into artifacts.
6. **Publish-side hardening is not the same as restricted-network correctness**
   - trusted publishing, advisories, and registry UX help upstream, but airgapped consumers still need explicit install/mirror/toolchain validation.
