# Frontier salience snapshot — 2026-03-17 (41)

This pass did **not** promote a new lane.
It sharpened an existing high-ranked cross-cutting proposal:

- **P-0451 Cfg Availability Ledger Kit** — because the archive still lacked a good release-grade artifact for the ordinary maintainer question that sits between “rustdoc can show conditional markers” and “our release review can actually reason about conditional API drift”: *what is available where, why does it look available there, and how much of that matrix is directly observed rather than merely documented or inferred?*

## Main judgment

The next worthy move in this frontier was **not** another rustdoc renderer, another raw rustdoc-JSON helper, or another generic public-API diff.
Those pieces already exist in partial form.

The sharper missing layer is the **availability ledger contract** above them:

- explicit availability classes,
- explicit origin receipts,
- fidelity reports,
- docs-only / docs.rs-only caveats,
- and release-to-release diffs of that surface.

That move is now better grounded because:

- the rustdoc `doc_cfg` stabilization work and RFC 3631 are making conditional-availability markers more first-class,
- rustdoc documents that `cfg(doc)` can widen docs visibility and that this `cfg` is not passed to doctests,
- docs.rs documents that `cfg(docsrs)` only applies to the final crate and that local preflight is only an approximation of the hosted environment,
- docs.rs hosts rustdoc JSON but warns consumers to look at `format_version`,
- Cargo’s feature rules still make additive/unified feature behavior easy to misread,
- and Cargo now passes `--check-cfg` to both rustc and rustdoc.

So the gap is no longer “Rust has no conditional API tooling”.
The gap is that maintainers still rarely publish a **reviewable matrix / origin / fidelity artifact** above that substrate.

## Broad portfolio ranking after this pass

1. **P-0525 Crate Diagnosis Surface Pack Kit** — still the sharpest missing receiver-facing troubleshooting-support artifact.
2. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest support-truth lanes for real users on real machines.
3. **P-0451 Cfg Availability Ledger Kit** — now one of the clearest implementation-ready cross-cutting lanes for conditional API truth.
4. **P-0472 Docs.rs Build Parity Evidence Kit** — critical adjacent lane, but narrower than item-level availability itself.
5. **P-0121 FFI Boundary & Bindings Conformance Kit** — still a high-value bridge for Rust↔foreign adoption.
6. **P-0197 Text Layout Conformance Kit** — still a large missing boring default outside Cargo-heavy work.
7. **P-0200 WebAuthn & Passkeys Interop + Device Lab Kit** — still a standout domain-specific workbench with very real ecosystem pain.

## Why this won over adjacent candidates right now

- It beat **more docs.rs follow-ons** because docs.rs parity still does not answer item-level availability truth by itself.
- It beat **more toolchain follow-ons** because whole-project support truth and per-item conditional API truth remain different review objects.
- It beat several strong **FFI/domain** candidates because this lane multiplies value across feature-heavy, platform-heavy, and docs-heavy crates rather than only one domain.

## What changed in the archive

Added:
- `meta/cfg-availability-ledger-product-plan-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-41.md`
- `entries/2026-03-17-220.md`
- `fixtures/cfg-availability-ledger-kit/`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/cfg-availability-ledger-kit.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- conditional docs markers,
- docs.rs parity,
- whole-project support claims,
- raw rustdoc-JSON import,
- and generic API/semver tools

into one fake “better conditional docs” story.

## Sources

- https://rust-lang.github.io/rust-project-goals/2025h2/rustdoc-doc-cfg.html
- https://rust-lang.github.io/rfcs/3631-rustdoc-cfgs-handling.html
- https://doc.rust-lang.org/rustdoc/unstable-features.html
- https://doc.rust-lang.org/rustdoc/advanced-features.html
- https://docs.rs/about/builds
- https://docs.rs/about/rustdoc-json
- https://doc.rust-lang.org/cargo/reference/features.html
- https://doc.rust-lang.org/cargo/reference/build-scripts.html
- https://doc.rust-lang.org/cargo/CHANGELOG.html
