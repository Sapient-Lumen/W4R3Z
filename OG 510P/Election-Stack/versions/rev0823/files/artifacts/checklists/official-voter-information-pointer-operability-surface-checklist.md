# Official voter-information pointer-operability surface checklist

Use this quickcheck when an election office needs a bounded way to keep official voter-information routes operable with ordinary touch, stylus, or coarse-pointer input and without hover-only or gesture-only discovery becoming the price of understanding the current answer.

## Inventory and review scope

- Identify the critical public-answer routes most likely to fail under touch or coarse-pointer use: lookup forms, filters, tabs, accordions, map pins, “more info” affordances, close buttons, language toggles, directions links, and help/contact fallbacks.
- Distinguish this from small-viewport reflow review, keyboard-only review, screen-reader review, map-content review, and motion review.
- Re-check routes whose critical actions depend on tiny icons, dense clusters of controls, hover cards, flyouts, swipe gestures, or draggable widgets.

## Target size and spacing

- Confirm that the critical next-step, details, dismiss, and help controls expose an adequately sized or adequately separated activation area for ordinary touch and coarse-pointer use.
- Re-check chips, tabs, date selectors, pagination controls, close icons, and disclosure chevrons that are visually present but easy to miss or mis-hit.
- Do not make the current answer/help lane depend on pixel-precision interaction with small icons or densely packed controls.

## Hover-revealed content and no-hover fallback

- Confirm that hover-triggered deadline notes, explanations, office-hour details, or warnings are still reachable without hover.
- Re-check menus, flyouts, popovers, tooltips, and map/list disclosures whose content disappears when the pointer moves or cannot be revealed on no-hover devices.
- Keep the authoritative answer available as visible text, an explicit disclosure action, or another no-hover path instead of a mouseover-only hint.

## Gesture dependence, dense maps, and fallback

- Re-check routes that use swipe, drag, trace, or fine-grained map interaction to reveal or change the answer.
- Preserve a simple tap/select/list alternative when a path-based or multipoint gesture would otherwise control the answer lane.
- Make sure map pins, clustered markers, or dense controls affecting the answer can be backed by a readable list/text fallback and a plainly visible first-party help/contact route.

## Evidence posture

- Preserve only route labels, reviewed pointer-state paths, target-size/spacing review state, hover-fallback review state, gesture-alternative state, dense-control fallback state, and last review time.
- Do not preserve raw touch traces, clickstream/session telemetry, individualized motor-ability guesses, or exhaustive device-video collections when bounded policy reconstruction is sufficient.
