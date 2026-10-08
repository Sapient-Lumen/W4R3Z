# Replace preview plan (rev749)

Rev749 adds a side-effect-free replace planner for the editor replace family.  The goal is to make bulk-edit trust inspectable before mutation: the editor can now answer how many replacements would happen, where the first samples are, what text would be replaced, and what replacement text would be inserted.

## Surfaces

- `micromax_editor.replace_plan.plan_replace(...)` returns a plain `ReplacePlan` object.
- `Editor.replace_plan(...)` adapts that planner to the active buffer, cursor, and `ignorecase` option.
- `replace` and `replaceall` now execute through the same plan before mutating.
- `replacepreview SEARCH VALUE [-a] [-l]` reports the plan without editing the buffer.
- `ed.replace-preview` exposes the same plan to Micromax scripts as a hostcall.

## Plan shape

`ReplacePlan` keeps both commit data and preview witnesses:

```python
ReplacePlan(
    ok=True,
    count=2,
    replace_all=True,
    literal=True,
    case_sensitive=False,
    start_index=0,
    matches=(ReplaceMatch(...),),
    new_text="X two X",
)
```

Hostcall rows use zero-based editor coordinates and a stable plain-list shape:

```text
[ok count replace_all literal case_sensitive start_index error rows]
```

Each match row is:

```text
[line col end_line end_col old new]
```

The command bar-facing message intentionally stays compact:

```text
replacepreview: would replace 2 occurrences; first 1:0 "one" -> "X" (+1 more)
```

## Trust policy

The planner mirrors the existing replace-family semantics:

- empty searches are rejected before planning
- invalid regex patterns fail without mutating
- zero-width regex matches fail before a partial edit can happen
- regex replacement templates are validated even when there are no matches, so `$2`/`$missing` mistakes are not hidden behind `not found`
- literal replacement honors the editor's `ignorecase` option the same way `replace` did before rev749

`ed.replace-preview` preflights its public argument shape before consuming the request.  If a script passes a non-string search/value or a non-integer flag, the original request data remains on the stack for inspection after the hostcall name has been consumed by the generic `hostcall` primitive.

## Why this is a seam

Before rev749, `replace` contained both planning and mutation logic in one command function.  That made it hard to expose trustworthy previews without duplicating semantics.  The new seam gives future work one place to extend:

- richer multi-sample preview rows
- prompt-current preview for typed replace commands
- qreplace startup preview/count reuse
- optional apply-with-plan checks that reject stale buffer versions
