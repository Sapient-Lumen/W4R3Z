# File event waits

`WaitForFileEvent` is the one-shot, in-macro sibling of VHK's project-level
`file_watchers:` lane.

Use it when a macro needs to react to the **next matching filesystem event**
without turning the whole project into a long-running watcher daemon.

Typical uses:
- wait for an export directory to receive a fresh file
- continue only after a log/config file is rewritten
- react to deletion/cleanup events during a workflow
- glue an external tool into a macro without shell loops

## Example

```yaml
name: wait_for_export_event
steps:
  - type: WaitForFileEvent
    directory: exports
    event: changed
    pattern: "*.csv"
    stable_ms: 250
    quiet_ms: 300
    timeout_ms: 30000

  - type: ReadFile
    path: "${file_path}"
    out_var: csv_text
```

## Event vocabulary

VHK keeps the authoring surface intentionally smaller than raw helper event
masks:

- `new`
- `changed`
- `deleted`
- `any`

When `inotifywait` is available, lower-level event names such as
`create`, `close_write`, `modify`, `moved_to`, and `delete` are mapped into
that smaller vocabulary. Otherwise VHK falls back to directory snapshot polling.

## Outputs

`WaitForFileEvent` populates:
- `file_event`
- `file_path`
- `file_name`
- `file_dir`
- `file_exists`
- `file_size`
- `file_mtime_ns`
- `file_event_helper`
- `file_event_raw`
- `file_batch_count`
- `file_batch_paths`
- `file_batch_names`
- `file_batch_kinds`

## Producer-friendly knobs

Like the project watcher lane, `WaitForFileEvent` supports:
- `exclude`
- `min_size`
- `stable_ms`
- `quiet_ms`
- `recursive`

That makes it usable with producers that create placeholders first, write in
bursts, or rename partial files into final names. `quiet_ms` specifically adds
a small quiesce window after the first match: if more matching events arrive,
VHK resets the timer, returns the most recent event, and annotates it with the
ordered burst summary in `file_batch_*`.

## Honesty notes

This is still a Linux-native best-effort lane, not a promise of perfect file
truth:
- native helper streams inherit inotify-style limitations
- very short waits may prefer polling because helper process startup dominates
- bursty producers can still require `stable_ms`, dedupe, or higher-level macro
  logic rather than assuming one low-level event means "fully done"
