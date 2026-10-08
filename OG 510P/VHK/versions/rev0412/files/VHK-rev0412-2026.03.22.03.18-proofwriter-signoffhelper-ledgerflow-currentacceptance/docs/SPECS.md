## 2026-03-18 addition: workspace-aware recorder segmentation and guards

- segmented `record-x11` output should not silently treat same-window workspace changes as generic focus transitions; workspace boundaries should be explicit and opt-in.
- `record-x11` should grow `--segment-on-workspace-change` so recorder output can preserve same-window workspace/desktop transitions when the author actually wants them.
- `--window-guard-mode event` should be allowed to emit `WaitForWindowEvent(event=workspace, ...)` for those boundaries, because workspace changes are already first-class WM events on i3/sway/Hyprland and a meaningful desktop-native workflow surface.

## 2026-03-18 addition: geometry-backed window events and recorder guards

- `WaitForWindowEvent` should grow an explicit `geometry` kind so geometry-sensitive macros and recorder output do not have to flatten rect changes back into state waits.
- i3/sway should map that lane onto honest window-change IPC when possible, while generic X11 / KWin / other desktops should expose it as a best-effort active-window geometry polling contract rather than claiming a universal rect-event stream.
- segmented recorder output should be allowed to preserve geometry refresh boundaries as `WaitForWindowEvent(event=geometry, ...)` when the guard lane is in event mode.

## 2026-03-18 addition: generic window vanish and open/close polling contracts

- generic X11 / KWin window waits should not stop at activation-only parity: `WaitForWindowVanish` must have a real snapshot-backed fallback too instead of accidentally dropping into i3-specific IPC code paths.
- polling-backed WM events on generic desktops should be able to surface best-effort `new` and `close` transitions by diffing window-list snapshots, while still staying honest that workspace/urgent/custom remain compositor-specific.
- generic `WaitForWindowEvent` / `WaitForWindowVanish` payloads should carry the last known window row when the transition being observed is `new` or `close`, so selector matching and post-event macro logic have real context instead of anonymous wakeups.

## 2026-03-18 addition: event-shaped recorder window guards

- segmented `record-x11` output should be able to preserve **future** focus/title/geometry transitions with `WaitForWindowEvent` rather than always flattening them into stateful `WaitForWindow` checks.
- that event lane should stay opt-in and should keep the first segment stateful, because macro start is a current-state proof while later segment boundaries are transition proofs.
- event-shaped recorder guards should currently require the recorded *active* window truth, not broad presence-only matching, and should preserve geometry-refresh boundaries as `WaitForWindowEvent(event=geometry, ...)` when the backend can honestly support that lane.
- generic polling-backed window events should obey the same contract and not invent a spurious initial event before any transition has actually happened.

## 2026-03-18 addition: explicit multi-click pointer semantics

- `MouseClickAt` now owns an explicit multi-click contract: `clicks` defaults to
  `1`, `delay_between_clicks_ms` defaults to `0`, and the runner moves to the
  target once before emitting the requested number of clicks
- optimizer/recorder cleanup may merge repeated `MouseClickAt` runs into one
  multi-click step when button, target coordinates, and modifier-clearing intent
  all match within a bounded inter-click gap
- the product should treat double-click/triple-click intent as a first-class
  authoring concept instead of leaving it encoded as raw repeated click events

## 2026-03-18 addition: title-aware recorder segmentation

- recorder segmentation should be able to *optionally* treat title changes
  inside the same window identity as segment boundaries, because Linux desktop
  flows often reuse one browser/editor window while the meaningful tab/document
  title changes.
- that title-aware lane should stay opt-in so normal segmentation can remain
  biased toward stable selectors and avoid making title fragility the default.
- when title-aware segmentation would cause multiple segments to share the same
  broad stable selector, recorder output should keep falling back to per-segment
  exact selectors rather than pretending the title change never mattered.

## 2026-03-18 addition: recorder window-transition segmentation

- `vhk record-x11` should be able to preserve active-window transitions inside
  one capture by segmenting the recorded stream when window identity changes
  during recording.
- segmented recorder output should be allowed to inject `WaitForWindow` guards
  at those boundaries instead of leaving every cross-app transition trapped in
  blind `Delay` steps.
- guard selection should stay conservative: use the per-segment stable selector
  when it is unique enough, but fall back to the per-segment exact selector when
  multiple recorded windows would otherwise collapse into the same broad stable
  match.
- when recorder-side relative mouse authoring is enabled, pointer coordinates
  should be translated per window segment rather than anchored once for the
  whole recording.

## 2026-03-18 addition: recorder-relative pointer authoring

- `vhk record-x11` should be able to emit relocatable mouse coordinates through
  `CoordMode(target=mouse, mode=window|client)` instead of freezing every
  recorded click to screen coordinates
- that authoring lane should be powered by captured active-window geometry and
  should stay honest about fallbacks (for example, `client` may need to fall
  back to the outer window rect when Linux backends cannot expose a distinct
  client rectangle)
- recorder-relative pointer output should remain adjacent to window-scope
  capture, because relative coordinates without honest app/window context are
  too easy to misuse

## 2026-03-18 addition: hotter paths stay thin, semantic paths stay explicit

- X11/i3-class hot paths should keep the lowest-latency trigger and replay lanes
  thin instead of routing every trigger through heavier planning/export layers
- Wayland text, pointer, shortcut, and structured-UI lanes should remain
  separate product surfaces because they have different authority and reliability
  envelopes
- AT-SPI/accessible-tree control should stay a first-class semantic lane for
  Linux-native automation rather than being flattened into vision or raw input

## 2026-03-17 addition: authority-aware setup and release handoffs

- setup-pack output must inherit the same project-level authority policy already used by planner/install/service generation
- release-lane plans must expose per-lane authority stories so release level and deploy style do not hide who actually owns trigger/injection authority on Linux
- release-deploy output must carry that same authority story into install snippets and deployment guidance
- release-stage payloads and per-lane READMEs must preserve the same ownership boundary so staged handoffs remain honest after export/shipping
- centralize the project-level authority-policy derivation in shared code instead of re-deriving it separately inside each pack builder

## 2026-03-17 addition: authority-aware installs and service scope

- native-install outputs must treat launcher/runtime/doc packaging as **userland ownership**, not as proof that portal sessions or evdev/uinput authority were also installed
- generated native app trees should ship a packaged authority guide so operators can review Linux boundary lines from the installed lane itself
- service-composition outputs must say which surfaces are actually session-owned, which remain desktop-mediated, and which stay adjacent privileged helpers/remappers
- privileged helpers and remappers stay explicit follow-on review/install work unless VHK grows a first-party reviewed lifecycle for them

# VHK specs (engine + future studio)

## Voice adapter seam

- VHK should treat voice control as an **adapter lane**, not a second automation runtime.
- `vhk gen-dragonfly-pack` now materializes that seam as a reviewable Dragonfly command module plus a JSON command ledger.
- `vhk gen-talon-pack` now materializes the same seam for Talon as a reviewable `.talon` command file, Python action module, and JSON command ledger.
- `plan-project` and related planner outputs should also surface a **voice command adapter lane** (`voice-command-adapter` / `voice-context-command-lane`) when authors have started curating `voice_phrases` and `voice_when` contexts, so Talon/Dragonfly export stops being a hidden post-processing trick and stays an explicit Linux adapter decision.
- `plan-project` and promotion-facing review output should also surface a **promotion authority envelope** (`promotion_authority_envelope_plan` / `promotion_authority_envelope_summary`) so user-session services, portal-mediated sessions, evdev/uinput remapper ownership, helper-daemon/uinput seams, and launcher-only userland surfaces stay explicit instead of collapsing into one generic “Linux support” claim.
- `vhk gen-autokey-pack` now materializes the X11 trigger-adapter seam for AutoKey as a reviewable folder tree of script + sidecar metadata pairs plus a manifest/README handoff, and it now treats AutoKey's coarse title-or-class window filter honestly by skipping scoped selectors unless `--allow-window-filter-approximation` is explicitly requested.
- `plan-project` and related route/pattern outputs now surface AutoKey as an explicit **X11 reviewable adapter lane** (`autokey-x11-adapter` / `autokey-reviewable-adapter`) instead of leaving it stranded as a lone exporter beside Espanso/remapper guidance.
- `plan-project` and related route/pattern/lesson outputs should also surface a **persistent uinput helper-daemon lane** (`uinput-helper-daemon` / `daemonized-uinput-helper-lane`) for Wayland-class repeated playback, so `dotoold`/`ydotoold`, socket ownership, and `/dev/uinput` policy become explicit deployment choices instead of hidden setup trivia.
- `plan-project` and review-facing audit output should also surface a **workload-oriented input lane dossier** (`input_lane_dossier`) that groups clipboard-first text, Wayland virtual-keyboard fast paths, daemon-backed uinput playback, portal-permissioned input, and X11-native replay into one operator-readable contract, so Linux input truth stops being scattered across helper names alone.
- `plan-project`, promotion-facing output, and capability-audit docs should also surface a **promotion input-lane map** (`promotion_input_lane_plan`) that says which workload-oriented lane should actually own each shipping surface (for example text packages leading with clipboard-first text while helper dossiers stay review-led around portal/daemon seams), so project-level promotion work does not drift away from runtime reality. Those same surfaces should also expose a **promotion activation-route map** (`promotion_activation_route_plan`) so startup/service/session ownership stays explicit alongside input-lane ownership. Finally, they should expose a **promotion operator-control map** (`promotion_operator_control_plan`) so status/reload/log ownership is explicit too, especially for service-managed, portal-session, and helper-daemon lanes. They should also expose a **promotion recovery map** (`promotion_recovery_plan`) so first-response, rollback, and re-entry ownership is explicit instead of being buried in prose. They should also expose a **promotion verification map** (`promotion_verification_plan`) so each shipping surface names the smoke/proof loop that actually demonstrates it is alive on Linux. Finally, they should expose a **promotion dispatch-budget map** (`promotion_dispatch_budget_plan`) so cold-start, first-use, and steady-state latency ownership is explicit per shipping surface instead of being flattened into one generic startup story.
- `plan-project` and related surface/route/pattern outputs should also distinguish **stable portal shortcut catalogs** from hotter or helper-sensitive Wayland hotkeys, so portal sessions stay an explicit catalog lane (`portal-global-shortcuts` evidence + `portal-session-catalog-lane`) instead of a silent default for every Wayland trigger.
- `plan-project` and related planner outputs should also surface **WM modal trigger lanes** (`wm-modal-trigger-layer` / `wm-modal-submap-lane`) for X11/i3-class, sway, and Hyprland projects, so grouped action families can live behind reviewed mode/submap entry chords instead of expanding the global hotkey grid forever.
- `plan-project` and related planner outputs should also surface a **picker-native chooser lane** (`picker-native-chooser` / `script-mode-picker-lane`) for prompt-rich and preset-driven workflows, so rofi/fuzzel/wofi-class launcher protocols stay an explicit Linux control surface instead of being flattened into generic palette prose.
- `plan-project` and related planner outputs should also surface an **app-native control protocol lane** (`app-native-control-adapter` / `app-native-protocol-lane`) when selectors clearly target apps like kitty, WezTerm, mpv, or qutebrowser that already expose deliberate control contracts, so VHK can prefer semantic adapters over blind key/pointer replay.
- `vhk gen-kitty-pack` should materialize the first concrete app-native terminal lane as a thin reviewable kitty remote-control handoff: route catalog, command ledger, and helper wrappers around `kitten @ send-text --match ... --stdin` for kitty-targeted `TypeText` routes that have enough selector evidence to stay honest.
- `vhk gen-wezterm-pack` should materialize the second concrete app-native terminal lane as a thin reviewable WezTerm CLI handoff: route catalog, command ledger, and helper wrappers around `wezterm cli send-text`, explicit pane ids when available, and best-effort title-based pane discovery via `wezterm cli list --format json` when VHK only has reviewable title evidence.
- `vhk gen-mpv-pack` should materialize the first concrete app-native media lane as a thin reviewable mpv JSON IPC handoff: route catalog, command ledger, and helper wrappers around local socket IPC for mpv-targeted macros whose names/descriptions/binding keys imply reviewable commands such as pause, stop, next, previous, seek, volume, mute, or fullscreen.
- `vhk gen-qutebrowser-pack` should materialize the first concrete app-native browser lane as a thin reviewable qutebrowser userscript handoff: route catalog, command ledger, and executable userscripts that preserve `QUTE_*` browser context while routing reviewed automation semantics back through `vhk run`.
- `plan-project` and related planner outputs should also surface an **MPRIS media service-bus lane** (`mpris-media-bus-adapter` / `mpris-follow-control-lane`) when authors are already waiting on `WaitForDbusSignal` against `org.mpris.MediaPlayer2*`, so media transport and metadata flows can use standard bus contracts instead of blind media-key replay or window-title polling.
- `vhk gen-playerctl-pack` should materialize that MPRIS lane as a thin reviewable adapter pack: route catalog, command ledger, and helper wrappers that let `playerctl --follow` own player discovery/follow semantics while VHK still owns macro execution.
- `plan-project` and related planner outputs should also surface a **desktop notification feedback lane** (`desktop-notification-feedback` / `notification-daemon-feedback-lane`) when authors are already emitting `Notify` steps or waiting on `org.freedesktop.Notifications`, so passive status/alert flows stay an explicit Linux session-service contract instead of being flattened into modal prompts or ad hoc stderr output.
- `Notify` should now preserve richer Linux notification intent directly in the step model (`app_name`, `icon`, `category`, `timeout_ms`, `replace_id`, `transient`, `out_id`, `progress`, `actions`, `out_action`), so replaceable progress/status loops, daemon-shaped action prompts, and app-branded passive feedback can stay declarative inside macros instead of leaking into ad hoc shell wrappers.
- The generated module must call back into `vhk run ...` so VHK remains the single source of execution semantics.
- Macro and preset metadata may carry `voice_phrases`, but those phrases stay intentionally simple and are normalized into literal spoken forms rather than arbitrary grammar code. Project linting should surface awkward cases early: phrases that normalize to nothing, punctuation/case variants that export as a different literal phrase, redundant variants that collapse to one spoken form, and explicit one-word global commands that deserve extra review.
- Macro and preset metadata may also carry `voice_when`, but voice exports only translate the subset they can represent honestly in the target toolchain; unsupported selector fields are skipped instead of being silently dropped.
- Spoken-phrase uniqueness is scoped to the effective export context, not the whole project: the same phrase may appear in multiple distinct voice contexts, but project linting should warn when a backend would still see a same-scope collision.
- Project linting should also surface adapter/export loss early: `voice_when` fields that Dragonfly/Talon cannot express, AutoKey scopes that require title-or-class approximation, GlobalShortcuts bindings that cannot be converted into freedesktop shortcuts-spec triggers or whose `when:` selectors stay runtime-only after global activation, Espanso scoped-hotstring plans that either rely on X11-only app filters or need synthetic composite configs to survive Espanso's one-active-config rule, xremap-scoped bindings whose selectors still depend on runtime-only fields such as `workspace`, `pid`, or state flags, keyd/Kanata/sxhkd/KMonad bindings whose `when:` selectors remain runtime-only inside VHK, sxhkd exports that target Wayland projects, and KMonad exports that change trigger shape into leader/layer flows or selector sublayers.
- Prompt-overlay presets are skipped by default in voice exports unless the operator explicitly opts in, because hidden interactive forms are a real usability boundary for spoken workflows.

