- added `WaitForDbusSignal` plus `docs/DBUS_SIGNAL_WAITS.md`
- taught the lightweight D-Bus layer to parse both `dbus-monitor` blocks and one-line `gdbus monitor` fallback signals, with honest fallback scoping around `sender` / `--dest`
- added targeted tests for D-Bus wait steps, `gdbus` line parsing, and stable match-rule/text helpers

- added `WaitForWindowEvent` plus `docs/WINDOW_EVENT_WAITS.md`
- taught planner/validator/doctor window-contract surfaces to track **WM event kinds** (`focus`, `workspace`, `title`, `urgent`, `new`, `close`, `custom`) instead of only selector/state/geometry/pointer-window needs
- added targeted tests for event-driven waits and session warnings around unsupported WM event kinds

- added project/session **window contract** analysis
- new module: `src/vhk/project/window_contracts.py`
- `plan-project --json` now emits `window_contract` so Linux-native planning can distinguish generic window usage from stateful selectors / geometry / pointer-window dependence
- `validate` now emits `session_window_contract` warnings when a backend can see windows generally but cannot honestly guarantee the specific state/geometry/pointer-window semantics a project asks for
- `doctor --json` now includes `window_introspection.window_contract_support`

## Why this mattered

The previous pass taught VHK how to *match* stateful window metadata, but the
project still described every window-heavy automation as the same generic
`window_introspection` capability. That was too coarse for Linux.

A project that only needs `class`/`title` matching is very different from a
project that needs:

- `sticky` / `fullscreen_mode` selectors
- strict geometry
- or the top-level window under the pointer

Those are different support and portability contracts. This revision makes that
difference explicit in the planner and validator instead of leaving it buried in
raw step definitions.

- added stateful window selectors across runtime matching surfaces
- `I3WindowSelector` now accepts best-effort state fields: `visible`, `fullscreen`, `fullscreen_mode`, `floating`, `sticky`, `minimized`, `hidden`, `mapped`, and `pinned`
- taught i3/sway tree matching, Hyprland runtime/client matching, and generic snapshot matching to use those state fields honestly
- added `tests/test_window_state_selectors.py`
- extended Hyprland wait tests so `WaitForWindow` can match stateful selectors instead of only title/class/PID
- added `docs/WINDOW_STATE_SELECTORS.md`

Why this mattered:

The previous pass taught VHK how to *observe* stateful window metadata, but not
how to *author against it*. That still left authors doing the awkward thing
Linux users do in shell scripts all the time: inspect some backend-shaped JSON,
then rebuild the state check manually in an expression or helper script. This
pass turns that metadata into a real runtime authoring surface while keeping the
repo honest that exported WM criteria are narrower than runtime selector power.

## Process-aware window context pass

This pass made the new window-introspection lane more AHK-like by teaching it
about owning processes, not just titles/classes.

What changed:

- added `src/vhk/system/processes.py` with Linux-native `/proc` helpers for
  best-effort process-name lookup
- extended `GetActiveWindow` and `GetWindowAtCursor` with `window_pid` /
  `window_process` convenience vars
- extended `GetWindowList` rows with `pid` / `process_name` where available
- taught runtime selector matching to understand `pid`
- kept WM config export honest: sway criteria can carry `pid`, while generated
  i3 criteria stay conservative
- added targeted tests for X11, Hyprland, active-window steps, cursor-window
  steps, and process-aware selector matching

Why this mattered:

AHK-style window automation often needs more than class/title matching. “Focus
the Firefox window owned by this process”, “cycle windows for one app”, and
“capture support context with executable hints” are all common workflows. Linux
supports them too, but through different seams: `_NET_WM_PID`/`xdotool` on X11,
IPC tree metadata on sway/i3, Hyprland client metadata, and KDE’s `kdotool`
bridge. This pass turns that lesson into a first-class runtime shape instead of
leaving process-aware logic to shell-outs.


## Idle resume/activity pass

- added `WaitForUserActivity` as the resume-side complement to `WaitForIdle`
- extended `src/vhk/system/idle.py` with `wait_for_user_activity()`
- documented timeout/resume authoring patterns in `docs/IDLE_AUTOMATION.md`
- updated product/spec/research/issue docs so VHK's idle story now matches what Linux tools actually teach

Why this mattered:

Linux idle tooling is rarely just “tell me when I am idle.” It is usually a
timeout/resume pair: fire when the session goes quiet, then do something else
when the human comes back. This pass turns that lesson into a first-class macro
primitive so authors do not have to fake resume logic with sleeps or ad-hoc
loops.

## Idle automation pass

- added `GetIdleMs` and `WaitForIdle` runner steps
- added `src/vhk/system/idle.py` as a best-effort idle probe/wait module
- documented explicit support lanes in `docs/IDLE_AUTOMATION.md`
- updated product/spec docs to keep the probe-vs-event split visible

