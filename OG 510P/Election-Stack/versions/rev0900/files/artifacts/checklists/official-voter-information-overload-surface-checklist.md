# Official voter-information temporary-overload checklist

Use this quickcheck when an election office needs a bounded way to keep current official voter-information pages legible during demand spikes, queue-page states, or short-lived service strain.

## Route scope

- Identify a small set of critical public-answer routes that should remain legible or explicitly temporarily unavailable under overload.
- Include the ordinary help/contact recovery lane in that critical set.
- Re-check the set after redesigns, migrations, election-calendar crunch periods, emergency notices, or major vendor/CDN changes.

## Temporary-state semantics

- Distinguish sitewide temporary unavailability from client-specific rate limiting.
- Use visibly temporary overload posture for routes that cannot safely serve normal traffic.
- Expose `Retry-After` or equivalent next-check guidance when feasible.
- Do not let an actually unavailable answer route masquerade as a blank or misleading `200 OK` success shell.

## Queue / holding page quality

- Keep temporary overload pages lightweight and low-dependency.
- Confirm the holding page still exposes the current official notice or answer boundary, not just branding.
- Confirm the holding page still exposes the ordinary help/contact lane.
- Minimize off-page resources so the temporary page still renders under the same strained conditions that triggered it.

## Discovery and continuity

- Protect crawler/discovery posture during short-lived overload; avoid accidentally turning temporary strain into permanent disappearance.
- Treat queue/waitroom posture separately from anti-bot challenge posture.
- Re-check official status/help/social/listing surfaces if they are being used as the continuity lane while the primary route is shedding load.
- Review whether a same-day or near-deadline event needs a more prominent official notice while overload persists.

## Evidence posture

- Preserve only route labels, overload classification state, temporary HTTP semantics, Retry-After/next-check posture, lightweight-page/dependency posture, help/notice continuity state, crawler/discovery boundary state, and last review time.
- Do not preserve giant load-test dumps, vendor dashboards, detailed capacity graphs, or sensitive abuse telemetry when bounded policy reconstruction is sufficient.
