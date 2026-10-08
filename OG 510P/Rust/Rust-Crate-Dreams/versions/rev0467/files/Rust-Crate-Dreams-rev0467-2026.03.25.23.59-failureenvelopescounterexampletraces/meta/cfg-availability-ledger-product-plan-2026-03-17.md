# Cfg Availability Ledger Kit — implementation-ready product plan (2026-03-17)

This note turns **P-0451 Cfg Availability Ledger Kit** from a good idea into a more buildable `0.1` crate.

The central judgment of this pass is that the missing value is **not** another rustdoc renderer, another raw rustdoc-JSON helper, or another general SemVer checker.
The missing value is a **maintainer-facing artifact layer** that makes conditional API availability reviewable across:

- targets,
- feature sets,
- docs-only visibility shims,
- docs.rs-only assumptions,
- and release-to-release drift.

The substrate is now strong enough that the remaining gap is coordination:

- rustdoc can already surface conditional availability markers with `#[doc(cfg)]` and `#[doc(auto_cfg)]`, and `auto_cfg` is enabled by default at the crate level;
- rustdoc also exposes `#[cfg(doc)]`, which can deliberately make items visible in docs even though they are not generally usable, and that `cfg` is **not** passed to doctests;
- docs.rs documents that `#[cfg(docsrs)]` only applies to the final crate being documented, not dependencies, and that its local-preflight tooling is only an approximation of the hosted environment;
- docs.rs hosts rustdoc JSON but warns that the JSON may have been built with an older rustdoc and that consumers need to look at `format_version`;
- Cargo now passes `--check-cfg` to both rustc and rustdoc invocations;
- and Cargo’s feature rules still make availability drift easy to misread because features are additive, unification uses the union, and moving public code behind a feature is usually not minor-release-safe.

That means the sharper `0.1` crate is a **ledger / receipt / diff / doctor** tool above existing substrate.

## What the crate should provide other people

For release reviewers, downstream maintainers, docs maintainers, and semver reviewers, the crate should provide:

1. **One compact availability contract** instead of prose split across source `cfg`s, rustdoc markers, docs.rs metadata, feature tables, and issue replies.
2. **A machine-readable matrix** for item-level availability over named target and feature slices.
3. **Origin receipts** that explain whether visibility came from real compile-time `cfg`, inherited re-export conditions, docs-only markers, docs.rs config, or inference.
4. **A fidelity report** that distinguishes observed slices from inferred or docs-only approximated slices.
5. **A human summary** suitable for changelogs, migration notes, and support replies.
6. **A release diff** that makes hidden conditional-API drift loud.
7. **A conservative doctor** that surfaces suspicious docs-vs-usable mismatches without pretending to solve arbitrary `cfg` logic.

For maintainers, the crate should provide:

1. one small pack file that is cheap to review,
2. explicit `manual_review_required` states instead of fake certainty,
3. a way to import rustdoc JSON / Cargo feature data / docs.rs assumptions instead of replacing them,
4. a stable schema for CI and release review,
5. and a CI gate for “this release silently changed who can use which public item”.

## Recommended `0.1` command surface

### `cargo availability-ledger init`
Create a starter `availability-ledger.toml` by importing:

- target slices from maintainer-declared profiles,
- feature slices from Cargo metadata / explicit maintainer lists,
- docs.rs metadata where present,
- and optional docs-only assumptions (`cfg(doc)`, `cfg(docsrs)`, custom rustc cfgs) when the maintainer chooses to model them.

Anything uncertain should be emitted as `manual_review_required`, not guessed.

### `cargo availability-ledger capture`
Capture one normalized ledger bundle from selected target/feature/doc profiles.
The result should include:

- item identities,
- availability class,
- origin receipts,
- fidelity levels,
- rustdoc JSON provenance,
- docs.rs / custom-cfg assumptions where imported,
- and per-slice notes.

### `cargo availability-ledger check`
Run the local validation pass:

- do declared slices exist,
- do item identifiers resolve,
- do availability classes parse,
- do origin receipts match allowed origin kinds,
- do docs-only or docs.rs-only sources appear where expected,
- is the rustdoc JSON format version recorded,
- and which cells still require manual review?

### `cargo availability-ledger doctor`
Render human-facing warnings for suspicious situations such as:

- `docs_visible_but_not_usable`
- `cfg_doc_relies_on_non_doctest_visibility`
- `docsrs_only_final_crate_scope_mismatch`
- `custom_cfg_without_expected_check_cfg`
- `item_moved_behind_feature`
- `feature_matrix_only_inferred`
- `manual_review_required`

`doctor` should be conservative and explain *why* a cell looks risky.

### `cargo availability-ledger summary`
Render a short receiver-facing summary answering:

- which public items require which features or targets,
- which visibility claims are docs-only,
- which slices are backed by direct evidence versus inference,
- and which release-to-release changes are likely SemVer-relevant.

