# Crate upgrade-pack product plan — 2026-03-19

This note refreshes **P-0514 Crate Upgrade Pack Kit** now that the surrounding Rust release substrate is stronger and the archive’s newer support-surface lanes are more implementation-ready.

The archive already decided that the missing value is a **receiver-facing release-to-release migration contract**.
This pass answers a narrower question:

> If somebody actually started building **P-0514** this week, what should the next sharper `0.1` provide other people, and what distinctions must stay first-class so the crate does not collapse back into changelog prose or release automation?

## Main judgment

A buildable `0.1` should still be a **small cargo subcommand plus library**.
But the sharper version should now publish one reviewable answer to five questions, not three:

1. which `from -> to` lane is being described,
2. what **kind** of hazards exist,
3. what **authority** produced each hazard,
4. which workspace/package/example lanes were actually exercised,
5. and what part of the migration was truly machine-fixed versus still left for human follow-through.

It should **not** become a semver checker, a changelog generator, a release bot, or a universal codemod framework.
Those remain adjacent imports.

## What the crate should provide other people

For downstream adopters, release reviewers, and docs/support tool authors, the crate should provide:

1. **One compact upgrade contract** instead of scattered changelog prose, release PR archaeology, compiler suggestions, and issue-thread folklore.
2. **Hazard-class truth** so people can distinguish `machine_fix_available`, `manifest_edit_required`, `behavior_check_required`, `manual_review_required`, and similar categories.
3. **Hazard-authority truth** so each hazard states whether it came from SemVer/public-API evidence, feature/default-policy drift, config/runtime policy drift, a witnessed behavior check, or a maintainer-authored note.
4. **Fixup-capability receipts** so each claimed automation path says which tool produced it, what applicability was observed, and which surfaces it actually touched.
5. **Package-scope truth** so a workspace can honestly say “the library member lane was checked, the CLI/example lane was not”.
6. **Lane-fidelity reports** so people can distinguish fully observed lanes from sampled, recipe-only, workspace-subset-only, or manual-review-only lanes.
7. **Minimal migration recipes** for common lanes such as API renames, feature-policy changes, config changes, or runtime-selection shifts.
8. **A diffable upgrade-support surface** so reviewers can see whether releases are getting easier or harder to adopt.

For maintainers, the crate should provide:

1. a compact pack file that is cheap to review,
2. conservative `manual_review_required` escape hatches,
3. a way to import SemVer/public-API and suggestion substrate without pretending it is complete,
4. one place to declare which workspace/package subsets are official,
5. and a CI gate for “this release changed how hard it is to upgrade”.

## Three review objects to keep first-class now

### 1. `hazard-authority.receipt.json`

The archive already had hazard classes.
This pass argues that `0.1` also needs a separate artifact for **authority**.

A good first schema should let each hazard say:

- `authority_kind` — one of `semver_public_api`, `feature_policy`, `config_policy`, `runtime_policy`, `behavior_witness`, `maintainer_note`, `docs_only`
- `origin_tool` — e.g. `cargo-semver-checks`, `cargo metadata`, `maintainer_declared`, `release_note_ref`, `manual_recipe`
- `evidence_status` — `observed`, `imported`, `declared`, `missing`
- `supports_classes` — which hazard classes it backs
- `notes` — compact caveats

Why it matters:

- `release-plz update` can integrate `cargo-semver-checks`, but it also warns that this does **not** catch every SemVer violation.
- Cargo’s SemVer guidance is conventional guidance, not a whole migration protocol.
- Feature/default-policy changes can still be upgrade hazards even when API diffs remain green.

Without a distinct authority artifact, maintainers will keep flattening all hazards into “the checker found this” or “the changelog mentions this”.

### 2. `package-scope.report.json`

The archive already had lane-fidelity reports.
This pass argues that workspaces need a sharper, human-readable artifact for **which packages and scenario classes were actually in-bounds**.

A good first schema should let a pack say:

- which packages were **subject**,
- which packages were only **companions**,
- which binaries/examples/tests/aux members were **witnessed**,
- which were **intentionally excluded**,
- and whether the lane is `single_package`, `published_subset`, `workspace_subset`, or `whole_workspace`.

