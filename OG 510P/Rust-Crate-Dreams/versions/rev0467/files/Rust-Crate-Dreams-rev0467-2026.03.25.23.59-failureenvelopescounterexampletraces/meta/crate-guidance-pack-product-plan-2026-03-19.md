# Crate guidance-pack product plan — 2026-03-19

This note refreshes **P-0512 Crate Guidance Pack Kit**.
The archive already decided that the missing value is a **receiver-facing compile-time / early-failure guidance contract** for crates whose users hit trait-bound errors, feature/runtime mismatches, proc-macro misuse, or unsupported cfg/target paths.
This pass answers a narrower question:

> If somebody actually started building **P-0512** this week, what should the next sharper `0.1` look like, what should it provide other people, and what crucial distinctions must not be flattened?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps crate authors publish one reviewable answer to:

- which failure families the crate officially recognizes,
- which parts of the guidance are **compiler-backed**, **snapshot-backed**, **code-level only**, or merely **failure-only**, 
- which channel the user-facing help actually arrives through,
- which smallest-good-path recipe was actually checked,
- which parts of the support story depend on toolchain, `rust-src`, nightly-only checks, or proc-macro panic avoidance,
- and how the guidance surface changed between releases.

It should **not** become another generic diagnostic renderer, another magical root-cause engine, another proc-macro framework, or another compile-fail runner.
Those are adjacent imports, not the product.

## What the crate should provide other people

For downstream users, support engineers, release reviewers, and docs/tooling authors, the crate should provide:

1. **One compact guidance contract** instead of scattered compiler notes, stale README snippets, and issue-thread folklore.
2. **A message-stability class** that can say `exact_snapshot`, `code_stable_shape_flexible`, `shape_stable`, `failure_only`, or `manual_review_required`.
3. **A guidance-channel receipt** that says whether the user will actually see help through compiler diagnostics, UI-stderr snapshots, proc-macro emission, `miette` metadata, docs anchors, or a mixed lane.
4. **A smallest-working recovery recipe** so “what should I do next?” has a real artifact rather than a prose paragraph.
5. **A recovery-origin receipt** so users can tell whether advice came from diagnostic attributes, compile-fail fixtures, rustdoc examples, `miette` diagnostic codes/help/URLs, or maintainer-authored anchors.
6. **A recipe-fidelity report** that says how much of the advertised recovery path was actually checked across features, editions, targets, proc-macro boundaries, and docs examples.
7. **An environment-sensitivity report** that records where `rust-src`, nightly-only doctest error-code checks, target differences, or proc-macro panic behavior still change what users see.
8. **A short summary** suitable for docs, issue templates, or release notes.
9. **A diffable support surface** so releases can be reviewed for guidance regressions, not just API drift.

For maintainers, the crate should provide:

1. a small pack file that is cheap to review,
2. a conservative `manual_review_required` escape hatch instead of fake certainty,
3. one place to keep diagnostic hooks, recipes, and docs references aligned,
4. a way to keep “failure still occurs” separate from “exact guidance stayed stable”,
5. and a CI-visible warning when guidance drifts while the crate still compiles.

## Recommended `0.1` command surface

### `cargo guidance-pack init`
Create a starter `guidance-pack.toml` by importing obvious candidates from:

- `#[diagnostic::on_unimplemented]` and `#[diagnostic::do_not_recommend]`,
- compile-fail fixtures (`trybuild`, `ui_test`, or equivalent),
- rustdoc `compile_fail` and runnable examples,
- `miette` diagnostic codes/help/URLs when present,
- proc-macro error helpers and maintainer-authored docs anchors.

The generated pack should be incomplete on purpose.
Anything uncertain should become `manual_review_required` rather than guessed.

### `cargo guidance-pack capture`
Emit one normalized guidance bundle from declared policy plus imported facts.
This should capture:

- failure family,
- guidance authority class,
- message-stability class,
- guidance channel(s),
- recovery recipes and docs anchors,
- origin of each recovery hint,
- checked recipe fidelity,
- and environment-sensitivity notes.

`capture` must work even when a crate has only advisory docs and no compiler-backed hooks.

### `cargo guidance-pack check`
Run the local validation pass:

- do declared failure families parse,
- do referenced diagnostic attributes still exist,
- do fixture outputs still expose the expected guidance shape,
- do docs/example anchors still resolve,
- do recipes still compile or build under the claimed lane,
- do message-stability claims still match the observed class,
- and which parts remain manual-review-only?

### `cargo guidance-pack doctor`
Render human-facing warnings for suspicious situations such as:

