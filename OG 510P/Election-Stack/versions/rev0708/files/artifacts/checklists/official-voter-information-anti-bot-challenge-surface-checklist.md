# Official voter-information anti-bot challenge checklist

Use this quickcheck when an election office needs a bounded way to keep current voter-information pages reachable to humans and crawlers while still controlling obvious abuse.

## Route scope

- Identify a small set of basic read-only public-answer routes separately from abuse-sensitive routes.
- Keep the office/help recovery lane in the basic public-answer set.
- Re-check the route split when new lookup flows, report forms, or search endpoints are introduced.

## Challenge posture

- Do not default every public answer page into the same CAPTCHA or managed-challenge wall.
- Prefer lighter controls on basic public-answer routes and stronger controls on abuse-sensitive routes.
- Re-check whether temporary challenge states are returning semantically wrong `200` success responses.
- Keep retry/help cues visible when a legitimate user may be blocked.

## Accessibility and recovery

- If CAPTCHA or similar human verification is used, confirm an accessible alternative exists.
- Avoid image-only CAPTCHA assumptions.
- Confirm the challenge step does not break the larger voter-help or reporting process.
- Keep a direct official help/contact lane visible from challenge state.

## Crawler posture

- Verify wanted crawler identity before blocking decisions are made.
- Review WAF/CDN rules for accidental crawler challenges after major traffic spikes or rule changes.
- Confirm discovery-critical crawlers are not quietly trapped behind challenge interstitials.
- Treat temporary crawler challenge states as temporary unavailability rather than successful fetches of the official answer page.

## Evidence posture

- Preserve only route labels, challenge-scope policy state, accessible-alternative state, help-lane visibility state, crawler verification/allow posture, temporary interstitial response posture, and last review time.
- Do not preserve raw WAF logs, device-fingerprint recipes, full IP blocklists, browser fingerprint data, session replays, or giant vendor debug exports when bounded policy reconstruction is sufficient.
