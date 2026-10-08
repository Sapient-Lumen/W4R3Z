# Official voter-information date-entry surface checklist

Use this quickcheck when an election office needs a bounded way to keep official voter-information routes workable when the public must enter or choose a date before the current answer appears.

## Inventory and review scope

- Identify the critical public-answer routes that require a date before the answer lane appears: registration-status lookups, ballot-status checks, appointment schedulers, deadline filters, and similar date-gated help paths.
- Distinguish this from general date/deadline semantics, generic field-entry review, keyboard-only review, screen-reader review, and small-viewport review.
- Re-check routes whose success depends on calendar popovers, browser-native date controls, segmented month/day/year fields, or hidden date-range limits.

## Date purpose, format, and typed fallback

- Confirm that each critical route states which date is required and, when needed, what format is expected.
- Do not rely on placeholder-only hints or icon-only calendar affordances to explain date entry.
- Keep a workable typed-date path available even when a calendar widget is present.
- Whenever reasonable, keep the keyboard active rather than forcing the voter to operate the picker.

## Widget behavior and segmented-date correction

- Treat the picker as a helper, not the only path to the answer lane.
- Confirm that segmented month/day/year fields remain plainly labeled and do not auto-advance focus.
- Re-check that focusing or partially entering a date does not auto-submit, silently reroute the page, or discard the entered value.

## Bounds, normalization, and fallback

- Make meaningful date bounds or allowed windows visible before failure instead of surfacing them only as a rejected submission.
- Confirm that typed, native-picker, custom-picker, and segmented-date paths resolve to the same authoritative answer for the same date.
- Keep a plainly visible first-party office/help fallback available when the main date-entry path remains brittle.

## Evidence posture

- Preserve only route labels, reviewed date paths, format-cue review state, widget-optionality review state, bounds review state, hidden-context-change review state, and last review time.
- Do not preserve raw entered dates, birth dates, copied appointment values, keystroke logs, or exhaustive session replay when bounded policy reconstruction is sufficient.
