# Default card: Conservative installable CLI product (2026 Q1)

Latest renewal receipt: `evidence/conservative-installable-cli-product-2026Q1-renewal-2026-03-22.md`


## Scope
This card applies to:
- public or semi-public command-line applications distributed outside one repository;
- cross-platform developer tools where ordinary users should prefer prebuilt binaries;
- CLIs that need explicit install instructions and a supportable release surface;
- products where release/distribution choices matter as much as crate-internal ergonomics.

Assumptions:
- stable Rust;
- ordinary Cargo package/workspace layout;
- maintainers want a boring, reviewable release/distribution lane;
- prebuilt binaries are desirable for at least some users;
- the product can document supported install/update/uninstall routes explicitly.

This is **not** the default for:
- internal repo-local automation;
- one-file scripts and bug repro utilities;
- library crates;
- GUI apps or mobile/desktop bundles;
- or CLIs whose main distribution route is already fixed by a local institutional package system.

## Why this default now
Rust’s latest challenges framing still says the ecosystem is excellent for **CLI tools**, but getting the right defaults still depends too much on tacit knowledge.
https://blog.rust-lang.org/2026/03/20/rust-challenges/

Cargo already makes several user-facing lifecycle truths explicit:
- `cargo install` ignores packaged lockfiles unless `--locked` is used and begins config discovery at `$CARGO_HOME/config.toml` for non-`--path` installs;
- `cargo uninstall` only removes packages installed with `cargo install` and uses explicit install-root precedence;
- `cargo package` always includes `Cargo.lock` by default, warns that `--exclude-lockfile` is not for general use, emits `.cargo_vcs_info.json`, and rebuilds from a pristine extracted package.
https://doc.rust-lang.org/cargo/commands/cargo-install.html
https://doc.rust-lang.org/cargo/commands/cargo-uninstall.html
https://doc.rust-lang.org/cargo/commands/cargo-package.html

At the same time, `cargo-dist` now provides the most coherent reusable release/distribution layer for this scope: it can plan, build, host, publish, and announce releases; generate installers; and emit machine-readable manifests. It also has first-class supply-chain hooks for signing, attestations, SBOMs, and auditable binaries.
https://axodotdev.github.io/cargo-dist/book/
https://axodotdev.github.io/cargo-dist/book/supplychain-security/index.html

`cargo-binstall` is also now mature enough to be treated as a serious optional route: it installs prebuilt binaries using repository release artifacts and manifest metadata, supports optional signature verification, and falls back to `cargo install` when needed.
https://github.com/cargo-bins/cargo-binstall
https://github.com/cargo-bins/cargo-binstall/blob/main/SUPPORT.md
https://github.com/cargo-bins/cargo-binstall/blob/main/SIGNING.md

For this exact project class, the archive’s current answer is:
**use `cargo-dist` as the default release/distribution layer, publish explicit supported install routes, keep `cargo install --locked` as the documented source fallback, treat `cargo-binstall` support as an optional route layer, and avoid a bespoke self-updater by default.**

## Decision label
**default-with-caveats**

It is the best current reusable starting lane for this scope, but route/ownership/update behavior is still fragmented enough that the default must stay explicit about caveats.

## Default lane summary
### Default lane
- release/distribution orchestration: **cargo-dist**
- artifact host/release surface: **generated release pipeline with machine-readable manifest**
- ordinary user routes: **prebuilt installers/artifacts for the target audience**
- source fallback for Rust users: **`cargo install --locked`**
- optional Cargo-native prebuilt path: **`cargo-binstall` metadata/support when worth it**
- supply-chain minimum: **checksums**, with optional SBOM / auditable / attestation support as needed
- update posture: **documented route-specific updates, no hidden self-updater by default**

### Serious alternative
- **source-first `cargo install --locked` lane** when the audience is mostly Rust developers and the product does not justify prebuilt-distribution complexity yet.

### Watch / not-default here
- bespoke auto-updaters added before route/ownership truth is explicit;
- every possible installer format enabled on day one;
- README advice that hides which routes are actually supported;
- release automation treated as if it were the whole lifecycle contract.

