# Default card: Conservative publishable library (2026 Q1)

Latest renewal receipt: `evidence/conservative-publishable-library-2026Q1-renewal-2026-03-22.md`

## Scope
This card applies to:
- reusable Rust libraries intended for crates.io or equivalent long-lived reuse;
- stable-Rust crates where boring contract discipline matters more than rapid experimental churn;
- libraries that want ordinary Cargo/docs.rs/release workflows;
- and teams that expect outside consumers, not only one local application, to depend on the crate.

Assumptions:
- stable Rust;
- ordinary Cargo workflows;
- docs.rs is part of the public documentation posture;
- the crate is not primarily a proc-macro, `-sys` wrapper, or native-toolchain-heavy FFI layer;
- public API evolution matters.

This is **not** the default for:
- proc-macro crates;
- `-sys` / bindgen / native-wrapper crates;
- runtime-specific service frameworks pretending to be libraries;
- one-workspace-only internal helper crates with no publication or semver ambition;
- or safety-critical / highly regulated crates that need much heavier evidence.

## Why this default now
The ecosystem already has lots of good crates.
The recurring problem here is not “can I publish a Rust library?” but “what boring reviewable lane should I normalize around before publication?”

The archive’s current answer for this scope is:

**an explicit-manifest, docs.rs-conscious, semver-gated library lane with owned public error types, minimal accidental public dependencies, and exact package-identity hygiene.**

Why this wins here:
- Cargo’s `rust-version` field exists specifically to declare the supported toolchain floor for a package.
  https://doc.rust-lang.org/cargo/reference/rust-version.html
- Cargo’s SemVer chapter explicitly treats compatibility for libraries as first-class release truth rather than vague convention.
  https://doc.rust-lang.org/cargo/reference/semver.html
- publishing on crates.io is permanent, which makes release discipline matter more for libraries than for local-only crates.
  https://doc.rust-lang.org/cargo/reference/publishing.html
- docs.rs documents both `[package.metadata.docs.rs]` and its nightly sandbox/build model, and `cargo docs-rs` exists specifically to reproduce docs.rs-oriented rustdoc settings in CI.
  https://docs.rs/about/metadata
  https://docs.rs/about/builds
  https://docs.rs/crate/cargo-docs-rs/latest
- Rust’s 2026 goals explicitly include **public/private dependencies** and **Cargo SBOM precursor** inside the “Secure your supply chain” theme.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- the official `cargo-semver-checks` goal makes “check compatibility before publish” a much more current answer than it used to be.
  https://rust-lang.github.io/rust-project-goals/2024h2/cargo-semver-checks.html
  https://crates.io/crates/cargo-semver-checks
- crates.io now exposes Security-tab advisories, Trusted Publishing only mode, SLOC, `pubtime`, and Browse source links, which improves public reviewability around published crates.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- current RustSec advisories include multiple malicious lookalike package names, which makes exact package identity part of conservative publication hygiene.
  https://rustsec.org/advisories/

## Default lane summary
### Default lane
- manifest contract: **explicit `rust-version` plus normal package metadata**
- docs posture: **docs.rs-aware docs with `[package.metadata.docs.rs]` where needed**
- docs CI: **`cargo docs-rs` when docs.rs-specific configuration matters**
- semver gate: **`cargo-semver-checks` before release**
- public error posture: **dedicated public error types, often derived with `thiserror`, not `anyhow` in public API**
- dependency posture: **minimize accidental public dependency exposure; treat public external types as contract surface**
- serialization posture: **use Serde when serialization is intentionally part of the public contract, not by reflex**

### Serious alternatives
- **internal-only workspace crate lane** when the crate is not really meant for outside consumers and publication/semver/docs overhead would be fake precision
- **specialized library lanes** for proc-macros, `-sys` wrappers, FFI bridges, and async-runtime-shaped libraries

### Watch / not-default here
- release automation choice (`release-plz`, `cargo-release`, homegrown automation) is an overlay decision, not the core lane;
- `anyhow` is excellent for applications, but not the conservative default for a public library API;
- `serde` is deliberately optional here because not every reusable library should expose serialization as part of its contract.

