# Official voter-information router surface checklist

- Inventory each official interactive voter-information router, state selector, map-backed chooser, or decision-tree tool the public is expected to rely on.
- Make the delivery role explicit: the router helps the voter reach the current controlling official destination; it does not become the rule source by itself.
- Say what question class the tool helps with and what it does not safely decide.
- Make branch-affecting assumptions visible enough that users are not misled about what the tool concluded from their answers.
- Do not hide whether address, jurisdiction, military/overseas status, or other special-case facts materially change the route.
- Keep the current official source anchors identifiable for action-changing results.
- Preserve a bounded decision-path trace for action-changing outputs, including router version, branch identifiers, anchor identifiers, result state, and timestamp.
- Use a small result-state taxonomy so the interface can distinguish direct route, scoped route, conflict stop, and unsupported path.
- Stop on unresolved official conflict instead of synthesizing a confident jurisdiction-specific result.
- Make the human-help fallback visible, including the current office/help path and phone number when one exists.
- Keep the router aligned with the current FAQ/help pages, office directory, signed notices, and any companion chatbot or hotline surface that cover the same question.
- Minimize personal data collection and do not retain raw addresses, session details, or clickstream telemetry longer than the policy requires.
- Do not turn a public router into a shadow case-management system for protected or record-specific voter facts.
- Publish `last_verified_at` and re-check the router after source-anchor, branch-logic, office-routing, deadline, or superseding-notice changes.
- When material route logic changes, publish an explicit update/superseding note instead of relying only on silent UI edits.