This repo currently ships the **engine** (headless runner + CLI tooling). The long-term
goal is a Pulover’s Macro Creator–class Studio (record/inspect/compose/debug/run) built
on top of the same runtime model.

This document makes the “what are we building?” **explicit**: a Linux-native automation
stack that can feel as effective as AutoHotkey does on Windows, while acknowledging the
real constraints of X11 vs Wayland.

---

## 1) Product definition

### 1.1 VHK Engine (this repo)

**VHK Engine** is a deterministic-ish macro runtime and toolchain.

It provides:

- A folder-based **project format** (project.yaml + macros + assets).
- A typed **step model** (YAML-authored workflow nodes).
- A **runner** that executes steps with:
  - variable interpolation (${var})
  - a safe expression language for conditions and computed values
  - uniform retry/backoff/jitter/continue-on-error knobs
- OS adapters for:
  - screenshots and region selection
  - keyboard/mouse injection (best-effort per desktop)
  - clipboard, notifications, dialogs, processes, filesystem waits + file watchers
  - first-class prompted forms for user-entered macro parameters
  - chooser/palette-style prompts that prefer launcher-native pickers on the
    active session instead of forcing every selection through a generic dialog
  - a project-level macro palette (`vhk palette`) built on the same Linux-native
    launcher stack, with recent-run ordering and lightweight macro metadata
- Vision primitives:
  - OpenCV template matching (including openQA needle metadata)
  - pixel search / pixel get color
  - OCR via Tesseract (file + screenshot-backed)
- WM primitives:
  - i3/sway IPC + selector helpers (and Hyprland helper surface)
  - best-effort cross-backend window wait/focus contracts for i3/sway, Hyprland, generic X11, and KDE/KWin where helper tooling exists
- IPC event bus:
  - a small local trigger surface (UNIX socket) for cross-tool integration
- Tooling:
  - project init/validate/lint/optimize/retime/scaffold
  - “inspect” style CLI helpers (window-spy, pick-window, preview-needle, doctor)
  - `vhk doctor` is expected to expose a capability-oriented diagnostics surface, especially on Wayland where capture, injection, hotkeys, and portals are separate concerns
  - `vhk validate` should be able to reuse that capability model to warn when a project is likely to outrun the current session
  - `vhk lint-project` should be able to present the same capability language alongside macro-hygiene advice, so authors review portability and brittleness in one pass
- `vhk plan-project` should also be able to turn those surfaces into a sequenced delivery plan (`implementation_waves`), so teams can move from target/toolchain advice to a staged Linux-native implementation order
- `vhk plan-project` should also emit an explicit `performance_profile`, so capture/OCR/polling pressure, fixed-delay budgets, and dispatch-sensitive macros are visible during design review instead of only after a flaky run log
- `vhk plan-project` should also emit explicit `macro_route_profiles`, so every macro states which Linux-native lane should own it (text tier, remapper, watcher service, launcher entry, helper-boundary runner, or runner core) instead of leaving route ownership trapped in architecture prose
- `vhk plan-project` should also emit explicit `macro_export_candidates`, so route ownership turns into concrete Linux-native promotion targets (Espanso-style text packages, keyd/xremap-class remapper exports, watcher services, launcher surfaces, or helper-boundary dossiers) instead of remaining only descriptive
- `vhk plan-project` should also aggregate those per-macro route choices into a `route_portfolio`, so reviewers can see which Linux-native lanes are actually dominating the project instead of scanning every macro row manually
- `vhk plan-project` should also aggregate those promotion targets into an `export_promotion_plan`, so project-level shipping work (text package, remapper export, watcher service, helper dossier) becomes sequenced, reviewable, and tool-backed instead of staying trapped in repeated macro advice
- `vhk plan-project` should also emit staged `promotion_waves`, so reviewers can see which Linux-native promotions belong in the immediate specialist-export wave versus later helper/auxiliary review waves
- `vhk plan-project` should also emit `promotion_readiness`, so each export surface has an explicit ready/review/blocked posture tied to fit, session capability signals, and known Linux-native boundary conditions
- `vhk plan-project` should also emit a queued `promotion_backlog`, so promotions, unblock work, and claim-discipline review tasks become an execution list instead of only a descriptive architecture summary
- `vhk plan-project` should also emit `promotion_evidence`, so each staged surface/gate names the checked-in proof artifacts it expects before the repo treats that posture as release-proof
- `vhk lint-project` should be able to turn those route/export hints into route-drift advice, so authors get promotion guidance while editing macros instead of waiting for a later architecture review
- `vhk plan-project` should also be able to emit an explicit artifact/deployment map (`artifact_blueprint`), so future scaffold/setup/release flows can agree on which exports, configs, services, and audit artifacts belong to the project
- `vhk plan-project` should also be able to group those outputs into install-facing `deployable_surfaces`, so teams can reason about text packages, launcher entrypoints, WM layers, services, helper seams, and audit packs without reverse-engineering the artifact list
- `vhk plan-project` should also be able to emit explicit `setup_recipes`, so future init/scaffold/setup flows can turn those surfaces into repeatable install, review, verification, and rollback handoffs
- `vhk plan-project` should also be able to emit explicit `host_requirements`, so service lifecycle, permissions/groups, and portal/session routing stop being implied by package hints alone
- `vhk init` should consume that planning language early by being able to emit starter onboarding artifacts (guide + machine-readable plan) derived from the same strategy model instead of creating only a bare project skeleton
- `vhk gen-operator-pack` should turn the same planner output into operator-facing deployment artifacts (guide + checklist + machine-readable plan) so install/review/rollback work can travel with the project
- `vhk gen-support-pack` should turn planner + diagnostics output into support-facing triage artifacts (guide + checklist + machine-readable plan + capture script) so Linux bug reports can preserve desktop facts, recent event evidence, and privacy review notes
- `vhk gen-portability-pack` should turn the planner's cross-desktop environment comparison into portability-facing artifacts (guide + rollout worksheet + machine-readable plan + review script) so teams can stage X11/Wayland/desktop claims honestly
- `vhk gen-claim-pack` should turn that rollout story into editable support claims (guide + claim manifest + machine-readable audit plan + audit script) so projects can state what they really support on Linux
- `vhk audit-target-claims` should make those claims enforceable by failing overclaims and checking that stronger support tiers come with proof artifacts
- `vhk bundle` should be able to embed a planner-backed target-claim snapshot into `vhk_bundle_manifest.json` so a shared zip can carry its own support matrix and proof summary
- `vhk inspect-bundle` should surface that embedded snapshot without requiring the recipient to unpack the bundle or rerun the planner
- `vhk gen-publish-pack` should turn the audited support matrix into public support/install docs so exported artifacts and release prose cannot drift from what the bundle metadata says
- `vhk gen-trigger-pack` should turn planner-backed trigger/remapper surface choices into a self-contained export bundle (generated configs + docs + machine-readable plan + refresh script) so Linux-native hotkey/remap layers stop being a pile of unrelated one-off commands

### 1.2 VHK Studio (planned)

**VHK Studio** is a visual macro builder that sits on top of the engine.

It must provide:

- A recorder (input + focus + WM events).
- Inspectors that produce robust selectors (window pickers, accessibility tree, visual ROI), with explicit accessibility-bus health and event visibility rather than a hand-wavy “a11y available” checkbox.
- A command palette / step library with standardized editors.
- A debugger (step, pause/resume, breakpoints, overlays, variable watch).
- Packaging & sharing (bundles, one-click install, portability story).

---

## 2) Runtime semantics

### 2.1 Macro execution model

- A macro is a **list of steps**.
- The runner executes steps sequentially.
- Each step runs with a **context** (variables dict) that is mutated by steps.
- Most string fields are interpolated (`"hello ${name}"`), then parsed/used.
- Prompt-oriented steps may write structured dictionaries (for example `PromptForm`), and dotted-path interpolation like `${form.version}` is part of the supported runtime model.
- `ChooseFromList` is expected to feel like a Linux-native picker: launcher-style
  UIs first when available, dialog/console fallbacks second.
- Macro metadata (`description`, `group`, `tags`, `hidden`) is part of the
  supported project model for palette/studio surfaces.
- `vhk palette` is part of the runtime story, not just a future GUI feature.
- Macros may expose named saved parameter presets, and those presets are part of the supported palette/runtime model rather than a Studio-only abstraction.
- Presets may optionally attach a small prompt overlay so one launcher action can combine stable vars with a few just-in-time user-supplied fields.
- Prompt steps and preset overlays may participate in a project-local prompt profile store, with auto-loaded last values, opt-in named profiles from the CLI, password-safe persistence semantics, and palette-facing saved-profile actions for prompted presets.
- Project palettes should also be exportable into Linux launcher surfaces (`.desktop` entries and quick actions), because menus/taskbars/drun launchers are part of the native runtime UX rather than a separate packaging afterthought.
- Project palettes should also be exportable as picker-native launcher scripts, so the same stable `entry_id` model can serve `.desktop` menus, `drun`, and script-mode pickers without inventing a second runtime abstraction.
- Project launchers should also be exportable into WM-native binding snippets for i3, sway, and Hyprland, because launcher integration on Linux is incomplete until the project can be attached to a real session hotkey.
- Project palettes should also be exportable as WM-native transient launcher layers (i3/sway modes, Hyprland submaps), so recent macros, presets, and saved prompt-profile actions can be reached without a permanently occupied global keyspace.
- WM launcher exports should also support include/source-oriented installation paths, because real i3/sway/Hyprland configs are often split into managed snippet trees rather than maintained as one giant file.
- WM launcher exports must respect each config language's command-separator rules instead of dumping raw shell strings. In particular, i3/sway `exec` payloads that contain `,` or `;` need to be quoted as one command string.

### 2.2 Control flow

Minimum supported structured control flow:

