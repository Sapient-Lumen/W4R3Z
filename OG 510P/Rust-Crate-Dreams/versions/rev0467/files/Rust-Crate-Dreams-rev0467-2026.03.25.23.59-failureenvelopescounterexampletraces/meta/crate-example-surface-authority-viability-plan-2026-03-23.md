# Crate Example Surface Pack Kit — authority/viability plan (2026-03-23)

This note sharpens **P-0524** around the hardest remaining receiver-facing questions:

1. which quickstart is officially blessed,
2. which entrypoints are viable in each command/feature/env lane,
3. and which surfaces are only visible in docs or docs.rs.

## Main judgment

The missing value is now best framed as an **official-start authority + entrypoint-viability kit**.

A good `0.1` should make three support questions boring:

- **Authority**: who or what blessed this path as the official quickstart?
- **Viability**: can this path build/run/test in the declared lane, or is it skipped/hidden/manual-review-only?
- **Visibility**: what appears in rustdoc/docs.rs, under what metadata/flags, and what does that *not* prove?

## What the crate should provide other people

For downstream adopters it should provide:

1. **One official start per adoption scenario** instead of README folklore.
2. **Authority receipts** showing where officiality came from.
3. **Entrypoint viability matrices** for README snippets, rustdoc examples, `examples/` targets, guide commands, and docs.rs-visible surfaces.
4. **Hosted visibility reports** that distinguish docs.rs/rustdoc appearance from local runnable proof.
5. **Witness joins** that keep success proof attached to the exact viable lane.
6. **Release diffs** that make “the getting-started path disappeared or moved behind features” obvious.
7. **Compact review bundles** that other tools or humans can reopen later.

For maintainers it should provide:

1. conservative imports from README/rustdoc/examples/docs.rs metadata,
2. cheap-to-review receipts instead of a giant portal,
3. `manual_review_required` as a normal outcome,
4. and a small receiver-facing summary that says where users should start.

## Recommended first-class artifacts

### `quickstart-authority.receipt.json`
Records the source of officiality for each declared start path.
Typical fields:

- `quickstart_id`
- `authority_kind` (`maintainer_pack`, `readme_anchor`, `crate_docs_landing`, `guide_anchor`, `release_note`, `manual_review_required`)
- `source_ref`
- `confidence`
- `conflicts`

### `entrypoint-viability.matrix.json`
Records whether each entrypoint works in named lanes.
Typical axes:

- entrypoint kind: `readme_snippet`, `rustdoc_example`, `example_target`, `guide_command`, `docsrs_surface`
- command family: `cargo_doc`, `cargo_test_doc`, `cargo_build_example`, `cargo_run_example`, `hosted_docsrs`
- lane: feature set, env class, target class, credential class
- result: `viable`, `visible_only`, `skipped_required_features`, `blocked_by_env`, `manual_review_required`

### `visibility-surface.report.json`
Captures what a hosted/local docs surface shows and why.
Typical fields:

- `surface_kind`
- `target_basis`
- `feature_basis`
- `scrape_examples_mode`
- `sandbox_constraints`
- `visibility_without_local_viability`
- `notes`

## Recommended `0.1` commands

### `cargo example-surface authority`
Derive or validate quickstart-authority receipts from README/docs/guide anchors and explicit pack declarations.

### `cargo example-surface viability`
Check entrypoint viability across named lanes, producing a matrix that distinguishes build-only, run-capable, skipped, and hosted-visible states.

### `cargo example-surface visibility`
Render hosted/local visibility truth from rustdoc/docs.rs-related inputs without claiming runnable success.

### `cargo example-surface bundle`
Emit one small portable archive with authority, viability, visibility, witness, and summary artifacts.

## 0.1 boundaries

A good `0.1` should:

- keep authority, viability, visibility, and witness separate;
- start with explicit lanes rather than global “works” claims;
- import docs.rs metadata and scrape-examples state conservatively;
- and treat missing or conflicting authority as normal.

A bad `0.1` would:

- claim docs.rs visibility proves local runnable success,
- guess that the most prominent example is the official quickstart,
- flatten `cargo test`, `cargo doc`, `cargo run --example`, and docs.rs into one support result,
- or become a generic tutorial generator.
