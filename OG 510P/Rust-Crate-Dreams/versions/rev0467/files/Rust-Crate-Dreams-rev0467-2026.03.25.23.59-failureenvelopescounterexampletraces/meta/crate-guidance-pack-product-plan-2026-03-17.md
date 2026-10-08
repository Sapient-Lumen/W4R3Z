# Crate guidance-pack product plan — 2026-03-17

This note exists to keep **P-0512 Crate Guidance Pack Kit** disciplined.
The archive already decided that the missing value is a **receiver-facing compile-time guidance contract** for crates whose users hit trait-bound errors, feature/runtime mismatches, proc-macro misuse, or unsupported cfg/target paths.
This pass answers a narrower question:

> If somebody actually started building **P-0512** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps crate authors publish one reviewable answer to:

- which failure families the crate officially recognizes,
- which parts of the guidance are **compiler-backed** versus **fixture-observed** versus **maintainer-authored advice**,
- which recovery recipe is the intended smallest good path,
- which anchors or URLs a user should follow next,
- how much of that recovery path was actually checked,
- and how the guidance surface changed between releases.

It should **not** become another diagnostic renderer, magical root-cause engine, hosted docs portal, or proc-macro diagnostics framework.
Those are adjacent imports, not the product.

## What the crate should provide other people

For downstream users, support engineers, release reviewers, and docs/tooling authors, the crate should provide:

1. **One compact guidance contract** instead of scattered compiler notes, stale README snippets, and issue-thread folklore.
2. **An authority distinction** that can say `compiler_backed`, `fixture_observed`, `docs_backed`, `advisory_only`, or `manual_review_required`.
3. **A smallest-working recovery recipe** so “what should I do next?” has a real artifact rather than a prose paragraph.
4. **A recovery-origin receipt** so users can tell whether advice came from `#[diagnostic]` attributes, compile-fail fixtures, rustdoc examples, `miette` diagnostic codes/URLs, or maintainer-authored anchors.
5. **A recipe-fidelity report** that says how much of the advertised recovery path was actually checked across features, editions, targets, proc-macro boundaries, and docs examples.
6. **A short summary** suitable for docs, issue templates, or release notes.
7. **A diffable support surface** so releases can be reviewed for guidance regressions, not just API drift.

For maintainers, the crate should provide:

1. a small pack file that is cheap to review,
2. a conservative `manual_review_required` escape hatch instead of fake certainty,
3. a way to import compile-fail fixtures and docs anchors without pretending they all prove the same thing,
4. one place to keep diagnostic hooks, recipes, and docs references aligned,
5. and a CI-visible warning when guidance drifts while code still compiles.

## Recommended `0.1` command surface

### `cargo guidance-pack init`
Create a starter `guidance-pack.toml` by importing obvious candidates from:

- `#[diagnostic::on_unimplemented]` and `#[diagnostic::do_not_recommend]`,
- compile-fail fixtures (`trybuild`, `ui_test`, or equivalent),
- rustdoc `compile_fail` and runnable examples,
- `miette` diagnostic codes/help/URLs when present,
- proc-macro error surfaces and maintainer-authored docs anchors.

The generated pack should be incomplete on purpose.
Anything uncertain should become `manual_review_required` rather than guessed.

### `cargo guidance-pack capture`
Emit one normalized guidance bundle from declared policy plus imported facts.
This should capture:

- failure family,
- guidance authority class,
- observed diagnostics or codes,
- recovery recipes and docs anchors,
- origin of each recovery hint,
- and checked recipe fidelity.

`capture` must work even when a crate has only advisory docs and no compiler-backed hooks.

### `cargo guidance-pack check`
Run the local validation pass:

- do declared failure families parse,
- do referenced diagnostic attributes still exist,
- do fixture outputs still expose the expected guidance,
- do docs/example anchors still resolve,
- do recipes still compile or build under the claimed lane,
- and which parts remain manual-review-only?

