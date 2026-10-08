# Plugin no-manager feedback

Rev390 tightens one small trust-first seam in the plugin surface: when the plugin subsystem is unavailable, plugin commands now identify which plugin surface failed instead of collapsing to a context-free `no plugin manager` line.

Before this revision, three different operations all hid behind the same wording:

- `plugin reload NAME`
- `plugin info NAME`
- `plugin errors [NAME]`

That was not incorrect, but it made logs and headless tests less inspectable than the rest of the newer command dialect. If a future LLM, script, or human saw `no plugin manager`, they still had to recover which command path produced it.

## What changed

These paths now fail as:

- `plugin reload: no plugin manager`
- `plugin info: no plugin manager`
- `plugin errors: no plugin manager`

The hostcall-backed reload path inherits the same wording automatically because it already reuses the shared reload-feedback helper.

## Why this matters

This is a tiny trust/debugging cleanup, not a new subsystem.

Micromax is moving toward a live scripting environment with safe host boundaries. When a subsystem is absent, the message should keep the failed surface visible so the next debugging step is obvious. A stripped-down harness, a headless test, or a future optional plugin runtime should not force someone to infer whether reload, info, or error inspection failed.

## Files

- `src/micromax_editor/editor.py`
- `src/micromax_editor/command_dispatcher.py`
- `tests/test_editor_pluginpick.py`
- `tests/test_plugin_hostcalls.py`
- `docs/304-plugin-reload-hostcall-dialect.md`