Why this mattered:

Linux automation often needs a truthful answer to “has the human stopped
touching the session yet?” Adjacent tools already prove that idle-aware flows
matter, but they also prove there is no single universal backend. This pass
makes idle a first-class macro concept while staying honest about how support is
actually obtained on X11, GNOME Wayland, and compositor-specific Wayland lanes.

## Host rehearsal pack pass

- added `vhk gen-host-rehearsal-pack`
- generated `docs/VHK_HOST_REHEARSAL.md` and `docs/VHK_HOST_REHEARSAL_PLAN.json`
- generated `scripts/vhk_refresh_host_rehearsal_pack.sh`
- materialized `build/publish/<bundle-name>/rehearsal/` with:
  - `README.md`
  - `vhk_host_rehearsal_handoff.json`
  - `refresh_host_rehearsal_inputs.sh`
  - `install_reviewed_lane.sh`
  - `status_reviewed_lane.sh`
  - `logs_reviewed_lane.sh`
  - `uninstall_reviewed_lane.sh`
  - `rehearse_reviewed_lane.sh`

Why this mattered:

The bundle-state runner made the service lane honest, but the repo still lacked
one obvious proving path a maintainer could follow end to end. This pass turns
that gap into concrete install/status/log/uninstall scripts rooted in the same
reviewed bundle/native/service story, while staying explicit that desktop-shell
discoverability still needs real host rehearsal beyond generated files.

# Worklog — 2026-03-08

## Bundle-state session runner pass

- added `vhk materialize-bundle`
- taught `vhk gen-service-compose-pack` to emit `materialize_bundle_root.sh` and `run_bundle_busd.sh`
- moved generated user units from direct project-root execution to a bundle-state runner that uses explicit config/state/cache roots
- updated install/uninstall/smoke scripts so the session-service lane copies and rehearses the bundle runner payload, not just units and env files

## Why this mattered

The service composition pass named the login/session problem honestly, but it
still left one major truth gap: the long-lived service lane ran from the mutable
project tree instead of the reviewed bundle/runtime artifact story the repo had
spent several revisions building.

This pass closes that gap in a pragmatic way:

- one shared `materialize-bundle` command becomes the reviewed-payload bridge
- the service lane can now extract a verified bundle into user state before
  starting watchers
- user units now name config/state/cache roots directly instead of smuggling
  runner state through working-directory assumptions

## Research folded into this revision

- systemd's directory directives keep validating explicit config/state/cache
  roots for user services over ad-hoc shell paths
- pipx's isolated-app model keeps reinforcing the value of one app/runtime
  root plus one exposed entrypoint instead of a mutable checkout as the product
- the combination suggests a better VHK service posture: ship a reviewed bundle,
  materialize it into owned state, and let the watcher plane run from there

## Session-service composition pass

- added `vhk gen-service-compose-pack`
- generated `docs/VHK_SERVICE_COMPOSE.md` + `docs/VHK_SERVICE_COMPOSE_PLAN.json`
- generated `scripts/vhk_refresh_service_compose_pack.sh`
- materialized `build/publish/<bundle-name>/service/` with:
  - `README.md`
  - `vhk_service_compose_handoff.json`
  - `refresh_service_compose_inputs.sh`
  - `install_user_session.sh`
  - `uninstall_user_session.sh`
  - `smoke_test_service_compose.sh`
  - `systemd-user/` VHK-owned busd units (when bus watchers exist)
  - `environment.d/` exports for user services
  - `autostart/` bridge entries for login-time startup

## Why this mattered

The native install lane finally gave VHK one believable local app tree, but it
still left the Linux login/session story mostly implicit. Real Linux-native
automation depends on how user services, XDG autostart, and helper daemons are
stitched together, not just on whether a bundle can be zipped.

This pass makes the next truthful step explicit and testable:

- one VHK-owned watcher service lane becomes reviewable
- session exports move into `environment.d` instead of shell folklore
- autostart becomes a bridge artifact instead of a sentence in docs
- external helpers remain named as adjacent services rather than being quietly
  absorbed into VHK claims

## Research folded into this revision

- systemd's user-session docs keep reinforcing that `graphical-session.target`
  and `graphical-session-pre.target` are the right vocabulary for graphical
  session services, but also that they are session-shaped rather than a blanket
  login guarantee.
- the XDG autostart spec and `systemd-xdg-autostart-generator` keep validating
  autostart desktop files as a pragmatic bridge layer instead of a replacement
  for explicit user units.
- `environment.d` keeps validating reviewable user-service environment exports
  over shell-profile assumptions.
- ydotool's current docs still reinforce that helper daemons and `/dev/uinput`
  permissions are their own lifecycle problem, which is why the new pack names
  those helpers without pretending VHK owns them.

