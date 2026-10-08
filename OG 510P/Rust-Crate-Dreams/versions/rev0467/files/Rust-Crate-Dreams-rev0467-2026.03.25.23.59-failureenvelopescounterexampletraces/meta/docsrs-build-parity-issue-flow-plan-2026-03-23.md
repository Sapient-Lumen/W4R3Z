# Docs.rs build parity — issue-flow refinement plan (2026-03-23)

This note deepens **P-0472 Docs.rs Build Parity & Evidence Kit**.
The earlier product plan already identified the right center of gravity.
This pass answers a narrower question:

> What should the crate provide other people in actual docs.rs failure / release-review workflows, and what should the operator flow look like in theory and practice?

## Main judgment

`0.1` should optimize for **issue flow**, not just preflight capture.
The crate’s real job is to turn “works locally, fails on docs.rs” into one small, honest, inspectable bundle.

That means the product should revolve around four operator moments:

1. **capture** a local docs.rs-oriented preflight,
2. **import** hosted docs.rs facts when available,
3. **diff** local and hosted results without pretending they are equivalent,
4. **pack** the smallest honest bundle for CI, release review, or an upstream issue.

## Why now

The docs.rs substrate is unusually concrete now:

- docs.rs publishes current sandbox limits,
- docs.rs documents `[package.metadata.docs.rs]`,
- docs.rs documents hosted rustdoc JSON availability,
- docs.rs explicitly recommends `cargo docs-rs` in CI,
- and docs.rs still says that local preflight is **not** a perfect reproduction.

That is exactly the kind of ecosystem shape where a parity/evidence crate becomes high-leverage.

## What the crate should provide other people

### For maintainers
- one boring preflight receipt instead of a shell transcript,
- one explanation of what docs.rs-facing metadata and target/feature policy were active,
- one fidelity statement telling how close the evidence is to hosted docs.rs,
- one phase-aware failure summary,
- one drift-cause report that separates observed fact from conservative inference,
- one issue/review bundle that can be attached upstream.

### For reviewers and release engineers
- one diffable bundle between release candidates,
- one compact answer about whether docs posture changed,
- one visible record of target-count / feature-policy / rustdoc-arg changes,
- one place to see whether hosted evidence exists or not.

### For upstream docs.rs maintainers
- one imported-hosted receipt plus local attempt summary,
- one redacted bundle with path/toolchain/metadata facts already normalized,
- one smaller, less repetitive issue payload.

## Recommended operator flow

### Step 1 — `capture`
Run a local docs.rs-oriented preflight.

Artifacts:
- `docsrs-env.receipt.json`
- `docsrs-config.report.json`
- `docsrs-limit.report.json`
- `docsrs-results.json`
- `preflight-fidelity.report.json`

Design rule:
Do not try to prove hosted parity here.
Just say what was attempted and what assumptions were active.

### Step 2 — `import-hosted`
Import hosted docs.rs build facts from a build summary, copied log, or saved release/build page material.

Artifacts:
- `hosted-build-import.receipt.json`
- optional `hosted-log-fragment.receipt.json`

Design rule:
Hosted import should be **import-first**.
`0.1` should not depend on fragile site scraping to be useful.

### Step 3 — `explain`
Produce a compact human-facing diagnosis.

Artifacts:
- `drift-cause.report.json`
- `docsrs-summary.md`

Suggested cause classes:
- `metadata_policy_shift`
- `default_target_shift`
- `docsrs_cfg_scope_difference`
- `readonly_fs_risk`
- `network_blocked_risk`
- `native_dependency_gap`
- `target_count_limit_risk`
- `nightly_or_builder_drift`
- `log_truncation`
- `manual_review_required`

### Step 4 — `diff`
Compare one bundle to another.

Artifacts:
- `docsrs-diff.json`

The diff should classify at least:
- `fidelity_changed`
- `metadata_changed`
- `target_policy_changed`
- `feature_policy_changed`
- `limit_risk_changed`
- `hosted_alignment_changed`
- `manual_review_required`

### Step 5 — `pack`
Emit a compact transport bundle.

Artifacts:
- `*.docsrsbundle.zip`
- `bundle-contents.manifest.json`
- `redaction.receipt.json`

The pack step is where the crate becomes useful to somebody else.

## Concrete `0.1` artifact vocabulary

Keep the first version small:

- `docsrs-profile.toml`
- `docsrs-env.receipt.json`
- `docsrs-config.report.json`
- `docsrs-limit.report.json`
- `docsrs-results.json`
- `preflight-fidelity.report.json`
- `hosted-build-import.receipt.json`
- `drift-cause.report.json`
- `docsrs-diff.json`
- `docsrs-summary.md`
- `bundle-contents.manifest.json`

Anything beyond that should be justified by a concrete proving-ground need.

## Important product boundaries

### Local preflight is not hosted parity
The crate must never flatten these.

### Hosted log import is not a guarantee of complete evidence
Build-log truncation and partial copies should remain visible.

### Metadata truth is not runtime/build-environment truth
A correct `Cargo.toml` still may fail under hosted limits or missing native dependencies.

### Rustdoc JSON availability is not documentation-build success
The crate can import rustdoc-JSON-facing facts without claiming the HTML docs story is solved.

### `cargo docs-rs` is an important substrate, not the whole product
The missing value is the receipt / diff / issue-bundle layer.

## Proving grounds for `0.1`

1. `#[cfg(docsrs)]` affects the documented crate but not a dependency lane.
2. Explicit docs.rs metadata changes the published target posture.
3. A crate depends on source-tree writes and should use `OUT_DIR`.
4. A crate needs network access that hosted docs.rs blocks.
5. A crate needs an unavailable native dependency.
6. A crate exceeds documented target-count or resource ceilings.
7. A hosted build log is partial or truncated.

If `0.1` cannot explain those seven, it is not yet doing the real job.

## What should wait until later

- full builder orchestration,
- registry-wide crawling,
- speculative hosted scraping integrations,
- documentation scoring dashboards,
- and broad machine-doc analytics beyond parity workflows.

The first win is a better issue/review bundle, not a docs platform.
