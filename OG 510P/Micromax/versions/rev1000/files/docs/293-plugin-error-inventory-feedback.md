# Rev351 — grouped plain plugin-error inventory

## What changed

Plain `plugin errors` now behaves like an inventory surface instead of a raw log dump.

Before rev351:

- `plugin list` gave a compact plugin-health summary
- `plugin reload NAME` confirmed the resulting plugin state
- `plugin info NAME` began with the same summary dialect
- filtered `plugin errors NAME` began with the same summary dialect too
- but unfiltered `plugin errors` still emitted one raw `plugin error: NAME: DETAIL` line per recorded failure

After rev351:

- `plugin errors` still says `plugin errors: (none)` when there are no recorded load failures
- otherwise it starts with a tiny grouped summary like `plugin errors: 2 plugin(s), 3 error(s)`
- each broken plugin then gets its own summary row using the same entry shape as `plugin list` / `plugin reload` / `plugin info` / filtered `plugin errors NAME`
- detail lines stay visible underneath each grouped plugin row

Example:

```text
plugin errors: 2 plugin(s), 3 error(s)
  - b [error, deps:missingdep] (2 errors)
    - missing dependency: missingdep
    - secondary issue
  - c [error, deps:otherdep] (1 error)
    - missing dependency: otherdep
```

## Why this matters

This is a small trust/flow move, not a new subsystem.

The plugin loop was already getting more honest, but the broadest failure-inspection path still forced humans and future LLMs to reconstruct state from raw lines. Grouping errors by plugin makes it easier to answer ordinary questions quickly:

- how many plugins are currently broken?
- how many total load failures exist?
- which errors belong to the same plugin?
- which plugin state/version/dependency summary goes with those failures?

That keeps plain `plugin errors` aligned with the repo's current direction:

- **trust**: failure inspection should tell the truth without forcing guesswork
- **flow**: quick plugin triage should be readable in one pass
- **taste**: nearby plugin commands should speak one concise, coherent dialect

## Code and tests

Code:

- `src/micromax_editor/command_dispatcher.py`

Focused tests:

- `tests/test_editor_pluginpick.py`