## Exact-target runtime embedding pass

- added `vhk gen-runtime-embed-pack`
- generated `docs/VHK_RUNTIME_EMBED.md` + `docs/VHK_RUNTIME_EMBED_PLAN.json`
- generated `scripts/vhk_refresh_runtime_embed_pack.sh`
- materialized `build/publish/<bundle-name>/runtime/embed/` with:
  - `README.md`
  - `vhk_runtime_embed_handoff.json`
  - `refresh_runtime_embed_inputs.sh`
  - `bootstrap_runtime_at_target.sh`
  - `embed_native_runtime.sh`
  - `embed_appimage_runtime.sh`
  - `embed_flatpak_runtime.sh`
  - `smoke_test_embedded_runtime.sh`
- taught generated AppImage/Flatpak build scripts to honor `VHK_EMBED_RUNTIME=1` and consume those exact-target helpers

## Why this mattered

The wheelhouse/runtime pack solved the dependency-handoff problem, but it still
left one dangerous temptation in place: copying a ready-made virtual
environment from one place to another and hoping it behaved like a portable
runtime.

This pass makes the next truthful step explicit and testable:

- build the runtime where it will actually live
- keep native/AppImage/Flatpak target paths reviewable
- let package build scripts opt into exact-path embedding instead of forcing
  maintainers to hand-stitch that step later

## Research folded into this revision

- Python's stdlib `venv` docs explicitly say environments are not considered
  movable or copyable, which validated the choice to generate target-path
  bootstrap scripts instead of packaging a prebuilt venv as if it were a
  universal runtime artifact.
- AppImage's AppDir docs continued to validate the stable `AppRun` +
  `usr/lib/...` runtime seam for package-local embedding.
- Flatpak's Python/module docs continued to reinforce that dependency
  generation and sandbox packaging should stay explicit, which is why the new
  embed helpers remain opt-in and builder-facing rather than becoming silent
  magic inside every package lane.

## Runtime handoff pass

- added `vhk gen-runtime-pack`
- generated `docs/VHK_RUNTIME.md` + `docs/VHK_RUNTIME_PLAN.json`
- generated `scripts/vhk_refresh_runtime_pack.sh`
- materialized `build/publish/<bundle-name>/runtime/` with:
  - `README.md`
  - `vhk_runtime_handoff.json`
  - `refresh_runtime_inputs.sh`
  - `requirements.runtime.txt` + `build-requirements.txt`
  - `wheelhouse/README.md`
  - `build_wheelhouse.sh`
  - `smoke_test_offline_install.sh`
  - `run_bundle_with_runtime.sh`
  - `emit_flatpak_python_modules.sh`

## Why this mattered

The distribution pack was truthful, but it still stopped one layer too early:
package skeletons could point at a reviewed bundle, yet the Python runtime story
was still a maintainer memory problem.

This pass makes the runtime handoff explicit and testable:

- dependency specs are copied into one reviewable place
- wheelhouse generation is a script, not tribal knowledge
- offline install smoke tests become part of the release story
- Flatpak bridge work starts from the same requirements file instead of a hand-typed module list

## Research folded into this revision

- pip's wheelhouse guidance validated the choice to generate a build-host-specific installation bundle instead of pretending runtime artifacts are magically portable.
- PyPA's venv guidance reinforced using isolated environments for smoke tests/native installs rather than mutating system Python.
- Flatpak's Python docs validated generating one requirements file and feeding it into `flatpak-pip-generator` as the next bridge for sandboxed builders.
- AppImage's AppDir docs reinforced keeping any future embedded runtime behind a stable in-AppDir path and launcher contract instead of guessing at ad-hoc bundle layouts.

## Distribution handoff pass

- added `vhk gen-distribution-pack`
- generated `docs/VHK_DISTRIBUTION.md` + `docs/VHK_DISTRIBUTION_PLAN.json`
- generated `scripts/vhk_refresh_distribution_pack.sh`
- materialized `build/publish/<bundle-name>/distribution/` with:
  - `README.md`
  - `vhk_distribution_handoff.json`
  - `refresh_distribution_inputs.sh`
  - `appimage/AppDir/` skeleton + `build_appimage.sh`
  - `flatpak/<app-id>.yaml` + `build_flatpak.sh`

## Why this mattered

The repo already had strong planner/release/publish surfaces, but package
metadata was still the sort of thing a maintainer would hand-author at the end.
That drift is exactly what makes Linux automation tools overclaim.

This pass keeps package metadata downstream of the same reviewed bundle story
and makes the packaging boundaries explicit:

- AppImage/Flatpak can be useful delivery shells
- they are not magical substitutes for native remapper/helper-daemon lanes
- package metadata should stay tied to the same public support/install docs and
  release-stage lane that the maintainer already reviewed

## Research folded into this revision

