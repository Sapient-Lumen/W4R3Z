# Official voter-information progressive-enhancement checklist

Use this quickcheck when an election office needs a bounded way to keep current voter-information pages usable even when JavaScript, widgets, or richer client behaviors degrade.

## Critical page scope

- Identify a small set of critical voter-task page classes rather than treating every page or component as equally important.
- Keep the office/help recovery lane in the critical set.
- Re-check the set when a new emergency page, lookup flow, or change-notice path is introduced.

## Basic-path review

- Confirm that major answer text appears in basic HTML or equally reliable server-rendered output.
- Confirm that the office/help lane remains visible without requiring a fragile widget initialization path.
- Prefer plain-language fallback text over spinner-only or blank-shell failure modes.
- Check degraded-client behavior on ordinary mobile conditions, not only a healthy desktop browser.

## Routing and link posture

- Keep critical next-step routes exposed through ordinary HTML links with `href` attributes.
- Avoid making the only recovery path depend on opaque click handlers, fragments, or script-only routers.
- Confirm that important notices and help destinations remain reachable even when richer navigation layers fail.

## Widget and dependency boundaries

- Treat map embeds, translation widgets, autocomplete layers, analytics/tag-manager additions, and consent/personalization logic as possible failure multipliers.
- Do not let optional widgets become the only way to reveal a current answer.
- Distinguish widgets that are optional enhancements from components that have become hidden mandatory gates.
- Re-check critical pages after template, CMS, localization, or third-party script changes.

## Evidence posture

- Preserve only critical page-class labels, progressive-enhancement review state, crawlable-routing state, rendered-answer visibility state, widget-boundary state, degraded-client recovery state, browser-support-boundary state, and last review time.
- Do not preserve full browser-matrix reports, raw JavaScript error streams, session replays, or full DOM dumps when bounded policy reconstruction is sufficient.
