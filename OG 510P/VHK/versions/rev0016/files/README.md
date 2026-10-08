# VHK (i3/sway) — engine + CLI scaffold

This repo is the **engine** and **headless runner** foundation for a future
"VisualHotKey + Pulover’s Macro Creator"-class studio on Linux (i3 on X11, sway on Wayland).

The long-form requirements/inventory live at:
- `docs/requirements.md`

## What exists today (v0.16)

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
  - `HttpRequest`, `DownloadFile`, `WaitForNewFile`
  - `ShowMessage`, `AskYesNo`, `InputBox`, `ChooseFromList`
  - `StartProcess`, `WaitForProcessExit`, `KillProcess`
- A **runner** that executes a step list with variables + interpolation + safe-ish
  expression evaluation.
- A minimal **vision** backend:
  - template matching via OpenCV (`ImageSearchFile`, `WaitForImageFile`)
  - openQA-style needle metadata support (`foo.png` + `foo.json`)
    - match areas + per-area `match` percent
    - exclude areas (masked matching)
    - click points (loaded for tooling)
  - pixel search in image files (`PixelSearchFile`, `WaitForPixelFile`)
  - OCR from image files via Tesseract (`OcrReadTextFile`)
  - Screen-capture convenience steps:
    - `ImageSearch`, `WaitForImage`
    - `OcrReadText`, `WaitForText`, `AssertText`
    - `ClickNeedle` (uses openQA click points when available)
    - `VisualAssert`, `VisualVerify`, `WaitForRegionChange`
  - `ReadFile`, `WriteFile`, `AppendFile`, `ListDirectory`, `WaitForFile`
  - `WaitForClipboardChange`
  - `MouseDrag`, `MouseWheel`
- A tiny **i3/sway IPC** client (pure Python) + runner steps.
  - socket discovery checks `SWAYSOCK`/`I3SOCK`, `sway --get-socketpath`, `i3 --get-socketpath`, and the X11 `I3_SOCKET_PATH` property.
- Cursor/reliability helpers inspired by xbanish / unclutter + xdotool caveats:
  - project setting `settings.hide_cursor_during_run: true`
  - explicit `CursorHide`, `CursorShow`, and `ResetModifiers` steps
  - `vhk doctor` now reports cursor helpers and deeper screenshot fallback helpers
- Playback profiles + more robust text injection:
  - `settings.runner_profile: normal|turbo`
  - turbo mode reduces incidental playback delays and can prefer clipboard-paste for larger printable text
  - `TypeText` now supports `backend=auto|native|clipboard|xvkbd`, optional clipboard preservation, and terminal-friendly paste shortcuts like `ctrl+shift+v`
- Thin wrappers over common desktop CLI tools (best-effort):
  - screenshots: X11 (`maim`, `scrot`, ImageMagick `import`, or `xwd`+ImageMagick), Wayland (`grim`)
  - region selection: X11 (`slop`), Wayland (`slurp`)
  - input: X11 (`xdotool`, `xvkbd`), Wayland keyboard (`wtype`), Wayland pointer (`ydotool`)
  - clipboard: X11 (`xclip`/`xsel`), Wayland (`wl-copy`/`wl-paste`)
  - notifications (`notify-send`/`dunstify`)
  - prompts/dialogs (`zenity`, `yad`, `kdialog`, with console fallback)
  - optional event helpers: `clipnotify` (clipboard on X11), `inotifywait` (filesystem waits)
- Project-level **clipboard watchers** inspired by CopyQ/clipmenu-style clipboard rules:
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
  - `vhk gen-wm-config <project_dir> --wm auto|i3|sway`
  - `vhk bundle <project_dir> <out.zip>`
  - `vhk list-macros <project_dir>`
  - `vhk list-watchers <project_dir>`
  - `vhk watch-clipboard <project_dir> <watcher_name>`
  - `vhk select-region` (slop on X11, slurp on Wayland)
  - `vhk capture-needle <project_dir> <name>`
  - `vhk capture-baseline <project_dir> <name>`
  - `vhk needle-info <needle.png>`
  - `vhk doctor` / `vhk doctor --json`
    - now reports optional event helpers like `clipnotify` and `inotifywait`
    - now reports dialog helpers like `zenity`, `yad`, `kdialog`, and `dialog`
  - `vhk render <project_dir> <macro>` (script view)
  - `vhk pick-window` (prints i3 criteria for clicked window)
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
vhk capture-needle examples/hello_project ok_button --out-dir assets/needles

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

New in this revision: `docs/CURSOR_AND_CAPTURE.md`.

## License

MIT.
