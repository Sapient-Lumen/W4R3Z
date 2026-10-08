# `plugin.json` metadata (rev71)

Plugins are directories under a plugin root (default: `plugins/`) containing an init file
and (optionally) a `plugin.json`.

This file is intentionally small:
- picker/search/detail surfaces should expose plugin state, dependency shape, and error grouping legibly, not just raw names
- no extra dependencies (we do not pull in a JSON schema validator)
- validation errors are designed to be obvious and actionable
- ordinary `plugin info NAME` detail should expose current error state directly too, not merely hint that errors exist
- ordinary `plugin info NAME` detail should keep dependency inventory count-aware too, including an explicit `requires: 0` when a plugin has no declared requirements
- exact `plugin reload NAME` command-bar previews should expose current known load-failure detail too, not merely a load-error count when Micromax already knows the failing reason
- exact available `plugin reload NAME` preview/runtime paths should keep `available plugin · not loaded` state witness too, not flatten known candidates back to generic `plugin not loaded`

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

## Detail surfaces

`plugin info NAME` is the ordinary detail path. It should now be explicit about current error state too:
- healthy plugins say `errors: 0`
- broken plugins list their current recorded load errors directly
- `plugin errors [NAME]` remains the more failure-focused companion view when you want grouped error inspection first

`plugin load NAME` and `plugin reload NAME` should stay honest on failure too:
- broken known plugins start with the same summary line used by `plugin list` / `plugin info` / `plugin errors`
- those reload failures list current recorded load errors directly
- restricted reloads of available-but-unloaded candidates say to use `plugin load NAME` instead of silently evaluating source
- truly unknown names fail plainly as `plugin reload: no such plugin: NAME`

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
- `plugin.reload` (now reuses the same trust-first reload feedback dialect as command-bar `plugin reload NAME`, so live scripting does not drift back to older generic reload-error messages)
- `plugin.errors`

The `plugin` command (`plugin list`, `plugin load NAME`, `plugin reload NAME`, `plugin info NAME`, `plugin errors [NAME]`, `plugin grants`, `plugin revoke NAME`) also surfaces recent load errors and restricted manual-load grants, and plain `showplugin NAME` now gives the same state/version/dependency/error-count loop one tiny side-effect-free exact inspection path. `plugin list`, successful `plugin reload NAME`, `plugin info NAME`, and filtered `plugin errors NAME` now use the same small inspectable state/version/dependency dialect at the start of their output. `plugin list` also starts with a tiny count-aware prefix now, so broad plugin health is glanceable before you read the per-plugin entries. Unfiltered `plugin errors` now also behaves like inventory instead of a raw log dump: it starts with a tiny plugin/error count summary, keeps that same count-aware shape even when no plugins are broken, and groups detail lines under those same per-plugin summary entries when errors do exist. Truly unknown plugin names fail plainly as `plugin info: no such plugin: NAME` or `plugin errors: no such plugin: NAME`, and a known plugin with no current errors now says so explicitly. `plugin info NAME` now keeps its dependency rows honest too: known dependencies reuse the same summary dialect, while truly absent requirements say `NAME [missing]` instead of collapsing broken and absent dependencies into one `missing` bucket. `pluginpick` also follows that same trust-first flow now: loaded plugins reload, broken plugins open filtered `plugin errors NAME`, and other known plugins open `plugin info NAME`.  Its picker rows and previews now reuse the same bracketed plugin-state summary dialect too, so searchable inspection does not fall back to older free-form status labels. Rev583 keeps those grouped picker menus compact too: grouped `pluginpick` rows stay at `[state, deps...]` while exact `showplugin NAME` completion is free to append the richer `errors=N` hint. When no plugin manager exists at all, grouped `pluginpick` submit now also fails explicitly as `pluginpick: no plugin manager` instead of pretending the query merely matched `0 plugin(s)`.


## Restricted manual load grants

In `--trust restricted`, scanning plugin metadata is not plugin evaluation. `plugin load NAME` is the explicit transition that records a session grant bound to the current plugin root, entry file, and package digest, then loads that one candidate. `plugin reload NAME` requires an active non-revoked grant and rechecks disk before using it; changed metadata, an entry-path change, or a same-path package byte change makes the older grant stale. Scripts cannot self-approve restricted loads or revoke grants, and `plugin grants` is hidden from script contexts unless `cap.plugin-read` is enabled. See `docs/816-manual-plugin-load-grants.md` and `docs/817-content-bound-plugin-grants.md`.
