# Cargo future-incompat triage product plan — 2026-03-20

This note tightens **P-0478 Cargo Future-Incompat Triage Kit** one step past owner maps, waiver expiry, release gates, and evidence-source receipts.
The sharper question is now:

> when a future-incompat finding exists, was it actually visible during the reviewed build, only visible in a recalled/full report, or latent-but-recorded under suppression or notification settings?

## Main judgment

A buildable `0.1` should still stay small: one cargo subcommand plus a library crate.
But it should now treat two more review objects as first-class:

1. **`finding-visibility.report.json`** — tells whether a finding was terminal-visible, report-only, suppressed-but-recorded, hidden by package-filtered recall, or notification-hidden.
2. **`suppression-basis.receipt.json`** — records why a finding became latent or partially hidden, such as `allow_attribute`, `cap_lints`, `report_frequency_never`, or `package_filtered_recall`.

Without those artifacts, the lane can still overstate what humans actually saw during a release review.
Cargo and rustc are already more expressive than that:

- Cargo can display full reports live or recall them later by id.
- Cargo can narrow recall to a specific package.
- Cargo can suppress terminal notifications entirely through `[future-incompat-report].frequency = "never"`.
- rustc's `--json=future-incompat` output can still carry diagnostic information even when the warning was suppressed by `#[allow]` or `--cap-lints`.

So the missing value is no longer just memory and ownership.
It is **visibility honesty** above the existing report substrate.

## What the crate should provide other people now

1. **Latent-debt truth** — a team can see that “terminal looked clean” and “future debt exists” are not always the same statement.
2. **Visibility posture** — every finding can say whether it was live-visible, report-only, suppressed-but-recorded, or hidden by a narrower recall surface.
3. **Suppression basis** — reviewers can see whether a finding became latent because of code-level suppression, `--cap-lints`, Cargo notification settings, or later report slicing.
4. **Release-gate honesty** — gates can fail on latent blockers without pretending those blockers were loudly shown to every reviewer during the original build.
5. **Diffable visibility changes** — teams can compare two snapshots and see when a finding moved from visible to latent, or vice versa, across toolchain/config/report-mode changes.

## First new schema pair to keep stable

### `finding-visibility.report.json`

A good first schema should let each finding say:

- a stable `finding_key`,
- the capture or report ref it belongs to,
- `visibility_posture` such as `terminal_visible`, `report_visible_only`, `suppressed_but_recorded`, `package_filtered_hidden`, `notification_hidden`, or `manual_review_required`,
- whether release policy should treat it as `active_blocker`, `latent_debt`, `advisory_only`, or `manual_review_required`,
- and what public/review summary is still honest.

### `suppression-basis.receipt.json`

A good first schema should let each record say:

- which `finding_key` it explains,
- `suppression_kind` such as `allow_attribute`, `cap_lints`, `report_frequency_never`, `package_filtered_recall`, or `summary_only_without_live_flag`,
- which evidence surface established that basis,
- whether the result should be classified as `latent_debt`, `display_suppressed`, `recall_narrowed`, or `manual_review_required`,
- and what follow-up review surface should be consulted next.

## First scenario families worth freezing

1. **Allow-suppressed future incompatibility still counts as latent debt**
   - a future-incompat finding is preserved in machine-readable capture,
   - terminal review looked clean,
   - release policy still wants explicit debt tracking.

2. **Package-filtered recall hides a workspace-wide blocker unless visibility is explicit**
   - the full workspace report contains a blocking finding,
   - a later `cargo report future-incompat --package ...` slice hides it,
   - and the bundle must say the recall surface is narrower than the original blocker surface.

## Working rule for future passes

Do **not** let this lane collapse into:

- generic lint-suppression accounting,
- broad build-history warehousing,
- or vague “show me the latest report” wrappers.

The product boundary here is narrower and more useful:

- **what debt exists,**
- **what humans actually saw,**
- **what stayed latent,**
- and **why**.
