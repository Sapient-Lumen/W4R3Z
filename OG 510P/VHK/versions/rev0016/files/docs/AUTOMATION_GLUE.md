# Automation glue: files, clipboard, and small waits

VHK v0.9 adds a small set of pragmatic “glue” steps that show up in many real
macro tools:

- `ReadFile` / `WriteFile` / `AppendFile`
- `ListDirectory`
- `WaitForFile`
- `WaitForClipboardChange`
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
- `WaitForClipboardChange` prefers `clipnotify` on X11 when available
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
