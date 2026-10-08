# Crate Example Surface Pack Kit — product plan (2026-03-17)

This note sharpens **P-0524 Crate Example Surface Pack Kit** into an implementation-ready `0.1` shape.

## Main judgment

The missing value is still **not** another docs portal, another tutorial CMS, another snapshot harness, another transcript renderer, or another template generator.
The sharper missing layer is a **crate-authored first-success contract** that makes three questions reviewable:

1. **Where did this quickstart’s prerequisite story come from?**
2. **What evidence actually witnessed success?**
3. **Which adoption scenarios have a trustworthy official start at all?**

That layer sits above today’s substrate:

- Rust’s vision-doc work calls for more supportive interfaces from crates.
- The 2025 survey says docs remain the preferred canonical reference and studying the code remains the next most important learning surface.
- The API Guidelines say example code is often copied verbatim by users.
- Cargo gives `examples/` first-class target status and compiles them under `cargo test` by default.
- Rustdoc scraped examples can link `examples/` back into docs, but remain unstable.
- docs.rs metadata and build constraints can materially change what readers see.
- `trycmd`, `term-transcript`, `mdBook`, and `cargo-generate` each cover a useful adjacent slice without publishing an official quickstart contract.

## Product shape

Keep `0.1` compact, boring, and review-first.
The first release should revolve around:

- one pack file,
- one discovery/import pass,
- one local check pass,
- one doctor pass for suspicious first-success claims,
- one short summary renderer,
- one diff path,
- one compact bundle export,
- and three review objects that had still been too implicit: **prerequisite origin**, **success witness**, and **scenario coverage**.

## What the crate should provide other people

For downstream users, the crate should provide:

1. **A smallest official quickstart per scenario** rather than an undifferentiated example list.
2. **Prerequisite provenance** so required features, credentials, services, boards, browsers, docs.rs metadata, or guide-specific assumptions are not treated as magic.
3. **Success witnesses** so quickstarts come with some explicit proof of life rather than “README says this should work.”
4. **Scenario-coverage truth** so crates can honestly say which adoption shapes have an official first-success path and which do not.
5. **Docs/example linkage truth** so README, rustdoc, guides, and `examples/` stop drifting independently.
6. **Normalization rules for dynamic output** so temp paths, ports, timestamps, and IDs do not make official starts unverifiable.
7. **Release diffs** so maintainers and downstream users can see when the official quickstart got harder, moved, or vanished.
8. **A short human summary** that can be pasted into docs, release review, or support threads.

For maintainers, the crate should provide:

1. a compact pack file that is cheap to review,
2. receipts/reports rather than a giant generated site,
3. adapter-first imports from existing docs/example/test substrate,
4. a conservative `manual_review_required` escape hatch,
5. and a release-review diff that makes first-success drift loud.

## Recommended `0.1` command surface

### `cargo example-surface init`
Create a starter `example-surface-pack.toml` by importing obvious candidates from:

- `README*`,
- rustdoc examples,
- `examples/`,
- optional guide roots,
- and docs.rs metadata when present.

