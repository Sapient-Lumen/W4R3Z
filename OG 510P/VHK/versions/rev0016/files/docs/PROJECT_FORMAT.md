# Project format

A VHK project is a folder that can be zipped and shared.

## `project.yaml`

Minimal form:

```yaml
name: my_project
macros:
  my_macro: macros/my_macro.yaml
```

If `macros:` is omitted, the loader will read all `macros/*.yaml`.

### Settings

Settings are optional and influence the headless runner:

```yaml
settings:
  # Desktop stack selection (auto/x11/wayland)
  desktop_backend: auto

  # Playback profile. "turbo" reduces incidental playback delays and can
  # prefer clipboard-paste text injection for larger printable text.
  runner_profile: normal
  turbo_delay_scale: 0.25
  turbo_type_clipboard_threshold: 80

  log_dir: logs
  event_log: true
  screenshot_on_error: false
  trace_wait_attempts: true
  panic_file: /tmp/vhk_panic
  dry_run: false
```

### Hotkey bindings (for i3 config generation)

Bindings are optional and used by `vhk gen-i3-config` (or `vhk gen-wm-config`):

```yaml
bindings:
  - keys: "$mod+Shift+h"
    macro: my_macro
    description: "Run my macro"
    vars:
      foo: bar
    # Optional: context-sensitive binding (only when focused window matches).
    # i3 criteria are regular expressions (PCRE), so anchor with ^...$ for exact.
    when:
      class: "Firefox"
      title: "^Mozilla Firefox$"
```

Notes:
- i3: VHK generates `bindsym --release … exec --no-startup-id …` lines.
- sway: VHK generates `bindsym --release … exec …` lines (no `--no-startup-id`).
- `--release` is recommended in the i3 docs for commands that should run after
  the keyboard grab is released.
- If `when:` is present, VHK emits i3 criteria (`[class=... title=...]`) so the
  binding is context-sensitive.

### Clipboard watchers

Projects can also define clipboard-triggered macro rules inspired by CopyQ/clipmenu
style “clipboard commands”:

```yaml
clipboard_watchers:
  - name: copied_url
    macro: open_copied_url
    selection: clipboard
    pattern: "https?://(\S+)"
    flags: [IGNORECASE]
    dedupe: true
    debounce_ms: 150
    continue_on_macro_error: true
    vars:
      source: clipboard_rule
```

Fields:
- `name`: watcher identifier used by `vhk watch-clipboard <project> <name>`
- `macro`: macro to run when the clipboard change matches
- `selection`: `clipboard` or `primary`
- `pattern`: optional regex filter; when omitted, every clipboard change triggers
- `flags`: optional regex flags (`IGNORECASE`, `MULTILINE`, `DOTALL`)
- `dedupe`: ignore repeated identical clipboard text
- `debounce_ms`: sleep after each handled event to avoid noisy loops
- `continue_on_macro_error`: keep the watcher alive after a macro failure
- `vars`: extra initial vars passed into the macro

Watcher-triggered macros receive these initial vars:
- `clipboard_text`
- `clipboard_selection`
- `watcher_name`
- `clipboard_match` / `clipboard_groups` / `clipboard_match_groups` / `clipboard_groupdict` when `pattern` matches
- any custom entries from `vars`

Each watcher also writes a metadata-oriented JSONL log under `logs/clipboard_watcher_<name>.jsonl`
so you can inspect what fired, what was skipped, and which macro run/event log was involved.

## Macro files

Example:

```yaml
name: hello
steps:
  - type: Log
    message: "Hello ${name}"
  - type: SetVar
    name: answer
    value: 42
  - type: If
    condition: "answer == 42"
    then_steps:
      - type: Log
        message: "It worked."
```

### Common step fields

All steps support these PMC-style fields:

Control-flow note:
- `While` is a **top-tested** loop and defaults to `max_iterations: 1000` so a bad condition does not hang forever.
- `Break` and `Continue` are only meaningful inside `While` / `ForEach` bodies.
- `Return` exits the current macro early. When used inside `CallMacro`, the child macro ends immediately and any already-set vars remain available for the `returns:` mapping.
- `Try` can optionally filter catch behavior with `catch_pattern` (regex against the error text) and always runs `finally_steps` when provided.

```yaml
- type: Log
  enabled: true
  comment: "optional note"
  delay_ms: 0
  repeat: 1
  retry_count: 0
  retry_delay_ms: 0
  retry_backoff: 1.0
  continue_on_error: false
  message: "hi"
```

## Step catalog (current)

