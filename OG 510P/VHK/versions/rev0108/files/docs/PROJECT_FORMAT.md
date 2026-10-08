# Project format

A VHK project is a folder that can be zipped and shared.

Useful CLI checks:

- `vhk validate <project_dir>` performs a **static** validation pass:
  - macro/binding/watcher references
  - expression syntax
  - existence of required visual assets (e.g. `needle_path` / `baseline_path`)

Project scaffolding:

- `vhk init <project_dir>` creates a starter `project.yaml` + folders.
- `vhk new-macro <project_dir> <name>` adds a new macro under `macros/`.
- `vhk record-x11 --project <project_dir> --macro <name>` records into a macro file (X11 only).


## Bundles

Projects are meant to be zipped and shared.

```bash
vhk bundle /path/to/project /tmp/my_project.zip
```

Bundles include a top-level `vhk_bundle_manifest.json` with basic integrity metadata:

- VHK version + created_at time
- file inventory (`path`, `size`, `sha256`, `mtime`)

This is intended for future “verify bundle” tooling and for integrity-aware caching.

You can also verify a bundle locally:

```bash
vhk verify-bundle /tmp/my_project.zip
```


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

  # Optional: IPC bus socket path for bus_watchers / busd. If unset, VHK chooses
  # a per-project path under XDG_RUNTIME_DIR when available.
  bus_socket: null

  # Optional: when using systemd socket activation and multiple file descriptors
  # are passed, select the correct one by name (from LISTEN_FDNAMES).
  #
  # Can also be overridden at runtime via VHK_BUS_FDNAME.
  bus_fdname: null

  # Optional: bus event name that triggers busd live reload (reserved namespace: vhk.*).
  # Disable by setting null or an empty string.
  bus_reload_event: vhk.reload

  # Optional: bus event name that requests busd shutdown (reserved namespace: vhk.*).
  # Disable by setting null or an empty string.
  bus_stop_event: vhk.stop

  dry_run: false
```

### Regions (ROI)

Projects can define named **regions of interest** to scope visual operations
to a stable rectangle (faster + less flaky than scanning the whole screen).

```yaml
regions:
  toolbar:
    x: 0
    y: 0
    w: 1400
    h: 120
```

Capture a region interactively:

```bash
vhk select-region --project /path/to/project --name toolbar
```

Use in macros:

```yaml
- type: WaitForImage
  needle_path: assets/needles/ok.png
  region: "@toolbar"
```

See `docs/NAMED_REGIONS.md`.

### Hotkey bindings (export targets)

Bindings are optional and can be exported to multiple targets:

- `vhk gen-wm-config` (i3/sway/hyprland snippets)
- `vhk gen-kanata-config` (Kanata)
- `vhk gen-keyd-config` (keyd)

```yaml
bindings:
  - keys: "$mod+Shift+h"
    # Optional stable identifier (used by some exporters / future Studio UI)
    name: "my_hotkey"
    macro: my_macro
    description: "Run my macro"
    vars:
      foo: bar
    # Optional: context-sensitive binding (only when focused window matches).
    # i3 criteria are regular expressions (PCRE), so anchor with ^...$ for exact.
    when:
      class: "Firefox"
      window_role: "browser"
      title: "^Mozilla Firefox$"
```

Notes:
- i3: VHK generates `bindsym --release … exec --no-startup-id …` lines.
- sway: VHK generates `bindsym --release … exec …` lines (no `--no-startup-id`).
- hyprland: VHK generates `bindr = MODS, KEY, exec, …` lines (release trigger).
- Optional: `vhk gen-wm-config --mode-enter Mod4+R` generates an i3/sway **mode** or
  Hyprland **submap** (leader-key keymap). See `docs/WM_MODES.md`.
- `--release` is recommended in the i3 docs for commands that should run after
  the keyboard grab is released.
- If `when:` is present:
  - i3/sway: VHK emits criteria (`[class=... window_role=... title=...]`) so the binding is context-sensitive.
  - hyprland: Hyprland binds don’t have i3-style criteria; VHK falls back to a portable gate by adding
    `--require-window <selector-json>` to the generated command.
  - If you export `--via-bus`, the `when:` selector is embedded into the bus payload as `require_window`.

### Hotstrings (text expansion)

Hotstrings are optional and are exported to a dedicated hotstring engine such as Espanso.

```yaml
hotstrings:
  - trigger: ":sig"
    macro: signature
    description: "Insert signature"
    mode: return
    force_mode: clipboard
    # Optional context condition (best-effort; see HOTSTRINGS.md for caveats)
    when:
      class: Firefox
    # Optional Espanso form layout (prompted expansions)
    form_layout: |
      Hello [[name]]
