# Cfg Availability Ledger Kit — usability boundaries (2026-03-20)

This note exists to keep **P-0451 Cfg Availability Ledger Kit** from flattening several related but non-identical truths into one fake “available API” verdict.

## Main rule

Do **not** collapse these into one claim:

1. **docs-visible** — the item appears in generated documentation;
2. **same-crate-compilable** — the defining crate can still compile the item in a selected slice;
3. **doctest-usable** — rustdoc-extracted examples can compile/use the item in the doctest path;
4. **downstream-compile-usable** — another crate can compile against the public path in a normal dependency slice;
5. **default docs surface** — what docs.rs shows by default when maintainers left target posture implicit.

These truths are adjacent, but they are not interchangeable.

## Why this boundary matters now

Current Rust substrate makes the distinctions explicit enough that the archive should stop treating them as folklore:

- RFC 3631 is about rendered availability markers, not duplicating every inactive configuration in docs.
- rustdoc’s `#[cfg(doc)]` guidance says items can appear in docs even though dependent crates cannot use them the same way.
- rustdoc also says `cfg(doc)` is not passed to doctests.
- Cargo doctests are their own rustdoc-driven compile/run path.
- docs.rs changed its default target list in October 2025, which means the default visible surface can drift even when project support policy did not.
- docs.rs rustdoc JSON is useful substrate, but hosted imports still carry `format_version` and environment caveats.

## Review objects that should stay first-class

### `usability-witness.receipt.json`

This artifact exists so one slice can say, explicitly:

- whether the item is docs-visible,
- whether the same crate compiles it in the chosen slice,
- whether doctests can use it,
- whether downstream users can compile against it,
- and what kind of evidence actually backs each claim.

This should prevent a docs-oriented witness from silently masquerading as a downstream usability witness.

### `default-surface-drift.report.json`

This artifact exists so a project can say, explicitly:

- what the previous default visible surface was,
- what the current default visible surface is,
- whether the visible change came from docs.rs defaults or from project-declared metadata,
- and whether any new real support evidence exists.

This should prevent “the default docs surface widened” from silently becoming “the project newly supports this target.”

## Doctor warnings worth keeping separate

The first implementation should be able to distinguish warnings such as:

- `docs_visible_without_downstream_witness`
- `docs_visible_without_doctest_witness`
- `doctest_witness_not_equivalent_to_downstream_use`
- `docsrs_default_surface_drift_without_contract_change`
- `hosted_import_carries_format_or_environment_caveat`
- `manual_review_required`

## Non-goals for this boundary note

This note is **not** asking P-0451 to become:

- a whole-project support contract (that remains **P-0484**),
- a docs.rs parity / local reproduction bundle (**P-0472**),
- a generic docs coverage system,
- or a full arbitrary-`cfg` proof engine.

It is only insisting that **audience-specific usability truth** and **default-surface drift truth** stay reviewable.
