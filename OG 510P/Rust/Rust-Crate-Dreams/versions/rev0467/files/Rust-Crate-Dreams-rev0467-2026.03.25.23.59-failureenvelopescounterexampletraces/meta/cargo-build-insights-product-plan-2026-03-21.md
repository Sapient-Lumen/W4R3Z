# Cargo Build Insights — product plan (2026-03-21)

This note sharpens **P-0035 cargo-build-insights** into an implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0035** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not try to replace Cargo's recorder, grow into a dashboard platform, or guess every build-performance remedy.
It should provide one boring, reviewable historical-build contract layer above today's Cargo session substrate.

`0.1` should make five things first-class:

1. **session import** — frozen imported facts with provenance and unknown-field preservation;
2. **series membership** — which sessions belong in one comparable family at all;
3. **comparison window** — why this baseline/head or rolling range was chosen, and for whom;
4. **regression judgment** — what changed, what stayed comparable, and what became caveated or split;
5. **exactness / redaction** — what is imported, normalized, inferred, hidden, or still manual-review-only.

## What `0.1` should provide other people

- one compact `build-insight-session.json`
- one compact `session-series.index.json`
- one compact `comparison-window.receipt.json`
- one compact `series-compatibility.report.json`
- one compact `series-summary.json`
- one compact `regression-explanation.json`
- one compact `import.receipt.json`
- one compact `exactness.report.json`
- one rendered `build-insights.summary.md`
- a diff/export flow for PR review or CI artifacts

## Commands worth shipping first

- `cargo build-insights init`
- `cargo build-insights import-session`
- `cargo build-insights freeze-series`
- `cargo build-insights compare`
- `cargo build-insights doctor`
- `cargo build-insights trend-alerts`
- `cargo build-insights summary`
- `cargo build-insights export`

## What to import, not reinvent

- Cargo `-Zbuild-analysis` JSONL session logs
- `cargo report sessions`
- `cargo report timings`
- `cargo report rebuilds`
- `cargo metadata --format-version` for stable workspace context
- Cargo external-tools JSON (`--message-format=json`) for stable produced-artifact / build-script / warning context
- optional maintainer annotations for branch, PR, or benchmark intent

## Suggested `0.1` doctor warnings

- `comparison_window_missing_audience`
- `regression_claim_without_series_compatibility`
- `toolchain_or_profile_split_hidden_by_single_series`
- `workspace_scope_change_missing_lane_split`
- `unknown_upstream_fields_dropped_during_import`
- `timings_html_attached_without_machine_basis`
- `manual_annotation_unmarked`
- `redaction_policy_missing_for_exported_bundle`

## First proving-ground scenarios

1. **PR head versus last green on `main`**
2. **Rolling branch slowdown across several CI sessions**
3. **Toolchain bump that forces a lane split instead of a regression claim**
4. **Workspace-scope change that should block a naive comparison**
5. **Redacted CI imports that remain reviewable after path/job cleanup**

## What to leave for later

- hosted dashboards or SaaS retention systems
- adaptive scheduling or automatic build-optimization advice
- full build-replay or self-profile integration
- organization-wide policy engines
- pretending one baseline policy fits PR review, release review, and local experimentation equally well
