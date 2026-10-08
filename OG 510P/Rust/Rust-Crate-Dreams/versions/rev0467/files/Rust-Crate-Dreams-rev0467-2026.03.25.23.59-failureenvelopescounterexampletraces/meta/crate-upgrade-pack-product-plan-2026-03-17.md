# Crate upgrade-pack product plan — 2026-03-17

This note exists to keep **P-0514 Crate Upgrade Pack Kit** disciplined.
The archive already decided that the missing value is a **receiver-facing release-to-release migration contract**.
This pass answers a narrower question:

> If somebody actually started building **P-0514** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps crate authors publish one reviewable answer to:

- which `from -> to` upgrade lanes they are really describing,
- what kind of hazards exist in each lane,
- which fixes were actually observed to be machine-applicable and where,
- which before/after recipes were checked across features, targets, runtimes, configs, and package subsets,
- and where behavior review or manual migration still begins.

It should **not** try to become a semver checker, a changelog generator, a release bot, or a universal codemod platform.
Those are adjacent imports, not the product.

## What the crate should provide other people

For downstream users, release reviewers, and docs/tool authors, the crate should provide:

1. **One compact upgrade contract** instead of changelog prose, release-PR archaeology, issue-thread folklore, and half-remembered migration notes.
2. **A hazard-class policy** so `machine_fix_available`, `manifest_edit_required`, `config_edit_required`, `behavior_check_required`, and `manual_review_required` stop being implicit vibes.
3. **Fixup-capability receipts** so each claimed automation path says which tool produced it, which applicability class it had, and whether it touched source only or also manifests/config/docs.
4. **Named migration-lane manifests** so a crate can honestly say “we checked 1.4 -> 1.5 on default + rustls, but not on the native-tls example binary.”
5. **Lane-fidelity reports** so people can distinguish fully observed lanes from sampled, recipe-only, or manual-review-only lanes.
6. **Short human summaries** that can be pasted into release notes, support replies, and upgrade docs without turning back into vague prose.
7. **A release diff** that makes quiet upgrade-surface drift loud.
8. **A small portable bundle** that CI, release PRs, support bots, and issue templates can all consume.

For maintainers, the crate should provide:

1. a compact pack file that is cheap to review,
2. conservative `manual_review_required` escape hatches instead of fake certainty,
3. a way to import semver/public-API/fix-suggestion substrate instead of replacing it,
4. one place to declare which migration lanes are official and which remain best-effort,
5. and a CI gate for “this release changed how hard it is to upgrade.”

## Recommended `0.1` command surface

### `cargo upgrade-pack init`
Create a starter `upgrade-pack.toml` by importing obvious candidates from:

- the current crate version and selected target version,
- semver/public-API reports when available,
- manifest feature/default changes,
- declared config/runtime/backend policies,
- known docs anchors or release-note links,
- and optional machine-fix lanes from rustc/rustfix/Clippy receipts.