- `If(condition, then_steps, else_steps)`
- `While(condition, steps, max_iterations)`
- `WaitUntil(condition, timeout_ms, poll_ms, max_poll_ms, jitter_ms, max_attempts?)`
- `WaitForBusEvent(event, pattern, condition, timeout_ms, socket_path, ...)`
- `WaitForDbusSignal(bus, sender?, path?, interface?, member?, match?, pattern?, condition?, timeout_ms, ...)`
- `GetSystemdUnitState(unit, scope?, ...)` / `WaitForSystemdUnitState(unit, status?, active_state?, sub_state?, timeout_ms, ...)`
- `GetIdleMs(out_ms, out_backend, out_source)` / `WaitForIdle(minimum_ms, timeout_ms, ...)` / `WaitForUserActivity(maximum_ms, armed_after_ms?, timeout_ms, ...)`
- `GetActiveWindow(include_geometry?, out_pid?, out_process?, ...)` / `GetWindowAtCursor(include_geometry?, require_window?, out_pid?, out_process?, ...)` / `GetWindowList(include_geometry?, selector?, focused_first?, ...)`
- `Try(steps, catch_steps, finally_steps, catch_pattern)`
- `Break`, `Continue`, `Return`

Semantics:

- `While` is **top-tested** and has a hard safety cap.
- `WaitUntil` is the default wait-driven primitive for any state that is already
  visible through variables, timers, process outputs, or prior step results.
- `WaitForBusEvent` is the event-driven primitive for helper-script / WM / service synchronization when the state change is easier to *emit* than to poll.
- `WaitForDbusSignal` is the desktop/service-bus sibling for cases where the upstream producer already emits a real D-Bus signal boundary (MPRIS, systemd, desktop scripts, portal-adjacent helpers) and VHK should react directly instead of forcing an intermediate bridge layer.
- `GetSystemdUnitState` / `WaitForSystemdUnitState` close the more common service-lifecycle gap: many Linux automation stories only need `systemctl show`-level truth (`ActiveState`, `SubState`, `LoadState`, `UnitFileState`) for a named unit, not raw D-Bus subscription logic in every macro.
- `GetIdleMs` / `WaitForIdle` / `WaitForUserActivity` make idle-aware automation first-class, but the support language stays explicit: direct probes exist today for X11 and GNOME Wayland, while compositor-specific Wayland idle lanes should often flow through external daemons that emit into the VHK bus.
- `GetActiveWindow`, `GetWindowAtCursor`, and `GetWindowList` make window introspection available inside macros, not only in CLI helpers, while still keeping acquisition backend-specific (i3/sway IPC tree, Hyprland `hyprctl`, X11 EWMH helpers, KDE `kdotool`). They also expose process-aware context (`pid`, `process_name`) whenever the backend exposes it cleanly.
- planner/validation/doctor now also carry a project/session **window contract** surface so VHK can distinguish plain app matching from richer demands such as stateful selectors, strict geometry, or pointer-window sampling.
- `Try` catch matching is string/regex based on error messages.
- `Return` exits the macro and writes a `return_value` variable.

### 2.3 Reliability knobs (per-step)

Every step may specify:

- `delay_ms` and `repeat`
- `retry_count`, `retry_delay_ms`, `retry_backoff`, `retry_jitter`, `retry_jitter_ms`
- `continue_on_error`

Contract:

- Retry applies to the step’s execution (including system/tool failures).
- `continue_on_error` must still produce a well-formed event log entry.

### 2.4 Observability contract

When `settings.event_log: true`:

- The runner writes a JSONL event log containing:
  - macro start/end
  - step start/end
  - wait polling attempts (`wait_attempt`)
  - diagnostics when failures occur (last screenshot, diffs, context json)

The event log is treated as part of the product API (used by Studio later).

### 2.4.1 Optimization-feedback contract

Observability is not just for debugging; it is part of the authoring loop.

Minimum expectations:

- `vhk report` should be able to summarize slow steps, retries, wait counts, and wait durations from the JSONL log.
- The report layer should expose **heuristic advice** for common Linux automation bottlenecks, including excessive fixed delays, vision-heavy polling, long literal typed-text throughput, and likely backend/capability mismatches.
- The optimization guidance should point users toward existing VHK flows when possible (`optimize`, `doctor`, `validate`, named regions, needle metadata) instead of inventing a separate tuning model.
- Text throughput is part of the optimization contract: long literal snippets may legitimately move to clipboard or hybrid segmented lanes, but interpolation-heavy or timing-sensitive text should remain explicit typed text.
- Later Studio surfaces should be able to reuse the same report/advice data, not re-derive it in a second private format.

### 2.5 Capability model

VHK should treat desktop support as a **capability matrix**, not a single `x11|wayland` boolean.

At minimum the engine/docs/doctor surface should reason about these separately:

- screen capture
- text injection
- pointer injection
- global hotkeys
- input capture
- window introspection

This is especially important on Wayland, where portal interfaces and compositor backends may implement only a subset of those abilities.

The doctor/spec/planner surface should treat portal routing as a two-layer model:

- live frontend portal interfaces (`org.freedesktop.portal.*`)
- installed backend manifests / routing metadata (`portals.conf` plus `.portal` files with backend id, DBus name, advertised interfaces, and `UseIn` desktop rules)

Host-facing artifacts should then carry a third derived surface: a **portal route contract** that compares configured routing, installed backend reality, and live frontend availability in one place.

Planner-facing strategy output should also be able to carry a compact **claim witness** surface when live host review is available: `planner_target_claims` for reviewed target lanes, `planner_claim_witness` for one summary posture, and current `host_truth` / `portal_route_contract` so wrong-host proof drift is visible before downstream claim or promotion packs run.

That lets VHK explain the difference between:

- a portal interface that is genuinely unavailable
- a backend that is installed but filtered out by desktop matching / `XDG_CURRENT_DESKTOP`
- a `portals.conf` entry that names a backend id not present on the host

---

## 3) Project + asset specs

### 3.1 Project folder format

Required:

- `project.yaml`
- `macros/` with one or more `*.yaml`

Recommended:

- `assets/` (needles, baselines, fixtures)
- `data/` (CSV/JSON artifacts)
- `logs/` (run outputs; excluded from bundles by default)

### 3.2 Bundle format

`vhk bundle` produces a `.zip` file with:

- all project files except excluded runtime artifacts (`logs/`, `.venv/`, `__pycache__/`)
- a top-level `vhk_bundle_manifest.json`

Manifest minimum fields:

- `schema` (int)
- `vhk_version`
- `created_at` (UTC ISO-ish string)
- `project_dir_name`
- `file_count`, `total_bytes`
- `files[]`: `path`, `size`, `sha256`, `mtime`
- optional `bundle_support_metadata`: planner-backed support snapshot with `claim_source`, target counts, claim-level counts, audit status counts, target rows, and review commands

Recommended reproducibility behavior:

- stable file ordering
- optional deterministic zip-entry timestamps
- honor `SOURCE_DATE_EPOCH` (or explicit CLI override) when requested
- record deterministic metadata in the manifest when normalization is active

Rationale:

- Enables later “verify bundle” tooling.
- Enables integrity-aware caching for image assets.
- Lets a bundle communicate its claimed Linux support lanes and missing proof artifacts without forcing the recipient to reverse-engineer the repo first.

### 3.3 Needle asset model (openQA-inspired)

Needle = `name.png` + optional `name.json` metadata.

Supported metadata concepts:

- match areas (different thresholds per area)
- exclude areas (masked matching)
- click points
- OCR areas

The engine must be able to:

- load/validate needle metadata
- run matching with match+exclude masks
- use click points in `ClickNeedle`
- use OCR areas in `OcrNeedleText` / `WaitForNeedleText`

---

## 4) Backend specs

### 4.1 Desktop/session detection

The engine must detect the active desktop backend:

- X11
- Wayland

Rules:

- Prefer `WAYLAND_DISPLAY` as authoritative when present.
- Avoid accidentally selecting X11-only tools inside Wayland sessions.

### 4.2 Input injection

Input injection is best-effort and backend-dependent.

**X11 (target for v1):**

- Default: `xdotool` for keyboard/mouse.
- Optional: `xvkbd` for text.

**Wayland:**

- Keyboard: `wtype` when the compositor supports a virtual keyboard protocol.
- Pointer/keyboard fallback: uinput tools (`ydotool`, `dotool`) when permitted.
- Future: portal/libei EIS via a helper (see `docs/LIBEI_EIS_AND_PORTALS.md`).

### 4.3 Screen capture + region selection

**X11:** `maim` preferred; `scrot`/ImageMagick fallbacks.

**Wayland (wlroots-first):** `grim` + `slurp`.

**Non-wlroots fallbacks:** desktop-native screenshot helpers (GNOME/KDE), or an
interactive portal flow.

### 4.4 WM integration

- i3/sway: IPC socket protocol (query tree, subscribe to events).
- Hyprland: best-effort config generation + inspector integration.

---

## 5) Performance targets

The goal is “AHK-feeling” responsiveness for common macros.

### 5.1 Wait loops

- Default poll interval: 100–250ms depending on step.
- `max_poll_ms` supports exponential backoff.
- Jitter reduces thundering herds and avoids accidental sync with animations.

### 5.2 Vision

- Prefer ROI-scoped operations.
- Cache decoded images when repeatedly evaluating inside loops.
- Provide multi-scale matching only when requested.

---

## 6) Security model

- Expressions are sandboxed (no imports, no attribute mutation, no arbitrary calls).
- Shell execution (`RunShell`) exists but is explicit.
- Bundles contain integrity data (checksums) but are not a trust boundary.

---

## 7) Test strategy

The repo should keep a high-signal unit/integration test suite that is:

- runnable headlessly in CI
- largely independent of a live X11/Wayland session
- heavy use of fixtures and file-backed vision tests

Minimum categories:

- expression evaluation + validation
- step schema validation
- runner control flow and retry semantics
- vision algorithms (template match, pixel search, OCR parsing)
- project tools (bundle, validate, lint, optimize, retime)

---

## 8) Roadmap slices

High-leverage next steps (engine-facing):

1. **Portal/libei prototype path** (small helper binary + feature flag).
2. **AT-SPI selectors** (read-only inspector first; then action steps), but modeled as a separate-bus / per-app coverage contract with desktop-metadata and vision fallbacks instead of a universal Linux promise.
3. **Recorder upgrades** (richer key state capture beyond current smoothing/thinning).
4. **Studio contract definition** (event log as debugger substrate).

- Palette/runtime metadata now includes optional icon names/paths plus invisible search terms, so launcher integrations can stay both searchable and visually informative without inventing a second menu model.
- Exported launcher scripts should be able to participate in richer Linux picker protocols when available (for example rofi script mode with `info`, `meta`, and `icon` row metadata) while still falling back to plain stdin/stdout picker behavior elsewhere.
- Rofi integration should be treated as an explicit custom-mode export (`name:script`), not as a magical script directory convention. VHK should be able to emit an exact rofi invocation or manifest for a project palette.


## WM integration bundles

VHK can export a complete WM integration bundle via `export-wm-bundle`. A bundle may include a launcher helper script, a WM binding or launcher-mode snippet, a bootstrap note describing the parent config line to add once, and a JSON manifest. Install mode writes those artifacts into conventional XDG bin/config targets instead of a self-contained directory.


## 8) `plan-project` architecture maps and stack profiles

- `vhk plan-project --json` should expose a stable planning surface that future
  Studio tools can reuse.
- That surface now includes:
  - `architecture_map` (components + risks + overall stance)
  - `deployment_profiles` / `stack_profiles` (scored stack-fit suggestions with commands and blockers, plus explicit thin-vs-stateful layer guidance)
  - `runtime_seams` (the ownership/contract split between runner core, trigger layers, text exports, services, selector packs, and helper boundaries)
  - `ecosystem_lessons` (normalized lessons borrowed from AHK / Pulover / Espanso / AutoKey / xremap / portal / remapper ecosystems)
- The intent is to make product-shape analysis actionable: authors should be
  able to see which layers belong in VHK core versus helper/export/service
  boundaries without re-deriving the same advice in multiple places.

## `plan-project` runtime seam contract

`vhk plan-project --json` now includes `runtime_seams: list[object]`.

Each item should contain at least:

- `id`
- `title`
- `layer_kind`
- `fit`
- `owner`
- `responsibility`
- `why_split`
- `latency_class`
- `contracts`
- `artifacts`
- `commands`
- `anchored_profiles`
- `notes`

The intent is to let future Studio/design/install flows talk explicitly about
which surfaces stay thin and which ones hold runtime state.

## `plan-project` ecosystem lesson contract

`vhk plan-project --json` now includes `ecosystem_lessons: list[object]`.

Each item should contain at least:

