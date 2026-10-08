# Bus daemon (busd)

The VHK bus socket is a **UNIX datagram socket**, which means it is effectively **single-consumer**:
only one process can bind the socket path at a time.

If you run multiple `vhk watch-bus ...` processes for the same project, they will compete for the
socket and you may lose events.

`vhk busd` solves this by:

- binding the bus socket **once**
- evaluating **multiple bus_watchers** in *project order*
- optionally stopping propagation when a watcher sets `consume: true`

## Run all enabled bus watchers

```bash
vhk busd /path/to/project
```

## Run selected watchers

```bash
vhk busd /path/to/project --watcher hotkeys --watcher on_build
```

## consume: first-match rule style

```yaml
bus_watchers:
  - name: hotkeys
    event: hotkey
    dispatch: true
    consume: true

  - name: debug_log
    event: "*"
    macro: log_everything
```

With `consume: true`, an event handled by `hotkeys` will not be evaluated by later watchers.

## Flagship i3/X11 warm-runtime handoff

For the main product lane, generate the whole stack at once:

```bash
vhk gen-i3-busd-stack /path/to/project --watcher hotkeys
vhk gen-i3-busd-stack /path/to/project --watcher hotkeys   --vhk-cmd /path/to/vhk-wrapper.sh   --vhk-pythonpath /path/to/repo/src
```

This writes:

- a **session-bound** systemd user socket+service pair for `vhk busd`
- an i3 config snippet that emits cheap `vhk-emit` bus events
- a short README with install steps
- a `control-plane.json` contract that names the generated control surface
- a `bin/macro_entrypoints_json.sh` helper that emits a machine-readable project-wide map of preferred run/dispatch/contract entrypoints
- a `bin/macro_contract_json.sh <macro>` helper that emits a machine-readable invocation contract for one macro
- a `bin/macro_author_queue_json.sh` helper that emits a ranked project-wide queue of which macro should enter the author loop next
- a `bin/macro_replay_board_json.sh` helper that emits one project-wide replay-proof board keyed by each macro's own newest matching run
- a `bin/macro_author_loop_json.sh <macro>` helper that emits one fused author/review/execute contract for one macro
- a `bin/macro_runtime_board_json.sh` helper that emits one project-wide execution-posture board for resident dispatch triage
- a `bin/macro_acceptance_ledger_json.sh` helper that emits the durable project signoff ledger for recorder/runtime debt
- a `bin/status_runtime_json.sh` helper that emits machine-readable readiness/status for operators and a private LLM
- a `bin/check_runtime_json.sh` helper that emits focused X11/i3 prerequisite blockers/warnings for the flagship stack
- a `bin/assert_runtime_ready.sh` gate that fails fast when the stack is not ready to use
- a `bin/next_action_json.sh` helper that emits machine-readable recommended next steps from prerequisite/runtime truth
- a `bin/stack_state_json.sh` helper that fuses manifest, readiness, runtime status, real macro inventory (including presets/groups/tags), latest-run truth, latest-dispatch truth, latest-run health, the author queue, the replay board, direct per-macro latest-run/report/trace routes, the runtime board, the acceptance ledger, the thin-dispatch catalog, and next action into one JSON snapshot
- a `bin/macro_dispatch_catalog_json.sh` helper that tells the resident stack which macro payloads are cheap enough to emit now, which generated wrappers own that contract, and which explicit blockers still force direct-run or stabilization
- a `bin/next_action.sh` helper that prints the same recommendation for a human operator
- a `bin/latest_run_json.sh` helper that emits machine-readable latest-run artifact truth
- a `bin/latest_dispatch_json.sh` helper that emits machine-readable truth for the newest checked/raw dispatch attempt plus its stored receipt path
- a `bin/latest_run_health_json.sh` helper that emits a machine-readable verdict about whether the newest run looks healthy enough to iterate on
- a `bin/latest_artifacts.sh` helper that prints a compact artifact-oriented latest-run view
- a `bin/` control surface for list/run/dispatch, checked dispatch, recorder/report/trace/history, latest-run artifact inspection, latest-dispatch inspection, and runtime operations

The generated stack assumes the daemon should follow `graphical-session.target` by
default. Use `--no-session-bound` only when you deliberately want a generic
user-login service instead.

The generated `control-plane.json` file plus the `bin/` scripts are the intended bridge for a private
LLM or other higher-level controller: they make direct runs, warm-runtime dispatch,
recorder/report loops, latest-run artifact inspection, latest-dispatch receipts, readiness checks, and recommended next actions explicit instead of
rebuilding CLI startup logic or raw JSON payloads from scratch every time.


## systemd user service

Generate only the service unit when you want a long-lived runner without socket
activation:

```bash
vhk gen-vhk-busd-service /path/to/project --watcher hotkeys
```

By default this unit is **session-bound** (`graphical-session.target`). Add
`--no-session-bound` if your target desktop does not publish that target and you
intend to fall back to a generic user-login service.

Tip: pair this with `--via-bus` exports so keybinds only emit fast bus events and
the long-lived daemon does the heavier work.

## systemd socket activation

For the preferred resident-runtime setup (and fewer startup races), use **systemd
socket activation**:

```bash
vhk gen-vhk-busd-socket-units /path/to/project --watcher hotkeys
```

By default the generated socket/service pair is also **session-bound**. Enable the
`*.socket` unit as printed, or use `vhk gen-i3-busd-stack ...` when you want the
i3 snippet and install README generated alongside it.

See: docs/SOCKET_ACTIVATION.md.

## Live reload

`busd` supports *live reload* so you can iterate on `project.yaml` / macros without
restarting the daemon.

### Reload via bus event

By default, `busd` treats the `settings.bus_reload_event` bus event (default:
`vhk.reload`) as an **internal control message**. When received, it reloads the
project from disk and continues.

Emit the event using:

```bash
vhk bus-reload /path/to/project
```

This is intentionally similar in spirit to `sxhkd`'s reload-on-signal workflow
(SIGUSR1) but works without a PID file because it uses the same bus socket.

### Reload via signals

Optionally, `vhk busd --reload-signals` installs SIGUSR1/SIGHUP handlers to
request reload (only works in the main thread).

## Stop / shutdown

`busd` also supports a portable “please exit” control event.

- Event name: `settings.bus_stop_event` (default `vhk.stop`)

Emit it with:

```bash
vhk bus-stop /path/to/project
```

This is useful for systemd units or scripts that want a clean shutdown without
tracking PIDs.

## Related: external control surfaces

For webhooks / dashboards / Stream Deck controllers that can only do HTTP, see:

- `docs/HTTP_CONTROL.md` (`vhk httpd`)


## Developer-tree runtime bootstrap

For local repo work before `vhk` is installed, the generated socket/service pair and the project-pinned `bin/` wrappers can now carry an explicit Python module bootstrap. Use `--vhk-pythonpath /path/to/repo/src` when generating the warm-runtime stack or standalone busd units; the resulting control-plane contract records that bootstrap so both humans and a private LLM can tell whether the stack is running in normal installed mode or developer-tree mode.
