# VHK (i3/sway) — engine + CLI scaffold

This repo is the **engine** and **headless runner** foundation for a future
"VisualHotKey + Pulover’s Macro Creator"-class studio on Linux (i3 on X11, sway on Wayland).

The long-form requirements/inventory live at:
- `docs/requirements.md`

The explicit engine + studio specs live at:
- `docs/SPECS.md`

## What exists today (v0.22)

- A small **project format** (folder-based) with macros in YAML.
- Structured control flow / error handling:
  - `While(condition, steps, max_iterations?)`
  - `Try(steps, catch_steps?, finally_steps?, catch_pattern?)`
  - `Break`, `Continue`, `Return`
  - `SetVar` now accepts plain expressions like `i + 1` in addition to literals/interpolation
- Data-oriented workflow helpers:
  - `ReadCsv`, `WriteCsv`, `ReadJson`, `WriteJson`
  - `ForEach(items_expr, item_var, steps)`
  - `RegexReplace`, `TrimText`, `SplitText`, `JoinText`
- Desktop/browser/network glue:
  - `OpenUrl`, `ComposeEmail`, `PasteClipboard`
  - `HttpRequest`, `DownloadFile`, `WaitForNewFile`, `WaitForDownload`
  - `ShowMessage`, `AskYesNo`, `InputBox`, `ChooseFromList`
  - `StartProcess`, `WaitForProcessExit`, `KillProcess`
- A **runner** that executes a step list with variables + interpolation + safe-ish
  expression evaluation.
- A minimal **vision** backend:
  - template matching via OpenCV (`ImageSearchFile`, `WaitForImageFile`, `ImageSearchAllFile`)
  - openQA-style needle metadata support (`foo.png` + `foo.json`)
    - match areas + per-area `match` percent
    - exclude areas (masked matching)
    - click points (loaded for tooling)
    - OCR areas (used by `OcrNeedleText` / `WaitForNeedleText`)
  - pixel search (`PixelSearch`, `WaitForPixel`) and image-file equivalents (`PixelSearchFile`, `WaitForPixelFile`)
    - optional `step` stride for faster scanning; waits cycle sampling phases when `step>1`
  - pixel FindAll + click-all (`PixelSearchAll`, `WaitForPixelAll`, `ClickPixelAll`) and file equivalent (`PixelSearchAllFile`)
    - optional `group: connected` to collapse contiguous pixels into blobs
  - pixel sampling (`PixelGetColor`) and image-file equivalent (`PixelGetColorFile`)
  - OCR from image files via Tesseract (`OcrReadTextFile`)
    - plus OCR bounding boxes: `OcrFindTextFile` (word/line bbox)
  - Screen-capture convenience steps:
    - `ImageSearch`, `WaitForImage`, `ImageSearchAll`, `WaitForImageAll`, `ClickImageAll`
    - `OcrReadText`, `WaitForText`, `AssertText`
    - `OcrFindText`, `WaitForTextBox`, `ClickText` (find/click by OCR bbox)
    - `OcrFindTextAll` + `ClickTextAll` (multi-match OCR bbox search + click for lists/grids)
    - OCR fuzzy matching: `match: fuzzy` with `fuzzy_threshold`/`fuzzy_mode`
    - `ClickNeedle` (uses openQA click points when available)
    - `VisualAssert`, `VisualVerify`, `WaitForRegionChange`, `WaitForRegionStable`
  - AHK-style coordinate mode translation:
    - `CoordMode(target=pixel|mouse, mode=screen|window|client)`
    - affects how regions and mouse coordinates are interpreted (outputs remain screen-absolute)
  - `ReadFile`, `WriteFile`, `AppendFile`, `ListDirectory`, `WaitForFile`
  - `WaitForClipboardChange`
  - `MouseDrag`, `MouseWheel`
- A tiny **i3/sway IPC** client (pure Python) + runner steps.
  - session auto-detection now treats `WAYLAND_DISPLAY` as authoritative, which helps avoid accidentally picking X11-only helpers inside XWayland-heavy sessions
  - socket discovery checks `SWAYSOCK`/`I3SOCK`, `sway --get-socketpath`, `i3 --get-socketpath`, and the X11 `I3_SOCKET_PATH` property.
- Cursor/reliability helpers inspired by xbanish / unclutter + xdotool caveats:
  - project setting `settings.hide_cursor_during_run: true`
  - explicit `CursorHide`, `CursorShow`, and `ResetModifiers` steps
  - `GetCursorPos` step (best-effort; uses compositor/tool helpers on Wayland)
  - `vhk doctor` now reports cursor helpers, deeper screenshot fallbacks, AT-SPI bus health, X11/XKB diagnostics, i3 IPC reachability, and X11 recovery commands
