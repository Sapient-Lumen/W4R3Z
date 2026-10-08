# Crate capability-contract product plan — 2026-03-17

This note exists to keep **P-0510 Crate Capability Contract & Interop Profile Kit** disciplined.
The archive already decided that the missing value is a **producer-published support / interop contract**.
This pass answers a narrower question:

> If somebody actually started building **P-0510** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps crate authors publish one reviewable answer to:

- which support profiles they are really claiming,
- which facts are declared versus directly observed versus merely inferred,
- which downstream obligations (`build.rs`, proc macros, native linkage, docs.rs overlays, target overlays, MSRV floors) are materially part of adopting the crate,
- which public interop ecosystems the crate intentionally exposes,
- and how much of the advertised support story was actually observed versus copied from policy.

It should **not** try to become a registry ranking engine, a whole-project support matrix, a per-item availability ledger, or a replacement for slice tools like MSRV/API/security analyzers.
Those are adjacent imports, not the product.

## What the crate should provide other people

For downstream adopters, docs/tool authors, and release reviewers, the crate should provide:

1. **One compact support contract** instead of README archaeology across manifest snippets, docs.rs settings, issue replies, and informal maintainer comments.
2. **A claim-class policy** so `declared`, `observed`, `inferred`, and `manual_review_required` stop being implicit vibes.
3. **Support-obligation receipts** so hidden adoption costs such as `build.rs`, `links`, proc macros, docs.rs overlays, or target overlays become explicit review objects.
4. **Interop export maps** so runtime coupling and ecosystem boundaries (`serde`, `tracing`, `http`, `tower-service`, `futures-core`, `bytes`, and friends) are visible without guessing from prose.
5. **Profile-fidelity reports** so teams can see whether “Tokio-neutral”, “alloc-only”, or “docs-supported on target X” are fully observed claims, partial imports, or policy-only claims.
6. **Short human summaries** that can be pasted into crate docs, release notes, issue templates, or internal allowlists.
7. **A diff surface** that makes quiet support drift loud across releases.
8. **A small portable bundle** that pathfinder-style selection tools, support bots, and CI checks can all consume.

For maintainers, the crate should provide:

1. a compact pack file that is cheap to review,
2. conservative `manual_review_required` escape hatches instead of fake certainty,
3. one place to join Cargo/docs.rs/rustdoc facts with crate-authored policy,
4. an importer boundary for slice tools rather than another attempt to absorb them,
5. and a CI gate for “this release silently changed what adoption means.”

## Recommended `0.1` command surface

### `cargo capability-contract init`
Create a starter `capability-contract.toml` by importing obvious candidates from:

- `Cargo.toml` package metadata,
- `rust-version`, `build`, and `links`,
- docs.rs metadata,
- rustdoc JSON,
- Cargo metadata,
- and optional slice-tool imports when available.