- `failure_only_claimed_as_exact_message_contract`
- `rust_src_presence_changes_snapshot_shape`
- `nightly_doctest_code_check_claimed_as_exact_message`
- `do_not_recommend_without_smallest_good_path`
- `proc_macro_panics_bypass_guidance_channel`
- `miette_url_present_but_recipe_witness_missing`
- `manual_review_required`

`doctor` should be a human-first renderer over explicit artifacts, not a magical compiler-introspection engine.

### `cargo guidance-pack summary`
Render a short receiver-facing note for docs or issue templates.
A good summary answers:

- what usually went wrong,
- which part of the guidance is exact versus shape-level versus advisory,
- which channel the user will actually encounter,
- what smallest path gets the user unstuck,
- and where manual review begins.

### `cargo guidance-pack diff <old> <new>`
Compare two receipts or packs and classify:

- `guidance_added`
- `guidance_removed`
- `message_stability_changed`
- `guidance_channel_changed`
- `environment_sensitivity_changed`
- `recovery_origin_changed`
- `recipe_changed`
- `recipe_fidelity_changed`
- `manual_review_boundary_changed`

### `cargo guidance-pack pack`
Emit one compact `.guidance-pack.zip` bundle for CI artifacts, docs portals, support bots, or pathfinder import.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `guidance_pack_model`
  - shared Rust types for packs, receipts, reports, summaries, and diffs
- `guidance_pack_import`
  - import logic for diagnostic attributes, compile-fail fixtures, rustdoc examples, `miette` metadata, proc-macro helpers, and maintainer-authored docs anchors
- `guidance_pack_check`
  - policy validation, fixture checking, recipe validation, message-stability checks, and doctor warnings
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
- `guidance-authority.policy.json`
- `recovery-origin.receipt.json`
- `recipe-fidelity.report.json`

This pass adds three more important artifacts:

- `message-stability.report.json` — what exactly is promised: exact stderr, code-level stability, shape-only stability, failure-only proof, or manual review.
- `guidance-channel.receipt.json` — which user-facing channel actually carries help: compiler, UI stderr snapshot, proc-macro `compile_error!`, `miette`, docs anchor, or mixed path.
- `environment-sensitivity.report.json` — which parts of the support contract vary with toolchain, `rust-src`, nightly-only doctest code checks, target/cfg, or proc-macro panic behavior.

Those files matter because guidance gets vague again if the archive only records that “some hint exists” but not:

- whether exact wording is part of the supported contract,
- which channel users actually see,
- and what environment differences still change the visible output.

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
6. **Environment-sensitivity facts**
   - `rust-src` presence
   - nightly-only error-code checks
   - target/cfg gating
   - proc-macro panic routes
7. **Manual review zones**
   - feature-specific recipes
   - target-specific examples
   - proc-macro syntax migrations
   - advice whose truth depends on external runtimes or tools

The importer should prefer visible uncertainty over synthesis.

## Message stability

The first implementation should treat **message stability** as a first-class review object and keep it separate from both guidance authority and recipe quality.

### What should count as message-stability classes in `0.1`

- `exact_snapshot`
- `code_stable_shape_flexible`
- `shape_stable`
- `failure_only`
- `manual_review_required`

### What should *not* be encoded as exact message stability in `0.1`

- “a `compile_fail` doctest exists”
- “nightly doctest error-code checking passed”
- “trybuild snapshot was green on my machine once”
- “a proc-macro emits something roughly helpful unless it panics”
- “there is a `miette` URL so the recovery path must be complete”

## Guidance channels

The first implementation should treat **channel** as explicit receiver-facing transport, not just provenance.

### Channels worth capturing in `0.1`

- compiler native diagnostic message / note / label
- snapshot-tested stderr via `trybuild` or `ui_test`
- proc-macro `compile_error!` or diagnostic helper emission
- `miette` code/help/url metadata
- maintainer-authored docs anchor
- mixed channel with explicit fallback order

### Channels that should stay manual in `0.1`

- arbitrary issue comments
- unofficial forum/blog posts
- brittle stderr scraping without fixture ownership
- “panic with a pretty message” treated as if it were structured guidance

## Proving-ground archetypes

A worthy first implementation should prove itself against at least five archetypes:

1. **Trait-heavy library**
   - `on_unimplemented` improves the error, while `do_not_recommend` hides a misleading blanket impl.
2. **Feature-rich async/framework crate**
   - the crate gives a real feature/runtime mismatch path, and exact wording is snapshot-checked only under controlled environments.
3. **Proc-macro crate**
   - the supported misuse path emits structured guidance, while panic routes are explicitly manual-review territory.
4. **Docs-heavy crate**
   - rustdoc `compile_fail` examples prove misuse still fails, but exact messaging stays a weaker promise.
5. **Rich runtime-diagnostic crate**
   - `miette` codes/help/URLs exist, but they are kept separate from proving the corrected path was actually exercised.
