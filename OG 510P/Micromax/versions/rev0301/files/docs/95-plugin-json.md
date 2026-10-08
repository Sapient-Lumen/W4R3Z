# `plugin.json` metadata (rev71)

Plugins are directories under a plugin root (default: `plugins/`) containing an init file
and (optionally) a `plugin.json`.

This file is intentionally small:
- no extra dependencies (we do not pull in a JSON schema validator)
- validation errors are designed to be obvious and actionable

## Minimal schema (v1)

All keys are optional unless stated otherwise.

```json
{
  "name": "example",              // optional; if present must match directory name
  "version": "0.1.0",             // optional; semver-ish
  "description": "…",             // optional
  "entry": "init.mx",             // optional; relative path inside the plugin dir
  "requires": ["other-plugin"]    // optional; plugin names, loaded first when present
}
```

Back-compat alias:
- `dependencies`: treated the same as `requires` when `requires` is absent.

Unknown keys are preserved in `Plugin.meta` so future tooling can evolve without breakage.

## Load order and dependency handling

When `requires` is present:
- the plugin manager attempts a dependency-aware load order (toposort)
- if a dependency is missing, the plugin is skipped and a non-fatal load error is recorded
- if a dependency cycle is detected, the cycle is reported and the remaining plugins are
  loaded in lexical order (best-effort)

## Entry file selection

If `entry` is present, the plugin manager loads that file.

Otherwise, it searches for the first existing entry in this order:
- `init.mx`
- `init.mmx`
- `init.mf`

The entry path must be relative to the plugin dir (no absolute paths, no `..` segments).

## Example

Directory:

```
plugins/
  autosave/
    plugin.json
    init.mx
```

`plugin.json`:

```json
{
  "version": "0.2.0",
  "description": "Save on idle",
  "requires": [],
  "entry": "init.mx"
}
```



## Host access

The editor exposes a tiny plugin-management host API:
- `plugin.list`
- `plugin.reload`
- `plugin.errors`

The `plugin` command (`plugin list`, `plugin reload NAME`) also surfaces recent load errors.
