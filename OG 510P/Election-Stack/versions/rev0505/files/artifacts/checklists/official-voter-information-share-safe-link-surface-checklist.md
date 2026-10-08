# Official voter-information share-safe link surface checklist

Use this quickcheck when an election office expects the public to bookmark, copy, forward, or later revisit the current URL for an official voter-information route.

## Inventory and scope

- Identify routes where the office expects the current URL itself to act as part of the kept record or helper handoff.
- Distinguish this from stale-link recovery, printable/PDF kept-record posture, and generic confirmation/reference-number existence.
- Re-check routes where a voter is likely to bookmark, text, email, or reopen the current answer later.

## Revisit-state classification

- Decide whether each route is public-share-safe, same-user revisit-safe, or not safely shareable.
- Do not imply a URL is broadly safe to forward when it is really account-bound, case-bound, or session-bound.
- When the URL cannot safely do the job, name the substitute artifact or path that does.

## History and current-state alignment

- Review whether the visible URL and browser-history entry track the controlling answer state when the route changes content dynamically.
- Re-check Back/Forward and copy-link behavior for single-page or highly scripted routes.
- Do not let the user keep a generic launcher URL when the meaningful answer lived only in hidden in-memory state.

## Sensitive-parameter discipline

- Check that shareable or bookmarkable URLs do not expose secrets, one-time tokens, personal identifiers, or similar sensitive values.
- Treat URL-borne personal or secret values as a failure state, not as a convenient shortcut.
- If the route must remain personalized, state that boundary and provide a first-party re-entry/help path.

## Evidence posture

- Preserve route labels, revisit-state classes, history-state alignment notes, sensitive-parameter policy, safe fallback/reference posture, help routing, and last review time.
- Do not preserve raw copied URLs from real voter sessions, forwarding telemetry, browser-history exports, or secret-bearing query strings when bounded policy reconstruction is sufficient.
