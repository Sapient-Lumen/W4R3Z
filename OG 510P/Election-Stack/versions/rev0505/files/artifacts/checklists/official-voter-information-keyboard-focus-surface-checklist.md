# Official voter-information keyboard-focus surface checklist

Use this quickcheck when an election office needs a bounded way to keep official voter-information routes usable through keyboard-only navigation and visible focus rather than assuming pointer input.

## Inventory and review scope

- Identify the critical public-answer routes whose current answer/help lane depends on links, buttons, lookups, disclosures, validation, or other interactive controls.
- Distinguish this from degraded-script review, first-load-overlay review, constrained-container review, and small-viewport/reflow review.
- Re-check routes that rely on click-only custom controls, reordered form layouts, sticky utility rails, or dynamic updates that move the voter through multiple steps.

## Focus reachability and semantics

- Confirm that critical actions use real links, buttons, form controls, or equivalently keyboard-operable controls instead of click-only facsimiles.
- Re-check that every control needed to reveal the current answer/help path can receive keyboard focus and be activated without pointer input.
- Avoid positive `tabindex` or CSS reordering that causes focus order to diverge from the visible task order unless there is a clearly better, testable reason.

## Visible focus and logical order

- Confirm that the current focus target is visibly identifiable throughout the reviewed path.
- Make sure focus order follows the visible or task order closely enough that voters do not lose orientation.
- Re-check that sticky content or other author-created layers do not hide the focused component during ordinary keyboard movement.

## Traps, dynamic updates, and fallback

- Confirm that widgets, disclosures, menus, and utility controls do not trap keyboard focus.
- After lookups, validation, or route-state changes, make sure the next relevant control or answer region remains discoverable and reachable.
- Preserve a visible first-party help/contact fallback when a control-specific keyboard failure makes the main route unreliable.

## Evidence posture

- Preserve only route labels, reviewed keyboard paths, focus-visibility state, focus-order state, keyboard-trap state, dynamic-update continuity state, and last review time.
- Do not preserve per-user keystroke logs, accessibility-session recordings, or other detailed interaction telemetry when bounded policy reconstruction is sufficient.
