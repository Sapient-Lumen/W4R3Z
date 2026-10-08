# Rev336: command palette file opens now report the landed target

Micromax's recent trust/flow work has been steadily enforcing one tiny rule: when an ordinary navigation or open action succeeds, the editor should say where it actually landed instead of expecting the user to infer it from screen state alone. `open`, buffer switching, jump commands, picker-driven docs navigation, and ordinary help browsing already follow that rule.

One common path still broke the pattern: selecting a `recentfile` or `openpath` row from `commandpick` opened the file, but the success path stayed verbally silent. That made the command palette feel subtly less trustworthy than the explicit `open ...` command even when both landed in the same place.

Rev336 fixes that with a deliberately tiny change. Successful file-opening selections from the command palette now report the same style of landed target as explicit open flows: `opened: path @ line:col`. Directory drill-down remains unchanged, and failure/capability messages stay as they were.

This is intentionally small, but it keeps the palette aligned with the broader product direction:

- **trust:** successful file-opening paths should say what happened
- **flow:** searchable open paths should preserve orientation, not just teleport state
- **coherence:** `commandpick` should not feel like a separate, quieter dialect of the editor

Focused tests pin both the recent-file path and the direct `openpath` path so this does not regress quietly later.
