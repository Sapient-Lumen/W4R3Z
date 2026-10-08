# GlobalShortcuts portal catalogs

`vhk gen-portal-shortcuts-spec <project_dir>` generates a reviewable catalog for
Wayland shortcut flows that use the XDG `GlobalShortcuts` portal.

This is **not** a permanent backend config like `keyd` or `xremap`. The portal
route still needs a live session plus an interactive bind/consent step.
The value of this file is that it makes the route reviewable:

- stable `shortcut_id` values
- preferred freedesktop shortcuts-spec trigger strings
- the bus payload VHK will forward on activation
- skipped bindings that could not be expressed honestly in the portal format

Example:

```bash
vhk gen-portal-shortcuts-spec /path/to/project --out ./build/vhk.portal-shortcuts.yml
vhk portal-hotkeys /path/to/project --catalog ./build/vhk.portal-shortcuts.yml --bind --listen
vhk portal-hotkeys /path/to/project --catalog ./build/vhk.portal-shortcuts.yml --bind --assignment-report ./build/vhk.portal-shortcuts.assigned.yml --max-events 1
vhk portal-hotkeys /path/to/project --catalog ./build/vhk.portal-shortcuts.yml --bind --assignment-history --max-events 1
vhk portal-assignment-history /path/to/project --json --drift-only
vhk portal-assignment-history /path/to/project --json --since 20260308T220000Z --changed-shortcut launch_hotkey
vhk export-portal-assignment-history /path/to/project --drift-only --out ./build/vhk.portal-shortcuts.history.md
vhk export-portal-assignment-history /path/to/project --format html --out ./build/vhk.portal-shortcuts.history.html
vhk gen-portal-assignment-presets /path/to/project --out ./build/vhk.portal-shortcuts.history-presets.yml --local-out "${XDG_CONFIG_HOME:-$HOME/.config}/vhk/portal-shortcuts/proj/history-presets.local.yml"
vhk portal-assignment-history /path/to/project --preset-file ./build/vhk.portal-shortcuts.history-presets.yml --preset recent-drift --json
vhk portal-assignment-history /path/to/project --preset-file ./build/vhk.portal-shortcuts.history-presets.yml --preset-file "${XDG_CONFIG_HOME:-$HOME/.config}/vhk/portal-shortcuts/proj/history-presets.local.yml" --preset recent-drift --json
vhk prune-portal-assignment-history /path/to/project --keep 10 --older-than-days 30 --dry-run
vhk diff-portal-assignment-report ./last-run.assigned.yml ./build/vhk.portal-shortcuts.assigned.yml --out ./build/vhk.portal-shortcuts.assigned.diff.yml --check
```

`vhk portal-hotkeys` can still derive shortcuts directly from `project.yaml`, but
`--catalog` pins the live portal bind/listen flow to the reviewed YAML so stable
shortcut ids, preferred triggers, and forwarded payloads come from one schema.

The generated YAML includes a `bind_command` and `bindless_listen_command`, and
when the output path is known it also includes catalog-aware commands such as
`bind_from_catalog_command`, `bind_and_capture_assignment_command`,
`list_assignment_history_drift_command`,
`prune_assignment_history_older_than_command_template`, and a
`compare_assignment_report_command_template` for diffing a new assignment ledger
against an earlier one.
That lets install docs point at one reviewed session flow and, when desired,
capture a requested-vs-assigned shortcut ledger straight from the portal's own
returned `trigger_description` data and compare later sessions against the same
reviewed catalog.

`--assignment-history` persists portal assignment ledgers under `XDG_STATE_HOME` (or `~/.local/state`) at `vhk/portal-shortcuts/<project>/`, keeping both a `latest/` copy and timestamped `history/` snapshots. When a previous `latest/` report exists, VHK also writes a matching latest/history diff file so portal drift stops depending on hand-managed filenames. `vhk portal-assignment-history` now supports drift-only, time-window, and changed-shortcut filters, `vhk export-portal-assignment-history` can turn that same filtered XDG-state view into either a shareable Markdown summary or a single-file HTML report, and `vhk prune-portal-assignment-history` can retain by count and also prune snapshots older than a chosen UTC-day cutoff after protecting the newest `--keep` entries. `vhk gen-portal-assignment-presets` closes the next operator gap by generating reusable named filter bundles for history/export/prune, and the history/export/prune commands can consume one or more `--preset-file` layers with one `--preset` name so project-shared presets and operator-local overrides do not have to live in the same file. `vhk inspect-portal-assignment-preset` now makes that layered resolution explicit, and the history/export/prune machine-readable payloads plus Markdown/HTML handoffs now carry the winning preset file, section, layer rank, and merge rule instead of hiding them in shell history.
