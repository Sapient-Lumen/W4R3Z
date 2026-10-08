# Docs.rs build-parity product plan — 2026-03-17

This note exists to keep **P-0472 Docs.rs Build Parity & Evidence Kit** disciplined.
The archive already decided that the missing value is a **docs.rs-facing receipt / diff / issue-bundle layer**.
This pass answers a narrower question:

> If somebody actually started building **P-0472** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps crate maintainers publish one reviewable answer to:

- what docs.rs-facing metadata and cfg assumptions were active,
- how close the local run was to hosted docs.rs,
- which documented sandbox constraints were relevant,
- what failed and in which phase,
- which drift causes look plausible,
- and what compact evidence can be attached to CI, release review, or an upstream issue.

It should **not** try to become a new docs host, a perfect local docs.rs emulator, or a giant nightly-management system.
Those are adjacent imports, not the core product.

## What the crate should provide other people

For downstream maintainers and reviewers, the crate should provide:

1. **A boring docs.rs preflight receipt** instead of “it worked on my laptop”.
2. **Fidelity honesty** about whether the run was only metadata analysis, a `cargo docs-rs`-style preflight, a local builder reproduction, or a joined local+hosted evidence bundle.
3. **A normalized docs.rs config view** so `default-target`, `targets`, `additional-targets`, feature flags, and rustdoc/cargo args are easy to review.
4. **A compact limit/policy report** for target count, read-only filesystem assumptions, network blocking, and build-log truncation risk.
5. **A drift-cause summary** that keeps “hosted fact”, “local observation”, and “best-effort inference” separate.
6. **A small bundle** that can be attached to CI artifacts or upstream docs.rs issues.
7. **A release-review diff** so metadata, target, and fidelity changes become visible across versions.

For maintainers, the crate should provide:

1. one compact bundle format rather than another ad hoc shell transcript,
2. a conservative `manual_review_required` path whenever parity is too uncertain,
3. import paths for hosted build summaries instead of assuming network scraping is always safe,
4. phase-aware failure summaries instead of one flat “docs build failed”,
5. and a minimal artifact vocabulary that stays stable as docs.rs changes around it.

## Recommended `0.1` command surface

### `cargo docsrs-evidence capture`
Run the local collection pass.
This should:

- read `[package.metadata.docs.rs]`,
- record the local toolchain and relevant environment,
- classify the run fidelity,
- execute a conservative local preflight,
- collect documented docs.rs limit facts,
- and emit a bundle.

### `cargo docsrs-evidence explain`
Render a short summary for humans.
This should answer:

- what we tried,
- how close it was to hosted docs.rs,
- what limits/policies mattered,
- what the failure phase was,
- and which drift causes seem most plausible.

### `cargo docsrs-evidence diff <old> <new>`
Compare two bundles and classify:

- `metadata_changed`
- `default_target_changed`
- `targets_changed`
- `feature_policy_changed`
- `fidelity_changed`
- `limit_risk_changed`
- `drift_cause_changed`
- `manual_review_required`

### `cargo docsrs-evidence import-hosted`
Import **hosted** facts from a build-summary URL, copied log, or saved `/releases/` summary.
This must stay import-first in `0.1`; the crate should not depend on unstable site scraping to be useful.

### `cargo docsrs-evidence pack`
Emit one compact archive for CI/release review/upstream issue filing.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `docsrs_evidence_model`
  - shared Rust types for profiles, receipts, reports, diffs, and bundles
- `docsrs_evidence_metadata`
  - `[package.metadata.docs.rs]` parsing and normalization
- `docsrs_evidence_capture`
  - local command execution, phase classification, limit/policy collection, fidelity classification
- `docsrs_evidence_hosted`
  - optional hosted summary/log import and normalization
- `docsrs_evidence_pack`
  - summary rendering, diffing, redaction, bundle writing
- `cargo-docsrs-evidence`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the bundle format is trusted:

- `docsrs_evidence_cargo_docs_rs`
- `docsrs_evidence_builder_import`
- `docsrs_evidence_ci`

## `0.1` artifact set

The archive already had the right center of gravity.
`0.1` should revolve around these files:

- `docsrs-profile.toml`
- `docsrs-env.receipt.json`
- `docsrs-config.report.json`
- `docsrs-limit.report.json`
- `docsrs-results.json`
- `docsrs-diff.json`
- `docsrs-summary.md`

This pass adds three artifacts that had previously been too implicit:

- `preflight-fidelity.report.json` — whether the result is `metadata_only`, `cargo_docs_rs_preflight`, `builder_local_reproduction`, `hosted_import_only`, `joined_local_hosted`, or `manual_review_required`.
- `hosted-build-import.receipt.json` — imported facts from docs.rs build summaries/logs, including source URLs and truncation posture.
- `drift-cause.report.json` — normalized candidate causes such as `default_target_shift`, `docsrs_cfg_scope`, `readonly_fs`, `network_blocked`, `missing_native_dependency`, `target_limit`, `nightly_or_builder_drift`, `log_truncation`, and `unknown`.