- AppImage handoffs were shaped around the documented AppDir model (`AppRun`,
  root desktop file, icon entry, `usr/share/...` conventions).
- Flatpak handoffs were shaped around documented application-id, desktop file,
  metainfo, and `finish-args` expectations.
- The docs now keep sandboxed package delivery separate from claims about
  host-global automation parity.


## Native install handoff pass

- added `vhk gen-native-install-pack`
- generated `docs/VHK_NATIVE_INSTALL.md` + `docs/VHK_NATIVE_INSTALL_PLAN.json`
- generated `scripts/vhk_refresh_native_install_pack.sh`
- materialized `build/publish/<bundle-name>/native/` with:
  - `README.md`
  - `vhk_native_install_handoff.json`
  - `refresh_native_install_inputs.sh`
  - `assemble_native_app.sh`
  - `install_xdg_local_app.sh`
  - `uninstall_xdg_local_app.sh`
  - `smoke_test_native_install.sh`
  - `app/` tree containing launcher + desktop metadata + bundle/runtime slots

## Why this mattered

The bundle/runtime/embed chain had become believable, but it still stopped one
layer before an actual conservative product lane. This pass turns the next
honest lesson into code: ship one reversible native app tree first, then let
package or helper-heavy lanes inherit from that proof instead of outrunning it.

## Research folded into this revision

- The XDG Base Directory spec validated using `~/.local/share` for per-user app
  data and `~/.local/bin` for per-user executables in a local-install story.
- pipx's docs/how-it-works pages reinforced the value of one isolated virtual
  environment per application plus one exposed launcher path.
- Desktop Entry spec guidance reinforced that a local launcher path can be
  written into `Exec=` explicitly during install rather than assuming every
  desktop session inherits shell PATH identically.


## Native entrypoint / desktop actions pass

- upgraded the generated native launcher so it no longer defaults to
  `inspect-bundle`; it now:
  - resolves embedded/system `vhk`
  - materializes the reviewed bundle into XDG cache
  - reuses that materialized tree until the shipped bundle stamp changes
  - opens the project palette by default
  - still supports direct bundle inspection and stable `--entry-id` palette
    actions
- upgraded the generated native desktop entry so it now includes quick actions
  for:
  - open palette
  - inspect reviewed bundle
  - refresh cached bundle
  - top palette entries from the project at generation time
- replaced the old install-time `awk` rewrite with a Python placeholder rewrite
  so all `Exec=` action groups stay aligned with the installed launcher path
- extended the smoke path/tests so they check launcher install, desktop actions,
  and placeholder rewriting instead of only file presence

## Why this mattered

The native lane had become installable, but it still launched into a maintainer
diagnostic. That was honest, but it was not product-real. This pass turns the
installed lane into something closer to how Linux users actually meet a tool:
a desktop entry, a launcher, a few quick actions, and a cached working project
state that does not require re-unzipping the reviewed payload on every launch.

## Research folded into this revision

- The Desktop Entry spec's additional-actions model validated using action
  groups for launcher quick actions instead of overloading the main `Exec=`
  path with every workflow.
- The XDG Base Directory spec reinforced that a materialized reviewed bundle
  belongs in user cache rather than user data, because it is derived,
  non-essential state that can be rebuilt from the shipped zip.

## Native packaged home/support surface pass

- upgraded the generated native app tree so it now ships packaged docs under `share/doc/vhk/`, including:
  - `VHK_APP_HOME.md`
  - `VHK_APP_HOME.json`
  - copied support/install/runtime/native/service/rehearsal docs when present
- upgraded the generated native launcher so it now supports:
  - `--about`
  - `--support-json`
  - `--list-docs`
  - `--print-doc-path <kind>`
  - `--open-doc <kind>`
  - `--status`
- upgraded the generated desktop entry so it now exposes quick actions for:
  - open palette
  - open app home
  - open support guide
  - inspect reviewed bundle
  - refresh cached bundle
  - top palette entries
- extended tests/smoke coverage so they now check packaged doc emission and the expanded desktop-action surface

## Why this mattered

The native lane had become installable and launcher-first, but its non-launcher surfaces still leaned too hard toward maintainer diagnostics. This pass pushes the installed lane closer to a real Linux application posture: the app ships its own packaged “start here” docs, desktop menus can reach those docs directly, and operators can inspect the installed lane without reconstructing context from the source checkout.

## Research folded into this revision

- The Desktop Entry spec's additional-actions model reinforced using launcher quick actions for app-home/support shortcuts instead of overloading the main `Exec=` path.
- `gio open` / `xdg-open` remain the right conservative Linux-level openers for packaged doc files because they delegate to the user's preferred handler inside a desktop session.



## Native stateful launcher-actions pass