Why it matters:

- Cargo workspaces are first-class and common.
- `release-plz` can update local dependencies and non-published packages, which is useful release substrate but not proof that every downstream lane was checked.
- `cargo metadata --format-version` makes package-graph import stable enough that this scope report is feasible.

Without this artifact, workspaces will keep over-claiming that “the upgrade lane passed” when only a library member or one happy-path package was exercised.

### 3. `fixup-capability.receipt.json` must stay follow-through-aware

The archive already had a fixup-capability receipt.
This pass makes one stronger rule explicit: **source edits are not whole-upgrade proof**.

`cargo fix` applies rustc suggestions to source code.
`rustfix` applies diagnostic suggestions to code strings.
That is useful substrate, but it does not imply that:

- manifest feature names changed,
- config keys changed,
- docs snippets changed,
- or release notes/manual steps disappeared.

So `0.1` should keep explicit surface tags such as:

- `rust_source`
- `cargo_manifest`
- `config_file`
- `docs_snippet`
- `workspace_metadata`

and should encourage a **follow-through summary** such as:

- `source_only_fix_observed`
- `source_plus_manifest_fix_observed`
- `recipe_still_requires_docs_update`
- `behavior_validation_still_manual`

## Recommended `0.1` command surface

The earlier command set still holds, but two commands should get sharper responsibilities.

### `cargo upgrade-pack capture`
Should capture:

- `from -> to` lane identity,
- imported SemVer/public-API findings,
- hazard classes,
- hazard authorities,
- fixup-capability receipts,
- package-scope report,
- recipe references,
- checked feature/target/runtime/package dimensions,
- and known manual-review boundaries.

### `cargo upgrade-pack doctor`
Should now render warnings such as:

- `hazard_authority_missing`
- `semver_green_but_feature_policy_hazard_present`
- `release_bot_updated_workspace_but_package_scope_partial`
- `source_fix_observed_but_manifest_followthrough_missing`
- `machine_fix_claim_without_applicability`
- `manual_review_required`

`doctor` should remain a human-first renderer over captured artifacts, not a magical verifier.

## Discovery/import order

A disciplined import order helps prevent fake certainty.

1. **Version / manifest / package facts**
   - crate versions
   - workspace membership
   - features/defaults
   - config/runtime/backend declarations
2. **SemVer/public-API facts**
   - imported `cargo-semver-checks` / public-API results
3. **Suggestion/fix facts**
   - rustc JSON suggestions
   - `cargo fix` / `rustfix` / Clippy receipts
4. **Observed recipes**
   - build/check/test/doc results for named lanes
5. **Manual-review zones**
   - behavior changes, excluded packages, docs/config/manual steps

The importer should always prefer visible uncertainty over synthesis.

## Suggested proving-ground scenarios

A disciplined `0.1` should prove itself on a small set of fixtures:

1. **feature-flag shift stays a real upgrade hazard even when public API diff is green**
2. **source fix observed, but manifest/docs follow-through still manual**
3. **release bot updates the workspace, but only a published library lane is really witnessed**
4. **behavior check remains manual despite semver-compatible API surface**
5. **workspace recipe covers lib member, not example/binary member**

## Why this could matter

This is the crate that would let maintainers say:

- “Here is the supported migration path from our previous release.”
- “Here is which evidence backs each hazard.”
- “Here is what tooling really auto-fixed.”
- “Here is which workspace/package lanes we actually checked.”
- “Here is what still needs a person.”

That is the sort of boring, high-leverage support layer that could make Rust crate upgrades feel less like folklore.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-semver-checks.html
- https://doc.rust-lang.org/cargo/reference/semver.html
- https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html
- https://release-plz.dev/docs/usage/update
- https://release-plz.dev/docs/config
- https://release-plz.dev/docs/usage
- https://docs.rs/crate/cargo-semver-checks/latest
- https://docs.rs/rustfix/latest/rustfix/enum.Filter.html
- https://doc.rust-lang.org/beta/nightly-rustc/rustfix/index.html
- https://docs.rs/crate/cargo-release/latest
- https://blog.rust-lang.org/inside-rust/2025/07/15/call-for-testing-hint-mostly-unused/
