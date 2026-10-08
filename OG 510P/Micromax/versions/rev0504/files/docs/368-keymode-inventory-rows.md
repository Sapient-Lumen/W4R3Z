# Keymode inventory rows (rev426)

`showkeymodes` was already a useful tiny human-facing snapshot, but it still lived only as ad hoc command text. Scripts could inspect `ed.keymode-rows`, yet that lower-level hostcall returned two separate values (`active` rows plus `known` mode names) and left the final human-facing register to local policy: callers still had to join stacks, synthesize the default `global` active row, and remember to hide tiny internal modes from the `known` line.

Rev426 keeps the fix deliberately small:

- `Editor.keymode_inventory_rows()` now exposes the exact active/known register behind plain `showkeymodes`
- hostcall `ed.keymode-inventory-rows` returns those rows directly
- plain `showkeymodes` now reuses the same row surface instead of rebuilding it inline

Wire shape:

```text
[[section mode once?] ...]
```

Examples:

```text
[["active", "global", 0], ["known", "global", 0]]
[["active", "goto", 1], ["active", "nav", 0], ["known", "global", 0], ["known", "goto", 1], ["known", "nav", 0]]
```

Why keep this even though `ed.keymode-rows` already exists? Because the two hostcalls answer different questions:

- `ed.keymode-rows` = raw active stack + raw known mode names
- `ed.keymode-inventory-rows` = the tiny already-curated human register behind `showkeymodes`

That split matches the rest of the editor's recent inventory cleanup: keep the lower-level raw substrate when it is useful, but also expose the exact human-facing register once humans already rely on it.