- `id`
- `title`
- `category`
- `fit`
- `source_tools`
- `summary`
- `product_implication`
- `commands`
- `related_profiles`
- `related_seams`
- `evidence`

These records intentionally turn research into planner output so product/design
work is not stranded in markdown notes.


## `plan-project` surface choice contract

`vhk plan-project --json` now includes `surface_choices: list[object]`.

Each item should contain at least:

- `id`
- `category`
- `score`
- `fit`
- `title`
- `summary`
- `strengths`
- `tradeoffs`
- `commands`
- `learn_from`
- `evidence`

The intent is to compare concrete Linux integration surfaces, not just project
shape. These records should stay explainable and machine-readable enough for a
future Studio or review UI.

## `plan-project` environment diff contract

`vhk plan-project --json` now includes `environment_diffs: list[object]`.

Each item should provide a stable planning view over a hypothetical target
environment and include at least:

- `id`
- `title`
- `backend`
- `score`
- `fit`
- `summary`
- `assumptions`
- `learn_from`
- `capability_statuses`
- `top_target`
- `top_profile`
- `preferred_surfaces`
- `blocking_capabilities`
- `diff_highlights`
- `commands`

These items are heuristic planning profiles, not live capability probes.
They exist so future Studio/help/install flows can compare environment shape
without needing to boot every target desktop first.

## `plan-project` portability gap contract

`vhk plan-project --json` now includes `portability_gaps: list[object]`.

Each item should include at least:

- `id`
- `title`
- `baseline`
- `score`
- `fit`
- `score_delta`
- `summary`
- `newly_blocked_capabilities`
- `degraded_capabilities`
- `relaxed_blockers`
- `keep_surfaces`
- `replace_surfaces`
- `new_preferred_surfaces`
- `migration_response`
- `commands`
- `learn_from`

The intent is to keep environment planning actionable. `environment_diffs`
shows how a project lands on multiple hypothetical desktops; `portability_gaps`
shows what the team must actually change when it moves from the strongest target
into a more conservative support lane.

## `plan-project` portability playbook contract

`vhk plan-project --json` now includes `portability_playbooks: list[object]`.

Each item should include at least:

- `id`
- `title`
- `priority`
- `goal`
- `summary`
- `artifacts`
- `commands`
- `install_checks`
- `related_surfaces`
- `learn_from`
- `baseline`

The intent is to bridge strategy and deployment.
`portability_gaps` says what changes between environments; `portability_playbooks`
should make those changes executable by naming the exports, install checks, and
validation commands that belong to the destination lane.



## `plan-project` reference pattern contract

`vhk plan-project --json` now includes `reference_patterns: list[object]`.

Each item should expose at least:

- `id`
- `title`
- `pattern_type`
- `score`
- `fit`
- `summary`
- `borrow: list[str]`
- `avoid: list[str]`
- `evidence: list[str]`
- `commands: list[str]`
- `learn_from: list[str]`

The purpose of this surface is to encode product-shape lessons from adjacent
Linux and automation tools directly into planner output. It should remain
explainable rather than trying to be an opaque recommendation model.


- concrete toolchain choices:
  - text injection paths (`xdotool`, `wtype`, clipboard-first, helper/uinput seams)
  - typed-vs-pasted text should stay explicit in authoring and planning: long literal single-line text may be promoted to clipboard-paste for throughput, `${...}` templates stay in the typed lane by default, and structured Tab/Enter-rich form text may optionally be split into a hybrid lane where navigation separators remain typed while large literal field chunks paste explicitly
  - pointer injection boundaries (`xdotool`, portal/helper, `ydotool` / `dotool`-class fallbacks)
  - capture paths (portal-first vs compositor/X11-native tooling)
  - trigger/context tooling (WM binds, portal shortcuts, `wmctrl`/`xprop`, `hyprctl`/`swaymsg`/`kdotool`)


## `plan-project` verification gate contract

`vhk plan-project --json` now includes `verification_gates: list[object]`.

Each item should include at least:

- `id`
- `title`
- `capability`
- `category`
- `priority`
- `gate_type`
- `summary`
- `acceptance_checks`
- `commands`
- `artifacts`
- `target_environments`
- `fallback_path`
- `recommended_toolchain`
- `evidence`

The intent is to bridge planning and release confidence.
`capability_coverage` explains where a feature is portable or conditional;
`verification_gates` should state what the team must actually prove before that
feature is treated as ready to ship.


## `plan-project` deployable surface contract

`vhk plan-project --json` now includes `deployable_surfaces: list[object]`.

Each item should include at least:

- `id`
- `title`
- `category`
- `entrypoint`
- `summary`
- `fit`
- `priority`
- `artifacts`
- `install_targets`
- `generator_commands`
- `validation_commands`
- `acceptance_checks`
- `related_capabilities`
- `related_surface_choices`
- `first_wave`
- `notes`

The purpose is to group file-level exports back into the Linux-facing surfaces
users actually install and depend on. `artifact_blueprint` answers which files
exist; `deployable_surfaces` answers which operational surface those files form.

## `plan-project` setup recipe contract

`vhk plan-project --json` now includes `setup_recipes: list[object]`.

Each item should include at least:

- `id`
- `title`
- `category`
- `audience`
- `priority`
- `when_to_use`
- `summary`
- `surface_ids`
- `surfaces`
- `artifacts`
- `install_targets`
- `generator_commands`
- `validation_commands`
- `acceptance_checks`
- `install_steps`
- `verify_steps`
- `rollback_steps`
- `related_capabilities`
- `first_wave`
- `playbooks`
- `notes`

The purpose is to turn planner output into explicit Linux-native setup handoffs.
`deployable_surfaces` names the operator-facing surface; `setup_recipes` names
the install/review/verification flow needed to make that surface real and safe
to ship.


## `gen-operator-pack` artifact contract

`vhk gen-operator-pack <project_dir>` should be able to emit a planner-backed
operator pack for an existing project.
A companion verification pack should turn the same planner output into shipping/release artifacts instead of leaving verification gates trapped in advisory JSON.

Generated artifacts:

- `VHK_OPERATOR_PLAN.json`
- `VHK_OPERATOR_GUIDE.md`
- `VHK_DEPLOYMENT_CHECKLIST.md`

The JSON plan is expected to preserve the same `plan-project` structure so
other tools can reuse it without inventing a second planning schema.

The markdown artifacts are expected to be human-facing handoff surfaces:

- guide: deployable surfaces, setup recipes, verification gates, wave order,
  reference patterns, and optionally current-session fit
- checklist: baseline refresh, install/rollback steps, shipping gates, and
  generator-command reminders

This command is intentionally not a promise of one-click installation.
Its job is to turn planner output into explicit Linux-native deployment docs
without pretending that X11, GNOME Wayland, KDE Wayland, wlroots, Hyprland,
remapper daemons, and helper-backed injection all share one honest install
script.

## `gen-support-pack` artifact contract

`vhk gen-support-pack <project_dir>` should be able to emit a planner-backed
support pack for an existing project.

Generated artifacts:

- `VHK_SUPPORT_PLAN.json`
- `VHK_SUPPORT_GUIDE.md`
- `VHK_SUPPORT_CHECKLIST.md`
- `scripts/vhk_capture_support.sh`

The JSON plan is expected to preserve the same `plan-project` structure while
adding support-oriented sections such as likely evidence artifacts, support
paths, privacy review notes, and capture commands.

The markdown artifacts are expected to be human-facing triage surfaces:

- guide: evidence collection loop, support artifacts, current-session fit,
  privacy review, and reproduction commands
- checklist: baseline refresh, evidence collection, privacy review, and
  handoff fields

The capture script is expected to be explicit and reviewable rather than
pretending that one opaque support upload flow is safe for every Linux setup.
It should prefer deterministic JSON reports, recent event evidence, and opt-in
project bundling over blind data collection.


## `gen-portability-pack` artifact contract

`vhk gen-portability-pack <project_dir>` should be able to emit a planner-backed
portability pack for an existing project.

Generated artifacts:

- `VHK_PORTABILITY_PLAN.json`
- `VHK_PORTABILITY_GUIDE.md`
- `VHK_TARGET_ROLLOUT.md`
- `scripts/vhk_review_portability.sh`

The JSON plan is expected to preserve the same `plan-project` structure while
adding a stable `target_rollout` ordering, portability review commands, and
lightweight path metadata for generated review bundles.

The markdown artifacts are expected to be human-facing cross-desktop review
surfaces:

- guide: target rollout order, capability coverage hot spots, portability gaps,
  migration playbooks, export surfaces, and optional current-session fit
- rollout worksheet: baseline refresh, target order, capability proof points,
  and handoff requirements to operator/verification/support packs

The review script is expected to be explicit and honest: it should capture the
current planner/doctor/validate baseline, regenerate the related handoff packs,
and write a review bundle without pretending that portability can be proven on
a single machine or with a single generic Linux backend.

## `gen-claim-pack` artifact contract

`vhk gen-claim-pack <project_dir>` should be able to emit a planner-backed
support-claim pack for an existing project.

Artifacts:

- `docs/VHK_CLAIM_GUIDE.md`
- `docs/VHK_TARGET_CLAIMS.yaml`
- `docs/VHK_CLAIM_AUDIT_PLAN.json`
- `scripts/vhk_audit_claims.sh`

The claim manifest should seed each target with:

- `target`
- `title`
- `recommended_level`
- editable `claim_level`
- blockers / caveats
- required artifacts
- required commands
- evidence state / maintainer notes

The generated guide should explain the claim tiers (`reference`, `supported`,
`caveated`, `experimental`, `unsupported`) and make it explicit that projects
should not silently translate a portability worksheet into blanket Linux claims.

## `audit-target-claims` contract

`vhk audit-target-claims <project_dir>` should read
`docs/VHK_TARGET_CLAIMS.yaml` by default and compare it against the current
planner output.

Audit expectations:

- unknown targets fail
- invalid claim levels fail
- stronger-than-recommended claims fail
- missing proof artifacts can fail stronger claims
- missing maintainer notes / evidence state can warn

The command should be usable both as a human-readable review table and as a
machine-readable JSON report suitable for CI or release-rehearsal scripts.

## `gen-publish-pack` artifact contract

`vhk gen-publish-pack <project_dir>` should be able to emit a planner-backed
publish/distribution pack for an existing project.

Artifacts:

- `docs/VHK_PUBLIC_SUPPORT.md`
- `docs/VHK_INSTALL_QUICKSTART.md`
- `docs/VHK_PUBLISH_PLAN.json`
- `scripts/vhk_refresh_publish_pack.sh`
- `build/publish/<bundle-name>/README.md`
- `build/publish/<bundle-name>/vhk_publish_handoff.json`
- `build/publish/<bundle-name>/refresh_publish_inputs.sh`
- `build/publish/<bundle-name>/bundle_release.sh`

The generated markdown artifacts should be audience-facing instead of purely
operator-facing:

- `VHK_PUBLIC_SUPPORT.md` should summarize the support matrix in release-note /
  README language while preserving claim tiers and proof expectations
- `VHK_INSTALL_QUICKSTART.md` should summarize rollout order, install surfaces,
  setup recipes, and bundle review commands for recipients

The JSON plan is expected to preserve the existing planner structure while
adding:

- `public_support_matrix`
- `recommended_rollout`
- `language_guardrails`
- `publish_headline` / `publish_summary`
- `publish_paths` / `publish_commands`
- `bundle_release_story` with enough detail to distinguish whole-project bundles
  from `release-stage` bundles chosen via `--bundle-target-profile <profile_id>`
- `publish_handoff` with a concrete review tree (`build/publish/<bundle-name>/`)
  that can copy public docs, keep stage references, and expose ship scripts

The refresh script is expected to regenerate the surrounding handoff packs,
refresh the publish pack itself, produce a deterministic bundle, and record
`vhk inspect-bundle` output for release review. When a bundle target profile is
selected, it should regenerate that lane's stage tree first and then call
`vhk bundle-stage` instead of `vhk bundle`. The handoff tree is expected to
copy the publish docs into `payload/docs/`, expose project-root-relative refresh
and bundle scripts, and include the chosen stage README/manifest when a
release-stage bundle is selected.


## Entrypoint support posture contract

Outward-facing export surfaces should consume the same audited publish/support
posture as bundle metadata. In practice that means:

- `export-launcher-script` should embed a support snapshot and expose human + JSON support inspection flags
- that support snapshot should ingest release-lane posture when available, so launcher/about surfaces can name a flagship desktop lane instead of collapsing to generic Linux wording
- `export-desktop-entry` should emit `X-VHK-Support-*` metadata keys and should not invent stronger wording than the publish headline supports
- desktop entries should also emit `X-VHK-Release-*` metadata so menu/install surfaces can carry the reference/support/caveated lane split forward
- self-contained `export-wm-bundle` outputs should carry public support/install docs plus a machine-readable support JSON file
- WM bundle support JSON and shareable bundle manifests should also carry a release-lane snapshot when available so downstream tooling can verify which desktop family is being treated as flagship
- `vhk-wm-bundle.json` should record those support artifacts so downstream tooling can verify that exported integration bundles remain honest