### `cargo guidance-pack doctor`
Render human-facing warnings for suspicious situations such as:

- `compile_fail_only_no_message_assertion`
- `do_not_recommend_without_smallest_good_path`
- `proc_macro_panics_instead_of_guidance`
- `docs_anchor_present_but_recipe_missing`
- `recovery_recipe_feature_or_target_drift`
- `manual_review_required`

`doctor` should be a human-first renderer over explicit artifacts, not a magical compiler-introspection engine.

### `cargo guidance-pack summary`
Render a short receiver-facing note for docs or issue templates.
A good summary answers:

- what usually went wrong,
- which part of the guidance is exact versus advisory,
- what smallest path gets the user unstuck,
- and where manual review begins.

### `cargo guidance-pack diff <old> <new>`
Compare two receipts or packs and classify:

- `guidance_added`
- `guidance_removed`
- `guidance_authority_changed`
- `recovery_origin_changed`
- `recipe_changed`
- `recipe_fidelity_changed`
- `anchor_changed`
- `manual_review_boundary_changed`

### `cargo guidance-pack pack`
Emit one compact `.guidance-pack.zip` bundle for CI artifacts, docs portals, support bots, or pathfinder import.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `guidance_pack_model`
  - shared Rust types for packs, receipts, reports, summaries, and diffs
- `guidance_pack_import`
  - import logic for diagnostic attributes, compile-fail fixtures, rustdoc examples, `miette` metadata, and maintainer-authored docs anchors
- `guidance_pack_check`
  - policy validation, fixture checking, recipe validation, and doctor warnings
- `guidance_pack_render`
  - summary rendering, diff writing, markdown output, and zip bundle emission
- `cargo-guidance-pack`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `guidance_pack_trybuild`
- `guidance_pack_ui_test`
- `guidance_pack_rustdoc`
- `guidance_pack_miette`
- `guidance_pack_proc_macro_error`

## `0.1` artifact set

The archive already had the right center of gravity.
`0.1` should still revolve around:

- `guidance-pack.toml`
- `compile-guidance.receipt.json`
- `recovery-recipe.manifest.json`
- `guidance-check.report.json`
- `guidance-diff.report.json`
- `support-path.summary.md`

This pass adds three more important artifacts:

- `guidance-authority.policy.json` — what `compiler_backed`, `fixture_observed`, `docs_backed`, `advisory_only`, and `manual_review_required` mean and what minimum evidence each class expects.
- `recovery-origin.receipt.json` — where each recovery hint came from, such as diagnostic attributes, compile-fail stderr, rustdoc examples, `miette` codes/URLs, or maintainer-authored docs anchors.
- `recipe-fidelity.report.json` — how completely an advertised recovery lane was checked across features, editions, targets, proc-macro invocation shape, and docs/example parity.

Those files matter because guidance gets vague again if the archive only records that “some hint exists” but not:

- how trustworthy that hint is,
- where it came from,
- and how much of the advertised fix path was actually checked.

## Discovery order

A disciplined import order helps prevent fake certainty.

1. **Declared failure families and recovery recipes**
   - `guidance-pack.toml`
   - maintainer-authored smallest-good-path recipes
2. **Compiler-backed hooks**
   - `#[diagnostic::on_unimplemented]`
   - `#[diagnostic::do_not_recommend]`
3. **Fixture-observed evidence**
   - `trybuild`
   - `ui_test`
   - comparable UI/compile-fail harnesses
4. **Docs/example anchors**
   - rustdoc examples
   - rustdoc `compile_fail` examples
   - docs-site or README anchors explicitly named by the maintainer
5. **Diagnostic metadata adapters**
   - `miette` code/help/URL metadata
   - proc-macro guidance helpers
6. **Manual review zones**
   - feature-specific recipes
   - target-specific examples
   - proc-macro syntax migrations
   - advice whose truth depends on external runtimes or tools

The importer should prefer visible uncertainty over synthesis.

