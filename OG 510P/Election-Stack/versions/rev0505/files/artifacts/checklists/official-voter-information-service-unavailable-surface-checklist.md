# Official voter-information service-unavailable surface checklist

Use this quickcheck when an election office needs a bounded way to keep official voter-information routes workable during temporary unavailability, planned maintenance, or partial degradation.

## Inventory and review scope

- Identify critical public routes that can enter a temporary-unavailable, maintenance, or partially degraded state.
- Distinguish this from overload/queue posture, in-session waiting, pending review, or a final unsuccessful voter-specific result.
- Re-check routes where deadline pressure makes downtime or partial loss especially risky.

## Service-state clarity

- State in ordinary language whether the route is temporarily unavailable, under maintenance, or only partly working.
- Name what still works and what is affected instead of using one generic outage phrase for every condition.
- Do not let a blank shell, generic 404, or no-result message stand in for a temporary service problem.
- Provide one clear next action: retry later, read the latest official notice, use an alternate official lane, or contact the office.

## Retry, fallback, and restoration posture

- Provide a bounded retry-after or check-back cue whenever the condition is known or expected to be temporary.
- Keep a direct official help/contact lane visible when the primary route is unavailable.
- Show the latest current notice or restoration update when service state may change over time.
- Make sure fallback guidance matches the underlying substantive surface and does not quietly reroute users to a wrong office or stale page.

## Accessibility and reviewability

- Keep unavailable/degraded-state messages available in accessible text on mobile, at zoom, with keyboard navigation, and with screen readers.
- Do not rely only on color, iconography, or a transient banner to communicate service state.
- Use a visible site-wide or page-level status treatment when the issue affects many pages or users.
- Test the unavailable/degraded state in project context, not just the normal success path.

## Evidence posture

- Preserve only route labels, reviewed unavailable-state paths, affected-function scope, fallback/check-back review state, HTTP-semantics review state, and last review time.
- Do not preserve raw outage telemetry, internal incident tickets, vendor case IDs, per-user failure logs, or backend root-cause notes when bounded public-state reconstruction is sufficient.