- Playback profiles + more robust text injection:
  - `settings.runner_profile: normal|turbo`
  - turbo mode reduces incidental playback delays and can prefer clipboard-paste for larger printable text
  - `TypeText` now supports `backend=auto|native|clipboard|xvkbd`, optional clipboard preservation, and terminal-friendly paste shortcuts like `ctrl+shift+v`
- Thin wrappers over common desktop CLI tools (best-effort):
  - screenshots: X11 (`maim`, `scrot`, ImageMagick `import`, or `xwd`+ImageMagick), Wayland (`grim`)
    - Wayland fallback: `spectacle` (KDE) or `gnome-screenshot` (GNOME) for full-screen capture when `grim` isn't available
  - region selection: X11 (`slop`), Wayland (`slurp`)
  - input: X11 (`xdotool`, `xvkbd`), Wayland keyboard (`wtype` / `dotool` / `ydotool`), Wayland pointer (`ydotool` / `dotool`)
  - clipboard: X11 (`xclip`/`xsel`), Wayland (`wl-copy`/`wl-paste`)
  - notifications (`notify-send`/`dunstify`)
  - prompts/dialogs (`zenity`, `yad`, `kdialog`, with console fallback)
  - optional event helpers: `clipnotify` (clipboard on X11), `inotifywait` (filesystem waits)
  - KDE Wayland helper: `kdotool` (improves `vhk window-spy` + `vhk cursorpos` on KWin)
- Project-level **clipboard watchers** inspired by CopyQ/clipmenu-style clipboard rules:
- Project-level **hotstrings** (text expansion triggers) exportable to Espanso
  - define `hotstrings:` in `project.yaml`
  - generate a match file with `vhk gen-espanso`
  - use `vhk run --print-return` to output expansions on stdout

  - regex-filter clipboard changes and trigger macros
  - metadata-only watcher JSONL logs for explainability/debugging
  - `list-watchers` + `watch-clipboard` CLI commands
- A JSONL **timeline event log** for runs + a simple panic switch.
- Cross-step **retry / continue-on-error** controls (Robot-Framework-ish).
- Better **failure diagnostics**:
  - `wait_attempt` events during polling waits
  - reuses the *last actual capture* for screenshot-on-error
  - writes an `error_<macro>_<step>.json` context file
  - writes visual diff images for failed visual compares/timeouts
