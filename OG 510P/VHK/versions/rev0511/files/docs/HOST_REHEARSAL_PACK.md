# Host rehearsal pack

`vhk gen-host-rehearsal-pack <project_dir>` turns the reviewed
bundle/native/service chain into one operable host-proof lane.

Generated artifacts:

- `docs/VHK_HOST_REHEARSAL.md`
- `docs/VHK_HOST_REHEARSAL_PLAN.json`
- `scripts/vhk_refresh_host_rehearsal_pack.sh`
- `build/publish/<bundle-name>/rehearsal/README.md`
- `build/publish/<bundle-name>/rehearsal/vhk_host_rehearsal_handoff.json`
- `build/publish/<bundle-name>/rehearsal/install_reviewed_lane.sh`
- `build/publish/<bundle-name>/rehearsal/status_reviewed_lane.sh`
- `build/publish/<bundle-name>/rehearsal/report_reviewed_lane.sh`
- `build/publish/<bundle-name>/rehearsal/logs_reviewed_lane.sh`
- `build/publish/<bundle-name>/rehearsal/uninstall_reviewed_lane.sh`
- `build/publish/<bundle-name>/rehearsal/rehearse_reviewed_lane.sh`

Why it exists:

- prove one conservative reviewed-bundle lane end to end instead of stopping at
  lower-level native/service handoffs
- validate desktop-entry alignment and name the `gtk-launch` probe id explicitly
- inspect systemd user-service state/logs when the project owns a first-party
  watcher lane
- keep install and rollback rooted in the same reviewed bundle payload instead
  of drifting back to the mutable project checkout

This is still a conservative Linux-native rehearsal surface. A passing script set
is stronger than prose, but it does not erase desktop-specific launcher
indexing, compositor policy, helper-daemon permissions, or portal consent.

Additional expectations:

- the rehearsal lane should be able to collect one machine-readable host rehearsal report under XDG state instead of forcing maintainers to copy/paste status output by hand
- that report should bridge the installed launcher’s own live status surface (`--status-json` / `--home-json`) with host-facing probes such as desktop-file validation and best-effort systemd user-unit verification
