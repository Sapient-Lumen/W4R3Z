# Native install pack

`vhk gen-native-install-pack <project_dir>` turns the reviewed bundle/runtime
chain into one conservative XDG-local app/install handoff.

Generated artifacts:

- `docs/VHK_NATIVE_INSTALL.md`
- `docs/VHK_NATIVE_INSTALL_PLAN.json`
- `scripts/vhk_refresh_native_install_pack.sh`
- `build/publish/<bundle-name>/native/README.md`
- `build/publish/<bundle-name>/native/vhk_native_install_handoff.json`
- `build/publish/<bundle-name>/native/assemble_native_app.sh`
- `build/publish/<bundle-name>/native/install_xdg_local_app.sh`
- `build/publish/<bundle-name>/native/uninstall_xdg_local_app.sh`
- `build/publish/<bundle-name>/native/smoke_test_native_install.sh`
- `build/publish/<bundle-name>/native/refresh_desktop_actions.sh`

Why it exists:

- prove one reversible native lane before overselling package lanes
- keep bundle, launcher, desktop metadata, and optional embedded runtime in one
  reviewable app tree
- install under XDG-local directories instead of mutating system paths

This is intentionally conservative. It does not claim that helper daemons, raw
input, or compositor-specific privileges are solved merely because the Python
app tree is now easier to install.

New in the latest pass:

- the installed launcher now materializes the reviewed bundle into XDG cache
  and opens the project palette by default
- the generated desktop entry now exposes quick actions for palette open, bundle
  inspection, cache refresh, and the most relevant palette entries
- install now rewrites desktop-entry placeholders across action groups instead
  of only patching the top-level `Exec=` line

New in the current pass:

- the native app tree now also ships packaged docs under `share/doc/vhk/`, including `VHK_APP_HOME.md` and `VHK_APP_HOME.json` as an installed-lane summary surface
- the generated launcher now understands `--about`, `--support-json`, `--list-docs`, `--print-doc-path <kind>`, `--open-doc <kind>`, and `--status` so a desktop action or operator can reach the packaged lane story without reopening the mutable project checkout
- the generated desktop entry now exposes quick actions for app-home and support docs in addition to palette launch, bundle inspection, cache refresh, and top palette entries


Additional launcher-state notes:

- the installed launcher now resolves its real app root through the installed symlink instead of assuming `$0` already points inside the app tree
- launcher state now lives under `XDG_STATE_HOME`/`~/.local/state` so pinned/recent entry data does not get mixed into user data or the shipped bundle payload
- the launcher now supports `--refresh-desktop-actions`, `--pin-entry <entry-id>`, `--unpin-entry <entry-id>`, `--list-recent-entries`, and `--list-pinned-entries`
- install now attempts one best-effort desktop-action refresh after the launcher link is in place, so the installed desktop file can follow actual pinned/recent state when a runtime is available
- quick actions remain opportunistic Linux sugar rather than a guaranteed control surface; some launchers expose them eagerly, while others hide them or require explicit toggles


Current live-status / service-awareness notes:

- the installed launcher now supports `--home-json` (with `--support-json` kept as a compatibility alias), `--status-json`, `--refresh-status-report`, and `--open-status-report`
- live status is written under `XDG_STATE_HOME` so the installed lane can emit a Markdown + JSON snapshot without mutating the shipped bundle payload
- the status snapshot resolves pinned/recent palette entry labels from the materialized reviewed bundle and, when systemd user services are expected, probes `systemctl --user show` for the generated unit names
- the desktop entry now also exposes quick actions for the packaged service guide and the live status report so an installed lane can surface both static guidance and current host state