- Control flow:
  - `Delay(ms)`
  - `RandomWait(min_ms,max_ms)`
  - `If(condition, then_steps, else_steps)`
  - `While(condition, steps, max_iterations?, out_iterations?)`
  - `Try(steps, catch_steps?, finally_steps?, catch_pattern?, out_error?)`
  - `Break()` / `Continue()` / `Return(value_expr?, out_var?)`
  - `CallMacro(macro, args, returns)`
  - `ForEach(items_expr, item_var, index_var?, key_var?, steps)`
- Variables:
  - `SetVar(name,value)` (literals, `${var}` interpolation, or plain expressions like `i + 1`)
  - `RegexReplace(text, pattern, replacement, flags?, count?, out_var)`
  - `TrimText(text, chars?, mode=both|left|right, out_var)`
  - `SplitText(text, sep?, maxsplit?, out_var)`
  - `JoinText(items_expr, sep?, out_var)`
- Shell:
  - `RunShell(command, check)`
- Vision (file-based MVP):
  - `ImageSearchFile(haystack_path, needle_path, region?, threshold?, out_*)`
  - `WaitForImageFile(..., timeout_ms, poll_ms, max_poll_ms, jitter_ms)`
  - `PixelSearchFile(image_path, color, region?, tolerance?, out_*)`
  - `WaitForPixelFile(..., timeout_ms, poll_ms, max_poll_ms, jitter_ms)`
  - `OcrReadTextFile(image_path, out_var, lang)`
  - `CaptureScreenshot(path?, region?, out_var)`
- Vision (screen-capture):
  - `ImageSearch(needle_path, region?, threshold?, screenshot_path?, out_*)`
  - `WaitForImage(..., timeout_ms, poll_ms, max_poll_ms, jitter_ms, max_attempts?)`
  - `OcrReadText(region?, screenshot_path?, out_var, lang)`
  - `WaitForText(pattern, match=contains|regex, case_sensitive?, timeout_ms, ...)`
  - `AssertText(pattern, match=contains|regex, case_sensitive?)`
  - `ClickNeedle(needle_path, region?, threshold?, click_point_id?, offset_x/y?, button?, clearmodifiers?)`
  - `VisualAssert(baseline_path, region?, color_tolerance?, max_changed_pixels?, max_change_ratio?)`
  - `VisualVerify(...)`
  - `WaitForRegionChange(region?, baseline_path?, color_tolerance?, min_changed_pixels?, min_change_ratio?, timeout_ms, ...)`
- Input:
  - `Key(keys, clearmodifiers?)`
  - `KeyDown(key, clearmodifiers?)`
  - `KeyUp(key, clearmodifiers?)`
  - `ResetModifiers()`
  - `TypeText(text, delay_ms_per_char?, clearmodifiers?, backend=auto|native|clipboard|xvkbd, selection?, preserve_clipboard?, paste_shortcut?)`
  - `MouseMove(x,y)` or `MouseMove(relative: true, dx, dy)`
  - `MouseClick(button, down?, up?, clearmodifiers?)`
  - `MouseDrag(x1,y1,x2,y2, button?, clearmodifiers?)`
  - `MouseWheel(clicks, axis=vertical|horizontal)`
  - `CursorHide()` / `CursorShow()`
  - `MouseClickAt(x,y, button?, clearmodifiers?)`
- Desktop helpers:
  - `Notify(summary, body?, urgency)`
  - `ClipboardRead(selection, out_var)`
  - `ClipboardSet(text, selection)`
  - `WaitForClipboardChange(selection, initial_text?, timeout_ms, ...)`
  - project-level `clipboard_watchers` + `vhk watch-clipboard`
  - `PasteClipboard(selection, clearmodifiers?)`
  - `OpenUrl(url)`
  - `ComposeEmail(to, cc?, bcc?, subject?, body?, attachments?)`
  - `HttpRequest(method, url, headers?, params?, body?, json_expr?, timeout_ms, allow_error_status?, out_*)`
  - `DownloadFile(url, path, headers?, timeout_ms?, create_parents?, overwrite?, out_*)`
  - `ShowMessage(text, title?, level=info|warning|error)`
  - `AskYesNo(text, title?, default_yes?, out_var)`
  - `InputBox(prompt, title?, default?, password?, out_var)`
  - `ChooseFromList(items_expr, title?, text?, multiple?, out_var)`
  - `StartProcess(command, shell?, cwd?, env?, out_pid)`
  - `WaitForProcessExit(pid, timeout_ms, poll_ms, max_poll_ms, jitter_ms, out_returncode, out_exited)`
  - `KillProcess(pid, signal=TERM, missing_ok?, wait_ms?, out_killed)`
