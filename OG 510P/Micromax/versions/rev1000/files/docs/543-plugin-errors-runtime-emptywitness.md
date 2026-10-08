# Rev602: runtime `plugin errors` keeps a live-inventory witness when the current error subset is empty

Problem:
- The no-arg runtime `plugin errors` path already distinguished `no plugin manager` from `0 plugin(s), 0 error(s)`.
- But when the plugin manager was live and healthy plugins existed, the runtime summary still flattened that state back to the same bare `0 plugin(s), 0 error(s)` line used by a truly empty configured manager.
- Nearby command-bar previews had already learned to keep a tiny broad inventory witness in that state.

Change:
- When `plugin errors` finds no current load errors, it now still checks the live plugin inventory.
- If any plugins are known, the summary becomes:
  - `plugin errors: 0 plugin(s), 0 error(s) · N plugin total · e.g. NAME [state, ...]`
- A genuinely empty configured manager still keeps the old compact `plugin errors: 0 plugin(s), 0 error(s)` line.

Why it matters:
- Headless plugin-debugging loops should not make a healthy live plugin system look identical to an empty one.
- This keeps the runtime no-arg `plugin errors` command aligned with the neighboring truthful-empty-subset preview work.

Tests:
- `test_plugin_errors_unfiltered_empty_is_count_aware`
- `test_plugin_errors_unfiltered_empty_keeps_inventory_witness`
