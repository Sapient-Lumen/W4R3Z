# Frontier salience note — 2026-03-22 (193)

## Main judgment

The archive should spend another pass on **P-0535 Dependency Lifecycle Transition Kit** before widening into another adjacent dependency-risk, vendoring, or crate-offramp sector.

## Why

Current official Rust/Cargo/Foundation signals make the missing layer sharper than “better dependency policy docs”:

- the January 2026 safety-critical write-up explicitly says teams often **use crates early, track carefully, shrink dependencies for higher-criticality parts**, and at higher criticality either avoid third-party crates or hide them behind abstraction layers for later replacement;
- the March 2026 challenges write-up says ecosystem maturity is uneven across domains and that tacit ecosystem knowledge still blocks good choices, which raises the value of compact, explicit lifecycle artifacts;
- Cargo’s config docs say `[patch]` can live in `.cargo/config.toml`, but that those files are **not usually checked into source control**, should generally yield to `Cargo.toml` for shared builds, and that config patches override manifest patches when both exist;
- Cargo’s source-replacement docs say replacement assumes the **same source code** and is therefore the wrong tool for patching or private-registry divergence;
- Cargo’s metadata docs say consumers should use `--format-version` and treat source identifiers as opaque, which makes imported graph/signature capture more like a receipt than a permanent truth table;
- Cargo’s lockfile docs keep `Cargo.toml` as the broad declaration and `Cargo.lock` as the exact realized graph;
- and the Rust Foundation’s 2026–2028 strategy keeps **Stable Infrastructure** and **Sustainable Maintenance** as core pillars, reinforcing boring review artifacts over another score or dashboard.

The missing crate is therefore not another dependency tree viewer, override helper, or source-parity proof.
It is a receiver-facing contract for:

1. **override authority and visibility**,
2. **typed transition posture**,
3. **imported-signal freshness**,
4. **exception reevaluation**, and
5. **release-to-release lifecycle drift**.

## Ranking consequence

Keep **P-0535** in the lead cluster and prefer another artifact-completeness pass there before opening a new adjacent lane.
The lane is most worthy when it keeps local transition authority, imported trust/support context, source-route semantics, and exception expiry/freshness distinct.

## What not to do

Do not spend the next pass on:

- another dependency-score dashboard,
- another vendoring or mirror wrapper that does not export lifecycle review objects,
- another local patch convenience helper,
- or another crate-offramp recipe pack.

Those are adjacent at best.
The sharper missing value is the boring lifecycle packet another maintainer or reviewer can actually diff.
