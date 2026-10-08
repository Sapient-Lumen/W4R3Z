# Accessibility Capture & Interop Lab fixtures

These fixtures exist to make **P-0202 Accessibility Capture & Interop Lab** look implementable instead of merely aspirational.

The receiver-facing question is:

> what files should another maintainer, reviewer, or QA engineer receive in order to understand what a platform accessibility backend actually exposed and how it differs from expectations or another platform?

## Minimal pack for 0.1

- `bundle-manifest.schema.json` — capture backend, OS/toolkit/app identity, capability notes, and redaction profile.
- `tree.snapshot.schema.json` — normalized accessibility tree with core semantics, extension lanes, and caveats.
- `event-stream.schema.json` — optional focus/value/selection/live-region events.
- `semantic-diff.report.schema.json` — portable versus platform-specific differences, comparability, and next actions.

## Design rules

- Stay **observer-side**: this pack describes what platforms exposed, not what a toolkit intended to emit.
- Preserve **capability and caveat reporting** as first-class outputs.
- Keep **redaction** explicit.
- Preserve `manual-review-required` and `not-comparable` as honest results.

## Intended first scenarios

1. `dialog_focus_linux_capture` — capture a modal-dialog focus sequence on one backend and record the observed tree/event stream.
2. `menu_role_mismatch_expected_vs_observed` — compare an expected semantics snapshot against platform capture and explain whether the drift is portable, platform-specific, or unsupported.
