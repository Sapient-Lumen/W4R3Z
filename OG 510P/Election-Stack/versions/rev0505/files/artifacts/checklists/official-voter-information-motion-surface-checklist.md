# Official voter-information motion and interruption-safe surface checklist

Use this quickcheck when an election office needs a bounded way to keep official voter-information routes readable without automatic movement, rotating panels, animated urgency theater, or interruption-heavy live updates becoming the price of understanding the current answer.

## Inventory and review scope

- Identify the critical public-answer routes most likely to move on their own: rotating heroes, live-status banners, countdowns, queue advisories, maps, lookup results, skeleton loaders, and emergency notices.
- Distinguish this from freshness review, screen-reader review, keyboard-only review, contrast review, and low-connectivity review.
- Re-check routes whose meaning depends on motion-first treatments such as carousels, pulsing warnings, shimmering placeholders, or scroll-linked animation.

## Reduced motion and still-reading path

- Confirm that non-essential motion respects reduced-motion preference where practical.
- Preserve a stable reading path for the current answer/help lane instead of assuming the default animated path is acceptable for everyone.
- Do not make the voter discover the answer only after waiting through a rotating or auto-advancing component.

## Automatic movement and interruption control

- Confirm that moving, blinking, scrolling, or auto-updating content that starts automatically has an obvious pause, stop, hide, disable, or still/manual alternative when needed.
- Re-check carousels, rotating notices, tickers, and auto-refresh panels whose motion competes with comprehension.
- Keep live updates from replacing or destabilizing the answer lane while a voter is reading.

## Interaction-triggered motion and urgency cues

- Re-check non-essential motion triggered by scrolling, hovering, focusing, filtering, map interaction, or form-state changes.
- Avoid making urgency, change, or next-step meaning depend on pulsing, flipping, sliding, or animated countdown behavior alone.
- Keep countdowns, deadline reminders, and queue/status signals understandable as stable text and labels even when motion is reduced or disabled.

## Evidence posture

- Preserve only route labels, reviewed motion-state paths, reduced-motion review state, pause/stop/manual-control posture, stable-answer-lane review state, and last review time.
- Do not preserve individualized motion-sensitivity guesses, medical/disability inferences, raw gaze or session telemetry, or exhaustive video captures when bounded policy reconstruction is sufficient.