```

Export to an Espanso match file:

```bash
vhk gen-espanso /path/to/project --out /tmp/vhk_project.yml

# For context-sensitive hotstrings, generate an Espanso package directory:
vhk gen-espanso /path/to/project --package-dir /tmp/espanso_vhk
```

See `docs/HOTSTRINGS.md`.

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
- `dedupe_scope`: `handled` (default) compares against the last text that *ran the macro*;
  `seen` compares against the last seen clipboard value
- `dedupe_window_ms`: when >0, skip values seen in the last N ms
- `cooldown_ms`: when >0, throttle macro runs (events are still logged)
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



### Bus watchers

Bus watchers let **external tools** trigger macros by emitting a small local IPC event.
This is a portable “escape hatch” for Linux automation: if something can run a command
or send a UNIX socket datagram, it can trigger VHK.

```yaml
bus_watchers:
  - name: build_done
    event: build_done
    macro: notify_build
    consume: false     # optional: stop propagation when this watcher handles an event
    pattern: "success"   # optional regex against bus_text
    flags: [IGNORECASE]
    vars:
      source: bus
```

Emit an event:

```bash
vhk emit-bus /path/to/project build_done --data '{"status":"success"}'
```

Run a watcher:

```bash
vhk watch-bus /path/to/project build_done
```

If you want multiple bus watchers active at once (single socket bind), use:

```bash
vhk busd /path/to/project
```

Watcher-triggered macros receive:
- `bus_event`, `bus_data`, `bus_text`, `watcher_name`
- `bus_match` / `bus_groups` / `bus_groupdict` when `pattern` matches
- any custom entries from `vars`

See `docs/BUS_EVENTS.md`.

Dispatch mode:

```yaml
bus_watchers:
  - name: hotkeys
    event: hotkey
    dispatch: true
```

This lets hotkey exporters emit events like `{"macro":"...","vars":{...}}` so one watcher can dispatch
to many macros.

### Window watchers

Projects can define **window-triggered** macro rules (focus changes and workspace
focus changes). These are intended to be a small, headless analogue of the
"on focus" / "on workspace" hooks people build with i3 IPC scripts and Hyprland
socket2 event listeners.

```yaml
window_watchers:
  - name: focus_firefox
    event: focus
    when:
      class: Firefox
    macro: on_focus
    dedupe: true
    dedupe_window_ms: 0
    cooldown_ms: 0
    debounce_ms: 50
    vars:
      source: window_rule

  - name: workspace_any
    event: workspace
    macro: on_workspace
