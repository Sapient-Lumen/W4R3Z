# Service composition pack

`vhk gen-service-compose-pack <project_dir>` extends the native install handoff
into one explicit Linux session-service composition tree.

It is intentionally not another packaging layer. The goal is to make the
login/session story reviewable:

- first-party VHK user-service units for the watcher/event plane when bus
  watchers exist
- `environment.d` exports for user services
- a reviewed-bundle materializer/runner so the service lane can execute from a shipped payload instead of the mutable checkout
- an XDG autostart bridge that can start the VHK-owned unit on login where that
  is still the simplest interoperable path
- install/uninstall/smoke-test scripts that let maintainers rehearse the flow
  without hand-copying files into `~/.config`

## Generated surfaces

The command writes:

- `docs/VHK_SERVICE_COMPOSE.md`
- `docs/VHK_SERVICE_COMPOSE_PLAN.json`
- `scripts/vhk_refresh_service_compose_pack.sh`
- `build/publish/<bundle-name>/service/`

That handoff tree includes:

- `README.md`
- `vhk_service_compose_handoff.json`
- `refresh_service_compose_inputs.sh`
- `install_user_session.sh`
- `uninstall_user_session.sh`
- `smoke_test_service_compose.sh`
- `systemd-user/`
- `environment.d/`
- `autostart/`
- `materialize_bundle_root.sh`
- `run_bundle_busd.sh`

## What it does not claim

This pack does **not** claim that VHK suddenly owns every helper daemon on the
machine.

External services such as `ydotoold`, `espanso`, `keyd`, `Kanata`, or `KMonad`
remain adjacent lifecycle concerns. The pack names them in docs when planner/
host-contract output suggests they matter, but it does not silently absorb them
into VHK's promise surface.

It also does not claim that every desktop handles user sessions identically.
`graphical-session.target`, XDG autostart, environment propagation, and
reviewed-bundle extraction are useful building blocks, not a universal Linux
login guarantee.
