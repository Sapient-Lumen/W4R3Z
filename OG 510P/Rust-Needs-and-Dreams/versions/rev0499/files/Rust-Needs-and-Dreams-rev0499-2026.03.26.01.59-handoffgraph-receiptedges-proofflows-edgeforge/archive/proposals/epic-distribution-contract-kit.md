# Epic Proposal: Distribution Contract Kit (`cargo acquire`, `distribution-pack/v0`)

## One-sentence pitch
Make Rust software acquisition boring by standardizing a consumer-side distribution contract that records channels, mirrors, fallback decisions, verification strength, and durable install receipts across source builds and prebuilt artifacts.

## Deliverables
- Schemas:
  - `distribution-subject/v0`
  - `distribution-catalog/v0`
  - `distribution-policy/v0`
  - `install-plan/v0`
  - `install-receipt/v0`
  - `distribution-pack/v0`
- Tools:
  - `cargo-acquire` reference implementation
  - adapters/importers for:
    - `cargo install`
    - `cargo-binstall`
    - `cargo-dist` manifests
    - mirror/airgap profiles
- Docs:
  - prebuilt-vs-source recipes
  - mirror/channel policy guide
  - restricted-network consumer guide
  - support / incident receipt cookbook
- Corpus + tests:
  - signed-binary lane
  - source-build fallback lane
  - host-down / mirror-fallback lane
  - unsigned / policy-blocked lane

## Why now
- `cargo install` is still a source-build convenience path and ignores packaged lockfiles unless `--locked` is used, so consumer installs can diverge from producer-time dependency selection.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
- The Rust book still presents `cargo install` as convenience, not a universal packaging solution, which means multiple acquisition channels are a built-in ecosystem reality.
  https://doc.rust-lang.org/book/ch14-04-installing-binaries.html
- `cargo-binstall` already makes prebuilt binaries practical, but its docs still describe signature support as initial/limited and metadata as explicit rather than ambient.
  https://github.com/cargo-bins/cargo-binstall/blob/main/README.md
  https://github.com/cargo-bins/cargo-binstall/blob/main/SIGNING.md
- `cargo-dist` now provides machine-readable manifests, installers, publishing hooks, and mirror-capable hosting, which means the producer side is converging enough that the consumer side can stop being shell-script folklore.
  https://github.com/axodotdev/cargo-dist
  https://github.com/axodotdev/cargo-dist/blob/main/CHANGELOG.md
- crates.io’s stronger Trusted Publishing controls and `pubtime` improve release-side truth, but they still do not answer what a user or CI actually installed.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

## Non-goals
- Replacing OS package managers
- Replacing `cargo install`, `cargo-binstall`, or `cargo-dist`
- Pretending every install path can have the same verification strength
- Treating release truth and install truth as the same event
- Hiding source-build fallbacks behind a “fast install” badge

## Strategic value
This is a worthy contribution because it gives the ecosystem a **consumer-side composition point**:
- producers can publish richer install candidates without forcing one host or installer;
- organizations can express channel/mirror/signature policy clearly;
- users and CI can retain durable receipts for what actually landed on disk;
- support and incident tools can stop reverse-engineering installs from terminal logs.

The real prize is not another installer.
The prize is an honest record of **what got installed, why, and with what evidence**.

## Milestones
1. **v0 schemas + single-tool lane**
   - subject / catalog / plan / receipt / pack
   - prebuilt-vs-source distinction
2. **v0.2 mirror and host fallback lane**
   - explicit host ordering and refusal reasons
   - durable mirror receipts
3. **v0.3 package-manager / install-script import lane**
   - imported candidate classes with lossiness notes
4. **v0.4 restricted-network lane**
   - `airgap-pack` imports
   - mirror-only and source-only policies
5. **v1 support / incident / archaeology consumers**
   - real downstream receipt consumers
   - stable schema + regression corpus

## Execution order
Use [`design/distribution-contract-pilot-program.md`](../design/distribution-contract-pilot-program.md) as the ranked rollout for this epic:
1. single-tool prebuilt-vs-source lane,
2. mirror / host fallback lane,
3. package-manager / install-script import lane,
4. restricted-network consumer lane,
5. support / incident / archaeology consumer lane.
