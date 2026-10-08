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
  - clipboard, notifications, dialogs, processes, filesystem waits
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

### 2.2 Control flow

Minimum supported structured control flow:

- `If(condition, then_steps, else_steps)`
- `While(condition, steps, max_iterations)`
- `Try(steps, catch_steps, finally_steps, catch_pattern)`
- `Break`, `Continue`, `Return`

Semantics:

- `While` is **top-tested** and has a hard safety cap.
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

Rationale:

- Enables later “verify bundle” tooling.
- Enables integrity-aware caching for image assets.

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

1. **Deterministic bundles** (stable ordering + optional SOURCE_DATE_EPOCH).
2. **Portal/libei prototype path** (small helper binary + feature flag).
3. **AT-SPI selectors** (read-only inspector first; then action steps).
4. **Recorder upgrades** (mouse move thinning + richer key state capture).
5. **Studio contract definition** (event log as debugger substrate).
