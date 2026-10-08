# Official voter-information third-party dependency checklist

Use this quickcheck when an election office needs a bounded way to keep critical public-answer routes legible even when external scripts, embeds, or other third-party origins are blocked, slow, or unavailable.

## Dependency inventory

- Identify a small set of critical public-answer routes that should remain legible without waiting on third-party reveal logic.
- Inventory the third-party origins or dependency classes present on those routes.
- Re-check that inventory after redesigns, vendor swaps, new tag-manager additions, experiment launches, or election-crunch publishing changes.

## Critical-path separation

- Keep the core answer, next-step guidance, and official help/contact lane in first-party controlled content.
- Treat maps, chat tools, media embeds, translation helpers, analytics, and similar vendor additions as supplemental unless a first-party equivalent is present.
- Lazy-load or defer non-primary embeds where feasible.
- Do not let a critical answer route become “wait for the vendor widget.”

## Failure and fallback posture

- Test what the page does when the main third-party origins are blocked, slow, or unavailable.
- Confirm that blocked external resources degrade to a visible first-party answer or help lane, not a blank shell, partial layout, or endless spinner.
- Distinguish third-party-origin failure from no-JavaScript failure, overload posture, and anti-bot posture.
- Re-check the route with privacy extensions, filtered networks, or request-blocking tools in mind.

## Governance and hardening

- Keep tag-manager and experiment scope narrow on critical answer routes.
- Review CSP, sandbox, or allowed-origin posture against the dependencies actually in use.
- Audit whether old third-party scripts still add clear value; remove them when they do not.
- Be careful with self-hosting or mirroring vendor code: improved availability control can create update and security-lag risks.

## Evidence posture

- Preserve only route labels, dependency classes, optional-vs-critical classification, first-party fallback state, tag-manager/experiment scope, allowed-origin/CSP review state, and last review time.
- Do not preserve sprawling vendor dashboards, per-user script-failure logs, full request waterfalls, or large CSP-violation feeds when bounded policy reconstruction is sufficient.