## `inspect-bundle` contract

`vhk inspect-bundle <bundle.zip>` should read `vhk_bundle_manifest.json` and
render the embedded support snapshot when present.

Inspection expectations:

- print bundle basics (`project_dir_name`, `created_at`, file counts, deterministic metadata)
- surface whether support metadata came from planner recommendations or an edited claim file
- summarize claim tiers and audit statuses across targets
- show per-target `claim_level`, `recommended_level`, audit `status`, and proof-artifact presence
- note whether the bundle includes the public support/install docs generated by `vhk gen-publish-pack`
- preserve a machine-readable `--json` mode for downstream tooling and CI dashboards



## `gen-setup-pack` artifact contract

`vhk gen-setup-pack <project_dir>` should turn planner `setup_recipes` into
project-level docs and shell entrypoints rather than leaving them trapped in
`vhk plan-project --json`.

Default artifacts:

- `docs/VHK_SETUP_GUIDE.md`
- `docs/VHK_SETUP_MATRIX.md`
- `docs/VHK_SETUP_PLAN.json`
- `scripts/vhk_apply_setup_recipes.sh`
- `scripts/vhk_verify_setup_recipes.sh`
- `scripts/vhk_install_toolchain_packages.sh`

Contract details:

- generated docs should preserve the planner's install / verify / rollback
  framing instead of collapsing everything into a fake universal installer
- shell scripts should only auto-run strings that look like real commands;
  prose guidance should remain documented, not executed
- the package bootstrap helper should default to printing distro-oriented
  install commands derived from planner `toolchain_choices`; execution should
  remain opt-in (`RUN_INSTALL=1`) because package names are only best-effort
  hints
- command strings should be rewritten to be portable from the project root when
  they would otherwise embed the maintainer's absolute project path
- `RECIPE_FILTER` should let users rerun only a subset of recipe ids
- the JSON plan should expose both the raw setup recipe story and the runnable
  command subsets derived from it
- the JSON plan should also expose normalized toolchain package groups plus
  aggregate package-manager commands for apt/dnf/pacman/zypper-class systems
- when host checks are available, the docs and JSON plan should also expose an
  observed deployment-truth summary (`host_truth`) plus the shared
  `portal_route_contract`, so setup guidance keeps configured routing,
  installed backend manifests, and live portal interfaces visible together

## `gen-session-fit-pack` artifact contract

`vhk gen-session-fit-pack <project_dir>` should join the planner's project-shape
story with the current session capability matrix so operators can answer a
practical Linux question: *is this project ready on this host, degraded here, or
blocked until helper/backend fixes land?*

Minimum outputs:

- `docs/VHK_SESSION_FIT.md`
- `docs/VHK_SESSION_FIXUPS.md`
- `docs/VHK_SESSION_PLAN.json`
- `scripts/vhk_review_session_fit.sh`

Contract details:

- the pack should summarize required capabilities actually used by the project
  (capture, text injection, pointer injection, hotkeys, window/context) instead
  of repeating the whole doctor matrix verbatim
- the pack should classify host fit conservatively (`ready`, `degraded`,
  `blocked`, `unknown`) from the current session snapshot
- blocked/degraded capabilities should be linked back to planner
  `toolchain_choices` and normalized setup/bootstrap groups so the fixup lane is
  reviewable instead of tribal knowledge
- the review script should refresh `doctor`, `validate`, `plan-project`, and
  the session-fit pack itself into a small evidence directory
- when an explicit `--evidence-lane <profile-id>` is selected, the pack JSON,
  markdown docs, and review script should keep that lane visible instead of
  silently falling back to the flagship default on rerun
- the pack must remain honest that package/bootstrap guidance is still
  best-effort and desktop-shaped; session fit is a review surface, not a
  fake universal installer

## `gen-host-contract-pack` artifact contract

`vhk gen-host-contract-pack <project_dir>` should turn planner `host_requirements`
plus a live host snapshot into a deployment contract that keeps Linux-native
operator work explicit instead of collapsing it into package hints.

Minimum outputs:

- `docs/VHK_HOST_REQUIREMENTS.md`
- `docs/VHK_HOST_FIXUPS.md`
- `docs/VHK_HOST_PLAN.json`
- `scripts/vhk_review_host_contract.sh`

Contract details:

- the pack should keep packages, services, permissions, and portal/session
  requirements visibly separate
- the JSON plan should expose per-requirement observed status (`ready`,
  `degraded`, `blocked`, `unknown`) without pretending every service can be
  auto-detected perfectly
- host fixups should be grouped back by capability so pointer/text/capture/
  hotkey problems are reviewable as product lanes, not only as distro chores
- the review script should refresh `doctor`, `validate`, `plan-project`, and
  the host-contract pack itself into a small evidence directory
- when an explicit `--evidence-lane <profile-id>` is selected, the pack JSON,
  markdown docs, and review script should preserve that proof context so
  host-side review does not drift back to the flagship lane
- the pack should preserve helper/uinput/portal-routing uncertainty honestly;
  this is a host review contract, not a one-click installer

## `gen-readiness-pack` artifact contract

`vhk gen-readiness-pack <project_dir>` should turn the host contract into a
live readiness proof. The key question is no longer only *what should this host
provide?* but also *which of those services, groups, sockets, and raw-input
paths are actually live right now?*

Minimum outputs:

- `docs/VHK_READINESS_REPORT.md`
- `docs/VHK_READINESS_FIXUPS.md`
- `docs/VHK_READINESS_PLAN.json`
- `scripts/vhk_refresh_readiness_report.sh`

Contract details:

- the pack should reuse planner `host_requirements` and host-contract language
  instead of inventing a second taxonomy for services/permissions/portals
- the JSON plan should expose per-requirement live readiness (`ready`,
  `degraded`, `blocked`, `unknown`) and keep the older host-contract status
  visible for comparison
- service proofs should be explicit about scope (`system` vs `user`) and should
  tolerate manager-unavailable or unit-missing states without pretending that
  systemd coverage is universal
- permission proofs should make current groups, `/dev/uinput`, and raw input
  event readability visible because Linux-native remappers/helper daemons depend
  on all three more often than package installers admit
- the refresh script should rerun `doctor`, `validate`, `plan-project`,
  `gen-host-contract-pack`, and `gen-readiness-pack` into a small evidence
  directory
- the pack must remain conservative: this is a deployment-readiness review
  surface, not a claim that every desktop uses the same service manager or
  permission policy


## `plan-project` macro route profile contract

`vhk plan-project --json` now also includes `macro_route_profiles: list[object]`, `macro_export_candidates: list[object]`, `route_portfolio: list[object]`, `export_promotion_plan: list[object]`, `promotion_input_lane_plan: list[object]`, `promotion_activation_route_plan: list[object]`, `promotion_operator_control_plan: list[object]`, `promotion_recovery_plan: list[object]`, `promotion_verification_plan: list[object]`, `promotion_performance_plan: list[object]`, `promotion_dispatch_budget_plan: list[object]`, `promotion_waves: list[object]`, `promotion_readiness: list[object]`, `promotion_backlog: list[object]`, and `promotion_evidence: list[object]`.

Each entry is expected to answer a practical Linux-native product question: *who
owns this macro?* Instead of only describing the whole project as “text-first”,
“helper-boundary”, or “event-driven”, the planner should say which individual
macro belongs to which lane.

Each profile should include at least:

- `macro`
- `route_id`
- `title`
- `fit` (`strong|good|conditional|weak`)
- `owner_layer`
- `execution_surface`
- `primary_activation_route_id`

Each export candidate should include at least:

- `macro`
- `route_id`
- `export_surface_id`
- `title`
- `fit`
- `reason`
- `tool_family`
- `commands`
- `primary_activation_route_id`

`vhk lint-project` may surface those as advisory `ROUTE_DRIFT_*` findings when a macro obviously fits one of those lanes better than “runner only”.

- `activation_route_status`
- `summary`
- `why`
- `learn_from`
- `commands`
- `capabilities`
- `evidence`
- `risks`

This contract exists so VHK can stay honest about route ownership: a remap-like
key transform should not quietly masquerade as “just another runner macro”, a
hotstring should not be forced to look like heavyweight replay, and a Wayland
pointer/capture flow should say out loud that it lives behind a helper seam.

`route_portfolio` groups those macro rows by `route_id` and should include at
least:

- `route_id`
- `title`
- `macro_count`
- `dominant_fit`
- `fit_counts`
- `top_activation_routes`
- `top_execution_surfaces`
- `example_macros`

`export_promotion_plan` groups the export candidates by promotion surface and
should include at least:

- `export_surface_id`
- `title`
- `priority`
- `macro_count`
- `dominant_fit`
- `fit_counts`
- `route_ids`
- `macros`
- `tool_family`
- `commands`
- `activation_routes`

These aggregates exist so `plan-project` can answer the next question after
"who owns each macro?": *what Linux-native promotion work should the project
actually ship next?*

`promotion_input_lane_plan` should include at least:

- `export_surface_id`
- `title`
- `shipping_posture` (`flagship|specialist|reviewed|orthogonal`)
- `primary_input_lane_id`
- `primary_input_lane_fit`
- `alternate_input_lane_ids`
- `recommended_input_lane_ids`
- `host_requirement_ids`
- `commands`
- `summary`

This contract exists so project-level promotion work stays tied to the lane that
should really own the shipped experience. A text package should be able to say
“ship through the clipboard-first text lane”, while a helper-boundary dossier
should stay explicitly review-led around portal or daemon-backed playback instead
of silently inheriting the repo's globally highest-scoring lane.

`promotion_activation_route_plan` should include at least:

- `export_surface_id`
- `title`
- `startup_posture` (`resident|session-bound|launcher-first|reviewed|orthogonal`)
- `primary_activation_route_id`
- `primary_activation_kind`
- `primary_activation_fit`
- `startup_owner`
- `steady_state`
- `entrypoint`
- `alternate_activation_route_ids`
- `recommended_activation_route_ids`
- `host_requirement_ids`
- `commands`
- `summary`

This companion contract exists so project-level shipping work keeps startup and
steady-state ownership visible. A text package should be able to say “ship via
a resident text surface route”, while a launcher surface should be able to say
“wake through launcher-entrypoint” without forcing reviewers to reconstruct
lifecycle ownership from separate activation docs.

## `plan-project` activation route contract

`vhk plan-project --json` now also includes `activation_routes: list[object]`.

Each item should contain at least:

- `id`
- `title`
- `activation_kind`
- `fit`
- `startup_owner`
- `steady_state`
- `entrypoint`
- `why`
- `commands`
- `verification_commands`
- `depends_on_requirements`
- `depends_on_seams`
- `related_surface_ids`
- `fallback_routes`
- `requirements`
- `notes`
- `evidence`

The intent is to let future Studio/install/release flows talk explicitly about
how a project wakes up and stays alive on Linux instead of inferring launch
ownership from scattered docs.

## `gen-activation-pack` artifact contract

`vhk gen-activation-pack <project_dir>` should turn planner activation routes
plus host/readiness evidence into a reviewable activation handoff.

Minimum outputs:

- `docs/VHK_ACTIVATION_ROUTES.md`
- `docs/VHK_ACTIVATION_FIXUPS.md`
- `docs/VHK_ACTIVATION_PLAN.json`
- `scripts/vhk_review_activation_routes.sh`

Contract details:

- the pack should reuse planner `activation_routes`, host-contract language, and
  readiness proofs rather than inventing a second launch taxonomy
- the JSON plan should expose per-route status (`ready`, `planned`, `degraded`,
  `blocked`, `unknown`) plus startup order and fallback routes
- the docs should keep launcher/manual, portal-session, service, remapper, and
  helper-daemon lanes visible as separate activation kinds
- the refresh script should gather the same review loop used by host-contract
  and readiness packs before refreshing the activation artifacts

## `gen-capability-audit-pack` artifact contract

`vhk gen-capability-audit-pack <project_dir>` should turn the repo's strategy promise of a "capability audit and fallback pack" into a real shipping artifact instead of leaving it implied inside `plan-project`.

Minimum contract:

- emit `docs/VHK_CAPABILITY_AUDIT.md`, `docs/VHK_CAPABILITY_FIXUPS.md`, and `docs/VHK_CAPABILITY_AUDIT_PLAN.json`
- combine current session capability facts, host requirements, readiness checks, and activation fallback routes into one audit view
- keep helper boundaries and portal routing visible instead of flattening them into generic compatibility language
- include claim posture when `docs/VHK_TARGET_CLAIMS.yaml` exists
- emit `scripts/vhk_refresh_capability_audit_pack.sh`
- emit a reviewable handoff tree under `build/capability-audit/<project>/` with a capture script that can regenerate doctor/validate/plan + host/readiness/activation/audit docs into one fresh snapshot

The point is not to "prove Linux works" in the abstract. The point is to keep uncomfortable desktop/session/helper truths close to the release story so public claims and support flows stay honest.



`promotion_waves` should stage the promotion plan into at least three ordered waves:

1. a high-priority specialist-export wave (text/remapper/service surfaces)
2. a medium-priority helper/conditional wave
3. a lower-priority auxiliary/launcher refinement wave

Each wave should expose at least `wave_id`, `order`, `priority`, `title`, `goal`, `surface_count`, `macro_count`, `export_surface_ids`, `route_ids`, and `commands`.

## `gen-promotion-pack` artifact contract

`vhk gen-promotion-pack <project_dir>` should turn `route_portfolio`, `export_promotion_plan`, `promotion_input_lane_plan`, `promotion_activation_route_plan`, `promotion_operator_control_plan`, `promotion_recovery_plan`, `promotion_verification_plan`, `promotion_performance_plan`, `promotion_dispatch_budget_plan`, `promotion_waves`, `promotion_readiness`, and `promotion_evidence` into reviewable project artifacts rather than leaving promotion work stranded in terminal tables.

Default artifacts:

- `docs/VHK_PROMOTION_PLAN.md`
- `docs/VHK_PROMOTION_FIXUPS.md`
- `docs/VHK_PROMOTION_PLAN.json`
- `docs/VHK_PROMOTION_BACKLOG.md`
- `scripts/vhk_review_promotion_plan.sh`

The promotion plan doc should summarize route ownership, staged waves, shipping-lane ownership (`promotion_input_lane_plan`), startup-route ownership (`promotion_activation_route_plan`), operator-control ownership (`promotion_operator_control_plan`), recovery ownership (`promotion_recovery_plan`), verification ownership (`promotion_verification_plan`), performance ownership (`promotion_performance_plan`), dispatch-budget ownership (`promotion_dispatch_budget_plan`), and surface-by-surface commands. Each promotion surface should show at least its shipping posture, primary input lane, primary activation route, primary dispatch posture, alternate lanes/routes, related host requirements, and review commands so reviewers do not have to reconstruct shipping reality from separate planner outputs. The fixups doc should call out high-priority promotions plus conditional/helper-boundary surfaces that still need explicit fallback language. The backlog doc should turn those same surfaces and gates into an ordered execution queue. The refresh script should rerun the planner and the related design/route packs so reviewers can update the evidence bundle in one step.

## `gen-route-selection-pack` artifact contract

`vhk gen-route-selection-pack <project_dir>` should turn activation routes plus
host/readiness evidence into an explicit **reference-route** decision. The
important question is no longer only *which routes exist?* but also *which one
should this project actually ship as the reference lane on this host, and which
ones stay fallback or experimental?*

Minimum outputs:

- `docs/VHK_ROUTE_SELECTION.md`
- `docs/VHK_ROUTE_FIXUPS.md`
- `docs/VHK_ROUTE_PLAN.json`
- `scripts/vhk_review_route_selection.sh`

Contract details:

- the pack should reuse planner `activation_routes` and the readiness/host
  language instead of inventing a third taxonomy for launch ownership
- the JSON plan should expose per-group primary routes, fallback routes, and
  promotion candidates so one lane can be marked as the reference route without
  hiding healthier backups
- the docs should preserve the distinction between universal/manual entry,
  trigger ownership, text surfaces, event planes, and helper/input edges
- the fixups doc should make it obvious when the preferred primary route is only
  `planned` or `degraded` while a fallback route is already `ready`

## `gen-target-route-pack` artifact contract

`vhk gen-target-route-pack <project_dir>` should compare route-selection decisions
across a conservative set of hypothetical Linux target profiles instead of only
reflecting the current host.

Generated artifacts:

- `docs/VHK_TARGET_ROUTE_MATRIX.md`
- `docs/VHK_TARGET_ROUTE_FIXUPS.md`
- `docs/VHK_TARGET_ROUTE_PLAN.json`
- `scripts/vhk_compare_target_routes.sh`

Contract notes:

- the pack should reuse planner-backed activation/route language instead of
  inventing a third trigger taxonomy
- target profiles are hypothetical planning profiles, not live deployment proof
- the JSON plan should expose per-profile reference routes plus a cross-profile
  group matrix showing which route ids diverge
- the matrix doc should make stable groups vs divergent groups obvious enough for
  release planning
- the fixups doc should call out groups where GNOME/KDE/wlroots/X11 targets want
  different primary routes so support claims and docs do not collapse those into
  one fictional universal lane
- the refresh script should rerun `plan-project`, `gen-activation-pack`,
  `gen-route-selection-pack`, and `gen-target-route-pack` in project-local form
- the refresh script should rerun `doctor`, `validate`, `plan-project`,
  `gen-host-contract-pack`, `gen-readiness-pack`, `gen-activation-pack`, and
  the route-selection pack itself into a small evidence directory


## `gen-release-lane-pack` artifact contract

`vhk gen-release-lane-pack <project_dir>` should consume the hypothetical target
route comparison and turn it into per-desktop release/support guidance instead
of leaving maintainers to hand-maintain release notes for each Linux family.

Generated artifacts:

- `docs/VHK_RELEASE_LANES.md`
- `docs/VHK_RELEASE_SNIPPETS.md`
- `docs/VHK_RELEASE_LANE_PLAN.json`
- `scripts/vhk_refresh_release_lanes.sh`

Contract notes:

- the pack should reuse target-route/activation language instead of inventing a
  fourth release taxonomy
- the JSON plan should classify each modeled target profile into release lanes
  such as `reference`, `supported`, `caveated`, or `experimental`
- the docs should preserve which primary routes were selected for universal,
  trigger, text, and event lanes on each target profile
- the snippets doc should produce copy-ready public/support language so README,
  release notes, and support docs do not drift apart
- the pack should surface missing docs/artifacts that a maintainer ought to ship
  before making stronger desktop/session claims
- the refresh script should rerun `plan-project`, `gen-target-route-pack`,
  `gen-publish-pack`, and `gen-release-lane-pack` in project-local form


## `gen-trigger-pack` artifact contract

`vhk gen-trigger-pack <project_dir>` should be able to emit a self-contained
trigger-layer export bundle, defaulting to `<project>/build/trigger_pack/`.

The command should group planner-backed trigger surfaces into one reviewable
artifact root instead of leaving authors to hand-run a series of unrelated
exports for i3/sway/Hyprland, sxhkd, keyd, Kanata, and KMonad.

Minimum outputs:

- `configs/wm/vhk.i3.conf`
- `configs/wm/vhk.sway.conf`
- `configs/wm/vhk.hyprland.conf`
- `configs/x11/vhk.sxhkdrc`
- `configs/remappers/vhk.keyd.conf`
- `configs/remappers/vhk.kanata.kbd`
- `configs/remappers/vhk.kmonad.kbd`
- `docs/VHK_TRIGGER_SURFACES.md`
- `docs/VHK_TRIGGER_MATRIX.md`
- `docs/VHK_TRIGGER_PACK.json`
- `scripts/vhk_refresh_trigger_pack.sh`

The generated configs should carry enough support-posture context that a
recipient can tell they came from VHK's audited Linux-support story, not from an
arbitrary hand-written config fragment.

The trigger-pack JSON should be machine-readable and include:

- project snapshot
- export root
- support headline / claim tiers
- generated surfaces with file paths + generator commands
- non-file/session-managed trigger surfaces (for example portal-driven paths)

The matrix doc should explain which generated trigger surfaces belong in which
target lanes, and should explicitly note when a preferred trigger path has no
static config artifact because it is session/portal managed instead.


## `gen-release-deploy-pack` artifact contract

`vhk gen-release-deploy-pack <project_dir>` should consume the release-lane pack,
setup-pack package hints, and target-route selections to answer the next
maintainer question: *what should I actually ship/install for each chosen desktop
lane?*

The pack should emit:
- `docs/VHK_RELEASE_DEPLOYMENT.md`
- `docs/VHK_RELEASE_INSTALL_SNIPPETS.md`
- `docs/VHK_RELEASE_DEPLOY_PLAN.json`
- `scripts/vhk_refresh_release_deploy.sh`

The JSON plan should:
- preserve per-lane `release_level` / `profile_id`
- classify each lane into a concrete `deploy_style` such as
  `desktop-autostart`, `wm-bundle`, `remapper-service`, or
  `launcher-fallback`
- emit a lane-specific artifact subset with generator commands instead of
  leaving every install/export detail implicit
- surface priority toolchain package groups derived from planner/setup output
- keep copy-ready install/activation commands and verification commands per lane
- carry forward `host_truth`, `host_requirements`, and the shared
  `portal_route_contract` so release-facing docs can compare configured,
  installed, and live session state at the same place maintainers review lane
  install claims
- compute one `flagship_target_fit` contract (and per-lane `target_fit_contract`
  rows where relevant) so release-facing docs can say how the current host
  aligns or drifts from the intended flagship lane instead of only describing
  local readiness

Outward-facing support/export surfaces should be able to ingest a summarized
release-deploy posture so launcher/about output, desktop-entry metadata, WM
bundle manifests, and shareable zip manifests can say which deploy style is the
flagship shipping story.

## `gen-release-stage-pack` artifact contract

`vhk gen-release-stage-pack <project_dir>` should consume the release-deploy pack and
materialize a project-local staging tree for each selected release lane. The command
should write:

- `docs/VHK_RELEASE_STAGE.md`
- `docs/VHK_RELEASE_STAGE_MATRIX.md`
- `docs/VHK_RELEASE_STAGE_PLAN.json`
- `scripts/vhk_refresh_release_stage.sh`
- lane roots under `build/release-stage/<profile_id>/` containing at least:
  - `README.md`
  - `install.sh`
  - `verify.sh`
  - `assemble_payload.sh`
  - `vhk_release_stage.json`
  - `payload/`

The JSON plan should:

- preserve the release-lane level (`reference`, `supported`, `caveated`,
  `experimental`) and deploy style for each lane
- describe the stage root and payload root per lane
- include stage-local assemble/install/verify command lists
- rewrite generated artifact paths from `build/release-lanes/` into
  `build/release-stage/<profile_id>/payload/`
- keep doc-copy commands visible so already-generated publish/release docs can be
  copied into the staged payload without inventing new paths
- surface current `host_truth`, reviewed `host_requirements`, and the shared
  `portal_route_contract` when host checks are available, so staged lane review
  can still compare configured routing, installed backends, and live portal
  interfaces instead of regressing to static packaging prose
- carry one per-lane `target_fit_contract` plus a top-level `flagship_target_fit`
  summary so staged review can compare the current host against the intended
  desktop profile instead of only repeating local host status

The refresh script should rerun `gen-release-deploy-pack` and
`gen-release-stage-pack` in project-local form.

## `bundle-stage` artifact contract

`vhk bundle-stage <project_dir> <out.zip> --target-profile <profile_id>` should
consume one materialized lane from `build/release-stage/<profile_id>/` and zip
that lane root directly instead of re-bundling the whole project checkout.

The stage bundle should:

- keep the lane root as the zip root so `README.md`, `install.sh`, `verify.sh`,
  `assemble_payload.sh`, `vhk_release_stage.json`, and `payload/` stay together
- embed `bundle_kind: release-stage` in `vhk_bundle_manifest.json`
- embed a lightweight `release_stage_metadata` snapshot (`profile_id`, title,
  release level, deploy style, payload root, and stage script paths)
- remain compatible with `vhk verify-bundle` and `vhk inspect-bundle`

Rationale:

- the same stage tree an operator reviews should be the source for a shareable
  zip handoff
- this keeps release-lane packaging aligned with staged payload assembly instead
  of silently falling back to a full project bundle

### 3.2.1 Distribution handoff

VHK should be able to derive packaging handoffs from the same reviewed bundle
story rather than inventing AppImage/Flatpak metadata in a second manual pass.

Minimum expectations:

- `vhk gen-distribution-pack` should consume the publish handoff and preserve
  the chosen bundle kind (`project` vs `release-stage`).
- The generated handoff should keep package metadata, desktop/metainfo files,
  and bundle-refresh scripts in one reviewable tree.
- AppImage output should materialize an AppDir-style skeleton with `AppRun`, a
  root desktop file, and icon metadata.
