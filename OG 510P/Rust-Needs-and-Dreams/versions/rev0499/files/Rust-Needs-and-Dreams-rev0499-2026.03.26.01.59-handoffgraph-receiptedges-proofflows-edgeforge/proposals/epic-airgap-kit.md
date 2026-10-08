# Epic Proposal: Airgap Kit (`cargo airgap`)

## One-sentence pitch
Turn restricted-network Rust from tribal knowledge into a first-class, diffable contract: declare allowed mirrors and sources, validate builds/tool installs/toolchain fetches, and ship the result as an `airgap-pack/v0`.

## Deliverables
- `cargo-airgap` reference implementation
- Schemas:
  - `airgap-profile/v0`
  - `airgap-lock/v0`
  - `airgap-check-report/v0`
  - `airgap-pack/v0`
- Adapters/integrations:
  - `cargo fetch`
  - `cargo build --offline` / `--frozen`
  - `cargo vendor`
  - source replacement / alternate registries
  - rustup mirror variables and target/component checks
  - optional mirror-tool adapters for ROMT / Panamax
- Docs:
  - mirror topology guide
  - `cargo install` restricted-network guide
  - CI / audit / policy attachment patterns
- `airgap-pilot-pack/v0` example bundles for the ranked first lanes

## Why now (signals)
- Cargo already documents offline fetch/build flows and source replacement, which means the substrate exists.
  https://doc.rust-lang.org/cargo/commands/cargo-fetch.html
  https://doc.rust-lang.org/cargo/faq.html
  https://doc.rust-lang.org/cargo/reference/source-replacement.html
- Cargo registries support both `git` and `sparse`, and Rust release notes record that sparse registry support for crates.io was stabilized, making mirror-friendly workflows more mainstream.
  https://doc.rust-lang.org/cargo/reference/registries.html
  https://doc.rust-lang.org/beta/releases.html
- `cargo install` explicitly uses system/user-level config discovery, and by default it ignores the packaged `Cargo.lock` unless `--locked` is passed. That is a practical reason offline bootstrap still trips teams up even when workspace builds are mirrored correctly.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
  https://doc.rust-lang.org/cargo/faq.html
- rustup already supports local mirrors through `RUSTUP_DIST_SERVER` and `RUSTUP_UPDATE_ROOT`, so toolchain mirroring is a real supported path, not a hack.
  https://rust-lang.github.io/rustup/environment-variables.html
- crates.io’s January 2026 update added Trusted Publishing Only Mode and other publish-side hardening, which is useful but still leaves consumer-side mirror/install validation as a missing layer.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Rust’s accepted crates.io mirroring goal is explicitly about cryptographic verification and secure mirrors for restrictive firewalls, unreliable internet, and CI mirrors, which makes this a live upstream seam rather than local folklore.
  https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
- ROMT and Panamax show that the ecosystem already needs and builds mirror tooling; what is missing is the shared profile/check/pack boundary around it.
  https://github.com/drmikehenry/romt
  https://github.com/panamax-rs/panamax

## Non-goals
- Replacing Cargo’s built-in offline/source-replacement features
- Standardizing one universal mirror server product
- Solving credential storage and enterprise auth portability in v0
- Treating warm local caches as equivalent to validated offline correctness

Use [`design/airgap-pilot-program.md`](../design/airgap-pilot-program.md) as the rollout layer: workspace build → developer-tool install → rustup mirror → secure mirror verification → integrated CI/bootstrap.

## Strategic value
This kit has high leverage because it connects:
- Rust adoption in regulated or restrictive environments,
- secure mirroring and supply-chain work,
- repeatable CI/bootstrap workflows,
- platform-team documentation debt,
- and downstream evidence for policy/release/compliance tooling.

It gives the archive a concrete answer to a practical question many organizations hit early: “Can we actually bootstrap and use Rust here without talking to the public internet?”

## Milestones
1. **v0**
   - publish schemas
   - ship ranked pilot packs for workspace-build and developer-tool-install lanes
   - validate builds/tests/tool installs/toolchain checks
   - emit `airgap-check-report/v0`
2. **v0.2**
   - add rustup/toolchain mirror pilot packs
   - generate profile/config templates
   - add mirror topology presets (`vendor`, `local-registry`, `sparse`, mixed)
   - add clearer reason codes and host-attempt logs
3. **v1**
   - add secure mirror verification lane
   - stronger CI/policy integration
   - mirror-tool adapters and pack import/export helpers
   - broader conformance corpus across OSes and bootstrap patterns
