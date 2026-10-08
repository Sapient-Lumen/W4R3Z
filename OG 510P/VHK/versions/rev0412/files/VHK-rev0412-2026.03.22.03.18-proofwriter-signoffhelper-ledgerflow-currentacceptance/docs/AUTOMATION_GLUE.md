# Automation glue: files, clipboard, and small waits

VHK v0.9 adds a small set of pragmatic “glue” steps that show up in many real
macro tools:

- `ReadFile` / `WriteFile` / `AppendFile`
- `ListDirectory`
- `WaitForFile`
- `WaitForFileEvent`
- `WaitForClipboardChange`
- `WaitForClipboardEvent`
- `MouseDrag` / `MouseWheel`

## Why these exist

Many everyday automations are only partly about GUI interaction. A practical
macro often needs to:

- wait for a download or export file to appear
- append a line to a run log
- read a generated text file
- react when the clipboard changes
- drag something on screen or scroll a list

This is the same general shape exposed by tools like Actiona and other desktop
automation suites: file IO, clipboard actions, window waits, image search, and
mouse/keyboard control all live side-by-side.

## Event helpers vs polling

VHK keeps the wait semantics consistent with its other wait steps:

- explicit timeout
- repeat attempts recorded in the event log
- helper-backed waiting when available
- polling fallback when helpers are missing

Current best-effort helper usage:

- `WaitForFile` prefers `inotifywait` when available
- `WaitForFileEvent` reuses the same helper/fallback policy, but waits for the next matching directory event instead of proving one path state; `quiet_ms` lets it coalesce bursty producer flows instead of returning the first low-level edge
- `WaitForClipboardChange` prefers `clipnotify` on X11 when available
- `WaitForClipboardChange` also prefers `wl-paste --watch` on Wayland when available
- `WaitForClipboardEvent` returns on a clipboard-owner event (even when the
  clipboard contents are identical to the baseline) when helpers are available
- both clipboard wait steps can additionally filter on `pattern` / `flags` /
  `condition`, so clipboard-driven parsing loops stay declarative instead of
  shelling out or hand-rolling `While` retry glue
- otherwise VHK falls back to polling with backoff/jitter

## Example

```yaml
name: wait_for_download_and_log
steps:
  - type: WaitForFile
    path: downloads/report.csv
    condition: exists
    timeout_ms: 30000

  - type: ReadFile
    path: downloads/report.csv
    out_var: csv_text

  - type: AppendFile
    path: logs/run.log
    text: "Loaded report (${project.name})\n"
```


## Clipboard filtering example

```yaml
name: wait_for_ticket
steps:
  - type: WaitForClipboardEvent
    pattern: "ticket-(\d+)"
    condition: "int(clipboard_match_groups['0']) >= 200"
    out_text: ticket_text
    out_match: ticket_match
```

This lets a macro sleep until the clipboard carries the shape it actually wants,
while still preserving `clipboard_changed` / `clipboard_event` metadata.
