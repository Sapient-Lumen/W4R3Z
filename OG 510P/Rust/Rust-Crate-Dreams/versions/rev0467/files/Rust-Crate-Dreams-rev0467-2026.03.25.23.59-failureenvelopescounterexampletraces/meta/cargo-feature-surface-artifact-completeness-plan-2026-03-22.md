# Cargo feature-surface artifact-completeness plan — 2026-03-22

This note deepens **P-0528 Cargo Feature Surface Contract Kit** around one product question:

> What should another engineer actually receive when a crate or workspace claims “we support these features”?

## Product stance

The crate should remain **receiver-facing, scope-honest, and conservative**.
It should not become:

- another feature lister,
- another combination runner,
- another workspace-unification helper,
- or another docs renderer.

Its job is to emit a compact pack that answers:

- which feature names are public contract versus hidden plumbing,
- which named profiles are actually supported,
- what exact command/workspace/target scope was observed,
- what public hosted-docs profile is being shown to users,
- and where conflict or unification behavior can still surprise downstream users.

## New first-class artifacts

### `resolution-scope.receipt.json`

For each observation, record:

- subject package or workspace subset,
- manifest root,
- resolver version,
- command family (`build`, `check`, `test`, `doc`, `metadata`, `tree`),
- selected packages,
- target/host scope,
- requested feature flags (`default`, `no_default`, explicit list, `all_features`),
- whether workspace-wide feature syntax or package-qualified features were used,
- caveats about what this observation scope does **not** prove.

This keeps one observed command from masquerading as the global feature contract.

### `hosted-feature-profile.receipt.json`

For a hosted docs surface, record:

- source (`docs_rs`, `local_docs_build`, `manual_review_required`),
- explicit `features`, `all-features`, `no-default-features` values,
- default target and target set,
- whether the public feature posture is inherited, explicit, or unknown,
- what public page/profile this influences,
- notes on why hosted docs posture is **not** itself a support verdict.

This keeps “the docs were built with these features” separate from “these are the supported downstream runtime profiles”.

### `feature-support-bundle.manifest.json`

For one exported pack, record:

- subject and release,
- required receipts,
- optional/imported receipts,
- supported named profiles,
- manual-review zones,
- hosted-doc imports,
- sharing or redaction posture.

This should be the thing another reviewer opens first.

## Receiver-facing workflow

### `capture`
Import feature table facts, named profiles, conflict policy, observation scope, and hosted-doc posture.

### `check`
Flag claims that overreach evidence, such as:

- docs.rs built with `all-features` being treated as support for every combination,
- workspace-wide `--no-default-features` observations being treated as single-package truths without scope notes,
- hidden `dep:` plumbing being presented as public contract,
- or unification tricks for speed being presented as downstream support guarantees.

### `diff`
Highlight whether the main change was public names, default set, supported profile status, conflict policy, hosted-doc posture, or observation-scope basis.

### `pack`
Emit one `feature-support-bundle.manifest.json` plus the underlying receipts.

## Good first scenario families

1. **Workspace-wide `--no-default-features` scope differs from a single-package expectation and needs an explicit scope receipt.**
2. **docs.rs built with `all-features` is a public-docs posture, not a runtime support verdict.**
3. **A portable bundle must keep support contract, observed scope, hosted-doc posture, and unification/conflict artifacts separate.**

## Boundary reminders

Keep P-0528 separate from:

- MSRV policy activation and command-floor work (**P-0036**),
- rebuild-causality comparison scope (**P-0469**),
- toolchain/target support posture (**P-0484**),
- and crate-knowledge export policy and excerpt lineage (**P-0536**).

The value here is the **joined feature-support artifact** above Cargo feature semantics and below a broader docs/support/search product.

## Sources

- https://doc.rust-lang.org/cargo/reference/features.html
- https://doc.rust-lang.org/cargo/reference/resolver.html
- https://doc.rust-lang.org/edition-guide/rust-2021/default-cargo-resolver.html
- https://docs.rs/about/metadata
- https://doc.rust-lang.org/beta/releases.html
- https://rust-lang.github.io/rfcs/2957-cargo-features2.html
- https://rust-lang.github.io/rfcs/3143-cargo-weak-namespaced-features.html
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
