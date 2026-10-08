# Official voter-information embedded-browser surface checklist

Use this quickcheck when an election office needs a bounded way to keep official voter-information routes readable and recoverable inside in-app browsers, webviews, or other constrained browser containers.

## Inventory and classification

- Identify the critical public-answer routes that voters commonly reach inside embedded or constrained browser containers.
- Classify whether the relevant container is browser-backed, app-controlled, weak in browser chrome, or known to alter download/deep-link/new-context behavior.
- Keep this separate from intentional external handoffs, ordinary sign-in walls, and device-permission prompts.

## Public-read boundary

- Confirm that a voter can still read the current official answer before being told to switch into a different browser.
- Do not make “open this in a real browser first” the price of first contact when the current answer can be shown safely on the page.
- Preserve the ordinary help lane even when the constrained container is a poor execution environment.

## Escape hatch and source clarity

- Expose a visible open-in-browser action, copyable canonical URL, or equivalent first-party recovery path when container behavior becomes the problem.
- Preserve enough first-party source identity that the voter can still tell the page is official even if address-bar chrome is weak or absent.
- Avoid assuming the host app gives users obvious share/copy/history affordances.

## Navigation and handoff recovery

- Re-check back navigation, return-to-page expectations, and host-app back-button behavior in constrained containers.
- Re-check downloads, deep links, popup/new-context workflows, and handler launches from constrained containers.
- Keep a first-party recovery lane visible when those actions behave differently from the full browser.

## Session and shared-state assumptions

- Do not silently assume remembered full-browser cookie/session state behaves the same way inside every constrained container.
- Re-check routes whose success depends on browser-shared state, sign-in continuity, or external-application return behavior.
- Treat container-specific breakage as a bounded public-answer failure, not as generic app noise.

## Evidence posture

- Preserve only route labels, container classes, public-read state, open-in-browser/copy-link recovery state, source-identity visibility state, navigation/handoff recovery state, shared-state-assumption state, and last review time.
- Do not preserve device fingerprints, app identifiers, browsing histories, referrer exhaust, or per-user embedded-browser telemetry when bounded policy reconstruction is sufficient.