- Flatpak output should materialize a reverse-DNS app id, a manifest, and
  explicit finish args instead of silently implying broad host access.
- The docs must keep sandboxed/package delivery separate from native remapper
  or helper-daemon lanes so VHK does not market a Flatpak/AppImage as if it
  were equivalent to host-global automation.


## `gen-runtime-pack` artifact contract

`vhk gen-runtime-pack <project_dir>` should extend the publish/distribution
chain into an explicit Python runtime handoff.

Minimum expectations:

- `vhk gen-runtime-pack` should preserve the chosen bundle kind (`project` vs
  `release-stage`) and emit artifacts under `build/publish/<bundle-name>/runtime/`.
- The generated handoff should include a requirements file, build-system
  requirements, a wheelhouse build script, an offline smoke-install script, and
  a machine-readable manifest.
- The runtime handoff should stay explicit that wheelhouses are builder/ABI
  sensitive and therefore need regeneration on the target class of system.
- The docs should position virtual environments as the reversible smoke/native
  install surface rather than mutating system Python.
- The runtime pack should provide one Flatpak bridge helper derived from the
  same requirements file so sandboxed builders do not retype dependency data by
  hand.
- Distribution launchers may reserve a stable embedded-runtime path, but VHK
  should not market package lanes as self-contained merely because a runtime
  handoff exists.


## `gen-runtime-embed-pack` artifact contract

`vhk gen-runtime-embed-pack <project_dir>` should extend the runtime handoff
into exact-target embedding helpers.

Minimum expectations:

- `vhk gen-runtime-embed-pack` should preserve the chosen bundle kind
  (`project` vs `release-stage`) and emit artifacts under
  `build/publish/<bundle-name>/runtime/embed/`.
- The generated handoff should include one bootstrap helper that creates the
  Python environment at a caller-provided target path from the reviewed
  wheelhouse rather than copying an already-built venv around.
- The handoff should include convenience wrappers for at least the native
  target, the AppImage runtime target (`AppDir/usr/lib/vhk-runtime`), and the
  Flatpak files target (`files/lib/vhk-runtime`).
- The generated smoke test should validate the embedded executable against the
  reviewed bundle so a maintainer can prove that exact-path runtime bootstraps
  are runnable before calling a lane self-contained.
- Distribution build scripts may optionally consume the embed helpers when
  `VHK_EMBED_RUNTIME=1`, but the docs must still keep package delivery
  separate from claims about host-global helper/remapper parity.


## `gen-native-install-pack` artifact contract

`vhk gen-native-install-pack <project_dir>` should extend the reviewed
bundle/runtime handoff into one conservative local-install lane.

Minimum expectations:

- `vhk gen-native-install-pack` should preserve the chosen bundle kind
  (`project` vs `release-stage`) and emit artifacts under
  `build/publish/<bundle-name>/native/`.
- The generated handoff should materialize one app tree containing a launcher,
  desktop file, metainfo, icon placeholder, and reviewed bundle payload path so
  maintainers can inspect the native lane as a filesystem layout instead of a
  prose-only plan.
- The handoff should include assemble, install, uninstall, and smoke-test
  scripts, with install/uninstall targeting XDG-local locations instead of
  mutating system directories.
- The install story should remain explicit that an embedded Python runtime is
  optional and built at the final install path; the native lane may be runnable
  with a system `vhk`, but it should not blur that fallback into a claim of full
  self-contained packaging.
- The docs should position this native lane as the conservative proving ground
  before AppImage/Flatpak or helper-daemon-heavy lanes are marketed as polished
  end-user products.
- The generated plan/docs should also surface current `host_truth` plus the
  shared `portal_route_contract` when host checks are available, so install
  caveats stay tied to observed helper/uinput/portal state instead of generic
  Linux prose.
- The native install handoff should also compute one `target_fit_contract` based
  on the chosen/flagship release lane so operators can see whether the current
  machine actually resembles the intended shipping lane.

## `gen-service-compose-pack` artifact contract

`vhk gen-service-compose-pack <project_dir>` should extend the native install
lane into an explicit session-service composition handoff.

Minimum expectations:

- `vhk gen-service-compose-pack` should preserve the chosen bundle kind
  (`project` vs `release-stage`) and emit artifacts under
  `build/publish/<bundle-name>/service/`.
- The generated handoff should include one machine-readable manifest, install
  and uninstall scripts, a smoke test, and a refresh script.
- When the project declares bus watchers, the handoff should materialize a
  first-party VHK user-service lane (preferably socket-activated) instead of
  leaving watcher startup as a README-only instruction.
- The handoff should also materialize one environment.d export file, one
  session-activation sync helper, and one XDG autostart bridge entry so
  PATH/session startup assumptions become reviewable filesystem artifacts.
- The docs must stay explicit that external helpers such as ydotoold, espanso,
  keyd, Kanata, or KMonad remain adjacent services to review separately rather
  than silently becoming VHK-owned lifecycle promises.
- The service pack should prefer a bundle-state runner over direct project-root
  execution: a reviewed bundle should be materialized into state/cache roots and
  then used as the long-lived watcher source instead of assuming the mutable
  checkout is the shipped product.
- The generated user unit should make state/config/cache roots explicit so the
  extraction path, helper scripts, and long-lived watcher state are reviewable
  rather than implied by shell working directories.
- Service-compose docs/plans should also surface current `host_truth` plus the
  shared `portal_route_contract` when available, because long-lived service
  handoffs are exactly where configured-vs-installed-vs-live Linux reality must
  stay reviewable.
- The handoff should emit one explicit session-activation policy that names the
  variables to sync into D-Bus/systemd activation environments and should wire
  that policy into the autostart bridge instead of assuming `environment.d`
  alone captures live graphical-session state.
- The handoff should also emit one explicit session-target policy plus a small
  probe helper, so maintainers can review whether the VHK-owned user unit is
  supposed to bind to `graphical-session.target`, what the default-target
  fallback is, and how to verify that lifetime binding on a real host.
- When the service lane is graphical-session-bound, generated user units should
  keep that binding visible in the unit metadata itself rather than hiding it in
  surrounding docs or shell comments.
- The handoff should also emit one explicit startup-handoff policy plus a
  small probe/helper doc, so maintainers can review which startup owner is
  primary (`graphical-session.target` vs XDG autostart), which owner is only a
  fallback, and how to avoid installing both by default for the same VHK-owned
  lane.
- Install helpers should prefer one startup owner by default and keep the other
  as an explicit opt-in fallback instead of wiring duplicate target/autostart
  hooks for the same lane.



## `gen-host-rehearsal-pack` artifact contract

`vhk gen-host-rehearsal-pack <project_dir>` should extend the reviewed native/service lane into one operable host rehearsal path.

Minimum expectations:

- `vhk gen-host-rehearsal-pack` should preserve the chosen bundle kind (`project` vs `release-stage`) and emit artifacts under `build/publish/<bundle-name>/rehearsal/`.
- The generated handoff should include install, status, report, logs, uninstall, and integrated rehearsal smoke scripts, plus one machine-readable manifest and one refresh script.
- The status/report path should validate the installed desktop file opportunistically, name the desktop launch id explicitly, bridge the installed launcher’s own live status report into a host-rehearsal report, and inspect user-service state/logs when a first-party VHK-owned daemon lane exists.
- The rehearsal scripts should compose the reviewed native install and session-service handoffs instead of bypassing them or silently running from the mutable project checkout.
- The docs/plans should also surface current `host_truth` plus the shared
  `portal_route_contract` when available, because installed-lane rehearsal is
  exactly where configured-vs-installed-vs-live Linux reality must stay
  reviewable.
- The rehearsal docs/plans should also preserve one `target_fit_contract` so an
  installed-lane proof can say whether the current host matches, drifts from,
  or exceeds the declared flagship lane.
- The docs must stay explicit that desktop discoverability remains shell/desktop-shaped even when the desktop file validates and the launch id is correct.


## Window-state selectors

Window introspection is now split into two related contracts:

- **state shape**: runtime steps may surface fields like `visible`,
  `fullscreen`, `fullscreen_mode`, `floating`, `sticky`, `minimized`,
  `hidden`, `mapped`, and `pinned`
- **state selectors**: `I3WindowSelector` can now filter on those same fields
  during runtime matching (`WaitForWindow`, `WaitForWindowVanish`,
  `GetWindowList(selector=...)`, watcher-side `require_window`, etc.)

This is intentionally broader than exported WM config criteria. Runtime VHK can
normalize backend-shaped state into one selector surface, while generated i3/
sway/Hyprland config snippets must stay limited to the criteria each WM
actually supports.


## 2026Q1 addition: filesystem burst coalescing

`file_watchers:` and `WaitForFileEvent` now distinguish between:
- per-path readiness (`min_size`, `stable_ms`)
- event-stream quiescence (`quiet_ms`)

That split keeps the authoring surface honest for Linux-native producer flows
where several low-level file events may belong to one logical completion.

## 2026-03-16 addition: promotion gates and claim discipline

`vhk plan-project` should not stop at route ownership or even surface readiness. It
should also expose a small set of explicit **promotion gates** that answer:

- which Linux-native surfaces are safe to promote now
- which ones still need desktop/session review
- whether the repo's current docs/release story are getting ahead of verified
  capability evidence

Minimum expectations:

- planner JSON should include `promotion_gates` plus `promotion_gate_summary`
- at least one gate should cover specialist surfaces (text/remapper/service), one
  should cover helper-boundary honesty, and one should cover broader claim
  discipline
- gate states should stay explainable (`pass`, `review`, `fail`) and should be
  derived from staged promotion surfaces instead of a separate hidden ruleset
- `vhk lint-project` should surface non-pass gates so review pressure appears in
  the same workflow authors already use for recorder cleanup and export honesty
- promotion-pack artifacts should include these gates so release/review work is
  phrased as explicit Linux-native promises instead of scattered prose

## 2026-03-16 addition: deployment-truth surfaces

Deployment-facing packs should not regress from the richer host/readiness truth
model back to package-only prose.

Minimum expectations:

- `gen-setup-pack`, `gen-native-install-pack`, `gen-service-compose-pack`, and
  `gen-release-deploy-pack` should all preserve a compact observed host/deploy
  truth summary when live checks are requested
- that summary should keep helper/uinput readiness, blocking issues, and portal
  routing evidence visible in both human docs and machine-readable plans
- portal review should stay split into configured routing, installed backend
  manifests, and live D-Bus interfaces rather than collapsing back into one
  generic "portal support" checkbox
- deployment packs should keep this truth compact and operator-facing: enough to
  guide installation/review without forcing users back into raw doctor JSON

## 2026-03-16 addition: target-fit contracts

Observed host truth and declared flagship targets are both useful, but they
answer different questions. VHK should keep them separate and then compare them
explicitly.

Minimum expectations:

- release-lane, release-deploy, release-stage, native-install, host-rehearsal,
  and host-dossier surfaces should be able to carry one compact
  `target_fit_contract` derived from the flagship or chosen release lane
- that contract should compare at least desktop family, backend posture, deploy
  style, trigger route choice, and requirement-status drift between the target
  lane and the observed host
- fit states should stay small and explainable (for example `aligned`,
  `drifted`, `degraded`, or `outside-profile`) so docs can say why a host is a
  mismatch without pretending to have exact runtime proof for every desktop
- later-stage docs should keep current host truth and target-fit side by side:
  "what this machine can do now" versus "how this machine compares with the lane
  we intend to ship"



## 2026-03-16 addition: claim-evidence witnesses

VHK should treat support claims as two different questions, not one:

- what the planner recommends for a target lane
- whether the current machine is a believable witness for that target lane

Minimum expectations:

- claim and audit surfaces should be able to attach one compact current-host
  witness review to each target claim when live session/host checks are present
- that witness review should stay small and explainable (`aligned`, `degraded`,
  `drifted`, `neutral`, `unknown`) rather than pretending to be exhaustive proof
- desktop-family mismatch should be visible as drift, especially for claims like
  GNOME Wayland, KDE Wayland, Hyprland, wlroots/sway, or X11/i3
- portal-first claim lanes should treat portal-route truth as part of the witness
  story, not just current session capabilities
- strong claims marked as locally `verified` should fail review when the current
  host clearly drifts from the target lane being claimed

## 2026-03-17 addition: promotion proof witnesses

Promotion review should learn from the same claim-witness discipline instead of
waiting until maintainers edit `VHK_TARGET_CLAIMS.yaml`.

Minimum expectations:

- `gen-promotion-pack` should be able to ingest the current-host claim witness
  review when live session/host checks are available
- promotion output should keep one compact proof posture visible (`pass`,
  `review`, `fail`) instead of hiding wrong-host proof drift behind generic
  readiness prose
