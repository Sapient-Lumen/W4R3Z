# Official voter-information low-connectivity surface checklist

Use this quickcheck when an election office needs a bounded way to keep official voter-information routes readable and recoverable on slow, fragile, or explicitly reduced-data network conditions.

## Inventory and review scope

- Identify the critical public-answer routes most likely to be reached over weak mobile signal, intermittent links, or reduced-data browsing.
- Distinguish this from true sitewide overload, challenge walls, embedded-browser quirks, and generic performance lab review.
- Re-check routes whose first contact currently depends on maps, media, large imagery, third-party widgets, or multi-request assembly before useful text appears.

## Initial answer lane

- Confirm that the current official answer/help lane appears before heavy media, maps, widgets, or noncritical follow-on requests complete.
- Do not hide already-known official text behind spinner-only waiting loops.
- Keep the first-contact lane text-first enough that a weak connection can still deliver it.

## Reduced-data handling

- Review whether `Save-Data`, reduced-data preferences, or similar low-transfer states change only the shell and not the underlying authoritative answer.
- Allow lighter media, styling, or polling/update behavior when appropriate, but do not create a second-class or stale answer route.
- Keep network-quality adaptation separate from answer-variance or experimentation logic.

## Optional media and manual fallback

- Re-check whether maps, media, and rich embeds are optional for first contact rather than the sole carrier of location, timing, or next-step instructions.
- Preserve a readable manual fallback for addresses, hours, deadlines, and office/help contact when rich assets stall.
- Keep a visible first-party help lane available even if secondary resources fail.

## Retry and user guidance

- Give bounded retry/refresh guidance when that is genuinely useful, but do not force indefinite retry loops as the only visible state.
- Distinguish weak-network user guidance from true temporary-unavailable or queue-page incident posture.
- Make sure the page still says what the voter should do next even before full enrichment arrives.

## Evidence posture

- Preserve only route labels, low-connectivity classes, initial-answer visibility state, optional-media fallback state, reduced-data handling state, help-fallback state, and last review time.
- Do not preserve carrier identifiers, IP-derived histories, per-user timing traces, device/network fingerprints, or detailed connection telemetry when bounded policy reconstruction is sufficient.
