# Web / external integration helpers

VHK now includes a small set of "don't make me shell out for this" steps for
common desktop-automation glue:

- `OpenUrl(url)` — open a URL (or file target) with the desktop default handler
  via `xdg-open`
- `ComposeEmail(...)` — open the preferred mail composer via `xdg-email`
- `PasteClipboard(selection)` — paste CLIPBOARD (`Ctrl+V`) or PRIMARY
  (`Shift+Insert`)
- `HttpRequest(...)` — make a one-shot HTTP request and store status/headers/body
- `DownloadFile(...)` — fetch a URL directly to a project-relative path
- `WaitForNewFile(...)` — wait until a fresh file matching a glob appears in a
  directory
- `WaitForFileEvent(...)` — wait for the next matching file event in a directory
- `WaitForDownload(...)` — download-tuned wrapper around `WaitForNewFile`

## Why these exist

Real macro tools routinely include small but high-leverage glue like opening
URLs, editing files, clipboard actions, and data/network helpers. The goal is to
let users build practical workflows without wrapping every external integration in
`RunShell`.

## Example

```yaml
name: fetch_release_notes
steps:
  - type: HttpRequest
    method: GET
    url: https://example.com/api/releases/latest
    out_json: release
  - type: WriteFile
    path: data/release_notes.txt
    text: "${release.notes}"
  - type: OpenUrl
    url: "${release.html_url}"
```

## Notes

- `HttpRequest` is intentionally sessionless/simple. It is aimed at quick glue
  and API calls inside a macro, not at becoming a full browser automation stack.
- `ComposeEmail` prefills a composer; it does **not** send mail automatically.
- `WaitForNewFile` is useful after browser-driven downloads when the final file
  name is not known ahead of time.

### `WaitForNewFile` outputs

When a file is detected, `WaitForNewFile` populates:

- `new_file_path` — full path to the matched file
- `new_file_name` — basename only
- `new_file_size` — size in bytes
- `new_file_mtime_ns` — file modification time (nanoseconds)

For tight timeouts (sub-second), the implementation prefers polling over
spawning `inotifywait`, since `inotifywait` uses integer-second timeouts and
process startup overhead can dominate very short waits.


### `WaitForNewFile` filters

When dealing with browser downloads and other "non-atomic" producers, it’s
common to see:

- temporary files such as `*.part` / `*.crdownload`
- zero-byte placeholders that later grow
- files that grow for a while before becoming stable

To help with these workflows, `WaitForNewFile` supports a few optional knobs:

- `exclude`: a glob (or list of globs) matched against the basename.
  Useful to ignore temporary download files.
- `min_size`: require the matched file to be at least N bytes.
- `stable_ms`: require (size, mtime) to remain unchanged for N milliseconds
- `quiet_ms`: wait for the matching event stream to go quiet and return ordered burst metadata
  before returning.
- `recursive`: search subdirectories too (useful if your download manager
  organizes into folders).
- `include_existing_changes`: when true (default), treat modified pre-existing
  files as candidates (helps overwrite-style producers). Set false to only
  consider *new paths*.
- `since_ns`: override the timestamp used for the existing-file modification
  heuristic. If omitted, VHK uses the run's start time. Set to `null` to
  disable the modification heuristic.

Example: wait for the newest non-temporary download to settle:

```yaml
- type: WaitForNewFile
  directory: ~/Downloads
  pattern: "*"
  exclude: ["*.part", "*.crdownload", "*.tmp"]
  min_size: 1
  stable_ms: 250
  timeout_ms: 60000
```


### `WaitForDownload`

`WaitForDownload` is a convenience step for the most common case: “a browser
download is happening somewhere under this directory; return when the final
filename appears and is stable.” It layers in default excludes for partial
downloads (e.g. `*.crdownload`, `*.part`, `*.download`) and defaults to
`min_size=1` and a small `stable_ms` window.

Example:

```yaml
- type: WaitForDownload
  directory: ~/Downloads
  pattern: "*.pdf"
  timeout_ms: 60000
```

## External triggers (bus)

Besides in-macro HTTP steps, VHK supports **external triggers** via the local
IPC bus (see `docs/BUS_EVENTS.md`). This makes it easy to integrate VHK with:

- window manager bindings (i3/sway/Hyprland)
- Stream Deck / Companion / Node-RED style controllers (via a thin helper)
- OSC controllers / mixers (via `vhk oscd`)
- DBus signals from KWin scripts (see `docs/KWIN.md`)
- Wayland GlobalShortcuts portal activations (see `docs/GLOBAL_SHORTCUTS_PORTAL.md`)


## HTTP control server

If you want a simple webhook-style trigger surface (Node-RED / Stream Deck / dashboards),
run `vhk httpd` and point your tool at its endpoints.

See: `docs/HTTP_CONTROL.md`.

## OSC control server

If you want a low-friction UDP trigger surface used by many controller tools,
run `vhk oscd`.

See: `docs/OSC_CONTROL.md`.


### `WaitForFileEvent`

Use `WaitForFileEvent` when the workflow cares about the **next matching event**
in a directory rather than proving the existence of one known path. It shares
`pattern`, `exclude`, `recursive`, `min_size`, `stable_ms`, and `quiet_ms`
knobs with the project-level file watcher lane and emits the same `file_*` vars
used by those watchers, including `file_batch_*` when burst coalescing is
enabled.
