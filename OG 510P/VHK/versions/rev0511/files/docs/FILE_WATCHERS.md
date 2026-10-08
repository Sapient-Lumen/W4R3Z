# File watchers

File watchers are the filesystem analogue of VHK's clipboard/window/bus watcher
lanes: keep **trigger policy** in `project.yaml`, then reuse the normal runner
for prompts, retries, logging, and side effects.

For one-shot in-macro waits instead of long-running watcher rules, use
`WaitForFileEvent` (see `docs/FILE_EVENT_WAITS.md`).

Typical uses:
- react when a download/export/render finishes
- turn a "drop a file here" folder into a macro trigger
- glue editor/build tools into VHK without inventing one-off shell loops

## Example

```yaml
file_watchers:
  - name: exports
    directory: exports
    pattern: "*.csv"
    event: new
    recursive: false
    exclude: ["*.tmp", "*.part", "*.crdownload"]
    stable_ms: 400
    quiet_ms: 300
    macro: on_export
    vars:
      source: file_rule
```

Run it:

```bash
vhk watch-file /path/to/project exports
```

## Event vocabulary

VHK keeps the authoring surface intentionally smaller than raw `inotify` masks:

- `new`
- `changed`
- `deleted`
- `any`

When `inotifywait` is available, VHK maps lower-level events such as
`create`, `close_write`, `modify`, `moved_to`, and `delete` into that smaller
vocabulary. When it is not available, VHK falls back to directory snapshot
polling and derives the same high-level events from file state differences.

## Macro vars

Watcher-triggered macros receive:
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
- `watcher_name`
- any custom entries from `vars`

## Settling / producer-friendly knobs

`stable_ms` and `min_size` are useful for producer flows where a file may appear
before it is truly ready:
- downloads that rename from `*.part` / `*.crdownload`
- render/export tools that write in bursts
- scripts that stage a file and then fill it


`quiet_ms` solves a different problem: *event bursts*. Many Linux-native tools
write temp files, rename into place, then touch metadata again. With `quiet_ms`,
VHK waits for the matching event stream to go quiet before it runs the macro,
then exposes ordered burst metadata (`file_batch_*`) so the macro can still see
what happened during that coalesced window.

## Honesty notes

This is a Linux-native surface, not a promise of perfect filesystem truth:
- `inotify` queues can overflow under load
- some filesystems and mounts behave poorly with native event streams
- polling fallback can only approximate rapid event bursts

For heavyweight deployment glue, VHK should also keep learning from adjacent
Linux-native lanes such as `systemd.path` and `incrond`, rather than assuming
one watcher shape owns every host story.