- A CLI:
  - `vhk run <project_dir> <macro_name>` (supports `--step` and `--dry-run`)
  - `vhk gen-i3-config <project_dir>`
  - `vhk gen-hyprland-config <project_dir>`
  - `vhk gen-wm-config <project_dir> --wm auto|i3|sway|hyprland`
    - optional: `--mode-enter Mod4+R` to generate an i3/sway **mode** or Hyprland **submap** (leader-key keymap)
  - `vhk gen-kanata-config <project_dir>` (Kanata hotkeys export)
  - `vhk gen-keyd-config <project_dir>` (keyd hotkeys export)
  - `vhk gen-kmonad-config <project_dir>` (KMonad macro-layer export)
  - `vhk gen-sxhkd-config <project_dir>` (sxhkd hotkeys export; X11)
  - `vhk gen-udev-uinput` (starter udev rules for /dev/uinput; see docs/UINPUT.md)
  - `vhk gen-ydotoold-service` (systemd user unit for ydotoold; see docs/INPUT_BACKENDS.md)
  - `vhk gen-dotoold-service` (systemd user unit for dotoold; see docs/INPUT_BACKENDS.md)
  - `vhk gen-espanso <project_dir>` (hotstrings export)
  - `vhk bundle <project_dir> <out.zip>`
  - `vhk list-macros <project_dir>`
  - `vhk list-watchers <project_dir>`
  - `vhk watch-clipboard <project_dir> <watcher_name>`
  - `vhk watch-window <project_dir> <watcher_name>`
  - `vhk select-region` (slop on X11, slurp on Wayland)
  - `vhk portal-screenshot` (XDG Desktop Portal screenshot; best-effort, usually interactive)
  - `vhk portal-pick-color` (XDG Desktop Portal color picker; best-effort)
  - `vhk pick-color` (samples under cursor or at --x/--y; Wayland falls back to portal picker)
  - `vhk capture-needle <project_dir> <name>`
  - `vhk capture-baseline <project_dir> <name>`
  - `vhk needle-info <needle.png>`
  - `vhk preview-needle <needle.png>` (debug: best match + optional annotated overlay; see docs/PREVIEW_NEEDLE.md)
  - `vhk doctor` / `vhk doctor --json`
    - reports optional event helpers like `clipnotify` and `inotifywait`
    - reports dialog helpers like `zenity`, `yad`, `kdialog`, and `dialog`
    - now probes AT-SPI bus health via `busctl` when available, surfaces `NO_AT_BRIDGE` / `GTK_MODULES`, checks X11 `XTEST`/`RECORD` availability via `xdpyinfo`, reports active XKB layout/options via `setxkbmap`, verifies i3/sway IPC reachability, runs a real screenshot self-test, discovers installed Tesseract language packs, estimates monitor DPI/scale from `xrandr`, and shows an emergency X11 `x11vnc -clear_keys` recovery command when possible
  - `vhk report <run.jsonl>` (summarize a run log; use `--project . --latest` to pick newest)
  - `vhk history <project_dir>` (recent run table; filter with `--status ok|fail`; export with `--csv`)
  - `vhk trace <run.jsonl>` (export a run log to Chrome/Perfetto trace JSON; see docs/TRACE_EXPORT.md)
  - `vhk render <project_dir> <macro>` (script view)
  - `vhk init <project_dir>` (create a new project skeleton: `project.yaml` + `macros/` + `assets/`)
  - `vhk new-macro <project_dir> <name>` (add a new macro file under `macros/`, optionally registering it)
  - `vhk schema --kind project|macro|...` (print JSON schema for editor validation/autocomplete)
  - `vhk schemas <project_dir>` (write `schemas/*.schema.json` + optional `.vscode/settings.json`)
  - `vhk validate <project_dir>` (static project checker: references + expressions + required visual assets)
  - `vhk lint <macro.yaml>` (advisor: flags hard sleeps + coordinate clicks; suggests waits/selectors)
  - `vhk lint-project <project_dir>` (bulk lint every macro under macros/)
  - `vhk scaffold <macro.yaml>` (non-breaking TODO scaffolds: inserts disabled WaitForImage/ClickNeedle stubs + comments)
    - review mode: `--check`, `--diff`
  - `vhk scaffold-project <project_dir>` (bulk scaffold every macro under macros/)
    - review mode: `--check`, `--diff`
  - `vhk pick-window` (prints i3 criteria for clicked window)
    - now captures `WM_WINDOW_ROLE`, suggests both a stable class/instance(/role) selector and an exact selector with title, and previews how many current i3 windows match each suggestion when IPC is reachable
  - `vhk window-spy` (active-window inspector for i3/sway/Hyprland/X11; Wayland-friendly)
  - `vhk record-selectors` (records focus/title changes and suggests a `when:` selector)
  - `vhk record-x11` (baseline lexical recorder on X11 via `xinput test-xi2 --root`; can write into a project with `--project`)
  - `vhk optimize <macro.yaml>` (post-process recordings: merge delays, squash mouse moves, compress key chords; optional TypeText collapsing)
    - review mode: `--check` (CI-friendly), `--diff` (unified diff)
  - `vhk optimize-project <project_dir>` (bulk optimize every macro under macros/)
    - review mode: `--check`, `--diff`
  - `vhk retime <macro.yaml>` (scale Delay/RandomWait and other delay-like knobs to speed up / slow down recordings)
  - `vhk retime-project <project_dir>` (bulk retime every macro under macros/)
  - `vhk cursorpos` (best-effort global cursor position; Wayland-friendly helpers)
  - `vhk cursor-step` (prints a macro step snippet at the current cursor position)
  - `vhk build-rule`
    - generates i3 `for_window` / `assign` snippets, devilspie2 Lua fallbacks, and wmctrl apply-once commands from selector fields or a clicked window
    - recommends `assign` for pure workspace placement, because i3 treats mapping-time assignment and runtime `for_window` rules differently
  - `vhk gen-systemd <project_dir> <macro>` (service+timer generator)
  - `vhk panic` / `vhk unpanic`

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

# Run the example project
vhk run examples/hello_project hello

# Generate i3 keybindings from project.yaml
vhk gen-i3-config examples/hello_project

# Capture a needle (interactive selection)
# Tip: use --delay-ms if you want time to switch focus / hover before selecting.
vhk capture-needle examples/hello_project ok_button --out-dir assets/needles --delay-ms 3000

# Create a shareable bundle
vhk bundle examples/hello_project /tmp/hello_project.zip
```

## Project layout

```
project/
  project.yaml
  macros/
    <macro>.yaml
  assets/
    ... (images / metadata)
  data/
  logs/
```

See `docs/PROJECT_FORMAT.md`, `docs/CONTROL_FLOW.md`, and `docs/TEXT_INPUT_AND_TURBO.md`.

Named regions of interest (ROI): `docs/NAMED_REGIONS.md`.

Expression language reference: `docs/EXPRESSIONS.md`.

Platform caveats / known issues: `docs/KNOWN_ISSUES.md`.

Performance notes (polling waits, caching): `docs/PERFORMANCE.md`.

New in this revision: `vhk build-rule` turns inspector-style selectors into ready-to-paste i3/devilspie2/wmctrl rules, including an `assign` recommendation for pure workspace placement and an optional apply-once path for the current session.

## License

MIT.