## Slot guidance
### Release/build slot
Prefer `cargo-dist` because it keeps **plan/build/host/publish/announce** explicit and emits machine-readable manifests instead of turning the release lane into a pile of shell scripts.

### Install-route slot
Support only the routes the team is ready to explain and own.
A conservative starting set is:
- prebuilt routes for ordinary users,
- plus `cargo install --locked` for Rust users.
Do not pretend Homebrew, shell, PowerShell, npm, MSI, and source install are all the same lifecycle story.

### Source-fallback slot
If the package is on crates.io, make `cargo install --locked` a real documented path.
Do not leave source installation as folklore.
Keep Cargo’s config-discovery and lockfile behavior visible because it differs from normal project builds.

### Cargo-native prebuilt slot
Treat `cargo-binstall` support as an optional separate route.
Use it when the audience overlaps with Cargo users and the release layout is stable enough to justify `[package.metadata.binstall]` maintenance.
Do not assume it is free just because it is convenient.

### Supply-chain slot
Checksums are the minimum boring default.
Add SBOMs, auditable-binary support, signing, and attestations when the support envelope warrants them, especially for security-sensitive or enterprise-facing tools.

### Update / ownership slot
The conservative default is **not** to ship a bespoke self-updater.
The conservative default is to publish route-specific update instructions and keep ownership scope explicit.
Add a stronger updater story only when the product genuinely needs it and can explain rollback/uninstall consequences.

## Serious alternatives and when they win
### Source-first `cargo install --locked` wins when
- the audience is mostly Rust developers;
- prebuilt artifacts are not worth maintaining yet;
- platform reach is narrow;
- or the tool is still closer to a crate-distributed developer utility than a user-facing product.

### `cargo-binstall`-heavy lane wins when
- the audience overlaps strongly with Cargo users;
- fast prebuilt install matters;
- artifact naming/layout are stable enough to support metadata;
- and the team is willing to maintain signing or exact archive conventions.

### Platform-package-manager-first lanes win when
- distribution is already constrained by an institutional or OS-specific channel;
- local packaging/review/signing rules dominate the release shape;
- or the CLI is effectively part of a larger managed fleet rather than a standalone Rust-native product.

## Escalate to a project-specific brief when
- enterprise signing/compliance requirements dominate;
- the tool needs a stronger updater/rollback model;
- package-admission or supply-chain review must be stricter than the lane default;
- multiple products/shareable libraries/workspaces complicate the release surface;
- or the team is mixing too many route classes without a clear ownership/support story.

## Canonical references
- Cargo install:
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
- Cargo uninstall:
  https://doc.rust-lang.org/cargo/commands/cargo-uninstall.html
- Cargo package:
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- cargo-dist introduction/book:
  https://axodotdev.github.io/cargo-dist/book/
- cargo-dist supply-chain security:
  https://axodotdev.github.io/cargo-dist/book/supplychain-security/index.html
- cargo-binstall overview:
  https://github.com/cargo-bins/cargo-binstall
- cargo-binstall support metadata:
  https://github.com/cargo-bins/cargo-binstall/blob/main/SUPPORT.md
- cargo-binstall signing:
  https://github.com/cargo-bins/cargo-binstall/blob/main/SIGNING.md

## Renewal inputs
Recheck before renewal:
- whether `cargo-dist` remains the clearest reusable release/distribution default;
- whether Cargo changes install/update/uninstall semantics materially;
- whether `cargo-binstall` support/signing changes enough to alter the optional-route story;
- whether this card should split into **developer-distributed CLI** versus **mass-consumer installable CLI**;
- whether stronger route/ownership receipts become practical in the wider archive.

Signal refs:
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

## Non-goals
- declaring `cargo-dist` the universal answer for every Rust binary;
- forcing `cargo-binstall` support into every public CLI;
- treating route-specific lifecycle behavior as already unified;
- replacing project-specific security, admission, or compliance review;
- or flattening internal CLI guidance and installable product guidance into one lane.
