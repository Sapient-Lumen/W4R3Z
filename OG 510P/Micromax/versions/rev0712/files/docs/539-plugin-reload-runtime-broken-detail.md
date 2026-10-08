# Rev598 — runtime `plugin reload NAME` keeps broken-target detail

Problem: exact `plugin reload NAME` completion rows already preserved real broken-target detail — `missing dependency: ... · not loaded` for one error and `N load errors · last: ... · not loaded` for multi-error targets — but the after-Enter reload action path still flattened the same known broken state back to a generic `errors: N` header plus bullets.

Why it matters: reload is an action surface, but it is also the fastest exact recovery/debug loop when one plugin fails to load. If Micromax already knows why the target is broken, the post-Enter feedback should not be less truthful or less legible than the pre-Enter row.

What changed:
- `Editor.plugin_reload_with_feedback(...)` now reuses `_plugin_exact_error_info(...)` for unloaded broken targets.
- Single-error failures now say `reload: missing dependency: ... · not loaded`.
- Multi-error failures now say `reload: N load errors · last: ... · not loaded` and still list the individual errors below.
- Available-but-unloaded targets keep the existing `reload: available plugin · not loaded` wording.

Guardrails:
- no host boundary changes
- no plugin state model changes
- no grouped picker changes
- healthy loaded reloads remain unchanged

Focused checks:
- `test_plugin_reload_failures_use_inventory_dialect_for_broken_and_unknown_targets`
- `test_plugin_reload_broken_target_keeps_multi_error_count_and_last_detail`
