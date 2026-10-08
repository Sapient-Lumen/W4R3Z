# Scenario: pubtime cooldown and as-of replay keep a fresh release out of the frozen basis

A team froze a starter set for `async_http_service` on 2026-01-15.
A promising new release appeared on 2026-01-14, but policy required a 72-hour cooldown before that release could be treated as freezeable evidence.

This scenario exists to prove that:

- `pubtime` can bound what was actually knowable and admissible at freeze time,
- current-view enthusiasm for a just-published crate must not rewrite the frozen decision basis,
- and replay should remain explicit about what was excluded by policy rather than pretending the old decision ignored obvious information.
