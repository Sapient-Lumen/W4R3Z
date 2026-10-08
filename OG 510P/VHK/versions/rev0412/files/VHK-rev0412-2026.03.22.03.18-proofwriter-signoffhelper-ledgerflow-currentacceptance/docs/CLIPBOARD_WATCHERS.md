# Clipboard watchers

VHK can run macros when clipboard content changes or when clipboard-owner events occur, and can optionally match a regex.

This is intentionally a small, headless analogue of the “clipboard commands /
rules” model seen in tools like CopyQ and clipmenu-style setups: keep the policy
in the project, reuse the normal runner for the actual work, and log enough metadata
to explain what happened later.

## Why this exists

Typical clipboard micro-macros are surprisingly useful:
- copied URL → open it in a browser
- copied PDF text → remove line breaks and normalize whitespace
- copied code block → run a formatter and put the result back on the clipboard
- copied path → open terminal / file manager there

## `project.yaml`

```yaml
name: clipboard_pack
clipboard_watchers:
  - name: copied_url
    macro: open_copied_url
    pattern: "https?://(\\S+)"
    flags: [IGNORECASE]
    selection: clipboard
    event_mode: change
    dedupe: true
    dedupe_scope: handled
    # Optional: skip values seen recently (milliseconds)
    dedupe_window_ms: 0
    # Optional: prevent macro loops (milliseconds)
    cooldown_ms: 0
    debounce_ms: 150
    vars:
      source: clipboard_rule

macros:
  open_copied_url: macros/open_copied_url.yaml
```

And the macro can consume watcher-provided vars:

```yaml
name: open_copied_url
steps:
  - type: OpenUrl
    url: "${clipboard_text}"
```

## CLI

```bash
# Inspect watchers
vhk list-watchers ./my_project

# Run one watcher loop until Ctrl+C
vhk watch-clipboard ./my_project copied_url

# Stop automatically after N clipboard events (useful for testing)
vhk watch-clipboard ./my_project copied_url --max-events 5
```

## Matching and vars

When `pattern` is set and the clipboard text matches it, the watcher passes:
- `clipboard_text`
- `clipboard_selection`
- `clipboard_changed`
- `clipboard_event`
- `clipboard_event_mode`
- `watcher_name`
- `clipboard_match`
- `clipboard_groups`
- `clipboard_match_groups`
- `clipboard_groupdict`
- custom `vars` from the watcher definition

If `pattern` is omitted, every clipboard change/event triggers the macro.

`event_mode` controls what counts as an event:
- `change` (default): only return when the clipboard text changes
- `event`: return on helper-backed clipboard-owner events even when the copied
  text is identical to the previous value; this is useful for repeated-copy
  workflows and AHK-style "same text copied again" triggers

## De-dupe and throttling knobs

Clipboard automation is easy to accidentally make noisy (or even loop) if the
watcher macro writes to the clipboard.

- `dedupe: true|false` controls whether the watcher should skip duplicates.
- `dedupe_scope: handled|seen`
  - `handled` (default): compare against the last clipboard value that actually
    *ran the macro*.
  - `seen`: compare against the last seen clipboard value (consecutive duplicates).
- `dedupe_window_ms`: if >0, skip clipboard texts seen in the last N ms.
- `cooldown_ms`: if >0, throttle macro runs; events are logged but the macro is
  not executed until the cooldown expires.

## Explainability

Each watcher appends metadata to:

```text
logs/clipboard_watcher_<name>.jsonl
```

The watcher log is intentionally metadata-oriented rather than a second full event
trace. Each line records:
- timestamp
- watcher name / macro name
- clipboard selection
- text length
- preview
- sha256 of clipboard text
- whether the event ran the macro or was skipped (duplicate / nonmatching)
- linked macro run event-log path when a macro actually ran

## Caveats

- On X11, VHK can benefit from `clipnotify` for efficient waits and same-text owner-event detection.
- On Wayland, VHK prefers `wl-paste --watch` when available, and falls back to
  polling if the compositor doesn't support the required protocol. In polling
  mode, `event_mode: event` degrades to content-change semantics because there
  is no honest same-text event signal.
- Clipboard-triggered automation can capture sensitive data. Keep watcher macros
  focused and deliberate.
