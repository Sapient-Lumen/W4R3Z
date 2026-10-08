# Plugin cleanup durable diagnostics (rev0887)

Rev0878 made failed plugin cleanup/retag reports visible through `plugin cleanup`
and `ed.plugin-cleanup-failure-rows`, but those reports were retained only in the
current process.  That was enough for immediate debugging and reload policy, but
it left a sharp operational gap: after a crash, restart, or handoff, the exact
failed surface could be gone.

Rev0887 adds an opt-in durable diagnostic receipt for cleanup failures.

## Options

The log is disabled unless both gates are true:

- `cap.persist` — the existing unsafe editor-persistence capability;
- `plugin.cleanup-log.persist` — the explicit cleanup-log opt-in.

Related options:

- `plugin.cleanup-log.file` — JSONL path, default
  `~/.config/micromax/plugin-cleanup.jsonl`;
- `plugin.cleanup-log.limit` — max records retained on disk, default `200`.

`cap.persist-root`, `persist.atomic`, `persist.fsync`, and `persist.maxbytes`
apply through the same persistence helper used by recent files, prompt history,
and savecursor state.

## Format

Each failed cleanup surface is one JSON line with a small stable shape:

```json
{"plugin":"alpha","action":"cleanup","group":"plugin:alpha","target_group":"","surface":"search","operation":"remove_search_group","detail":"RuntimeError: search cleanup broke"}
```

The timestamp field `ts` is also included.  The log is diagnostic evidence, not a
replay authority.  Loading it produces the same compact rows used by
`plugin cleanup`: `[plugin action group target_group surface operation detail]`.

## Runtime behavior

When a cleanup/retag/generation report fails, `PluginManager` still keeps the
bounded in-memory report used by unload/reload policy.  If durable logging is
enabled, the editor also appends the failed rows to the JSONL file and clamps the
file to the configured limit.

`plugin cleanup [NAME]` and `ed.plugin-cleanup-failure-rows` now merge in-memory
rows with persisted rows, deduplicating identical current-process entries.  This
means an operator can restart and still inspect the most recent cleanup failure
as long as the cleanup log is enabled and readable.

## Non-claims

This is not a recovery journal.  It does not make cleanup rollback durable, does
not persist plugin runtime state, does not mark a plugin unloaded after restart,
and does not provide hostile-code containment.  It is intentionally a receipt for
human and headless diagnostics.
