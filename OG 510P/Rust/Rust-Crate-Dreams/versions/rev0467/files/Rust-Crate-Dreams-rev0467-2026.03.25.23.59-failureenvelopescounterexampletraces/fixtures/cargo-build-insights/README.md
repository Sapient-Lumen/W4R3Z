# Cargo Build Insights fixtures

This fixture family exists to make **P-0035 cargo-build-insights** more concrete.

The goal is not to model every Cargo internal.
The goal is to define a small, boring artifact family for **historical build warehousing** above Cargo's evolving build-analysis/session substrate.

## Intended first scenarios

1. `session_import_regression_baseline` — import a small baseline/head pair and freeze it into a reviewable regression bundle.
2. `branch_drift_trend_alert` — a branch or CI series shows repeated slowdown / rebuild drift over several runs.
3. `toolchain_change_series_split` — a toolchain change forces the crate to split one apparent series into two comparable lanes.
4. `workspace_scope_change` — package/target selection drift means a naive comparison should be blocked or heavily caveated.
5. `manual_redaction_policy_review` — a bundle remains useful after path/user/job redaction.
6. `pr_head_vs_last_green_main_needs_explicit_window` — a review bundle must state why this baseline/head pair was chosen.
7. `redacted_ci_series_still_needs_export_policy` — cleaned bundles still need explicit export posture and window truth.

## Minimal bundle for 0.1

Core:
- `session-series.index.json`
- `comparison-window.receipt.json`
- `build-insight-session.json`
- `series-summary.json`
- `regression-explanation.json`
- `import.receipt.json`
- `exactness.report.json`
- `notes.md`

Optional overlays:
- `series-compatibility.report.json`
- `trend-alert.json`
- `warehouse-policy.toml`

## Design rule

This fixture family should optimize for **honest longitudinal judgments**.

Good:
- `series_split_required`
- `baseline_selection_changed`
- `observed_metric_regression`
- `manual_review_required`
- `redaction_applied_but_comparison_still_useful`

Bad:
- pretending every series comparison is apples-to-apples,
- pretending imported Cargo sessions already define the downstream stable schema,
- or quietly flattening toolchain / profile / scope drift into one generic slowdown claim.

## Planning rule (2026-03-16)

Every scenario should preserve three truths explicitly:

1. **source truth** — which claims came from `cargo report`, build-analysis JSONL, Cargo JSON messages, metadata, or manual annotation;
2. **comparison-window truth** — why these baseline/head or rolling-range sessions were selected and for which audience;
3. **comparability truth** — whether sessions remain in one comparable series or must be split;
4. **exactness truth** — imported fact vs normalized observation vs conservative inference vs manual-review-only.
