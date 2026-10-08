# Official voter-information external-handoff surface checklist

Use this quickcheck when an election office intentionally sends voters from a current official page to another site, origin, application handler, file, or new browsing context.

## Inventory and classification

- Identify the current critical public routes that intentionally hand users to another destination or context.
- Classify whether the handoff is external/non-federal, auth-required, file/application-based, or new-context (`_blank`, popup, or similar).
- Keep this separate from third-party code that executes inside the current page.

## Destination clarity

- Confirm that the first-party page tells the voter where the handoff goes and why it exists before the jump.
- Label external or non-federal destinations clearly and consistently.
- Label authentication-required destinations, non-HTML/file launches, and new-tab/new-window behavior where they occur.

## Directness and trigger quality

- Link directly to the most relevant destination rather than a generic vendor or portal homepage.
- Use a real link for real navigation targets; avoid fake anchors or JS-only click traps as the sole viable route.
- Do not make a popup or secondary window the only way to reach the next official step.

## Recovery and fail-open posture

- Preserve a first-party answer/help lane when the external destination, new context, or application handler fails or is no longer authoritative.
- Keep ordinary browser affordances usable where practicable, including copy/open/bookmark behavior.
- Re-check blocked-popup, JS-disabled/error, and handler-unavailable states for routes that rely on outbound jumps.

## Notice quality

- Meet non-federal/external notice needs without turning every handoff into a disruptive roadblock modal.
- Use descriptive link text and context instead of vague controls like “Continue” or “Go now” where the destination would otherwise be unclear.
- Indicate file type/size for non-HTML resources when the link may trigger a download or application launch.

## Evidence posture

- Preserve only outbound route labels, destination classes, direct-destination state, same-tab/new-context/handler state, recovery posture, and last review time.
- Do not preserve individualized outbound clickstreams, browsing histories, or cross-site telemetry when bounded policy reconstruction is sufficient.