## Slot guidance
### Manifest slot
Prefer an explicit package contract:
- `rust-version`
- license
- repository / homepage / documentation where applicable
- readme
- categories / keywords when they materially aid discovery
- deliberate feature declarations

Do not leave these as “we’ll polish them after 1.0” if the crate is already intended for publication.

### Docs slot
Treat docs.rs as part of the public product:
- configure `[package.metadata.docs.rs]` when features or targets need it;
- test the docs path in CI with `cargo docs-rs` when docs.rs-specific behavior matters;
- keep examples and top-level docs aligned with the public API you actually want consumers to use.

### Compatibility slot
Treat semver as a review gate, not a post-hoc apology.
For publishable crates, normalize on `cargo-semver-checks` in release review.

### Public API slot
Prefer owned public surface area.
If your public API exposes foreign dependency types, treat that as deliberate contract surface, not an incidental convenience.

### Error slot
If the crate exposes errors publicly, prefer named error types.
`thiserror` is a good boring fit for that shape.
Avoid `anyhow` in public signatures.

### Serialization slot
Add Serde only when serialization is part of the intended reusable API or file/network contract.
Do not make “derive Serialize/Deserialize on everything” the default posture for a generic library.

## Serious alternatives and when they win
### Internal-only crate lane wins when
- the crate is only shared within one workspace or one organization;
- outside semver commitments are not real yet;
- docs.rs is not part of the actual support surface;
- and publication metadata would only simulate maturity.

### Specialized library lane wins when
- the crate is a proc-macro;
- the crate’s public API is fundamentally FFI/native-toolchain-shaped;
- the crate intentionally exposes async runtime choices in its main API;
- or the crate needs special evidence around unsafe code, safety, or platform support.

## Escalate to a project-specific brief when
- your public API deliberately exposes many foreign dependency types;
- you depend on nightly or unstable Cargo/library features;
- docs.rs requires heavy stubbing or platform fakery;
- the crate has native dependencies, `build.rs`, or nontrivial cross-compilation constraints;
- or the crate is part of a regulated, safety-critical, or security-sensitive domain.

## Canonical references
- Cargo manifest and `rust-version`:
  https://doc.rust-lang.org/cargo/reference/manifest.html
  https://doc.rust-lang.org/cargo/reference/rust-version.html
- Cargo features and semver:
  https://doc.rust-lang.org/cargo/reference/features.html
  https://doc.rust-lang.org/cargo/reference/semver.html
- Cargo publishing:
  https://doc.rust-lang.org/cargo/reference/publishing.html
- docs.rs metadata and builds:
  https://docs.rs/about/metadata
  https://docs.rs/about/builds
- `cargo docs-rs`:
  https://docs.rs/crate/cargo-docs-rs/latest
- `cargo-semver-checks`:
  https://crates.io/crates/cargo-semver-checks
  https://rust-lang.github.io/rust-project-goals/2024h2/cargo-semver-checks.html
- public/private dependencies and SBOM goal framing:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  https://doc.rust-lang.org/cargo/reference/unstable.html
- `thiserror`:
  https://docs.rs/thiserror
- Serde:
  https://serde.rs/
  https://docs.rs/serde

## Renewal inputs
Recheck before renewal:
- Cargo `rust-version`, semver, and publishing guidance;
- docs.rs metadata/build model;
- `cargo docs-rs` viability and scope;
- `cargo-semver-checks` direction and integration status;
- crates.io Security/source/pubtime/Trusted Publishing signals;
- RustSec lookalike or malicious-crate pressure;
- whether public/private dependency stabilization materially changes the default guidance.

Signal refs:
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://rustsec.org/advisories/

## Non-goals
- choosing a universal release automation stack;
- forcing every library to expose Serde traits or `thiserror`;
- pretending this card replaces package-admission review;
- or claiming this is the right lane for proc-macros, FFI-heavy crates, or runtime-first libraries.
