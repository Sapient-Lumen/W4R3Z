# Scenario — hot-lib-reloader before/after events bracket reload, not old-generation drain

`hot-lib-reloader` exposes `wait_for_about_to_reload` and `wait_for_reload`, and explicitly recommends serialization / deserialization around those events.
Those hooks are strong handoff boundaries, but they do not by themselves prove that all old callbacks, tasks, or route families drained.
