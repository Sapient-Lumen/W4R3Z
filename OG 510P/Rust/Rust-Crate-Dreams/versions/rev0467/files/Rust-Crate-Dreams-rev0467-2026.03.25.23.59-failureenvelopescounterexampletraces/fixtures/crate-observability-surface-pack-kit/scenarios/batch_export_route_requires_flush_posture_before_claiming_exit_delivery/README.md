# Scenario family — batch export route requires explicit flush posture before claiming exit delivery

This fixture family exists for crates that export traces or logs through batch processors.

It is meant to catch support drift such as:

- the crate advertises an OpenTelemetry route as part of its official support surface,
- but the route only becomes honest on clean shutdown, `force_flush`, or last-provider drop,
- or the route summary talks like spans/logs are delivered synchronously,
- or exit-sensitive routes are described as if they were complete by default.

A good observability pack should make four things explicit:

1. whether the route is batch async rather than inline,
2. whether `force_flush`, `shutdown`, or last-provider-drop is relied on,
3. whether timeout-sensitive shutdown still leaves manual-review territory,
4. and whether the completeness class remains `exit_sensitive` when no stronger guarantee exists.