The generated pack should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` rather than guessed.

### `cargo upgrade-pack capture`
Emit one normalized receipt bundle from a declared release-to-release lane.
This should capture:

- `from -> to` lane identity,
- imported semver/public-API findings,
- hazard classes,
- fixup capability receipts,
- recipe references,
- checked feature/target/runtime/package dimensions,
- and known manual-review boundaries.

### `cargo upgrade-pack check`
Run the local validation pass:

- do declared upgrade lanes parse,
- do recipes still resolve,
- do imported hazards and declared hazard classes agree,
- can selected lanes build/check/test/doc under the advertised matrix,
- and which parts remain partial, behavior-review-only, or manual-review-only?

### `cargo upgrade-pack doctor`
Render human-facing warnings for suspicious situations such as:

- `machine_fix_claim_without_observed_applicability`
- `manifest_or_config_edit_missing_from_fixup_receipt`
- `semver_green_but_behavior_check_required`
- `workspace_lane_claimed_but_binary_or_example_not_checked`
- `default_feature_change_missing_recipe`
- `manual_review_required`

`doctor` should be a human-first renderer over captured artifacts, not a magical verifier.

### `cargo upgrade-pack summary`
Render a short receiver-facing note that answers:

- what lane we are upgrading along,
- which hazards matter most,
- what tooling can auto-fix,
- what still needs a person to edit or validate,
- and how much of the lane was actually checked.

### `cargo upgrade-pack diff <old> <new>`
Compare two receipts or packs and classify:

- `hazard_added`
- `hazard_removed`
- `hazard_class_changed`
- `fixup_capability_changed`
- `recipe_changed`
- `lane_fidelity_changed`
- `manual_review_boundary_changed`

### `cargo upgrade-pack pack`
Emit one compact `.upgradepack.zip` bundle for CI artifacts, release review, docs generation, and support handoff.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `upgrade_pack_model`
  - shared Rust types for packs, manifests, reports, receipts, and diffs
- `upgrade_pack_import`
  - import logic for semver/public-API findings, manifest deltas, release-note refs, and fix-suggestion receipts
- `upgrade_pack_check`
  - recipe validation, hazard classification, lane-fidelity checks, and doctor warnings
- `upgrade_pack_pack`
  - summary rendering, diff writing, markdown output, and zip bundle emission
- `cargo-upgrade-pack`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `upgrade_pack_semver`
- `upgrade_pack_rustfix`
- `upgrade_pack_clippy`
- `upgrade_pack_release_plz`
- `upgrade_pack_workspace`

## `0.1` artifact set

The archive already had a good core.
`0.1` should still revolve around:

- `upgrade-pack.toml`
- `upgrade-hazards.report.json`
- `fixup-hints.receipt.json`
- `migration-recipe.manifest.json`
- `upgrade-check.report.json`
- `upgrade-diff.report.json`
- `upgrade-notes.summary.md`

This pass adds three more important artifacts:

- `hazard-class.policy.json` — what `machine_fix_available`, `manifest_edit_required`, `config_edit_required`, `behavior_check_required`, and `manual_review_required` mean and what minimum evidence each class expects.
- `fixup-capability.receipt.json` — where fix claims came from (`cargo fix`, `rustfix`, Clippy, codemod, manual note), what applicability was observed, and which files/scopes were actually touched.
- `lane-fidelity.report.json` — how much of the named upgrade lane was actually observed across features, targets, runtimes, configs, and package subsets.

Those files matter because upgrade stories get vague again if the archive only records hazards and recipes but not:

- what *kind* of hazard is being claimed,
- what automation capability was actually observed,
- and how complete the real lane coverage was.

## Discovery order

A disciplined import order helps prevent fake certainty.

1. **Version and manifest facts**
   - crate versions
   - feature/default changes
   - config/runtime/backend declarations
2. **SemVer/public-API facts**
   - imported witness/verdict outputs
3. **Machine-fix facts**
   - rustc JSON suggestions
   - `cargo fix` / `rustfix` / Clippy receipts
4. **Observed recipes**
   - build/check/test/doc results for named lanes
5. **Manual-review zones**
   - behavior changes, workspace-only lanes, and unsupported package subsets

The importer should prefer visible uncertainty over synthesis.

## Hazard-class policy

The first implementation should treat **hazard classes as first-class review objects** and keep them separate from raw semver verdicts.

### What should count as hazard classes in `0.1`

- `machine_fix_available`
- `source_edit_required`
- `manifest_edit_required`
- `config_edit_required`
- `behavior_check_required`
- `manual_review_required`
- `unsupported_lane`

### What should *not* count as hazard classes in `0.1`

- “semver compatible” as proof no upgrade work exists
- “the changelog mentions it” as proof a lane is covered
- “cargo fix changed some files” as proof the whole lane is fixed
- “one library member built” as proof the whole workspace lane is checked

## Fixup-capability policy

The first implementation should treat **automation capability** as explicit review material.
A good `0.1` should model origins such as:

- `cargo_fix`
- `rustfix`
- `clippy_fix`
- `maintainer_codemod`
- `manual_recipe_only`
- `no_fix_available`

with applicability classes such as:

- `machine_applicable`
- `maybe_incorrect`
- `has_placeholders`
- `unspecified`

and scope tags such as:

- `rust_source`
- `cargo_manifest`
- `config_file`
- `docs_snippet`
- `workspace_metadata`

If a fix only touched Rust source but the upgrade also needs manifest/config/docs edits, the receipt should say so.
`0.1` should prefer “source fix observed, manifest edit still manual” over pretending the lane is fully automated.

## Lane-fidelity policy

The first implementation should treat **coverage completeness** as a first-class review object.
A good `0.1` should model:

- `fully_observed`
- `sampled`
- `recipe_only`
- `fix_only`
- `docs_only`
- `workspace_subset_only`
- `manual_review_required`

with explicit dimensions such as:

- feature sets,
- targets,
- runtime/backend choices,
- config profiles,
- and package subsets.

If a lane was checked only for the library crate and not the example binary, or only for the default feature set and not `no-default-features`, the fidelity report should make that obvious.

## First fixture families to take seriously

The existing archive already had useful starter fixtures.
A real `0.1` should now force at least these cases to stay reviewable:

1. **Machine fix applies but manifest feature rename remains**
   - Source edits can be auto-applied, but `Cargo.toml` or feature-selection guidance still needs manual changes.
2. **SemVer green but behavior review required**
   - Public API may be compatible while defaults, retry/backoff, batching, or runtime behavior changed enough to require explicit downstream validation.
3. **Workspace recipe checks only the library lane**
   - The named migration recipe passed for a library member, but the CLI/example/binary lane was not checked and must not inherit the claim.

## `0.1` non-goals

- reimplementing semver/public-API analyzers
- becoming a release bot or changelog platform
- building a universal codemod/refactoring engine
- promising that all upgrade pain can be classified mechanically
- claiming workspace-wide migration confidence from one package or one feature profile

## Suggested proving grounds

- popular libraries that already run semver checks and release automation but still answer migration questions by hand
- framework crates with runtime/backend/default-feature shifts
- workspaces with shared libraries plus higher-touch binaries/examples
- crates where rustfix/cargo-fix can help but are visibly not the whole story

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://doc.rust-lang.org/cargo/reference/semver.html
- https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- https://doc.rust-lang.org/beta/rustc/json.html
- https://docs.rs/rustfix/latest/rustfix/enum.Filter.html
- https://release-plz.dev/docs/usage/update
- https://crates.io/crates/cargo-release
