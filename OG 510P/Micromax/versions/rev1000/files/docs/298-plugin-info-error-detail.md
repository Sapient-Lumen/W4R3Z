# Rev356: plugin info should show current error detail directly

The plugin loop had become honest almost everywhere:
- `plugin list` exposed inventory clearly
- `plugin reload NAME` confirmed the resulting state
- `plugin errors [NAME]` showed failure detail plainly
- `pluginpick` rows, previews, and section labels reused the same compact summary dialect

But one ordinary path still hid too much.

When a person types `plugin info NAME`, they are asking for detail. Before this revision, broken plugins still only showed a line like `errors: 2 (last: ...)`, which meant the natural detail path still pushed people into an immediate second `plugin errors NAME` round-trip just to see the actual current failure lines.

## What changed

`plugin info NAME` now behaves more like a real detail surface:
- healthy plugins now say `errors: 0` after the rev363 count-aware follow-up (rev356 originally used `errors: (none)`)
- broken plugins say `errors: N`
- current recorded error lines are listed directly under that count

Example:

```
plugin info: b [error, deps:missingdep]
  entry: main.mx
  root: /tmp/.../plugins/b
  requires: missingdep
    - missingdep: missing
  errors: 1
    - missing dependency: missingdep
```

Healthy plugins stay explicit too:

```
plugin info: a [loaded, v1.0.0]
  version: 1.0.0
  entry: main.mx
  root: /tmp/.../plugins/a
  desc: demo plugin
  errors: 0
```

## Why this matters

This is small, but it keeps the detail path honest.

A detail command should not make users infer whether the current error shape is empty, singular, or multi-line. It also should not make the first follow-up action be another command just to see the actual lines behind a summary count.

That keeps plugin inspection aligned with the repo's current product direction:
- trust first
- tiny inventory/detail paths that tell the truth
- searchable and plain command paths that stay in one coherent dialect
