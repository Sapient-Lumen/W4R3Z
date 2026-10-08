# Clipboard watchers

VHK can run macros when clipboard content changes and optionally matches a regex.

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
    dedupe: true
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

# Stop automatically after N clipboard-change events (useful for testing)
vhk watch-clipboard ./my_project copied_url --max-events 5
```

## Matching and vars

When `pattern` is set and the clipboard text matches it, the watcher passes:
- `clipboard_text`
- `clipboard_selection`
- `watcher_name`
- `clipboard_match`
- `clipboard_groups`
- `clipboard_match_groups`
- `clipboard_groupdict`
- custom `vars` from the watcher definition

If `pattern` is omitted, every clipboard change triggers the macro.

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

- On X11, VHK can benefit from `clipnotify` for efficient waits.
- On Wayland, VHK currently falls back to repeated reads for the watcher loop even
  though tools like `wl-paste --watch` point to a better future backend.
- Clipboard-triggered automation can capture sensitive data. Keep watcher macros
  focused and deliberate.