- fixed the generated native launcher so it now resolves the installed app root through the launcher symlink instead of assuming `$0` already points inside the app tree
- upgraded the installed launcher so it now keeps state under `XDG_STATE_HOME` / `~/.local/state`, including recent and pinned entry lists for launcher-facing workflows
- added launcher modes for:
  - `--refresh-desktop-actions`
  - `--pin-entry <entry-id>`
  - `--unpin-entry <entry-id>`
  - `--list-recent-entries`
  - `--list-pinned-entries`
- added `build/publish/<bundle-name>/native/refresh_desktop_actions.sh` as a reviewable handoff script for regenerating the installed desktop entry from the shipped template plus live launcher state
- upgraded install so it now best-effort refreshes the installed desktop entry after the launcher symlink exists
- extended native-install tests so they now check symlink-aware launcher resolution, XDG state paths, refresh-action surfaces, and the new helper script

## Why this mattered

The native lane had become much more product-real, but one installed-lane truth was still wrong: the launcher computed its app root from `$0`, which breaks once the install flow exposes it through `~/.local/bin` as a symlink. Fixing that made the installed lane honest on real hosts, and the follow-on launcher-state work turns desktop quick actions from frozen generation-time guesses into something the installed app can refresh around actual usage.

## Research folded into this revision

- The XDG Base Directory spec explicitly reserves `XDG_STATE_HOME` / `~/.local/state` for restart-persistent, user-specific state such as history, which fits launcher recent/pinned entry state better than data or cache roots.
- Desktop-entry additional actions remain a good fit for launcher quicklists, but they stay static per desktop file; that makes a generated refresh path the honest Linux-native move.
- Rofi's current `drun` docs still say desktop actions are hidden by default unless `-drun-show-actions` is enabled, which reinforces treating launcher actions as opportunistic polish rather than a universal control plane.


## Native live-status / service-hint pass

- upgraded the generated native launcher so it now supports:
  - `--home-json` (with `--support-json` retained as a compatibility alias)
  - `--status-json`
  - `--refresh-status-report`
  - `--open-status-report`
- the installed lane now writes a live status snapshot under XDG state (`VHK_APP_STATUS.json` + `VHK_APP_STATUS.md`) rather than trying to mutate packaged docs inside the shipped app tree
- the live status snapshot now folds together:
  - runtime source (embedded/system/missing)
  - bundle/materialized/project paths
  - packaged doc inventory
  - pinned/recent launcher entries resolved against the materialized palette
  - expected VHK-owned user-service units plus best-effort `systemctl --user show` state when available
- upgraded the generated desktop entry so it now exposes quick actions for:
  - open service guide
  - open live status report
- extended native-install tests/smoke expectations so they now check the status-root/status-json/status-md surfaces, the new launcher modes, and the richer desktop-action set

## Why this mattered

The installed lane had become launcher-first and doc-aware, but it was still too static: you could open packaged guidance, yet the installed app could not summarize its own current health without dropping back into ad-hoc shell inspection. This pass turns that gap into a Linux-native surface: write live status into XDG state, keep packaged docs immutable, and use `systemctl --user` only as a best-effort probe rather than as a hidden hard dependency.

## Research folded into this revision

- The XDG Base Directory spec still reserves `XDG_STATE_HOME` for restart-persistent state that is not portable enough for user data, which fits live launcher/status snapshots better than either shipped docs or cache.
- freedesktop desktop-entry actions remain a good additive shortcut surface for opening packaged service guidance and the live status report, but they should stay additive rather than become the only control plane.
- systemd’s user-introspection tools remain the honest way to query VHK-owned unit state when those units exist, so the launcher now treats `systemctl --user show` as a best-effort status probe instead of inventing its own parallel service-status format.



## Host rehearsal report-bridge pass

- extended `gen-host-rehearsal-pack` so the generated handoff now includes `report_reviewed_lane.sh` and explicit XDG-state report paths
- the new report script now bridges the installed launcher’s live `--status-json` / `--home-json` surfaces into one host-rehearsal JSON + Markdown report under `XDG_STATE_HOME/vhk/rehearsal/<command>/`
- folded best-effort host probes into that same report path:
  - desktop-file validation output when `desktop-file-validate` is available
  - active user-manager unit search paths from `systemctl --user show -p UnitPath --value`
  - static installed-unit verification from `systemd-analyze --user verify` when the project ships VHK-owned user units
- updated the rehearsal smoke path so it now asserts the report JSON/Markdown are actually produced under a temporary XDG state root

## Why this mattered

The installed native lane could already summarize itself, and the rehearsal lane could already install/status/log/uninstall it, but they still stopped short of one combined host-proof artifact. This pass makes the two surfaces meet in the middle: one reviewed bundle can now produce one host-rehearsal report that ties installed-launcher state to desktop and user-service visibility.

## Research folded into this revision

