# Cooperation benchmark programs should publish direct selected-command open-target audit fields for compact-card next-action surfaces

When a compact-card next-action surface already publishes one direct selected-command inspect target, it should also publish tiny audit witnesses for that human-open document.

Operational rules:

1. publish `selected_next_command_open_target_bytes` and `selected_next_command_open_target_sha256` alongside `selected_next_command_open_target`;
2. publish `selected_fallback_command_open_target_bytes` and `selected_fallback_command_open_target_sha256` alongside `selected_fallback_command_open_target`;
3. mirror those values onto `primary_action.target_open_target_bytes`, `primary_action.target_open_target_sha256`, `primary_action.fallback_open_target_bytes`, and `primary_action.fallback_open_target_sha256`; and
4. derive those witnesses from the same retained markdown/document paths named by the selected inspect targets, failing closed when the companion document is absent.

This keeps the post-command inspect step locally auditable without forcing inheritors to reopen manifests or unrelated report bindings just to confirm the exact retained document they are supposed to trust after running the first command.