Those matter because the docs.rs docs now make several awkward facts explicit:

- `cargo docs-rs` is helpful but not a perfect replica,
- `docsrs` cfg only applies to the final rustdoc invocation,
- all non-`x86_64-unknown-linux-gnu` targets are cross-compiled,
- most of the source tree is read-only,
- network access is blocked,
- build logs are capped,
- and target defaults can shift even when crate-local metadata stays implicit.

So the missing value is no longer another docs runner.
It is the **reviewable explanation layer** above these facts.

## Fidelity policy

The first implementation should treat fidelity as a first-class review object.

### Fidelity classes for `0.1`

- `metadata_only`
  - parsed docs.rs metadata and environment facts, but no meaningful build attempt
- `cargo_docs_rs_preflight`
  - local preflight close to docs.rs argument/config behavior, but not the hosted sandbox
- `builder_local_reproduction`
  - evidence imported from or produced by a local docs.rs builder workflow
- `hosted_import_only`
  - no local reproduction, only imported hosted build summary/log evidence
- `joined_local_hosted`
  - both local preflight and hosted evidence available
- `manual_review_required`
  - we cannot honestly classify the run or drift

### What `0.1` should *not* do

- pretend local preflight equals hosted docs.rs,
- scrape arbitrary site HTML as its only import path,
- promise deterministic nightly reproduction forever,
- or flatten every failure into “docs.rs bug”.

## Proving-ground archetypes

A worthy first implementation should prove itself against at least five archetypes:

1. **Feature-heavy library with explicit docs.rs metadata**
   - target/feature normalization
   - landing-page target posture
2. **Crate using `#[cfg(docsrs)]` and `DOCS_RS`**
   - final-rustdoc scope vs dependency/build.rs behavior
3. **Crate with `build.rs` generating files**
   - read-only source tree vs `OUT_DIR`
4. **Crate needing extra native dependencies in the docs.rs environment**
   - missing-build-env cause classification
5. **Crate with noisy failure output**
   - build-log truncation and manual-review handling

If `0.1` cannot survive those five, the product vocabulary is still too narrow.

## Adoption staircase

Do not require the ecosystem to jump directly to full builder reproduction.

### Stage 1 — metadata and fidelity capture
- parse docs.rs metadata
- record local toolchain/environment
- emit fidelity and limit reports

### Stage 2 — local preflight bundles
- run conservative local checks
- emit phase-aware results and drift-cause candidates

### Stage 3 — hosted import
- import copied docs.rs build summaries/logs
- join hosted and local evidence without pretending they are the same thing

### Stage 4 — release diffs
- compare current bundle to the previous release
- make docs posture drift loud in review

### Stage 5 — CI / issue integrations
- stable summary and bundle exports for release review and docs.rs issue templates

## What should wait until later

Leave these for later unless `0.1` proves cramped without them:

- automatic live scraping of arbitrary docs.rs pages
- a full docs.rs builder orchestration system
- rich hosted dashboards
- registry-wide crawling of all crates
- nightly pinning / updating policy managers
- documentation coverage scoring
- broad rustdoc JSON analysis beyond what parity bundles need

## Good failure modes

The crate should fail conservatively.
Preferred failure behavior:

- `cargo docs-rs` green but network access assumptions unclear → `manual_review_required`
- hosted log obviously truncated → `log_truncation` + `manual_review_required`
- metadata omitted and defaults changed underneath the crate → `default_target_shift`
- missing native dependency in hosted build env → `missing_native_dependency`
- dependency/workspace crate relied on `#[cfg(docsrs)]` → `docsrs_cfg_scope`
- source-tree writes detected → `readonly_fs`

## Why this still looks worth building

The adjacent tools are real, which is exactly why this proposal now looks sharper rather than weaker.

- docs.rs itself now publishes the current nightly, sandbox limits, cfg scope, and target/cross-compilation behavior.
- docs.rs documents rich metadata controls including `default-target`, `targets`, `additional-targets`, feature flags, and cargo/rustdoc args.
- docs.rs explicitly recommends `cargo docs-rs` in CI, while also saying it does not perfectly replicate the hosted environment.
- docs.rs publishes release/build summaries and documents how to build unpublished crates with the builder locally.
- docs.rs now hosts rustdoc JSON and warns that format versions can vary with the producing rustdoc.
- the October 2025 default-target change proved that “we left docs posture implicit” is a real source of drift.

That combination strengthens the case that the missing value is the **receipt / fidelity / drift-cause / issue-bundle layer above docs.rs substrate**, not another build wrapper.

## Non-goals for `0.1`

- not a replacement for docs.rs
- not a full local clone of the hosted service
- not a new docs renderer
- not a nightly pinning service
- not a generic rustdoc JSON analysis framework
- not a documentation coverage dashboard

## Sources

- docs.rs builds page
- docs.rs metadata page
- docs.rs about page
- docs.rs rustdoc JSON page
- docs.rs default-target change announcement
- docs.rs repository README
- `cargo docs-rs` README
