# Scenario — hot-lib-reloader reload events make handoff explicit, not magical

`hot-lib-reloader` exposes `wait_for_about_to_reload` and `wait_for_reload` events and explicitly points to serialize/deserialize handoff as the way to bridge state around reload.

That means an iteration bundle should separate:
- the reload route existing,
- fresh code becoming reachable after the handoff boundary,
- and continuity that depended on explicit serialization or reinitialization.
