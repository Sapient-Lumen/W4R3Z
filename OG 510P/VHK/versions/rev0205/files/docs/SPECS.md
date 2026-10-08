# VHK specs (engine + future studio)

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
- IPC event bus:
  - a small local trigger surface (UNIX socket) for cross-tool integration
- Tooling:
  - project init/validate/lint/optimize/retime/scaffold
  - “inspect” style CLI helpers (window-spy, pick-window, preview-needle, doctor)
  - `vhk doctor` is expected to expose a capability-oriented diagnostics surface, especially on Wayland where capture, injection, hotkeys, and portals are separate concerns
  - `vhk validate` should be able to reuse that capability model to warn when a project is likely to outrun the current session
  - `vhk lint-project` should be able to present the same capability language alongside macro-hygiene advice, so authors review portability and brittleness in one pass
- `vhk plan-project` should also be able to turn those surfaces into a sequenced delivery plan (`implementation_waves`), so teams can move from target/toolchain advice to a staged Linux-native implementation order
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
- Inspectors that produce robust selectors (window pickers, accessibility tree, visual ROI).
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
- The report layer should expose **heuristic advice** for common Linux automation bottlenecks, including excessive fixed delays, vision-heavy polling, and likely backend/capability mismatches.
- The optimization guidance should point users toward existing VHK flows when possible (`optimize`, `doctor`, `validate`, named regions, needle metadata) instead of inventing a separate tuning model.
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
2. **AT-SPI selectors** (read-only inspector first; then action steps).
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
- The handoff should also materialize one environment.d export file and one XDG
  autostart bridge entry so PATH/session startup assumptions become reviewable
  filesystem artifacts.
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



## `gen-host-rehearsal-pack` artifact contract

`vhk gen-host-rehearsal-pack <project_dir>` should extend the reviewed native/service lane into one operable host rehearsal path.

Minimum expectations:

- `vhk gen-host-rehearsal-pack` should preserve the chosen bundle kind (`project` vs `release-stage`) and emit artifacts under `build/publish/<bundle-name>/rehearsal/`.
- The generated handoff should include install, status, report, logs, uninstall, and integrated rehearsal smoke scripts, plus one machine-readable manifest and one refresh script.
- The status/report path should validate the installed desktop file opportunistically, name the desktop launch id explicitly, bridge the installed launcher’s own live status report into a host-rehearsal report, and inspect user-service state/logs when a first-party VHK-owned daemon lane exists.
- The rehearsal scripts should compose the reviewed native install and session-service handoffs instead of bypassing them or silently running from the mutable project checkout.
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
