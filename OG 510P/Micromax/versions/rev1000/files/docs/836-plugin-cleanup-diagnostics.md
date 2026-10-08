# Rev0878 — Plugin cleanup diagnostics are reachable

Rev0874 made runtime-group cleanup and retag sweeps report structured failures.
Rev0875 made failed cleanup/retag commit paths fail closed. Rev0876 narrowed the
group-sweep restore boundary. Rev0877 added generation-scoped delayed-state
cleanup reports and combined group+generation restore on commit failure.

One high-risk gap remained: those reports were still mostly Python-internal
objects. A failed unload/reload left a useful `RuntimeGroupOperationError`, but
a user or headless tool had no direct, stable way to ask: *which cleanup surface
failed, for which plugin, and why?*

## Landing

Rev0878 adds a small diagnostics surface instead of another registry layer:

- `PluginManager.runtime_group_failure_rows(NAME?)` returns compact retained
  rows for failed cleanup, retag, and generation-cleanup surfaces.
- `Editor.plugin_cleanup_failure_rows(NAME?)` exposes only rows visible to the
  current plugin-read authority.
- `plugin cleanup [NAME]` shows retained failed surfaces after failed unload or
  reload cleanup.
- `ed.plugin-cleanup-failure-rows` exposes the same rows to headless consumers
  as `[plugin action group target_group surface operation detail]`.
- Prompt completion now advertises and previews the cleanup diagnostics command.
- `mxaudit --check` guards the manager row API, editor row API, command,
  hostcall, and prompt-completion seam.

Example command shape:

```text
plugin cleanup alpha: 1 failure(s)
  - alpha cleanup search.remove_search_group: RuntimeError: search cleanup broke
```

## Why this matters

Fail-closed cleanup policy is only half useful if the retained evidence is hard
to reach. This revision lets the normal plugin tooling answer the operational
question after a failed unload/reload: whether the problem came from group
cleanup, staged retag, or generation cleanup, and which host surface raised.

## Non-claims

This is diagnostics UX, not stronger containment. It does not add hostile-code
isolation, does not make cleanup reports durable across process restarts, does
not rollback document edits or external effects, and does not replace the broad
runtime snapshot used for source/lifecycle/callback transactions.

## Tests

Focused tests cover:

- exact and broad `plugin cleanup` command output;
- unknown and zero-failure cleanup targets;
- `ed.plugin-cleanup-failure-rows` hostcall rows;
- manager row filtering for stable and staged runtime groups;
- command-bar usage/completion drift;
- host-feature registration; and
- `mxaudit` guard coverage.
