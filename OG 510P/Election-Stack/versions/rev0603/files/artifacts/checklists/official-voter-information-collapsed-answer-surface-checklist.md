# Official voter-information collapsed-answer surface checklist

Use this quickcheck when an election office publishes current voter-information answers inside accordions, disclosures, expandable FAQ items, or other hide/reveal containers.

## Inventory and scope

- Identify official routes where the controlling answer, exception, or next-step boundary is hidden inside a collapsed panel.
- Distinguish this from section-target continuity, reader-mode extraction, keyboard/focus operability, and generic JavaScript dependency at the route level.
- Re-check routes where copied links, “On this page” navigation, or ordinary returns may land near a disclosure that still needs to be opened.

## Reveal policy and answer visibility

- Keep the controlling answer visible by default when most users need it, or make the reveal path unmistakable when collapse is justified.
- Do not bury a mandatory rule, deadline, or disqualifying condition inside a stack of generic closed panels.
- Treat the visible disclosure label as part of the public answer surface, not a cosmetic afterthought.

## Labels, defaults, and direct targeting

- Use panel labels that state the real voter question or condition rather than vague text such as “More information” or “Details.”
- Check whether critical panels should be open by default, summarized visibly, or auto-opened on direct targeting.
- Verify that copied fragments, jump links, and ordinary revisits reveal the relevant panel instead of landing near a still-collapsed answer.

## Degraded script and implementation context

- Review what happens if enhancement code does not load, partially loads, or loses state after navigation or refresh.
- Do not rely on hidden closed-state content as the only copy of a critical answer unless the degraded path still preserves honest visibility or recovery.
- Test heading structure, button semantics, expanded/collapsed state, keyboard flow, screen-reader behavior, zoom, and small-screen readability in the real route context.

## Evidence posture

- Preserve reviewed routes, critical disclosures, default-open policy notes, label-specificity notes, direct-target reveal posture, degraded-script posture, and last review time.
- Do not preserve named-user disclosure-click telemetry, individualized expansion histories, or session-replay exhaust when bounded policy reconstruction is sufficient.
