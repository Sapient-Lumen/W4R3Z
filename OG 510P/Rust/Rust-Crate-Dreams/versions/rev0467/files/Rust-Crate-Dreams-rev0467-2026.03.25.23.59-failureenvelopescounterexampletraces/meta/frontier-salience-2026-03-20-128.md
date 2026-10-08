# Frontier salience snapshot — 2026-03-20 (128)

This pass did **not** promote another generic Cargo explainer, another feature-combination runner, or another workspace-speed tool.
It added **P-0528 Cargo Feature Surface Contract Kit** because the archive still lacked one receiver-facing layer above Cargo’s feature semantics.

## Main judgment

The sharper missing layer is not “how do features work?” and not “how can I run more combinations?”.
The sharper missing layer is a **feature support contract** that publishes:

- which feature names are public support surface,
- which are hidden dependency plumbing,
- which named activation profiles are really supported,
- which conflicts are explicit,
- and where unification/default/resolver behavior can still surprise users.

## Why this moved now

Current Cargo substrate already makes the problem precise:

1. Cargo’s feature reference warns that default features are convenient but can be difficult to suppress across a graph, and that removing features or optional dependencies is usually not SemVer-compatible.
2. Cargo’s feature reference also documents `dep:` and `?` syntax because public feature names and dependency plumbing are not the same thing.
3. Cargo explicitly says mutually exclusive features should be avoided if possible, which means crates still need a way to publish conflict policy when they cannot avoid them.
4. Cargo explicitly says the full feature-combination space is exponential, which means “supports features” is not enough without a named-profile and witness story.
5. Resolver-v2 and the edition guide make target/build/dev splitting real, which means the effective feature surface can differ by context.
6. RFC 2957 explicitly says `cargo metadata` does not fully expose the newer resolver story, which keeps a higher-level receipt layer useful.
7. The ecosystem already has combo and unification tools (`cargo tree -e features`, `cargo hack`, `cargo-feature-combinations`, `cargo hakari`), which makes a contract layer more buildable rather than less necessary.

## Why this beat nearby work

The archive already had adjacent lanes for:

- cfg/item availability,
- Cargo config truth,
- MSRV policy activation,
- generic capability contracts,
- upgrade-pack feature-change notes,
- and resolver explanation.

What it still lacked was one compact way to say:

- “these are the public features we actually support,”
- “these hidden toggles are not part of the public contract,”
- “these named combinations are the ones we stand behind,”
- and “this workspace or resolver behavior can still change what you effectively get.”

That is a real crate contribution, not just another diagnostics command.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
2. **P-0514 Crate Upgrade Pack Kit**
3. **P-0520 Crate Lifecycle Surface Pack Kit**
4. **P-0523 Crate Test Surface Pack Kit**
5. **P-0528 Cargo Feature Surface Contract Kit**
6. **P-0518 Crate Observability Surface Pack Kit**
7. **P-0474 cargo-config-layer-receipt-kit**
8. **P-0124 schema-compatibility-workbench-kit**
9. **P-0017 Trust Lens**
10. **P-0121 ffi-boundary-conformance-kit**

## What changed in the archive

Added:
- `entries/2026-03-20-308.md`
- `meta/frontier-salience-2026-03-20-128.md`
- `meta/cargo-feature-surface-product-plan-2026-03-20.md`
- `meta/cargo-feature-surface-lane-boundaries-2026-03-20.md`
- `proposals/cargo-feature-surface-contract-kit.md`
- `fixtures/cargo-feature-surface-contract-kit/README.md`
- feature-surface / activation-profile / conflict-policy / unification-risk schemas
- three scenario families covering grouped dependency wiring, exclusivity policy, and resolver-v2 split risk

Updated:
- `README.md`
- `INDEX.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## Freshness anchors

- Cargo features reference — https://doc.rust-lang.org/cargo/reference/features.html
- Cargo resolver reference — https://doc.rust-lang.org/cargo/reference/resolver.html
- Cargo unstable feature-unification reference — https://doc.rust-lang.org/cargo/reference/unstable.html
- `cargo tree` reference — https://doc.rust-lang.org/cargo/commands/cargo-tree.html
- Rust 2021 resolver guide — https://doc.rust-lang.org/edition-guide/rust-2021/default-cargo-resolver.html
- RFC 2957 — https://rust-lang.github.io/rfcs/2957-cargo-features2.html
- RFC 3143 — https://rust-lang.github.io/rfcs/3143-cargo-weak-namespaced-features.html
- `cargo hakari` docs — https://docs.rs/cargo-hakari/latest/cargo_hakari/about/index.html
- `cargo-feature-combinations` docs — https://docs.rs/cargo-feature-combinations/latest/cargo_feature_combinations/
- `cargo-hack` docs — https://github.com/taiki-e/cargo-hack
