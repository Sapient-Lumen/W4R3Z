# Epic Proposal: Consumer Install Kit (`cargo installproof`, `install-pack/v0`)

## One-sentence pitch
Make Rust software installation boring by standardizing a portable consumer-install contract that records visible candidates, selection/fallback decisions, verification posture, on-disk mutations, and managed-content claims across source builds, prebuilt binaries, package-manager lanes, and imported installer flows.

## Deliverables
- Schemas:
  - `install-brief/v0`
  - `install-subject/v0`
  - `install-candidate/v0`
  - `install-catalog/v0`
  - `install-policy/v0`
  - `install-plan/v0`
  - `install-receipt/v0`
  - `install-pack/v0`
  - `install-handoff/v0`
- Tools:
  - `cargo-installproof` reference implementation
  - adapters/importers for:
    - `cargo install`
    - `cargo-binstall`
    - cargo-dist manifests/installers
    - CI fallback wrappers
    - package-manager / installer import lanes
- Docs:
  - source-build versus prebuilt install guide
  - mirror / host fallback guide
  - signature / checksum policy guide
  - managed-content and install-root guide
  - downstream handoff guide for update/support/policy consumers
- Corpus + tests:
  - `cargo install` lockfile-posture lane
  - prebuilt signed-vs-unsigned lane
  - host-down / mirror-fallback lane
  - CI fallback lane
  - package-manager import lane

## Why now
- `cargo install` is explicit that packaged lockfiles are ignored unless `--locked` is used, that install metadata is tracked in the install root by default, and that `--no-track` disables both that metadata file and Cargo’s concurrent-install protection.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
- Cargo packaging docs now say `--exclude-lockfile` is not for general use because some consumers expect the lockfile, including `cargo install --locked`.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- `cargo-binstall` already makes prebuilt binaries practical but still exposes explicit signature policy and limited signature support rather than an ambient ecosystem-wide install contract.
  https://github.com/cargo-bins/cargo-binstall
- cargo-dist now has mirror-aware hosting fallback, which means host order and actual selected source are first-class install facts rather than deployment trivia.
  https://github.com/axodotdev/cargo-dist/blob/main/CHANGELOG.md
- `taiki-e/install-action` publicly exposes fallback choices between `cargo-binstall` and `cargo install`, which proves CI acquisition is already plural.
  https://github.com/taiki-e/install-action
- `axoupdater` already has an install-receipt concept, which is useful evidence that receipts are real but still too tool-local.
  https://docs.rs/axoupdater/latest/axoupdater/
- crates.io’s stronger publish-side truth (`Trusted Publishing`, `pubtime`) still does not answer what any given machine or CI runner actually installed.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

## Non-goals
- Replacing OS package managers, `cargo install`, `cargo-binstall`, cargo-dist, or updater tools.
- Pretending every install path can have the same verification strength.
- Flattening release truth, install truth, and update continuity into one event.
- Hiding local-path installs, skipped checks, or unmanaged files behind a generic success bit.
- Inventing one monopoly installer or one mandatory host for Rust binaries.

## Strategic value
This deserves promotion because it gives the ecosystem the missing **leaf-level acquisition/install composition point**:
- producer-side release and verification artifacts can stay canonical upstream;
- consumers and CI can retain durable install receipts downstream;
- update/uninstall tools can start from explicit managed-content claims instead of path folklore;
- support and policy consumers can stop reconstructing installs from screenshots and shell transcripts.

The prize is not another installer.
The prize is a durable consumer-install record of **what was visible, what was chosen, what was verified, what was mutated, and what this tool claims to manage**.

## Milestones
1. **v0 subject/catalog/receipt lane**
   - `install-subject`, `install-catalog`, `install-plan`, `install-receipt`, `install-pack`
   - ordinary `cargo install` receipts with honest lockfile posture
2. **v0.2 prebuilt-verification lane**
   - prebuilt candidates, signature policy, target-match posture
3. **v0.3 mirror/fallback lane**
   - explicit host ordering and refusal reasons
   - durable selected-host receipts
4. **v0.4 CI and package-manager import lane**
   - imported wrapper/package-manager installs with lossiness notes
5. **v1 downstream handoffs**
   - Update Continuity / support / incident / policy consumers
   - stable schema + regression corpus

## Execution order
Use [`design/consumer-install-kit.md`](../design/consumer-install-kit.md) as the leaf-level artifact design.
Use [`design/consumer-install-lane-map.md`](../design/consumer-install-lane-map.md) as the archive rule for keeping install lanes separate.
Use [`design/consumer-install-pilot-program.md`](../design/consumer-install-pilot-program.md) as the ranked rollout for proving those lanes.
Use [`design/distribution-contract-pilot-program.md`](../design/distribution-contract-pilot-program.md) as the stack-level rollout above the leaf install boundary.

## Success metrics
- reviewers can reconstruct what install candidates were visible and why one was chosen;
- receipts preserve whether a source build used packaged lock truth, recomputed resolution, or a local lock;
- prebuilt verification posture and skipped checks remain explicit;
- managed-content scope is explicit enough for later update/uninstall tooling;
- support / policy / lifecycle consumers can import install truth without rescraping terminals or CI logs.