- promotion docs/fixups should name the host evidence boundary directly so a
  sway/Hyprland box is not casually treated as verified proof for GNOME/KDE
  portal-first claims
- promotion backlog/evidence should include at least one explicit task/evidence
  entry when current-host proof posture is not pass

## 2026-03-17 addition: explicit evidence lanes

VHK should let maintainers compare the current host against one explicitly
selected release lane instead of only the default flagship lane.

Minimum expectations:

- `plan-project`, session-fit, host-contract, claim, audit, promotion, and
  capability-audit surfaces should accept one stable `evidence_lane_profile` /
  `--evidence-lane <profile-id>` input
- the selected lane should remain visible in both machine-readable and human
  output so refresh scripts do not quietly fall back to the flagship default
- host-aware commands that probe live readiness must forward that proof context
  all the way into downstream pack/audit builders; collecting `host_snapshot` or
  `--evidence-lane` values and then dropping them is a contract bug
- evidence-lane review should stay separate from editable claims; it is current
  proof context, not project truth
- explicit lane review should name selection source (`explicit` vs
  `flagship-default`) so operators can tell when a report was deliberately pinned
- wrong-host proof should become reviewable earlier when maintainers are
  preparing support, promotion, or audit narratives for one specific desktop lane


## 2026-03-17 addition: narrow Wayland text fast paths

Wayland text entry should stay split into explicit lanes rather than collapsing
into one generic backend story.

Minimum expectations:

- planner/toolchain output should not treat `wtype` as the unconditional default
  answer for generic Wayland text injection when no host/session proof exists
- planner output should be able to surface one explicit `wtype`-class surface or
  pattern for projects that genuinely want a fast typed-text path
- that surface should stay clearly narrower than package/clipboard text lanes and
  narrower than helper/uinput daemon fallbacks
- docs and release-facing output should name virtual-keyboard/protocol support as
  part of the support contract instead of implying that every Wayland desktop has
  the same typed-text capabilities
- fast typed-text lanes should continue to point back to exported/package text
  surfaces as the broad fallback rather than trying to become the whole text
  automation story


## 2026-03-17 addition: daemonized helper lanes should stay explicit on Wayland

When a project crosses from reviewable text/package lanes into repeated helper-backed
playback, VHK should treat daemon lifecycle as part of the product surface.

Minimum expectations:

- planner output should be able to surface one explicit persistent helper lane for
  reviewed `dotoold`/`dotoolc` or `ydotoold`-class deployments
- that lane should stay separate from narrow `wtype`-class text fast paths and
  from broad clipboard/package exports
- the surfaced commands should include helper service generation and
  `gen-udev-uinput` so the operator sees lifecycle + permission work early
- ecosystem lessons should teach that daemon/socket ownership is part of Linux
  automation design, not just an install footnote

- `vhk plan-project` should also emit a `promotion_performance_plan`, so shipped surfaces do not just name ownership and proof lanes but also their latency/throughput envelope: hot path, batching strategy, related planner hotspots, and the Linux-native lane that should actually own performance.
- `vhk plan-project` should also emit a `promotion_dispatch_budget_plan`, so shipped surfaces state whether they are supposed to be edge-resident, service-resident, daemon-warm, session-resume, or launch-cold instead of pretending one startup model can satisfy text expansion, remapping, watcher services, helper flows, and launcher surfaces equally well.


## Session readiness guard contract (rev0305)

Service-compose output now includes an explicit **session readiness** contract.
That contract is separate from authority ownership, activation sync, target
binding, and startup ownership.

Required review points:
- which live session variables are mandatory (`XDG_RUNTIME_DIR` plus a reviewed display identity)
- whether `graphical-session.target` must be active for the lane
- which variables stay merely observational/optional
- which generated probe/`ExecCondition=` path enforces the contract for VHK-owned units


## Session readiness evidence contract (rev0306)

Host rehearsal and host dossier output should treat session readiness as
operator evidence, not just a service-pack implementation detail.

Required review points:
- capture the installed `verify_session_readiness.sh` verdict in rehearsal and dossier output
- preserve probe stdout/stderr so a skipped/not-ready lane is reviewable offline
- pair that probe with a compact `systemctl --user show` slice (`LoadState`, `ActiveState`, `SubState`, `Result`, `UnitFileState`, `FragmentPath`, `ExecMainCode`, `ExecMainStatus`)
- keep the evidence additive: missing systemd or missing probe scripts should surface as `unavailable`, not as proof that the lane is healthy
- make the JSON/Markdown handoffs say whether the lane looked `ready`, `not_ready`, `error`, or `unavailable`

## Installed-lane readiness status contract (rev0307)

The native-install and support surfaces should not flatten session readiness back
into generic launcher or user-unit state.

Required review points:
- the installed launcher status JSON/Markdown should preserve one compact readiness verdict (`ready`, `not_ready`, `unavailable`, `error`)
- that verdict should be derived from the installed `verify_session_readiness.sh` probe when present, not inferred only from `ActiveState=`
- nearby user-unit state should include at least `Result` and `ConditionResult` so clean `ExecCondition=` skips stay distinguishable from service faults
- `gen-support-pack` should point maintainers at the installed status/home bridge before escalating to a heavier rehearsal or dossier capture
- missing probes or missing installed launchers should remain reviewable as `unavailable`, not be silently treated as success


## Installed-lane runtime health contract (rev0308)

The installed launcher/support surfaces should also preserve one compact
**runtime health** verdict for the owned lane instead of flattening everything
back into readiness or generic unit state.

Required review points:
- installed status JSON/Markdown should preserve one runtime-health verdict (`healthy`, `skipped_not_ready`, `degraded_restart_churn`, `degraded_failed`, `degraded_probe_error`, `degraded_unit_missing`, `stopped`, `no_owned_service`, `unavailable`)
- runtime health should be derived from the combination of readiness verdict, expected unit ownership, and nearby `systemctl --user show` properties such as `ActiveState`, `SubState`, `Result`, and `NRestarts`
- socket-owned lanes should not be mistaken for broken services just because the backing `.service` is idle while the `.socket` stays active/listening
- start-limit or obvious restart churn should be surfaced explicitly instead of forcing operators to infer it from raw unit state text
- `gen-support-pack` should ask maintainers to capture both readiness and runtime-health verdicts before escalating to rehearsal/dossier collection

## Installed-lane startup handoff contract (rev0309)

The installed launcher/support surfaces should also preserve one compact
**startup-handoff** verdict for the reviewed lane instead of flattening startup
ownership into generic unit state or generic autostart presence.

Required review points:
- installed status JSON/Markdown should preserve one startup-handoff verdict (`primary_user_unit_owner`, `fallback_autostart_owner`, `duplicate_start_risk`, `autostart_hidden_no_owner`, `autostart_tryexec_missing`, `masked_no_owner`, `no_startup_owner`, `manual_or_external_owner`, `unavailable`)
- that verdict should be derived from both user-unit enablement state and the effective XDG autostart desktop state, not from either one in isolation
- autostart review should treat `Hidden=true` and missing `TryExec` targets as distinct Linux-native reasons the fallback owner is not actually active
- support output should ask maintainers to capture startup-handoff truth alongside readiness and runtime-health before escalating to rehearsal/dossier collection



## Installed-lane startup handoff drift contract (rev0310)

The installed launcher/support/rehearsal/dossier surfaces should also preserve
one compact **startup-handoff drift** verdict so operators can tell whether
startup ownership is stable, recently changed, or repeatedly degraded instead of
seeing only one live startup snapshot.

Required review points:
- installed status JSON/Markdown should preserve one startup-handoff drift verdict (`first_snapshot`, `stable`, `changed_recently`, `recovered_to_primary`, `drifted_from_primary`, `chronic_duplicate_risk`, `chronic_missing_owner`, `flapping_owners`, `unavailable`)
- that drift verdict should be derived from a short local history of startup-handoff snapshots, not inferred only from the current host state
- local history should stay bounded and reviewable instead of growing without limit
- support, rehearsal, and dossier output should surface both the current startup-handoff verdict and its drift summary before escalating to raw logs


## Installed-lane runtime health drift contract (rev0311)

The installed launcher/support/rehearsal/dossier surfaces should also preserve
one compact **runtime-health drift** verdict so operators can tell whether
runtime state is stable, recently changed, repeatedly degraded, or recovered
instead of seeing only one live health snapshot.

Required review points:
- installed status JSON/Markdown should preserve one runtime-health drift verdict (`first_snapshot`, `stable`, `changed_recently`, `recovered_healthy`, `drifted_from_healthy`, `changed_degraded_mode`, `chronic_restart_churn`, `chronic_failed`, `chronic_inactive_or_missing`, `flapping_health`, `unavailable`)
- that drift verdict should be derived from a short local history of runtime-health snapshots, not inferred only from the current host state
- local history should stay bounded and reviewable instead of growing without limit
- support, rehearsal, and dossier output should surface both the current runtime-health verdict and its drift summary before escalating to raw logs
- runtime-health drift should remain distinct from startup-handoff drift because Linux hosts can keep one startup owner while the owned service still oscillates between healthy, failed, skipped, and churned states


## Installed-lane incident signature contract (rev0312)

The installed launcher/support/rehearsal/dossier surfaces should also preserve
one compact **incident-signature** verdict so operators can tell whether the
reviewed lane was cleanly skipped, condition-skipped, start-limit churned,
actually failed, or simply had no recent incident signal.

Required review points:
- installed status JSON/Markdown should preserve one incident-signature verdict (`healthy_no_recent_incident`, `stopped_no_recent_incident`, `clean_session_skip`, `condition_skip`, `start_limit_churn`, `service_failure`, `missing_unit`, `probe_error`, `no_owned_service`, `journal_unavailable`, `unavailable`)
- incident classification should combine installed readiness/runtime-health verdicts with live unit state instead of guessing from one field alone
- when `journalctl --user` is available, installed status should preserve a short recent journal sample rather than only reporting abstract verdict text
- support, rehearsal, and dossier output should surface the incident-signature verdict before escalating to raw logs so clean skips and start-limit churn stop looking like the same problem

## Installed-lane incident-signature drift contract (rev0313)

The installed launcher/support/rehearsal/dossier surfaces should also preserve
one compact **incident-signature drift** verdict so operators can tell whether
recent incidents are first-seen, stable, chronic, flapping, or recovered to a
quiet lane.

Required review points:
- installed status JSON/Markdown should preserve one incident-signature drift verdict (`first_snapshot`, `stable`, `changed_recently`, `recovered_to_quiet`, `drifted_from_quiet`, `changed_skip_mode`, `changed_incident_mode`, `chronic_start_limit`, `chronic_service_failure`, `chronic_missing_unit`, `chronic_probe_error`, `flapping_incidents`, `unavailable`)
- that drift verdict should be derived from a short local history of incident-signature snapshots, not inferred only from the most recent journal excerpt
- local history should stay bounded and reviewable instead of growing without limit
- support, rehearsal, and dossier output should surface both the current incident-signature verdict and its drift summary before escalating to raw logs
- incident-signature drift should remain distinct from runtime-health drift because the same runtime-health class can still hide different incident stories (for example a clean skip versus a hard condition skip)



### 2.4 Recorder context capture

- Recorder-assisted authoring should make app/window scope cheaper to capture than to ignore.
- `vhk record-x11` may sample the active window while recording and emit a reviewable selector payload with at least `stable` and `exact` suggestions.
- When recording directly into a project, the recorder may apply only the `stable` selector to the macro's top-level `when:` field; title-sensitive or regex-heavy alternatives should stay reviewable evidence instead of being silently promoted.
- Recorder-assisted authoring may also emit `CoordMode(target=mouse, mode=window|client)` plus rewritten relative pointer coordinates when active-window geometry was captured successfully; `client` mode may fall back to the outer rect when no separate client geometry exists.
- Recorder-assisted authoring may also segment one recording into window-scoped slices, inject `WaitForWindow` guards at captured window boundaries, and split long `Delay` spans so those guards land near the actual transition instead of only between later actions. That guard lane should default to the recorded *active* window truth (`focused: true`) rather than only proving that some matching window exists in the background, while still allowing an explicit wider `present` scope for authors who truly want that behavior.
- When multiple recorded segments would otherwise share the same broad stable selector, recorder-side segment guards may promote the per-segment exact selector for disambiguation instead of pretending a class-only selector is sufficient.
- Relative recorder output should compose with that same segment lane, so `CoordMode(target=mouse, mode=window|client)` recordings can translate pointer coordinates per recorded window segment instead of assuming one anchor for the entire macro.
- This lane should stay conservative and Linux-native: app/class/instance/workspace evidence is useful authoring metadata, but it is not a substitute for semantic UI automation, accessibility trees, or route-specific adapters.
