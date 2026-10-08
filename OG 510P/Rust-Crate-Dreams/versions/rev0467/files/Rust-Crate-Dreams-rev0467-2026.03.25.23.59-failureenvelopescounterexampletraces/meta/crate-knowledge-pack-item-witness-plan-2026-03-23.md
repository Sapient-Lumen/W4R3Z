# Crate Knowledge Pack — item witness and identity-fidelity plan (2026-03-23)

This note deepens **P-0536 Crate Knowledge Pack Kit** around one product question:

> when a crate-knowledge pack says “this claim cites item X”, what reviewable artifact preserves that this is really *the same item* across versions, targets, and imported doc surfaces instead of merely *a nearby page or a reused opaque ID*?

## Main judgment

The next high-leverage move is to freeze two more receiver-facing artifacts:

1. `item-witness.manifest.json`
2. `identity-fidelity.report.json`

These should sit beside:
- `material-basis.receipt.json`
- `export-policy.receipt.json`
- `excerpt-lineage.report.json`
- `claim-trace.report.json`
- `citation-locator.receipt.json`
- `citation-capability.report.json`

Do not flatten those into one fake “the claim is pinned and therefore the identity is settled” story.

## Why this matters now

Fresh official docs make the missing layer unusually concrete:

- RFC 2963 says rustdoc JSON item IDs are opaque, only valid within one JSON blob, and not guaranteed to be stable across compiler invocations;
- that same RFC says rustdoc HTML is explicitly not stabilized and not intended as a scraping contract;
- docs.rs exposes floating shorthand routes and target-aware builds;
- docs.rs download archives are useful imports but are not equivalent to stable public item anchors;
- RFC 3662 says `doc.parts` is unstable and not compatible across disparate rustdoc versions;
- Cargo/rustdoc keep target and target-kind selection explicit.

That means a worthy crate here should no longer stop at “we know what URL to cite.”
It should export a reviewable answer for **what conceptual item the citation is about**.

## 1. `item-witness.manifest.json`

Purpose:
- bind exported excerpts and claims to a reviewable notion of item identity;
- keep blob-local opaque IDs, human-reviewable item keys, and rendered citation routes visibly separate.

Suggested fields:
- `crate`
- `profile`
- `witnesses[]`
  - `id`
  - `source_material_ids[]`
  - `excerpt_ids[]`
  - `claim_ids[]`
  - `resolved_version`
  - `target`
  - `item_path`
  - `kind`
  - `identity_basis` (`path_kind_target_span`, `path_kind_target`, `path_kind`, `manual_review_required`)
  - `rustdoc_json_item_id`
  - `rustdoc_json_scope` (`blob_local_opaque_id`)
  - `source_span`
    - `filename`
    - `begin_line`
    - `begin_col`
    - `end_line`
    - `end_col`
  - `citation_locator_ids[]`
  - `fallback_locator_ids[]`
  - `notes[]`
- `notes[]`

Questions it answers:
- What exact crate/version/target/path/kind/source-span combination was this claim attached to?
- Which raw rustdoc JSON item ID was observed, and what are its scope limits?
- Which locator receipts point at review surfaces for this witness?
- Is this witness strong enough to survive a route change without pretending to be a stable universal ID?

## 2. `identity-fidelity.report.json`

Purpose:
- classify how confidently a witness or witness-pair can be treated as “the same item” across versions, targets, or builds.

Suggested fields:
- `crate`
- `profile`
- `cases[]`
  - `case`
  - `witness_ids[]`
  - `fidelity_level` (`exact_same_version_target`, `exact_same_version_path_kind`, `cross_version_rechecked`, `approximate`, `manual_review_required`)
  - `safe_reuse_scope` (`same_blob_only`, `same_version_target`, `same_version`, `cross_version_with_recheck`, `none`)
  - `risks[]`
  - `notes[]`
- `global_limitations[]`

Questions it answers:
- Can this witness be reused only inside one blob, or across a pinned release on the same target?
- Was a cross-version identity claim rechecked using path/kind/span instead of blindly reusing an opaque ID?
- Which witness pair is only approximate and should force manual review?

## Product stance

The crate should remain bundle-first and review-first.
Do **not** spend the next serious implementation pass on:
- answer generation,
- embeddings,
- hosted docs search,
- HTML anchor mining as a fake identity source,
- or reuse of rustdoc JSON item IDs across bundles as if they were stable public identifiers.

First freeze the boring witness contract.

## Good proving grounds

1. a crate where one public item has a straightforward same-version, same-target witness;
2. a version bump where the item stays conceptually the same but the route or version selector changes;
3. a target-specific item where default-target routing would misrepresent what was reviewed;
4. a doctor case where two bundles reuse the same rustdoc JSON item ID without shared blob scope and must be rejected.

## Doctor checks worth adding early

- warn when a claim trace or citation locator has no witness edge;
- warn when a witness relies only on `rustdoc_json_item_id` and claims cross-version durability;
- warn when target-sensitive witnesses point only at default-target locators;
- warn when `identity_basis = path_kind` is exported as if it were same-target same-span certainty;
- warn when a pack says “same item” but only proves “same package page.”

## Worked boundary examples to keep straight

- **The same docs.rs route** is not automatically the same conceptual item if version or target changed.
- **The same rustdoc JSON item ID** is not a cross-bundle identity proof.
- **A source span** is useful witness material, but it is still only one part of a witness.
- **A package page or README heading** can support package-level review without proving item identity.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rfcs/2963-rustdoc-json.html
- https://doc.rust-lang.org/rustdoc/unstable-features.html
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/redirections
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://doc.rust-lang.org/cargo/commands/cargo-rustdoc.html
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://rust-lang.github.io/rfcs/3662-mergeable-rustdoc-cross-crate-info.html