### `cargo availability-ledger diff <old> <new>`
Compare two ledgers and classify:

- `item_added`
- `item_removed`
- `newly_available`
- `newly_unavailable`
- `availability_class_changed`
- `origin_changed`
- `fidelity_changed`
- `docs_only_drift`
- `feature_gate_changed`
- `target_gate_changed`
- `manual_review_required`

### `cargo availability-ledger pack`
Emit one compact `.availabilityledger.zip` bundle for CI artifacts, release review, docs review, or downstream support.

## Recommended crate/workspace split

A good starting shape would be:

- `availability_ledger_model`
  - shared Rust types for packs, matrices, receipts, reports, and diffs
- `availability_ledger_capture`
  - rustdoc JSON import, Cargo feature/profile import, docs.rs metadata import
- `availability_ledger_check`
  - policy validation, doctor warnings, origin/fidelity checks
- `availability_ledger_pack`
  - markdown rendering, diff writing, zip bundle emission
- `cargo-availability-ledger`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional at first:

- `availability_ledger_docsrs`
- `availability_ledger_public_api`
- `availability_ledger_rustdoc_json`

## `0.1` artifact set

The proposal already had the right center of gravity.
`0.1` should still revolve around:

- `availability-ledger.toml`
- `availability.matrix.json`
- `availability.diff.json`
- `availability.receipt.json`
- `availability.summary.md`

This pass adds three more important artifacts:

- `availability-class.policy.json` — what classes like `stable_public`, `requires_feature`, `requires_target`, `docs_visible_only`, `docsrs_assumed_only`, `inferred_only`, and `manual_review_required` mean.
- `availability-origin.receipt.json` — whether an item’s visibility came from direct `cfg`, inherited re-export `cfg`, `#[doc(cfg)]`, `#[doc(auto_cfg)]`, `#[cfg(doc)]`, docs.rs config, build-script custom cfg, or other inference.
- `matrix-fidelity.report.json` — which matrix cells were directly observed, docs-only observed, imported from hosted JSON, inferred from declared rules, or left uncertain.

Those artifacts matter because the lane stays vague if it records *that* an item is shown without recording:

- what kind of availability claim is being made,
- where that claim came from,
- and how much of the matrix is actually backed by observed evidence.

## Availability-class policy

The first implementation should keep **availability class** separate from origin and separate from fidelity.

### Suggested classes for `0.1`

- `stable_public`
- `requires_feature`
- `requires_target`
- `requires_feature_and_target`
- `docs_visible_only`
- `docsrs_assumed_only`
- `inferred_only`
- `hidden_internal`
- `manual_review_required`
- `unknown`

### What should not count as an availability class in `0.1`

- “appears in the docs page somewhere”
- “exists in one rustdoc JSON file”
- “a docs.rs badge says the target builds”
- “the compiler accepted one custom cfg”

## Origin policy

The first implementation should treat **origin** as a first-class review object.
A downstream user often needs to know not just *that* an item is visible, but *why*.

### Origin kinds worth distinguishing in `0.1`

- `direct_cfg`
- `inherited_cfg`
- `doc_cfg_override`
- `doc_auto_cfg`
- `cfg_doc_visibility`
- `docsrs_cfg`
- `docsrs_rustc_arg`
- `build_script_custom_cfg`
- `inferred_from_profile`
- `manual_review_required`

This matters because `#[cfg(doc)]`, `#[doc(cfg)]`, `#[doc(auto_cfg)]`, and docs.rs config can all make documentation look more available than a normal build slice.

## Fidelity policy

The first implementation should keep **matrix fidelity** explicit.
A ledger should be able to say whether a cell is:

- directly observed from a selected rustdoc/feature/target run,
- observed only in a documentation-oriented slice,
- imported from hosted docs.rs artifacts,
- inferred from rules and metadata,
- or not verified enough to trust.

### Suggested fidelity classes

- `direct_observation`
- `docs_only_observation`
- `hosted_import`
- `rule_inference`
- `mixed`
- `manual_review_required`

## Discovery order

1. maintainer-declared slices and classes
2. rustdoc JSON imports
3. Cargo feature/profile data
4. docs.rs metadata and hosted imports
5. origin classification
6. fidelity classification
7. doctor warnings and release diff

The importer should prefer visible uncertainty over synthesis.

## Recommended proving grounds

- feature-heavy libraries with optional-dependency indirection and re-exported APIs
- platform-heavy crates with `unix` / `windows` / `wasm32` slices
- crates using `#[cfg(doc)]` or `#[cfg(docsrs)]` to improve docs discoverability
- crates using custom cfgs supplied through build scripts or docs.rs metadata
- release-review workflows where a minor version quietly moved public code behind a feature

## Strong fixture families for `0.1`

