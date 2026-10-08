# Crate Example Surface Pack Kit — product plan (2026-03-19)

This note sharpens **P-0524 Crate Example Surface Pack Kit** into a more implementation-ready `0.1` shape.

## Main judgment

The missing value is still **not** another tutorial engine, another docs portal, another transcript renderer, another template generator, or another snapshot harness.

The sharper missing layer is a **crate-authored first-success contract** that makes seven review questions boring:

1. **Which quickstart is officially supported for each adoption scenario?**
2. **What environment class does that path really require?**
3. **Where did each prerequisite come from?**
4. **What success signal counts as proof of life?**
5. **Was that success actually witnessed or only summarized?**
6. **Do README, rustdoc, guide, and `examples/` surfaces still agree?**
7. **Did the first-success surface get harder across releases?**

That layer sits above real substrate that already exists:

- the Rust vision-doc work says crates need more **supportive interfaces**;
- the 2025 survey still says online docs and code are the main learning surfaces;
- the API Guidelines warn that users copy examples verbatim;
- Cargo gives `examples/` first-class target status and compiles them under `cargo test` by default;
- rustdoc can execute documentation examples and can scrape examples into docs with unstable support;
- docs.rs exposes metadata controls and a sandboxed build environment with blocked network access;
- `trycmd`, `term_transcript`, `mdBook`, and `cargo-generate` each cover useful adjacent slices.

So the gap is no longer “Rust needs examples.”
The gap is that maintainers still do not have **one reviewable first-success bundle**.

## Product shape

Keep `0.1` compact, boring, and review-first.

The center of gravity should be seven first-class review objects:

- **quickstart path**
- **environment class**
- **prerequisite origin**
- **success witness**
- **docs/example linkage**
- **scenario coverage**
- **normalization boundary**

Everything else in `0.1` should help author, check, diff, or summarize those objects.

## What the crate should provide other people

For downstream users, this crate should provide:

1. **A smallest official quickstart per scenario** instead of a flat pile of examples.
2. **Environment honesty** so local-only, loopback, credentialed, browser, and board/device paths stay distinct.
3. **Prerequisite lineage** so hidden features, docs.rs metadata, guide-only assumptions, and CI-only setup do not masquerade as README facts.
4. **Witnessed first success** so “it worked” becomes inspectable.
5. **Docs/example linkage truth** so README snippets, rustdoc examples, guides, and `examples/` stop drifting independently.
6. **Scenario-coverage honesty** so a crate can say “we have reference examples, but no honest local quickstart yet.”
7. **Normalization boundaries** so maintainers can normalize temp paths or timestamps without hiding semantic drift.
8. **Release diffs** so getting-started regressions become reviewable.

For maintainers, the crate should provide:

1. one compact pack file,
2. conservative discovery/import,
3. check + doctor + diff workflows,
4. a clear `manual_review_required` escape hatch,
5. and one short summary suitable for docs, release notes, or support threads.

## Recommended `0.1` command surface

### `cargo example-surface init`
Generate a starter `example-surface-pack.toml` by importing likely entrypoints from:

- `README*`,
- crate-level rustdoc,
- `examples/`,
- optional guide roots,
- and docs.rs metadata.

Anything uncertain should land as `manual_review_required`, not as fake confidence.

### `cargo example-surface check`
Verify that:

- the declared entrypoint still exists,
- the environment class still matches the path,
- prerequisite-origin receipts still point at the right source,
- docs anchors still link to real examples,
- the success signal matches the observed witness,
- and normalization rules remain narrow enough to be trustworthy.

### `cargo example-surface doctor`
Render diagnosis such as:

- `missing_success_witness`
- `hidden_prerequisite`
- `docs_linkage_stale`
- `scenario_without_official_path`
- `normalization_overreach`
- `official_quickstart_not_smallest_path`
- `manual_review_required`

### `cargo example-surface summary`
Render a receiver-facing “start here” summary.

### `cargo example-surface diff <old> <new>`
Compare releases and classify:

- `quickstart_added`
- `quickstart_removed`
- `prerequisite_changed`
- `success_witness_changed`
- `scenario_coverage_changed`
- `docs_linkage_changed`
- `example_output_changed`
- `normalization_changed`
- `support_level_changed`
- `manual_review_required`

### `cargo example-surface pack`
Emit one compact support bundle for CI artifacts, release review, downstream evaluation, or support threads.

## Recommended crate/workspace split

A good first workspace shape would be:

- `example_surface_model`
  - shared Rust types for packs, receipts, reports, summaries, and diffs
- `example_surface_discovery`
  - README/rustdoc/`examples/`/guide/docs.rs import logic
- `example_surface_check`
  - linkage checks, local execution hooks, witness capture, normalization checks
- `example_surface_diff`
  - release-to-release surface comparisons
- `example_surface_pack`
  - bundle writing and Markdown summary rendering
- `cargo-example-surface`
  - user-facing cargo subcommand

Optional adapters should remain optional:

- `example_surface_trycmd`
- `example_surface_term_transcript`
- `example_surface_mdbook`
- `example_surface_docsrs`
- `example_surface_trybuild`

## `0.1` proving-ground fixtures

`0.1` should prove itself against at least these archetypes:

1. **CLI quickstart**
   - README command
   - normalized stdout/stderr witness
   - dynamic path/timestamp normalization boundary
2. **Async client**
   - loopback quickstart
   - credentialed real-service path clearly demoted
3. **Guide-heavy crate**
   - README + guide + `examples/` linkage drift detection
4. **Proc-macro crate**
   - compile-success starter path
   - explicit compile-fail adjacency
5. **Embedded / `no_std` crate**
   - host-simulated vs board-only truth
   - honest admission when there is no host-first path

## Non-goals

- Not a replacement for docs.rs, mdBook, rustdoc, or `cargo-generate`.
- Not a generic tutorial CMS.
- Not a generic snapshot-testing framework.
- Not a project generator.
- Not a crate selector; that remains **P-0509**.
- Not a downstream test-fixture crate; that remains **P-0523**.
- Not a docs.rs parity crate; that remains **P-0472**.

## Path to boring stability

1. Stabilize the artifact vocabulary before adding clever execution backends.
2. Keep normalization conservative and auditable.
3. Prefer local or loopback-first quickstarts where possible.
4. Make “no honest path yet” a respected output rather than a failure.
5. Treat docs/example drift as a support regression, not as harmless documentation debt.
