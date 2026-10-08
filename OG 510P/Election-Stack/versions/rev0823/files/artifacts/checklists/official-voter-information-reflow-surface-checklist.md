# Official voter-information reflow surface checklist

Use this quickcheck when an election office needs a bounded way to keep official voter-information routes readable and actionable on narrow viewports, enlarged text, browser zoom, and similar small-screen states.

## Inventory and review scope

- Identify the critical public-answer routes most likely to be reached on phones, narrow browser windows, enlarged-text states, or magnified views.
- Distinguish this from generic performance review, low-connectivity review, first-load overlay review, and embedded-browser quirks.
- Re-check routes whose current answer depends heavily on fixed-width cards, sticky chrome, tables, maps, embedded viewers, or compact side-by-side layouts.

## Zoom and text-resize posture

- Confirm that the route does not disable user zoom or otherwise assume the default text size is the only legitimate reading state.
- Re-check that critical text, labels, buttons, dates, hours, and contact paths remain usable when text is resized to the bounded review threshold.
- Keep viewport, magnification, and text-resize behavior separate from answer-variance or experimentation logic.

## Reflow and reading path

- Confirm that ordinary reading content reflows without requiring horizontal panning through text.
- Prefer a linear or single-column reading path for first contact when the viewport is narrow.
- Treat maps, tables, and other genuinely two-dimensional elements as bounded exceptions rather than the only answer lane.

## Controls, chrome, and fallback

- Re-check whether sticky headers, footers, floating widgets, or utility rails hide the answer lane or critical controls on small screens.
- Make sure lookup fields, submit buttons, and help/contact controls remain reachable and labeled when the viewport shrinks or text grows.
- Preserve a parallel readable text/help fallback when a map, table, viewer, or other two-dimensional subcomponent becomes hard to use.

## Evidence posture

- Preserve only route labels, reviewed viewport classes, text-resize/zoom state, reflow state, bounded horizontal-scroll exceptions, control-visibility state, text-fallback state, and last review time.
- Do not preserve detailed device fingerprints, per-user viewport histories, zoom telemetry, accessibility-preference exhaust, or other client traces when bounded policy reconstruction is sufficient.
