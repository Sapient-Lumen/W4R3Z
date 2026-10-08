# Cfg Availability Ledger lane boundaries — 2026-03-17

This note keeps **P-0451 Cfg Availability Ledger Kit** from collapsing into several adjacent lanes that look similar from a distance but solve different receiver questions.

## Main distinction

**P-0451** is about an **item-level conditional-availability ledger**.
Its center of gravity is:

- which public item is available in which slice,
- what kind of availability claim that is,
- where that claim came from,
- which slice was actually observed,
- how any displayed gate summary was normalized,
- and whether the item’s effective availability is inherited through re-export lineage rather than declared directly on the item a user sees.

That is narrower than whole-project support policy and richer than a raw rustdoc-JSON dump.

## Keep separate from adjacent lanes

### Versus whole-project support contracts (**P-0484**)
- **P-0484** answers whether a crate or workspace supports a toolchain/target environment as a whole.
- **P-0451** answers whether a **specific public item** is available in a named target/feature/docs slice.
- A crate can have a broad support contract while still having surprising per-item conditional drift.

### Versus docs.rs parity / replay bundles (**P-0472**)
- **P-0472** explains hosted-versus-local docs build fidelity and drift causes.
- **P-0451** explains the conditional API surface itself.
- “docs.rs built” is not the same thing as “this item is honestly available in this slice”.

### Versus producer-side capability contracts (**P-0510**)
- **P-0510** summarizes what a crate claims to support at the crate level.
- **P-0451** drills into item-level conditional reachability and visibility.
- A capability contract can say “supports wasm32” while an availability ledger still records which items vanish there.

### Versus generic public-API / SemVer slice tools
- Generic public-API diff tools answer whether names/types changed.
- **P-0451** answers whether a public item became newly available, newly unavailable, docs-visible-only, docs.rs-assumed-only, or uncertain in a named slice.
- SemVer review is one consumer of the ledger, not the ledger itself.

### Versus raw rustdoc-JSON helpers
- rustdoc JSON is substrate.
- **P-0451** is the review artifact layer above that substrate.
- The missing value is not “parse rustdoc JSON”, but “publish a trustworthy availability ledger and diff another team can review”.

## Review objects that must stay separate

When deepening **P-0451**, do not flatten these into one fake availability verdict:

1. **availability class** — `stable_public`, `requires_feature`, `docs_visible_only`, etc.
2. **origin** — direct `cfg`, inherited `cfg`, `#[doc(cfg)]`, `#[cfg(doc)]`, docs.rs config, build-script custom cfg, inference.
3. **slice witness** — which target/feature/docs profile was actually observed and how.
4. **gate normalization** — how a raw `cfg` expression was simplified into a human-facing gate summary.
5. **re-export lineage** — whether the exported item inherited its effective gate from another path.
6. **fidelity** — direct observation, docs-only observation, hosted import, inference, or manual review.

## Failure modes to resist

- Treating a docs-visible item as generally usable.
- Treating a simplified `doc(auto_cfg)` label as the full gate truth.
- Treating `#[cfg(docsrs)]` on the final crate as if it also applied to dependencies.
- Treating a re-exported public path as if its gate were declared locally.
- Treating a hosted rustdoc JSON import as equivalent to a local slice witness.
- Treating custom cfgs from `build.rs` as trustworthy when the expected values were never registered for checking.

## Good proving grounds

- feature-heavy crates using optional dependencies and re-exports
- platform-heavy crates with `unix` / `windows` / `wasm32` splits
- crates using `#[cfg(doc)]` to widen documentation visibility
- crates relying on `#[doc(auto_cfg(hide(...)))]` or `#[doc(cfg(...))]` to simplify what users see
- docs.rs metadata profiles that add features or custom `rustc` cfgs
- workspaces where docs.rs-only cfgs do not reach dependencies

## Sources

- RFC 3631 rustdoc cfg handling: https://rust-lang.github.io/rfcs/3631-rustdoc-cfgs-handling.html
- Rustdoc advanced features (`cfg(doc)` is not passed to doctests): https://doc.rust-lang.org/rustdoc/advanced-features.html
- Rustdoc unstable features (`doc(auto_cfg)` default, hide/show semantics): https://doc.rust-lang.org/rustdoc/unstable-features.html
- docs.rs builds (`cfg(docsrs)` scope, sandbox notes): https://docs.rs/about/builds
- docs.rs metadata (custom features/targets/rustc-args): https://docs.rs/about/metadata
- Cargo build scripts (`cargo::rustc-cfg`, `cargo::rustc-check-cfg`): https://doc.rust-lang.org/cargo/reference/build-scripts.html