- systemd’s current docs still make `systemctl --user show -p UnitPath --value` the better source for the running user manager’s actual unit search path than `systemd-analyze unit-paths` alone.
- `systemd-analyze --user verify` is a useful static truth surface for installed user-unit correctness, especially when the goal is to validate one reviewed lane without requiring that every service already be healthy and running.


## Capability audit pack pass

The strategy already talked about a capability-audit/fallback pack, but the repo still made users reconstruct that story by reading `plan-project`, `gen-host-contract-pack`, `gen-readiness-pack`, and `gen-activation-pack` separately.

This pass closes that gap with `vhk gen-capability-audit-pack`, which now:

- writes `docs/VHK_CAPABILITY_AUDIT.md`, `docs/VHK_CAPABILITY_FIXUPS.md`, and `docs/VHK_CAPABILITY_AUDIT_PLAN.json`
- emits `scripts/vhk_refresh_capability_audit_pack.sh`
- emits `build/capability-audit/<project>/` with a `collect_capability_audit.sh` handoff that captures a fresh doctor/validate/plan snapshot plus regenerated host/readiness/activation/audit docs
- optionally folds claim posture into the audit when `docs/VHK_TARGET_CLAIMS.yaml` exists
- extends support capture so cross-session bug reports can include the capability audit without extra maintainer folklore

This is a useful correction to the repo's shape: Linux capability limits were already modeled, but they were not yet packaged as one review surface that release/support work could actually consume.


## Host dossier pack pass

- added `gen-host-dossier-pack` on top of the existing native + service + host-rehearsal lane
- the new pack writes `docs/VHK_HOST_DOSSIER.md`, `docs/VHK_HOST_DOSSIER_PLAN.json`, `scripts/vhk_refresh_host_dossier_pack.sh`, and a new `build/publish/<bundle-name>/dossier/` handoff
- the dossier handoff now includes:
  - `collect_host_dossier.sh`
  - `archive_host_dossier.sh`
  - `smoke_test_host_dossier.sh`
  - copied support/rehearsal/native/service docs when present
- `collect_host_dossier.sh` bridges the installed launcher's `--home-json` / `--status-json` / `--list-docs` surfaces with the rehearsal report, session env capture, best-effort `loginctl show-session`, `systemctl --user show`, and `journalctl --user` excerpts under `XDG_STATE_HOME/vhk/dossier/<command>/`
- `archive_host_dossier.sh` zips that reviewed packet after collection instead of leaving support capture as terminal history only
- support-pack planning now names the installed host dossier as a recommended artifact for install/service/desktop-shell issues

## Why this mattered

The repo could already install one conservative lane, rehearse it, and generate a host report, but it still lacked a shareable installed-host packet. This pass makes that story more operator-real: one reviewed lane can now produce one dossier root and one archive that support can inspect offline after privacy review.

## Research folded into this revision

- `loginctl show-session` remains the right place to name the real live session instead of inferring too much from one environment variable.
- `systemctl --user show` and `journalctl --user` answer different support questions, so the dossier now captures both when they are available.
- per-user journal access is still not guaranteed everywhere, so the dossier records that as a gap instead of treating missing logs as success.

## Host dossier share-safe pass

The host dossier had become a useful operator artifact, but it still stopped at “collect raw support packet, then remember to scrub it.” That was too much manual trust for a project that is explicitly trying to become Linux-native and operator-real.

This pass adds a real privacy lane on top of the dossier handoff:

- `redact_host_dossier.sh` now builds `share-safe/` under the dossier root
- `VHK_HOST_DOSSIER_REDACTION.json` records what the generator redacted and whether suspicious leftovers still need review
- `archive_share_dossier.sh` now zips the redacted tree, while `archive_host_dossier.sh` remains available for trusted internal debugging
- support-pack planning now points to the share-safe dossier archive as the default external handoff instead of the raw zip

Why this mattered: VHK had already learned to collect launcher state, rehearsal output, and user-service visibility, but the repo still made the privacy boundary implicit. This revision makes that boundary explicit and testable.


## WaitUntil + compact native-runtime spec pass

This pass tightened one of the repo's most important authoring seams: VHK had a
lot of wait-capable concrete steps, but it still lacked one small generic
primitive for “keep checking this expression until it becomes true.” Authors
could approximate that with `While`, but that pushed them toward handwritten
polling loops instead of one shared wait surface.

What changed:

- added a new `WaitUntil` step with `timeout_ms`, `poll_ms`, `max_poll_ms`,
  `jitter_ms`, `max_attempts`, `out_value`, and `out_attempts`
- wired it into the runner with backoff-aware polling and traceable wait
  attempts
- added control-flow tests for success and timeout behavior
- documented the step in `README.md`, `docs/SPECS.md`, and
  `docs/PROJECT_FORMAT.md`