## Guidance-authority policy

The first implementation should treat **guidance authority** as a first-class review object and keep it separate from recipe quality.

### What should count as guidance authority in `0.1`

- `compiler_backed`
- `fixture_observed`
- `docs_backed`
- `advisory_only`
- `manual_review_required`

### What should *not* be encoded as guidance authority in `0.1`

- “the README once mentioned this fix”
- “a compile-fail doctest exists so the exact message is stable”
- “a proc-macro emits something roughly helpful on my machine”
- “there is a URL, therefore the recipe is correct”

The authority policy should be versioned and diffable.
If a maintainer cannot explain why a lane is `compiler_backed` rather than `fixture_observed` or `manual_review_required`, the lane should fall back conservatively.

## Recovery-origin receipts

The first implementation should treat **origin** as explicit provenance, not a comment string.

### Origins worth capturing in `0.1`

- diagnostic attributes on traits or impls
- compile-fail fixture stderr snapshots
- rustdoc example anchors or `compile_fail` docs
- `miette` diagnostic codes/help/URLs
- proc-macro guidance helpers or emitted `compile_error!`
- maintainer-authored docs anchors

### Origins that should stay manual in `0.1`

- arbitrary issue comments
- unofficial blog posts or forum answers
- unstructured grep over external docs
- brittle stderr scraping without declared fixture ownership

## Recipe fidelity

The first implementation should treat **recipe fidelity** as the answer to “how much of the advertised fix path was actually checked?”

### Fidelity dimensions worth capturing in `0.1`

- feature coverage
- edition coverage
- target/cfg coverage
- proc-macro invocation shape coverage
- rustdoc/example parity
- manual steps remaining

### What should *not* count as full fidelity in `0.1`

- a rustdoc `compile_fail` example that proves only that code fails
- a fixture that matches stderr but never validates the corrected path
- a good recipe that was checked only on the default feature set when the guidance claims a wider lane

## Proving-ground archetypes

A worthy first implementation should prove itself against at least five archetypes:

1. **Trait-heavy library**
   - `on_unimplemented` improves the error, while `do_not_recommend` hides a misleading blanket impl.
2. **Feature-rich async/framework crate**
   - failure guidance explains which runtime/feature lane is supported and validates the smallest working configuration.
3. **Proc-macro crate**
   - misuse should emit something better than a panic and point to a corrected invocation shape.
4. **Unsupported-target crate**
   - docs and fixtures should agree about when a fallback path exists versus when manual review begins.
5. **Docs-rich library**
   - rustdoc examples should stay aligned with diagnostic codes, URLs, and fixture-checked recovery paths.

## Three fixture families to prioritize

1. `compile_fail_doctest_catches_failure_but_not_message_drift`
   - proves why rustdoc `compile_fail` is useful but insufficient for exact guidance fidelity.
2. `do_not_recommend_hides_blanket_impl_but_recipe_missing`
   - proves that suppressing a bad recommendation still needs a smallest-good-path artifact.
3. `proc_macro_diagnostic_url_points_to_stale_syntax`
   - proves that a helpful code/URL pair can still drift away from the supported invocation shape.

## Non-goals for `0.1`

- not a general-purpose terminal renderer,
- not a hosted docs or tutorial platform,
- not a full support bot,
- not a proc-macro diagnostics replacement layer,
- not a root-cause engine for runtime failures,
- and not a substitute for pathfinder or capability-contract lanes.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rfcs/3368-diagnostic-attribute-namespace.html
- https://doc.rust-lang.org/reference/attributes/diagnostics.html
- https://doc.rust-lang.org/beta/releases.html
- https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html
- https://docs.rs/trybuild/latest/trybuild/
- https://docs.rs/ui_test/latest/ui_test/
- https://docs.rs/miette/latest/miette/trait.Diagnostic.html
- https://docs.rs/proc-macro-error2/latest/proc_macro_error2/