- Filesystem:
  - `ReadCsv(path, encoding?, delimiter?, has_header?, out_var, out_row_count)`
  - `WriteCsv(path, rows_expr, encoding?, delimiter?, append?, include_header?, fieldnames?)`
  - `ReadJson(path, encoding?, out_var)`
  - `WriteJson(path, value_expr, encoding?, indent?, create_parents?)`
  - `ReadFile(path, encoding?, out_var)`
  - `WriteFile(path, text, encoding?, create_parents?)`
  - `AppendFile(path, text, encoding?, create_parents?)`
  - `ListDirectory(path, pattern?, recursive?, files_only?, dirs_only?, sort?, out_var)`
  - `WaitForFile(path, condition=exists|missing|changed, timeout_ms, ...)`
  - `WaitForNewFile(directory, pattern=*, timeout_ms, ...)`
- i3 IPC:
  - `I3Command(command, out_var?)`
  - `I3GetTree(out_var)`
  - `I3GetWorkspaces(out_var)`
  - `WaitForWindow(selector, timeout_ms, ... , out_var, out_con_id, focus?)`
  - `FocusWindow(selector)`

## Assets

### Needles (openQA-style)

If a `.json` file exists next to the needle image (e.g. `foo.png` + `foo.json`),
VHK will load it and (if it contains any `match` areas) match using only those
sub-regions.

This is inspired by openQA needles: JSON can define `match`, `exclude`, and `ocr`
areas, plus optional `click_point` inside match areas.

VHK v0.4+ currently:
- uses **match areas** for template matching
- respects **exclude areas** via template masking
- supports per-area **match percentage** (openQA `match: 90` = 0.90)
- supports click points for `ClickNeedle` (openQA-style)

Use the helper:

```bash
vhk capture-needle ./my_project ok_button --out-dir assets/needles --tags "ok,button"
```


### Visual baselines

`VisualAssert` / `VisualVerify` compare a fresh capture against a baseline image.
The comparison is intentionally strict and explainable:

- images must be the same size
- if the baseline has an openQA-style sidecar JSON, VHK:
  - compares only `match` areas when present
  - ignores `exclude` areas
- `color_tolerance` is a per-pixel max-channel threshold before a pixel counts as changed

This makes baseline images usable as a lightweight "visual assert" asset model
without inventing a second metadata format.

Use the helper:

```bash
vhk capture-baseline ./my_project login_panel --out-dir assets/baselines
```

### Reliability knobs

Every step now supports lightweight retry / continue controls:

- `retry_count`: how many times to retry the step after the first failure
- `retry_delay_ms`: sleep before the next retry
- `retry_backoff`: multiplier applied to the retry delay after each failure
- `continue_on_error`: keep running the macro after retries are exhausted

This is intentionally a small headless analogue of patterns seen in tools like
Robot Framework (`Wait Until Keyword Succeeds`, `Run Keyword And Continue On Failure`).

### Text injection notes

`TypeText` now has multiple practical delivery modes:
- `backend: native` uses the normal keyboard backend (`xdotool`, `wtype`, or `ydotool`)
- `backend: clipboard` writes the text to the chosen clipboard selection and pastes it using `paste_shortcut`
- `backend: xvkbd` uses `xvkbd` as an X11-only fallback for text-heavy / Unicode-sensitive cases
- `backend: auto` keeps the normal backend by default, but the project-level `runner_profile: turbo` can switch large printable text to clipboard-paste automatically

Clipboard mode can preserve and restore the prior clipboard contents:

```yaml
- type: TypeText
  text: "${large_body}"
  backend: clipboard
  preserve_clipboard: true
  paste_shortcut: ctrl+shift+v
```

This is especially useful for terminal widgets and for large text payloads where per-character typing is slow or fragile.

### Cursor + capture notes

VHK now has a tiny explicit cursor-management model for X11-oriented runs:

- project setting: `settings.hide_cursor_during_run: true`
- steps: `CursorHide()`, `CursorShow()`, `ResetModifiers()`

Implementation notes:
- cursor hiding is best-effort and currently prefers `unclutter` / `unclutter-xfixes`; `xbanish` remains useful as a session companion but is less suitable for explicit hide/show lifecycle control
- screenshot backend selection on X11 now prefers `maim`, then `scrot`, then ImageMagick `import`, then `xwd` piped into ImageMagick as a last-resort fallback
- PNG outputs from ImageMagick-backed capture paths are written as `PNG32:` targets to preserve alpha and avoid the classic “transparent regions turn black” failure mode