The generated contract should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` rather than guessed.

### `cargo capability-contract observe`
Emit one normalized receipt bundle from the current crate.
This should capture:

- declared support profiles,
- observed support obligations,
- public interop exports,
- source freshness,
- and known manual-review zones.

### `cargo capability-contract check`
Run the local validation pass:

- do declared profiles parse,
- do imported facts match the manifest/docs/rustdoc inputs,
- do declared support claims contradict observed obligations,
- do interop export claims match the public API surface,
- and which facts remain inferred-only or manual-review-only?

### `cargo capability-contract doctor`
Render human-facing warnings for suspicious situations such as:

- `runtime_neutral_claim_but_public_tokio_type_exposed`
- `alloc_only_claim_but_docsrs_std_overlay_present`
- `hidden_build_rs_or_links_obligation`
- `docs_target_claim_relies_on_docsrs_default_only`
- `profile_declared_without_matching_observed_facts`
- `manual_review_required`

`doctor` should be a human-first renderer over captured artifacts, not a magical verifier.

### `cargo capability-contract summary`
Render a short receiver-facing note that answers:

- what support profiles the crate is claiming,
- which obligations adopting it really brings,
- which interop ecosystems it intentionally exposes,
- what was directly observed,
- and how much of the support story still depends on policy or manual review.

### `cargo capability-contract diff <old> <new>`
Compare two receipts or contracts and classify:

- `profile_added`
- `profile_removed`
- `obligation_added`
- `obligation_removed`
- `interop_export_changed`
- `claim_class_changed`
- `profile_fidelity_changed`
- `manual_review_boundary_changed`

### `cargo capability-contract pack`
Emit one compact `.capabilitypack.zip` bundle for docs generation, CI artifacts, allowlist review, and downstream support handoff.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `capability_contract_model`
  - shared Rust types for contracts, receipts, reports, and diffs
- `capability_contract_import`
  - manifest/docs.rs/rustdoc/Cargo metadata import logic
- `capability_contract_check`
  - obligation detection, interop export classification, profile-fidelity checks, and doctor warnings
- `capability_contract_pack`
  - summary rendering, diff writing, markdown output, and zip bundle emission
- `cargo-capability-contract`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `capability_contract_msrv`
- `capability_contract_public_api`
- `capability_contract_semver`
- `capability_contract_security`
- `capability_contract_ci`

## `0.1` artifact set

The archive already had a good core.
`0.1` should still revolve around:

- `capability-contract.toml`
- `observed-capabilities.receipt.json`
- `interop-exports.report.json`
- `profile-conformance.report.json`
- `capability-diff.report.json`
- `capability-summary.md`

This pass adds three more important artifacts:

- `claim-class.policy.json` — what `declared`, `observed`, `inferred`, and `manual_review_required` mean and what minimum evidence each class expects.
- `support-obligation.receipt.json` — where build scripts, native linkage, proc-macro use, docs.rs overlays, target overlays, and MSRV facts came from and how they were observed.
- `profile-fidelity.report.json` — how complete each published support profile is across manifest facts, docs.rs metadata, rustdoc JSON, Cargo metadata, and optional imported receipts.

Those files matter because support stories get vague again if the archive only records a contract and a conformance verdict but not:

- what *kind* of claim is being made,
- what hidden obligations were actually observed,
- and how complete the observed support story really is.

## Discovery order

A disciplined import order helps prevent fake certainty.

1. **Manifest facts**
   - `rust-version`
   - `build`
   - `links`
   - `package.metadata`
2. **docs.rs facts**
   - docs.rs metadata
   - target/default-target overlays
   - rustdoc JSON availability
3. **Cargo graph facts**
   - `cargo metadata`
   - proc-macro/build-dependency/native-linkage hints
4. **Public interop facts**
   - rustdoc JSON and public API scans
5. **Optional slice-tool imports**
   - MSRV/API/semver/security receipts
6. **Manual-review zones**
   - docs-only support claims, public/private runtime leakage, target caveats, and policy-only claims

The importer should prefer visible uncertainty over synthesis.

## Claim-class policy

The first implementation should treat **claim class** as a first-class review object and keep it separate from the fact being claimed.

### What should count as claim classes in `0.1`

- `declared`
- `observed`
- `inferred`
- `manual_review_required`

### What should *not* count as claim classes in `0.1`

- “it appears in crate docs” as proof the claim is observed
- “docs.rs built” as proof all targets/profile variants are supported
- “Cargo metadata contains it” as proof the public API reflects it
- “a slice tool exists” as proof the joined support story is solved

## Support-obligation policy

The first implementation should treat **adoption obligations** as explicit review material.
A good `0.1` should model obligations such as:

- `build_script_present`
- `native_links_present`
- `proc_macro_present`
- `docsrs_metadata_overlay`
- `custom_target_list`
- `msrv_declared`
- `workspace_metadata_inherited`
- `manual_review_required`

with origin classes such as:

- `manifest_observed`
- `docsrs_metadata_observed`
- `cargo_metadata_observed`
- `rustdoc_json_observed`
- `slice_tool_imported`
- `maintainer_declared`

If an obligation is only visible in docs.rs metadata or a workspace inheritance path, the receipt should say so.
`0.1` should prefer “docs.rs overlay observed; crate-local support claim still manual” over pretending the full support story is obvious.

## Profile-fidelity policy

The first implementation should treat **support-profile completeness** as a first-class review object.
A good `0.1` should model:

- `fully_observed`
- `mostly_observed`
- `policy_backed`
- `partial_overlay`
- `manual_review_required`

across dimensions such as:

- manifest facts present
- docs.rs metadata imported
- rustdoc JSON imported
- Cargo metadata imported
- optional slice-tool imports present
- target/profile caveats acknowledged

## First built-in profile families

A disciplined `0.1` should stay narrow:

1. `runtime_neutral_public_api`
2. `tokio_coupled_public_api`
3. `alloc_only_library`
4. `docsrs_overlay_profile`
5. `native_linkage_exposed`
6. `proc_macro_exposed`

The crate should be able to express richer profiles later, but `0.1` should focus on shared, boring producer-side truths.

## Recommended first proving grounds

- async crates using Tokio internally while advertising runtime-neutral public boundaries
- crates claiming `no_std` / `alloc` support while docs.rs or examples build with `std` overlays
- crates with proc macros, `build.rs`, or `links` that materially change downstream adoption cost
- crates with package-versus-workspace metadata interactions that can confuse support claims
- crates whose public interop surface matters as much as their raw functionality

## Why this is worth building now

This lane is sharper now because current official Rust work still emphasizes both **crate navigation** and **smoother library interop**, the 2025 State of Rust survey still says **docs and code** are the main learning surfaces, Cargo/docs.rs already expose real substrate (`package.metadata`, `rust-version`, docs.rs metadata, rustdoc JSON, `cargo metadata`), and crates.io itself is surfacing more decision-relevant information such as security advisories.
That means the missing value is increasingly the **joined, maintainer-published support contract above the substrate**, not the absence of substrate itself.

## What to keep separate

- Keep **P-0510** separate from task-first decision packs (**P-0509**).
- Keep **P-0510** separate from shared ecosystem interop profiles (**P-0511**).
- Keep **P-0510** separate from item-level availability ledgers (**P-0451**).
- Keep **P-0510** separate from whole-project toolchain/target support (**P-0484**).
- Keep **P-0510** separate from slice tools for MSRV/API/semver/security analysis.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2025h1/eii.html
- https://doc.rust-lang.org/cargo/reference/manifest.html
- https://doc.rust-lang.org/cargo/reference/rust-version.html
- https://doc.rust-lang.org/cargo/reference/build-scripts.html
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
