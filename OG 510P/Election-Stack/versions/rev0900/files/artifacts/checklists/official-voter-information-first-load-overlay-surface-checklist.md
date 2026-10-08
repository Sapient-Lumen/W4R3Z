# Official voter-information first-load overlay checklist

Use this quickcheck when an election office needs a bounded way to keep cookie/consent notices, privacy overlays, or other first-load administrative modals from blocking the public answer lane.

## Inventory and classification

- Identify the critical public-answer routes that show a first-load overlay or sticky consent/policy notice.
- Classify whether the overlay is a cookie/tracking notice, privacy/policy notice, preference-center handoff, or some other administrative first-load overlay.
- Keep this separate from official emergency/status alerts and separate from sign-in or CAPTCHA walls.

## Answer-lane priority

- Confirm that a voter can read the current official answer and reach the ordinary help lane without accepting optional tracking, experimentation, or personalization.
- Keep the overlay short, plain-language, and clearly subordinate to the route.
- Do not turn the overlay into a scrolling mini-site or the main first-contact experience.

## Dismissibility and accessibility

- Make sure close or choice controls are visible on small screens and at zoom.
- Re-check keyboard navigation, focus visibility, portrait/landscape mobile behavior, and screen-reader behavior in the real implementation.
- Do not let sticky banners or overlays obscure the focused control, footer help links, or the close/choice controls themselves.

## Dismissal and failure posture

- Confirm that dismissing or rejecting the overlay removes the overlay but does not silently swap the page to a different answer route or blank shell.
- Test the route with overlay scripts/components blocked or degraded.
- If the consent manager or overlay component fails, fail open to a readable first-party answer or help lane.

## Evidence posture

- Preserve only route labels, overlay classes, optional-consent boundary state, answer-lane visibility state, dismissibility/mobile-focus review state, dismissal side-effect state, fail-open state, and last review time.
- Do not preserve per-user consent records, tracking identifiers, long banner-interaction telemetry, or full consent-manager exports when bounded policy reconstruction is sufficient.
