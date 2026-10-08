# Rev600: dedupe one-error filtered runtime plugin detail

## What changed

Filtered runtime `plugin info NAME` and `plugin errors NAME` already had a compact
first error line after rev599:

- `errors: missing dependency: missingdep`
- `errors: 2 load errors · last: secondary issue`

But the single-error path still echoed the same failure again as a one-item bullet
list underneath. Rev600 keeps the same truthful summary line and only emits the
per-error bullets when there is more than one recorded load failure.

## Why it matters

This is a tiny trust/taste cleanup:

- exact one-plugin runtime inspection should not become noisier than the exact
  command-bar row when both already know the same single failure
- nearby exact/runtime paths already treat one known failure as a one-line
  witness and reserve bullet lists for genuinely plural error inventories
- future humans or LLMs reading command output get the failure once, not twice

## Scope

Small and local:

- `src/micromax_editor/command_dispatcher.py`
- `tests/test_editor_pluginpick.py`
- repo/context breadcrumbs only

No VM or host-boundary changes.
