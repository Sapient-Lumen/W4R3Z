# Frontier salience snapshot — 2026-03-17 (55)

This pass did **not** promote a new lane.
It sharpened an already-high-value cross-cutting proposal:

- **P-0451 Cfg Availability Ledger Kit** — because the archive still needed a more reviewable answer to the common state where docs, features, targets, docs.rs settings, and re-exported public paths all imply slightly different stories about whether an API is *actually* available.

## Main judgment

The next worthy move here was **not** another rustdoc renderer, another raw rustdoc-JSON helper, another docs.rs replay runner, or another generic public-API diff tool.
Those already cover important substrate slices.

The sharper missing layer is the **item-level conditional-availability contract** above them:

- explicit slice-witness receipts,
- explicit gate-normalization reports,
- explicit re-export-lineage reports,
- explicit availability classes,
- explicit origin receipts,
- explicit fidelity reports,
- and explicit release diffs for conditional drift.

That move is better grounded now because:

- RFC 3631 and rustdoc’s `doc(auto_cfg)` work make conditional availability more visible but still do not publish a release-grade ledger;
- rustdoc’s `cfg(doc)` support can intentionally widen documentation visibility, while rustdoc’s own docs say that cfg is **not** passed to doctests;
- docs.rs says `cfg(docsrs)` only applies to the final crate being documented, not dependencies;
- docs.rs metadata can add features, targets, and custom `rustc` / `rustdoc` args that materially change what users see;
- Cargo build scripts and `cargo::rustc-check-cfg` make custom cfgs more checkable, but do not by themselves explain a public item’s effective slice-level availability;
- and Cargo feature rules still make “quietly moved behind a feature” drift easy to miss.

So the gap is no longer “Rust cannot show conditional availability”.
The gap is that maintainers still rarely publish a **reviewable slice witness / gate normalization / lineage-aware availability ledger** above those pieces.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
4. **P-0451 Cfg Availability Ledger Kit** — now stronger because slice witness, gate normalization, and re-export lineage make conditional API truth more reviewable instead of letting doc markers masquerade as usability.
5. **P-0519 Crate Authority Surface Pack Kit** — still one of the strongest ambient-power review lanes.
6. **P-0510 Crate Capability Contract & Interop Profile Kit** — still the strongest producer-side fact surface for a single crate.
7. **P-0524 Crate Example Surface Pack Kit** — still the strongest first-success support lane.
8. **P-0525 Crate Diagnosis Surface Pack Kit** — still the strongest steady-state troubleshooting lane.
9. **P-0513 Crate Runtime Handoff Pack Kit** — still the strongest post-failure support-bundle lane.
10. **P-0512 Crate Guidance Pack Kit** — still the strongest compile-time recovery lane.

## Why this won over adjacent candidates right now

- It beat **more docs.rs parity follow-ons** because hosted-build fidelity and item-level availability truth are adjacent but distinct.
- It beat **more capability-contract follow-ons** because the archive still needed a sharper per-item answer before another crate-level support pass.
- It beat **more toolchain-target follow-ons** because whole-project support claims still do not tell users whether a given public item is actually there in a named slice.
- It beat **more SemVer/public-API follow-ons** because structural API diffs still do not tell you whether a public path became docs-only, docs.rs-only, or newly feature-gated.

## What changed in the archive

Added:
- `meta/frontier-salience-2026-03-17-55.md`
- `meta/cfg-availability-ledger-lanes-2026-03-17.md`
- `fixtures/cfg-availability-ledger-kit/README.md`
- `fixtures/cfg-availability-ledger-kit/slice-witness.receipt.schema.json`
- `fixtures/cfg-availability-ledger-kit/gate-normalization.report.schema.json`
- `fixtures/cfg-availability-ledger-kit/reexport-lineage.report.schema.json`
- `fixtures/cfg-availability-ledger-kit/doc_auto_cfg_hide_simplifies_real_gate_surface/`
- `fixtures/cfg-availability-ledger-kit/docsrs_cfg_final_crate_scope_hides_dependency_slice_gap/`
- `fixtures/cfg-availability-ledger-kit/reexported_item_inherits_hidden_target_gate/`
- `entries/2026-03-17-235.md`

Updated:
- `proposals/cfg-availability-ledger-kit.md`
- `meta/cfg-availability-ledger-product-plan-2026-03-17.md`
- `README.md`
- `INDEX.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/known-existing.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- rustdoc gate markers,
- docs-visible-only items,
- docs.rs metadata overlays,
- hosted rustdoc-JSON imports,
- local slice witnesses,
- re-exported public paths,
- and generic public-API diffs

into one fake “conditional API support” story.

## Sources

- https://rust-lang.github.io/rfcs/3631-rustdoc-cfgs-handling.html
- https://doc.rust-lang.org/rustdoc/advanced-features.html
- https://doc.rust-lang.org/rustdoc/unstable-features.html
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://doc.rust-lang.org/cargo/reference/build-scripts.html
- https://doc.rust-lang.org/cargo/reference/features.html
