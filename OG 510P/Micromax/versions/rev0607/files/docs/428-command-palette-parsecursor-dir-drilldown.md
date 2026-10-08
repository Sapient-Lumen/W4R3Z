# Rev428? no, rev486: command-palette parsecursor directory drill-down

Problem:
- rev483 taught visible directory rows to say `drill down`, and rev482/rev485 taught the exact typed `Open` row to reuse more of Micromax's real path context.
- With `parsecursor` enabled, the typed open row for a query like `guide/:2` already normalized to `directory | drill down`.
- But submit still checked the raw unparsed query for drill-down, so Enter failed as `open: is a directory: guide` instead of reopening the palette inside `guide/`.
- Right before Enter, the row and the submit path disagreed about the same target.

What changed:
- Tightened the `openpath` submit branch in `src/micromax_editor/editor.py`.
- The capability-gated directory drill-down check now parses the target first with the same shared `_parse_open_target(...)` helper used by the later open path.
- When the parsed target is a directory, palette submit now reopens the palette on that real folder even if the typed query carried a `:line[:col]` suffix.

Why this matters:
- This is a trust fix, not a new feature.
- A visible palette row should not promise `directory | drill down` and then fail because submit looked at a different spelling of the same target.
- The shared `parsecursor` path now stays honest across both row rendering and submit behavior.

Constraints kept:
- No new host capability.
- No new command/hostcall surface area.
- The drill-down still respects `cap.fs-list` and `cap.fs-root`; only the target normalization changed.