- added `docs/NATIVE_RUNTIME_SPEC_2026Q1.md` as a compact product/runtime spec
  that makes the repo's intended Linux-native shape easier to reason about than
  the giant omnibus spec alone

Why this mattered: if VHK wants the “AHK feel,” the baseline authoring advice
has to be “wait for observable state” rather than “sleep for 500ms and hope.”


## Bus-event wait + event-driven sync pass

- added `WaitForBusEvent`, a first-class one-shot bus wait step for local IPC synchronization
- added `wait_for_bus_event()` and shared bus-payload decoding helpers in `vhk.system.event_bus`
- documented why this should usually use a dedicated socket path when `vhk busd` already owns the normal project bus
- added tests covering JSON payload filtering, plain-text payload decoding, and timeout behavior

## Active-window runtime introspection pass

This pass promoted active-window inspection from “helpful CLI” to “real runtime
primitive.”

What changed:

- added `GetActiveWindow`, which samples the current focused window into the
  same watcher-style variable shape used by `window_watchers`
- added `get_active_window_snapshot()` in `vhk.system.active_window` so runner
  code and future CLIs can share one best-effort snapshot helper
- attached optional `window.geometry` on a best-effort basis, with an explicit
  `require_geometry` switch so macros can choose honesty over silent magic
- documented the lane in `README.md`, `docs/PROJECT_FORMAT.md`,
  `docs/WINDOW_SPY.md`, and the new `docs/WINDOW_INTROSPECTION.md`
- added tests for the step plus snapshot downgrade/require behavior

Why this mattered:

AHK-style authoring depends heavily on being able to ask “what window is active
right now?” Linux absolutely supports that question, but not through one single
API. X11 still leans on `xdotool`/`xprop`, sway/i3 lean on compositor trees,
Hyprland leans on `hyprctl activewindow`, and KDE Wayland still needs
`kdotool`/KWin scripting.

The repo already had pieces of that story (`window-spy`, watcher context,
selector matching). The missing product seam was runtime parity: one-shot macros
could not conveniently sample the same data shape that watcher-triggered macros
already received. `GetActiveWindow` closes that gap.


## Window-list runtime pass

This pass extended the new window-introspection lane from *focused window* to
*open windows*.

What changed:

- added `GetWindowList`, a runtime step that returns a `windows` array plus
  `window_count`
- added `get_window_list_snapshot()` in `vhk.system.active_window`
- added `vhk window-list` as the operator/debugging sibling of `window-spy`
- added tests for runner, CLI, Hyprland enumeration, and KDE Wayland
  enumeration via `kdotool search`

Why this mattered:

AHK-style automation does not stop at “what is focused right now?” A lot of
real macros need to ask “what windows exist?” before choosing, filtering, or
counting targets. Linux absolutely supports that workflow, but through different
backend seams: i3/sway trees, `hyprctl clients`, X11 EWMH helpers, and KDE’s
`kdotool search`.

The repo already had the active-window half of that story. `GetWindowList`
closes the enumeration half while keeping the Linux-native honesty: one stable
macro-facing data shape, but no false claim that Wayland desktops expose one
universal open-window API.


## Window-at-cursor runtime pass

This pass filled in the pointer-oriented half of the new window-introspection
story.

What changed:

- added `GetWindowAtCursor`, a runtime step for sampling the best-effort
  top-level window currently under the mouse pointer
- added `get_window_at_cursor_snapshot()` in `src/vhk/system/active_window.py`
- added `vhk window-at-cursor` as the CLI sibling of the runtime step
- extended `src/vhk/system/kdotool.py` with `get_window_under_cursor_id()` so
  KDE Wayland can use kdotool's pointer window stack directly
- documented the lane in `README.md`, `docs/PROJECT_FORMAT.md`,
  `docs/WINDOW_SPY.md`, the new `docs/WINDOW_AT_CURSOR.md`, and the research /
  issues docs

Why this mattered:

AHK-style authoring is not only about active-window inspection. A lot of real
macros begin with “what window is under the mouse right now?” Linux supports
that too, but not through one universal API: X11 can often ask `xdotool`, KDE
Wayland can often ask `kdotool`, and i3/sway/Hyprland often need cursor
position plus compositor geometry. VHK now exposes one stable runtime and CLI
surface for that question without pretending the backend differences disappeared.


## Window-state metadata pass

This pass extended VHK's new window-introspection lane from **identity** to
**state**.

What changed:

- enriched `GetActiveWindow`, `GetWindowAtCursor`, and `GetWindowList` with
  best-effort state fields such as `visible`, `fullscreen`, `fullscreen_mode`,
  `floating`, `sticky`, `minimized`, `mapped`, `hidden`, and `pinned` where the
  backend exposes them