1. **Docs-visible but not generally usable**
   - `#[cfg(doc)]` or `#[doc(cfg)]` makes an item appear in generated docs while dependent crates or doctests still cannot use it in the same way.
2. **docs.rs-only assumptions**
   - `#[cfg(docsrs)]` or docs.rs custom rustc args expose an API/documentation slice that is not a normal dependency slice.
3. **SemVer-sensitive feature drift**
   - a release moves a previously public item behind a feature or changes a feature gate in a way that is easy to miss in coarse API diffing.

## Non-goals for `0.1`

- solving arbitrary `cfg` logic with full proof strength,
- replacing rustdoc rendering,
- emulating every hosted docs.rs behavior,
- or becoming a general public-API / SemVer / MSRV platform.

## Source anchors

- https://rust-lang.github.io/rust-project-goals/2025h2/rustdoc-doc-cfg.html
- https://rust-lang.github.io/rfcs/3631-rustdoc-cfgs-handling.html
- https://doc.rust-lang.org/rustdoc/unstable-features.html
- https://doc.rust-lang.org/rustdoc/advanced-features.html
- https://docs.rs/about/builds
- https://docs.rs/about/rustdoc-json
- https://doc.rust-lang.org/cargo/reference/features.html
- https://doc.rust-lang.org/cargo/reference/build-scripts.html
- https://doc.rust-lang.org/cargo/CHANGELOG.html


## Deepening addendum — slice witness, gate normalization, and re-export lineage

The earlier product plan still needed three more review objects to prevent the first implementation from overstating availability.

### `slice-witness.receipt.json`
This artifact records the exact slice that was observed:

- target triple,
- selected features,
- docs profile (`normal`, `cfg_doc`, `docsrs`),
- custom cfgs,
- witness kind (`direct_rustdoc_json`, `docs_only_rustdoc`, `docsrs_hosted_import`, `rule_inference`),
- and the rustdoc JSON format provenance when applicable.

The important point is that a hosted docs.rs import must not silently masquerade as a local usability witness.

### `gate-normalization.report.json`
This artifact records how raw gate expressions were normalized into the human-facing summary that people actually see.

The first implementation should treat these normalization cases as distinct:

- identity
- `doc(auto_cfg)` simplification
- `doc(cfg)` override
- `cfg(doc)`-added visibility
- docs.rs overlay
- manual review required

This matters because a short label like `feature = "tls"` may still hide a real implementation gate such as `all(feature = "tls", any(unix, windows))`.

### `reexport-lineage.report.json`
This artifact records whether an exported public path inherits its effective gate from another path.

The first implementation should distinguish:

- direct definition,
- `pub use`,
- inherited cfg,
- overridden cfg,
- and manual-review-required lineage.

This matters because top-level ergonomic re-exports often look unconditional even when the defining item is target-gated.

## Doctor warnings worth adding next to the earlier set

The first implementation should be able to warn about:

- `normalized_gate_not_equivalent_to_downstream_use`
- `docsrs_final_crate_scope_mismatch`
- `reexport_lineage_hides_effective_gate`
- `hosted_import_without_local_slice_witness`

## Fixture families that now matter more

- `doc_auto_cfg_hide_simplifies_real_gate_surface/`
- `docsrs_cfg_final_crate_scope_hides_dependency_slice_gap/`
- `reexported_item_inherits_hidden_target_gate/`

## Deepening addendum — usability witness and default-surface drift

The earlier product plan still needed two more review objects to prevent docs-facing visibility from masquerading as ordinary use.

### `usability-witness.receipt.json`
This artifact records, for a selected item/slice:

- whether the item is docs-visible,
- whether the same crate compiles it in that slice,
- whether doctests can use it,
- whether downstream users can compile against it,
- and what evidence basis supports each claim.

The important point is that a docs-only slice or hosted docs.rs witness must not silently masquerade as a downstream usability witness.

### `default-surface-drift.report.json`
This artifact records when the *default visible surface* changed because docs.rs defaults or other hosted assumptions moved.

The first implementation should distinguish at least:

- `docsrs_default_targets_changed`
- `project_metadata_changed`
- `mixed`
- `manual_review_required`

This matters because the October 2025 docs.rs default-target change proved that the first surface a reader sees can move without any corresponding support-contract change.

## Doctor warnings worth adding next to the earlier set

The first implementation should be able to warn about:

- `docs_visible_without_downstream_witness`
- `docs_visible_without_doctest_witness`
- `doctest_witness_not_equivalent_to_downstream_use`
- `docsrs_default_surface_drift_without_contract_change`
- `hosted_import_carries_format_or_environment_caveat`

## Fixture families that now matter more

- `cfg_doc_visible_item_needs_separate_doctest_and_downstream_usability_witness/`
- `docsrs_default_target_shift_changes_default_docs_surface_without_new_support/`