```

Run with:

```bash
vhk watch-window /path/to/project focus_firefox
```

Watcher-triggered macros receive these initial vars:
- `wm` (i3/sway/hyprland/unknown)
- `wm_event` (focus/workspace/title/urgent/new/close/custom)
- `wm_event_name` (raw WM event name)
- `wm_event_data` (raw WM event data / payload)
- `window` (active window info dict; best-effort)
- convenience fields: `window_title`, `window_class`, `workspace`, `urgent`
- `prev_window` when `include_prev: true`

See `docs/WINDOW_WATCHERS.md` for platform notes.

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

## Editor autocomplete (JSON Schema)

VHK can generate JSON Schemas for `project.yaml` and `macros/*.yaml` to enable
autocomplete/validation in editors that support `yaml-language-server` (VS Code
YAML extension, Neovim `yamlls`, etc.).

See `docs/SCHEMAS.md`.
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
  - `ImageSearchAllFile(haystack_path, needle_path, region?, threshold?, scales?, max_results?, overlap_threshold?, sort?, scan_order?, out_matches?)`
  - `WaitForImageFile(..., timeout_ms, poll_ms, max_poll_ms, jitter_ms)`
  - `PixelSearchFile(image_path, color, region?, tolerance?, tolerance_mode?, step?, match_strategy?, scan_order?, out_*)`
  - `PixelSearchAllFile(image_path, color, region?, tolerance?, tolerance_mode?, step?, group=none|connected, pick=center|first|best, min_area?, max_results?, sort=scan|dist, scan_order?, out_matches?, out_count?)`
  - `WaitForPixelFile(..., tolerance_mode?, step?, match_strategy?, scan_order?, timeout_ms, poll_ms, max_poll_ms, jitter_ms)`
  - `PixelGetColorFile(image_path, x, y, region?, out_*)`
  - `OcrReadTextFile(image_path, region?, out_var, lang, preprocess?, scale?, psm?, oem?, tess_config?)`
  - `OcrFindTextFile(image_path, region?, pattern, match=contains|regex|fuzzy, fuzzy_threshold?, fuzzy_mode=partial|ratio, case_sensitive?, level=word|line, match_strategy=first|best_conf, scan_order?, preprocess?, scale?, psm?, oem?, tess_config?, out_*)`
  - `OcrFindTextAllFile(image_path, region?, pattern, match=contains|regex|fuzzy, fuzzy_threshold?, fuzzy_mode=partial|ratio, case_sensitive?, level=word|line, sort=scan|best_conf, scan_order?, max_results?, min_conf?, preprocess?, scale?, psm?, oem?, tess_config?, out_matches?, out_count?)`

> **OCR tuning tip:** If OCR is flaky on small UI fonts, try `preprocess: auto` (grayscale + autocontrast + binarize) and `scale: 2`. You can also set `psm`/`oem`/`tess_config` to pass options through to Tesseract.

> **OCR matching tip:** If OCR output is close-but-not-exact (common in games and low-contrast UIs), use `match: fuzzy` with `fuzzy_threshold` (default 0.8) and `fuzzy_mode: partial` to tolerate small OCR mistakes.

  - `CaptureScreenshot(path?, region?, out_var)`
  - `CoordMode(target=pixel|mouse, mode=screen|window|client)`
- Vision (screen-capture):
  - `ImageSearch(needle_path, region?, threshold?, screenshot_path?, out_*)`
  - `ImageSearchAll(needle_path, region?, threshold?, scales?, max_results?, overlap_threshold?, sort?, scan_order?, screenshot_path?, out_*)`
  - `WaitForImage(..., timeout_ms, poll_ms, max_poll_ms, jitter_ms, scan_rate_hz?, max_attempts?, stable_ms?, stable_attempts?, cursor_avoid?, cursor_corner?, cursor_margin?, cursor_restore?, debug_on_timeout?, out_debug_screenshot?)`
  - `WaitForImageAll(..., min_count?, screenshot_path?, out_matches?, out_count?, timeout_ms, poll_ms, max_poll_ms, jitter_ms, scan_rate_hz?, stable_ms?, stable_attempts?, cursor_avoid?, cursor_corner?, cursor_margin?, cursor_restore?, debug_on_timeout?, out_debug_screenshot?, ...)`
  - `WaitForImageVanish(..., timeout_ms, poll_ms, max_poll_ms, jitter_ms, scan_rate_hz?, require_seen?, stable_ms?, stable_attempts?, debug_on_timeout?, out_*last_seen*)`
  - `PixelSearch(color, region?, tolerance?, tolerance_mode?, step?, match_strategy?, scan_order?, screenshot_path?, out_*)`
  - `PixelSearchAll(color, region?, tolerance?, tolerance_mode?, step?, group=none|connected, pick=center|first|best, min_area?, max_results?, sort=scan|dist, scan_order?, screenshot_path?, out_matches?, out_count?)`
  - `WaitForPixel(color, region?, tolerance?, tolerance_mode?, step?, match_strategy?, scan_order?, timeout_ms, poll_ms, max_poll_ms, jitter_ms, scan_rate_hz?, ...)`
  - `WaitForPixelAll(color, region?, tolerance?, tolerance_mode?, step?, group=none|connected, pick=center|first|best, min_area?, max_results?, sort=scan|dist, scan_order?, min_count?, timeout_ms, poll_ms, max_poll_ms, jitter_ms, scan_rate_hz?, ...)`
  - `WaitForPixelVanish(color, region?, tolerance?, tolerance_mode?, step?, match_strategy?, scan_order?, timeout_ms, poll_ms, max_poll_ms, jitter_ms, scan_rate_hz?, require_seen?, stable_ms?, stable_attempts?, out_*last_seen*)`
  - `PixelGetColor(x, y, region?, screenshot_path?, out_*)`
  - `OcrReadText(region?, screenshot_path?, out_var, lang, preprocess?, scale?, psm?, oem?, tess_config?)`
  - `OcrFindText(region?, screenshot_path?, pattern, match=contains|regex|fuzzy, fuzzy_threshold?, fuzzy_mode=partial|ratio, case_sensitive?, level=word|line, match_strategy=first|best_conf, scan_order?, preprocess?, scale?, psm?, oem?, tess_config?, out_*)`
  - `OcrFindTextAll(region?, screenshot_path?, pattern, match=contains|regex|fuzzy, fuzzy_threshold?, fuzzy_mode=partial|ratio, case_sensitive?, level=word|line, sort=scan|best_conf, scan_order?, max_results?, min_conf?, preprocess?, scale?, psm?, oem?, tess_config?, out_matches?, out_count?)`
  - `WaitForText(pattern, match=contains|regex|fuzzy, fuzzy_threshold?, fuzzy_mode=partial|ratio, case_sensitive?, preprocess?, scale?, psm?, oem?, tess_config?, timeout_ms, poll_ms?, max_poll_ms?, jitter_ms?, scan_rate_hz?, max_attempts?)`
  - `WaitForTextVanish(pattern, match=contains|regex|fuzzy, fuzzy_threshold?, fuzzy_mode=partial|ratio, case_sensitive?, preprocess?, scale?, psm?, oem?, tess_config?, timeout_ms, poll_ms?, max_poll_ms?, jitter_ms?, scan_rate_hz?, require_seen?, stable_ms?, stable_attempts?, out_seen?, out_last_text?, out_last_present?)`
  - `WaitForTextBox(pattern, match=contains|regex|fuzzy, fuzzy_threshold?, fuzzy_mode=partial|ratio, case_sensitive?, level=word|line, match_strategy=first|best_conf, scan_order?, preprocess?, scale?, psm?, oem?, tess_config?, timeout_ms, poll_ms?, max_poll_ms?, jitter_ms?, scan_rate_hz?, max_attempts?, ...)`
  - `AssertText(pattern, match=contains|regex|fuzzy, fuzzy_threshold?, fuzzy_mode=partial|ratio, case_sensitive?, preprocess?, scale?, psm?, oem?, tess_config?)`
  - `ClickText(pattern, match=contains|regex|fuzzy, fuzzy_threshold?, fuzzy_mode=partial|ratio, case_sensitive?, level=word|line, match_strategy=first|best_conf, scan_order?, preprocess?, scale?, psm?, oem?, tess_config?, timeout_ms, poll_ms?, max_poll_ms?, jitter_ms?, scan_rate_hz?, max_attempts?, offset_x/y?, button?, clearmodifiers?)`
  - `ClickTextAll(pattern, match=contains|regex|fuzzy, fuzzy_threshold?, fuzzy_mode=partial|ratio, case_sensitive?, level=word|line, sort=scan|best_conf, scan_order?, max_results?, min_conf?, preprocess?, scale?, psm?, oem?, tess_config?, timeout_ms, poll_ms?, max_poll_ms?, jitter_ms?, scan_rate_hz?, max_attempts?, offset_x/y?, button?, clearmodifiers?, delay_between_clicks_ms?)`
  - `ClickPixelAll(color, region?, tolerance?, tolerance_mode?, step?, group=none|connected, pick=center|first|best, min_area?, max_results?, sort=scan|dist, scan_order?, min_count?, offset_x/y?, button?, clearmodifiers?, delay_between_clicks_ms?)`
  - `ClickImageAll(needle_path, region?, threshold?, scales?, max_results?, overlap_threshold?, sort?, scan_order?, min_count?, click_point_id?, offset_x/y?, button?, clearmodifiers?, delay_between_clicks_ms?)`
  - `ClickNeedle(needle_path, region?, threshold?, click_point_id?, offset_x/y?, button?, clearmodifiers?)`
  - `VisualAssert(baseline_path, region?, color_tolerance?, max_changed_pixels?, max_change_ratio?)`
  - `VisualVerify(...)`
  - `WaitForRegionChange(region?, baseline_path?, color_tolerance?, min_changed_pixels?, min_change_ratio?, timeout_ms, ...)`
  - `WaitForRegionStable(region?, baseline_path?, color_tolerance?, max_changed_pixels?, max_change_ratio?, rolling_baseline?, timeout_ms, poll_ms?, max_poll_ms?, jitter_ms?, scan_rate_hz?, stable_ms?, stable_attempts?, debug_on_timeout?)`

> **Image match coordinates:** `ImageSearch*`/`WaitForImage*` return the **top-left** of the matched rectangle (AHK-style). `ClickImageAll` (and `ClickNeedle`) click the **center** of the rectangle by default (Sikuli-ish) unless the needle metadata defines a click point.

> **Scan rate vs polling:** Most `WaitFor*` steps support `poll_ms` (sleep between scans) and an optional `scan_rate_hz` (scans per second, SikuliX-style). If `scan_rate_hz` is set it takes precedence and keeps the scan interval fixed.
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
  - `GetCursorPos(out_x=cursor_x, out_y=cursor_y, out_backend=cursorpos_backend)`
  - `MouseClickAt(x,y, button?, clearmodifiers?)`
- Desktop helpers:
  - `Notify(summary, body?, urgency)`
  - `ClipboardRead(selection, out_var)`
  - `ClipboardSet(text, selection)`
  - `WaitForClipboardChange(selection, initial_text?, timeout_ms, ...)`
  - `WaitForClipboardEvent(selection, initial_text?, timeout_ms, ...)`
  - project-level `clipboard_watchers` + `vhk watch-clipboard`
  - `PasteClipboard(selection, clearmodifiers?)`
  - `OpenUrl(url)`
  - `ComposeEmail(to, cc?, bcc?, subject?, body?, attachments?)`
  - `HttpRequest(method, url, headers?, params?, body?, json_expr?, timeout_ms, allow_error_status?, out_*)`
  - `WaitForHttp(method, url, headers?, params?, body?, json_expr?, timeout_ms, ok_statuses?, status_min?, status_max?, text_contains?, text_regex?, condition?, poll_ms, respect_retry_after?, out_*)`
  - `DownloadFile(url, path, headers?, timeout_ms?, create_parents?, overwrite?, atomic?, tmp_suffix?, sha256?, out_*)`
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
  - `WaitForNewFile(directory, pattern=*, recursive?, exclude?, include_existing_changes?, since_ns?, min_size?, stable_ms?, timeout_ms, ...)`
  - `WaitForDownload(directory, pattern=*, recursive?, exclude?, min_size?, stable_ms?, timeout_ms, ...)`
- i3 IPC:
  - `I3Command(command, out_var?)`
  - `I3GetTree(out_var)`
  - `I3GetWorkspaces(out_var)`
  - `WaitForWindow(selector, timeout_ms, poll_ms?, max_poll_ms?, jitter_ms?, use_events?, stable_ms?, stable_attempts?, out_var, out_con_id, out_workspace, focus?)`
  - `WaitForWindowVanish(selector, timeout_ms, poll_ms?, use_events?, require_seen?, stable_ms?, stable_attempts?, out_seen?, out_last_con_id?, out_last_workspace?, out_last_window?)`
  - `FocusWindow(selector)`

### PixelSearch tolerance modes

Pixel search steps support two tolerance interpretations:

- `tolerance_mode: euclidean` (default): distance is Euclidean in BGR space
  (`sqrt(db^2+dg^2+dr^2)`), which behaves smoothly when you want an overall
  "closest color" match.
- `tolerance_mode: per_channel`: distance is the maximum per-channel absolute
  difference (`max(|db|,|dg|,|dr|)`), which matches the common "variation"
  mental model found in AHK/AutoIt-style PixelSearch APIs.

The returned `px_dist` is this computed distance for the returned pixel.

### PixelSearch step (stride)

Pixel search steps also support an optional `step` parameter (mirroring AutoIt's
`PixelSearch` `step` argument):

- `step: 1` (default) checks every pixel.
- `step: 2` checks every other pixel, etc. This can be much faster on large
  regions, but it can miss matches if the target pixel falls between sampled
  points. AutoIt's docs explicitly warn that larger step values reduce accuracy.

For `WaitForPixel` / `WaitForPixelFile`, VHK automatically **cycles sampling
phases** across attempts when `step > 1` so that repeated polls eventually
cover all pixels (without paying the full cost on every attempt).

### PixelSearch match strategies and scan order

Historically, tools disagree on what a "pixel search" should return:

- Some ecosystems return the **first** pixel that meets the tolerance when scanning the region
  (AutoIt documents this explicitly: top-to-bottom, left-to-right, first match returned).
- Others prefer the **best** (closest) pixel, which is nicer for diagnostics.

VHK defaults to `match_strategy: best` and returns the closest pixel (minimum distance).
If you want classic AHK/AutoIt-style behavior, use:

- `match_strategy: first`
- `scan_order: tlbr|trbl|bltr|brtl`

`scan_order` controls the traversal direction for `first` and also acts as the
**tie-breaker** for `best` when multiple pixels have the same distance.

When using `step > 1`, `first` searches only the sampled grid for that attempt.
For waits, VHK cycles sampling phases so repeated polls still cover all pixels.


### Color literal formats

VHK accepts several color literal formats for pixel steps:

- `#RRGGBB` (recommended)
- `0xRRGGBB` (AutoHotkey-style hex literal)
- `R,G,B`
- `[R,G,B]`

To help port scripts from ecosystems that default to **BGR** hex ordering
(e.g. some legacy AutoHotkey commands unless the `RGB` option is used),
VHK also accepts an explicit prefix:

- `bgr:#BBGGRR` or `bgr:0xBBGGRR`

By default, hex literals are interpreted as RGB.


### CoordMode (coordinate frames)

Many automation APIs interpret coordinates relative to something other than the
whole screen. AutoHotkey famously defaults PixelSearch/ImageSearch coordinates to
the **active window's client area** unless you change it with `CoordMode`.

VHK supports a pragmatic subset of this idea via a `CoordMode` step:

```yaml
- type: CoordMode
  target: pixel   # pixel | mouse
  mode: window    # screen | window | client
```

Behavior:

- `target: pixel` affects the interpretation of `region` fields for screen-capture
  steps (`CaptureScreenshot`, `ImageSearch`, `WaitForImage`, `PixelSearch`,
  `WaitForPixel`, OCR steps, and visual compare steps). It also affects the
  `(x,y)` inputs for `PixelGetColor`.
- `target: mouse` affects `(x,y)` inputs for `MouseMove`, `MouseClickAt`, and
  `MouseDrag` when those steps use absolute coordinates.
- `mode: screen` means coordinates are absolute.
- `mode: window` means coordinates are relative to the active window's outer
  rectangle.
- `mode: client` means coordinates are relative to the active window's client
  rectangle (best-effort).

VHK always emits and stores **absolute screen coordinates** for outputs such as
`match_x/match_y` and `px_x/px_y`. `CoordMode` only changes how *inputs* are
interpreted.


## Assets

### Needles (openQA-style)

If a `.json` file exists next to the needle image (e.g. `foo.png` + `foo.json`),
VHK will load it and (if it contains any `match` areas) match using only those
sub-regions.

This is inspired by openQA needles: JSON can define `match`, `exclude`, and `ocr`
areas, plus optional `click_point` inside match areas.

VHK v0.4+ currently:
- uses **match areas** for template matching
- respects **exclude areas** via template masking (even if you don't define any `match` areas)
- supports per-area **match percentage** (openQA `match: 90` = 0.90)
- supports click points for `ClickNeedle` (openQA-style)

Note: OpenCV's template matching only supports masks for a subset of methods,
so when an exclude mask is present VHK uses a mask-capable scoring method
internally.

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
- `retry_jitter`: `none` (default) or `full` (randomize delay to reduce lockstep retries)
- `retry_jitter_ms`: additive +/- jitter window applied after jitter strategy
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
