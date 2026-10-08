# Rev347: plain plugin inventory should be legible

Micromax-editor already had a good **rich plugin path**: `pluginpick` grouped rows by errors vs loaded vs available, `plugin info NAME` exposed metadata, and `plugin errors [NAME]` exposed load/dependency failures. The quiet gap was the **plain inventory path**: `plugin list` still collapsed everything to raw names and then sprayed trailing error lines.

That shape worked, but it was a lower-fidelity dialect than the nearby picker/detail surfaces:
- it was hard to see at a glance what was loaded vs blocked
- dependency/version hints were hidden behind follow-up commands
- the trailing error lines made the summary feel noisier without being more inspectable

Rev347 keeps the change intentionally small.

## What changed

`plugin list` now emits one concise summary line with one inspectable entry per plugin:
- `loaded` / `available` / `error` state
- visible `vVERSION` when known
- visible `deps:...` hints when declared

Example shape:
- `plugins: a [loaded, v1.0.0]; b [loaded, v2.0.0, deps:a]; c [error, v0.3.0, deps:missingdep]`

## Why this matters

This is a **trust/flow** improvement, not a feature expansion.

The editor already had the raw information. The problem was that the first command a person or future LLM would naturally try for plugin inventory (`plugin list`) still required extra inference.

The goal is simple:
- plain inventory should be **legible**
- richer commands should still exist for deep detail
- the default summary should tell the truth without extra spelunking

## What this does not try to do

This does **not** add a plugin manager UI, install/uninstall flows, enable/disable state, or a broader package system. It just makes the existing plain inventory path more honest and easier to scan.