The generated pack should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` instead of guessed.

### `cargo example-surface check`
Run the local validation pass:

- does each declared entrypoint still exist,
- do support levels and environment classes parse,
- do declared docs anchors resolve,
- do quickstarts build/run as promised where safe,
- do prerequisite-origin receipts stay consistent with current sources,
- do success witnesses still fit the declared success signal,
- do normalization rules explain unstable output,
- and which entries remain manual-review-only?

### `cargo example-surface doctor`
Explain why a quickstart is not yet trustworthy enough to publish as official.
Typical outputs should include:

- `missing_success_witness`
- `hidden_prerequisite`
- `docs_linkage_stale`
- `scenario_without_official_path`
- `normalization_overreach`
- `manual_review_required`

### `cargo example-surface summary`
Render a short receiver-facing onboarding summary.
This should be boring enough to paste into crate docs or release notes.

### `cargo example-surface diff <old> <new>`
Compare two receipts/packs and classify:

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
Emit one compact bundle for CI artifacts, release review, or downstream support threads.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `example_surface_model`
  - shared Rust types for pack files, receipts, reports, diffs, and normalization profiles
- `example_surface_discovery`
  - import logic for README/rustdoc/`examples/`/guide/docs.rs metadata candidates
- `example_surface_check`
  - linkage checks, prerequisite-origin checking, local command execution, success-witness capture
- `example_surface_pack`
  - report writing, markdown summary rendering, diffing, bundle emission
- `cargo-example-surface`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core format is trusted:

- `example_surface_trycmd`
- `example_surface_trybuild`
- `example_surface_term_transcript`
- `example_surface_docsrs`
- `example_surface_mdbook`

## `0.1` artifact set

`0.1` should revolve around these files:

- `example-surface-pack.toml`
- `example-catalog.receipt.json`
- `quickstart-path.manifest.json`
- `adoption-scenario.manifest.json`
- `example-environment.report.json`
- `prerequisite-origin.receipt.json`
- `success-witness.receipt.json`
- `scenario-coverage.report.json`
- `docs-example-linkage.report.json`
- `example-output.report.json`
- `example-support-check.report.json`
- `example-normalization.profile.json`
- `example-surface-diff.report.json`
- `example-summary.md`

The center of gravity is now clearer than before:

- **prerequisite-origin** keeps feature flags, credentials, guide-only steps, and docs.rs metadata from being treated as folklore,
- **success-witness** keeps “works on my machine” from masquerading as a checked official path,
- and **scenario-coverage** keeps a crate with many examples from being mistaken for a crate with an honest first-success path in each important adoption shape.

## Discovery order

A disciplined import order helps prevent accidental platform creep.

1. **README / crate-level docs** — likely user starting point.
2. **Rustdoc examples** — item-level examples and doctest-friendly snippets.
3. **`examples/` targets** — Cargo-native example surface.
4. **Guide roots** — `guide/`, `book/`, `docs/`, or explicitly configured paths.
5. **docs.rs metadata** — features/build flags that change how docs and examples land.

The importer should prefer surfacing uncertainty over synthesizing false confidence.

## Recommended receipt classes

### Prerequisite origin classes

- `cargo_manifest`
- `package_metadata_docsrs`
- `readme_text`
- `rustdoc_text`
- `guide_text`
- `example_target_metadata`
- `adapter_fixture`
- `ci_observation`
- `maintainer_assertion`
- `manual_review_required`

### Success witness classes

- `compile_success`
- `normalized_stdout`
- `normalized_stderr`
- `generated_file_present`
- `http_exchange_observed`
- `rendered_doc_fragment`
- `board_or_device_observed`
- `maintainer_summary_only`
- `manual_review_required`

### Scenario coverage classes

- `official_quickstart_present`
- `reference_examples_only`
- `docs_only`
- `manual_review_required`
- `no_honest_path_yet`

## Normalization policy

The first implementation should keep normalization explicit and conservative.

### What should be normalizable in `0.1`

- absolute paths
- temp directories
- user/home directories
- ephemeral TCP ports
- timestamps
- UUID-like/random identifiers
- API tokens or credential-shaped strings

### What should *not* be normalized automatically

- semantic payload values that users may care about
- broad regex rewriting of arbitrary program output
- network responses that would hide real contract changes
- compiler diagnostics beyond clearly declared placeholders

If a maintainer must normalize too much to keep a quickstart green, that is evidence the path may not be a good official quickstart.

## Proving-ground archetypes

A worthy first implementation should prove itself against at least five archetypes:

1. **CLI crate**
   - README command snippets
   - normalized stdout/stderr witnesses
   - dynamic output normalization
2. **Async SDK / service client**
   - pure-local or loopback quickstart
   - credentialed real-service path clearly demoted or separated
   - prerequisite origin made explicit
3. **Embedded / `no_std` crate**
   - host-simulated versus board-only honesty
   - scenario coverage that may explicitly admit no host-first path
4. **Proc-macro crate**
   - compile-success starter path plus linked compile-fail companions
5. **Guide-heavy crate**
   - README + mdBook + rustdoc + `examples/` linkage

If `0.1` cannot survive those five, the vocabulary is still too narrow.

## Adoption staircase

### Stage 1 — import and annotate
- generate a starter pack
- let maintainers mark official quickstarts, prerequisite origins, and manual-review areas

### Stage 2 — local checks
- verify anchors, paths, and basic success witnesses
- keep environment classes explicit

### Stage 3 — scenario coverage
- identify where a crate has examples but lacks an official start for an important scenario

### Stage 4 — release diffs
- compare current release versus previous release
- make downgraded first-success support visible

### Stage 5 — optional ecosystem adapters
- import `trycmd`, rustdoc, docs.rs metadata, guide tooling, transcript tooling
- remain adapter-first, not replacement-first

## Good failure modes

Preferred failure behavior:

- unresolved guide linkage → `manual_review_required`
- credentialed example with no safe local mode → `scenario_without_official_path`
- dynamic output without normalization profile → `missing_success_witness`
- docs/example disagreement → explicit linkage failure
- example disappeared between releases → `quickstart_removed`
- prerequisite named only in prose with no origin receipt → `hidden_prerequisite`

## Non-goals for `0.1`

- not a replacement for rustdoc
- not a replacement for docs.rs
- not a replacement for `trycmd`, `trybuild`, or transcript tooling
- not a project template engine
- not a tutorial CMS
- not a hosted docs portal
- not a promise that every example can be executed in CI
