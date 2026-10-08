# Crate off-ramp frontier — successor authority, stopgap honesty, and witnessed migration scope (2026-03-23)

This note deepens **P-0515 Crate Off-Ramp Pack Kit** around one sharper question:

> When a crate tells other people to leave, what exactly makes that exit story authoritative, current enough, and actually witnessed?

## Main judgment

The archive already had a solid answer for:
- **what successor class is being claimed** (`successor-map.report.json`),
- **which stopgap signals exist** (`deprecation-surface.receipt.json`), and
- **what migration recipe is being declared** (`offramp-recipe.manifest.json`).

What it still left too easy to flatten was the difference between:
1. a compiler-visible deprecation note,
2. a maintainer-authored successor declaration,
3. a security-only stopgap,
4. a link that still resolves,
5. and a migration path that was actually run under a meaningful matrix.

That gap matters more now because current official Rust material is unusually explicit about the pieces but still leaves the handoff fragmented:
- the March 2026 challenges write-up says ecosystem navigation and tacit knowledge are still real friction;
- the January 2026 crates.io update adds richer security / trusted-publishing / SLOC substrate but not a stable receiver-facing successor contract;
- the Rust Reference says `#[deprecated]` can carry a `since` and `note`, and rustdoc will show them;
- the rustc lint docs still say deprecations should usually include what to use instead;
- Cargo’s SemVer guide explicitly discusses deprecation staging and even suggests gating deprecations behind a feature for major-version preparation;
- and Cargo’s yank docs still say yanks remove versions from new resolution without deleting code or explaining the long-term exit path.

So the sharper missing crate contribution is not just “better deprecation messaging”.
It is a compact support contract for:
- **who authored the successor claim**,
- **whether a stopgap has an honest horizon**,
- and **what migration evidence was actually witnessed**.

## Review objects to promote now

### 1. `successor-authority.receipt.json`
Purpose: say where the successor/off-ramp claim came from and what class of authority it carries.

Suggested classes:
- `crate_pack_declared`
- `deprecated_note_declared`
- `docs_page_declared`
- `advisory_stopgap_only`
- `yank_pressure_only`
- `third_party_inference`
- `manual_review_required`

### 2. `stopgap-horizon.report.json`
Purpose: distinguish a true long-term successor from a temporary shim or last-safe pin whose expiry, review window, or replacement maturity is still open.

Suggested classes:
- `temporary_shim_window`
- `last_safe_pin`
- `migrate_now`
- `deadline_known`
- `deadline_unknown`
- `successor_maturity_pending`
- `manual_review_required`

### 3. `recipe-witness.report.json`
Purpose: record what exit recipe actually ran, under which matrix, and what still needs behavior / feature / runtime review.

Suggested classes:
- `manifest_rename_checked`
- `feature_mapping_checked`
- `tests_passed`
- `docs_build_checked`
- `adapter_required`
- `behavior_review_required`
- `matrix_partial`
- `recipe_not_witnessed`

### 4. `offramp-support-bundle.manifest.json`
Purpose: portable inventory that keeps successor class, authority basis, stopgap horizon, declared recipe, and witnessed recipe scope separate.

## What a worthy crate should provide other people after this pass

1. **Authority honesty** — “the compiler shows a deprecation note” should not silently become “the maintainer published a long-term successor contract”.
2. **Stopgap honesty** — “pin here for now” should not silently become “this is the real future”.
3. **Witness honesty** — “we wrote a recipe” should not silently become “this migration is broadly proven”.
4. **Portable reviewability** — one support bundle should let another team see successor class, authority origin, horizon, and witness scope without issue archaeology.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- https://doc.rust-lang.org/reference/attributes/diagnostics.html
- https://doc.rust-lang.org/rustc/lints/listing/warn-by-default.html#deprecated
- https://doc.rust-lang.org/cargo/reference/semver.html
- https://doc.rust-lang.org/cargo/commands/cargo-yank.html