- taught sway/i3-like snapshots to carry IPC state directly
- taught X11 snapshots to derive minimization/fullscreen/sticky state from EWMH
  `_NET_WM_STATE` and to derive `visible` conservatively from desktop + sticky
  + hidden state
- taught Hyprland snapshots to pass through the state fields it already emits
  in client metadata when available
- documented the state shape in `README.md`, `docs/PROJECT_FORMAT.md`, the
  window-lane docs, and the new `docs/WINDOW_STATE_SHAPE.md`
- added focused tests for i3/sway, Hyprland, X11, and pointer-window selection
  behavior when invisible rows are present

Why this mattered:

The previous passes made VHK much better at answering “what window is this?”
But a lot of real automation needs the next question too: “what **state** is it
in right now?” Linux already exposes pieces of that answer through sway IPC,
EWMH, compositor-specific client metadata, and KWin bridges. This pass turns
that into a stable macro-facing vocabulary without pretending every backend
exposes the same contract equally well.

## rev0201: file watchers + filesystem-triggered macro lane

This pass turned filesystem-triggered automation into a first-class project surface instead of leaving it split across one-shot waits and ad-hoc shell loops. VHK now supports `file_watchers:` in `project.yaml`, a `vhk watch-file` command, inotify-backed waiting when `inotifywait` is present, and a polling fallback when it is not.

Why this mattered:
- Linux users already lean on tools like `inotifywait`, `incrond`, and `systemd.path` to turn file events into automation triggers.
- VHK already had `WaitForFile` / `WaitForNewFile`, but it still lacked the long-running rule-engine equivalent that clipboard/window/bus watchers already had.
- The new lane keeps the authoring vocabulary intentionally smaller than raw inotify masks: `new`, `changed`, `deleted`, `any`. That keeps macros portable across helper-backed and polling-backed hosts without pretending the underlying mechanisms are identical.

What shipped:
- `FileWatcher` project model + loader support
- `vhk.core.file_watchers.run_file_watcher()`
- `vhk watch-file`
- `vhk list-watchers` now shows file watchers (and bus watchers too)
- `vhk gen-systemd-watcher --file ...` support
- docs: `docs/FILE_WATCHERS.md` plus README / project-format updates

Caveat captured in docs/issues:
- file watchers are Linux-native and useful, but they are not perfect truth. Inotify overflow and mount/filesystem quirks still mean VHK should surface helper/fallback health more explicitly in future doctor/readiness work.


## 2026-03-08: one-shot file-event waits

This pass followed through on the new `file_watchers:` lane by adding an
in-macro sibling: `WaitForFileEvent`. That closes the gap between "project has a
long-running file watcher" and "one macro just needs to block until the next
matching change arrives".

Why it was worth doing:
- Linux already has strong prior art here (`inotifywait`, `entr`,
  `systemd.path`, `watchexec`).
- VHK already had `WaitForFile` / `WaitForNewFile`, but those prove path state
  rather than waiting for the next matching directory event.
- the new step reuses the same smaller event vocabulary as project watchers, so
  authors do not need to learn raw helper masks just to write reliable macros.

What landed:
- `WaitForFileEvent` model + runner support
- compact CLI rendering for the new step
- docs updates in README / project format / automation glue / web+external docs
- targeted tests for helper-backed and end-to-end polling flows

The bigger product lesson remains the same: Linux-native automation is stronger
when VHK exposes *small, stable authoring vocabularies* over backend-shaped
truth instead of pretending every helper/desktop has the same raw semantics.


## Revision 0203 — filesystem burst coalescing

This pass turned the new file-event lane into a quieter and more Linux-native surface. VHK now supports `quiet_ms` on both `file_watchers:` and `WaitForFileEvent`, returns ordered batch metadata (`file_batch_*`), and can coalesce bursty event streams into one logical automation run instead of firing on the first low-level edge.

What changed:
- `wait_for_file_event(..., quiet_ms=...)` now waits for a matching quiet window and annotates the returned event with burst metadata
- `file_watchers:` pass through `quiet_ms` and expose `file_batch_*` vars to macros
- CLI/project-format/docs now describe the difference between per-file readiness (`stable_ms`) and event-stream quiescence (`quiet_ms`)

- added `GetSystemdUnitState` / `WaitForSystemdUnitState` plus `docs/SYSTEMD_UNIT_STATES.md`
- added `src/vhk/system/systemd_units.py` and targeted tests for systemd-unit probes + runner steps

This pass turned the repo's growing service composition story into a direct runtime primitive. The project already generated and diagnosed systemd user-unit surfaces, but macro authors still had to drop into shell parsing or raw D-Bus ideas when they wanted to synchronize with a unit lifecycle. `GetSystemdUnitState` and `WaitForSystemdUnitState` now keep that authoring surface close to `systemctl show` and the manager's native `ActiveState` / `SubState` vocabulary instead.
