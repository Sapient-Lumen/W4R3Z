# Capabilities (host-owned world)

Micromax’s VM is intentionally tiny and portable. The editor (and any other
embedded host) **owns the outside world**.

That means:

- scripts/plugins should be safe by default
- anything “unsafe” is explicitly **capability-gated**
- scripts can probe availability via `host.feature?`

The editor exposes a small registry via `host.capabilities`:

```text
( -- rows )  "host.capabilities" hostcall
rows = [ [feature option kind enabled doc] ... ]
```

## Enabling capabilities

Capabilities are controlled by editor options (best-effort, host-specific).

In `~/.config/micromax/init.mx`:

```text
set cap.open-url true
set cap.shell true

set cap.clipboard-write true   (allow scripts to export clipboard via terminal/external backends)
set cap.clipboard-read true    (allow scripts to import clipboard via external tools)

set cap.persist true
set cap.persist-root ~/.config/micromax   (optional sandbox for persistence files)

set cap.fs-open true
set cap.fs-save true
set cap.fs-read true
set cap.fs-list true
set cap.fs-stat true
set cap.fs-root ./   (optional sandbox root)
```

Notes:

- `cap.clipboard-write` gates *system* clipboard exports triggered from script
  context for both `clipboard=terminal` (OSC 52) and `clipboard=external`
  (wl-copy/xclip/etc). Interactive copy/cut remains allowed.
- `cap.clipboard-read` gates *system* clipboard imports triggered from script
  context (via `ed.clipboard-import` or scripted Paste). Interactive Paste
  remains allowed.

Or at runtime:


```text
set cap.open-url true
toggle cap.shell
```

When you change a `cap.*` option, the editor refreshes `host.features` so
`host.feature?` reflects the new state.

## Current capabilities

### `ed.open-url` (unsafe)

Opens an external URL via the host system browser.

- feature: `ed.open-url`
- option: `cap.open-url`

Used by the docs browser: following an external link will only open it when
this capability is enabled.

### `ed.shell` (unsafe)

Runs a shell command and captures stdout/stderr.

- feature: `ed.shell`
- option: `cap.shell`

This is intentionally minimal (synchronous, short timeout). Hosts that want a
real job system should provide a different surface.


### `ed.clipboard-export` (unsafe-ish)

Allows **script-originated** clipboard changes to be exported to the *system*
clipboard when a privileged backend is in use (e.g. terminal OSC 52).

- feature: `ed.clipboard-export`
- option: `cap.clipboard-write`

This does **not** affect the internal clipboard, and does not block
interactive copy/cut.


### `ed.clipboard-import` (unsafe-ish)

Allows scripts/plugins to **read/import** the system clipboard via external
tools (when `clipboard=external`).

- feature: `ed.clipboard-import`
- option: `cap.clipboard-read`
- hostcall: `ed.clipboard-import` ( -- ok text err )

This does **not** affect interactive paste (Ctrl-v) for humans, but blocks
script-originated clipboard reads by default.

### `ed.open` (unsafe)

Opens a file from disk into a buffer.

- feature: `ed.open`
- option: `cap.fs-open`

Why this is capability-gated: combined with `ed.text`, it provides ambient
filesystem read access to scripts.

When `cap.fs-root` is set, relative paths resolve under it and targets outside
it are denied.


Note: this gate is enforced for **script-originated** requests (hostcalls and scripted
command execution via `ed.command` / `ed.prompt-submit`, including palette-driven opens
via `ed.command-palette` + `ed.prompt-submit`). Interactive users can still
use `:open` normally.


### `ed.save` (unsafe)

Saves the current buffer to disk.

- feature: `ed.save`
- option: `cap.fs-save`

When `cap.fs-root` is set, the save target must remain within it.


Note: this gate is enforced for **script-originated** requests (hostcalls and scripted
command execution via `ed.command` / `ed.prompt-submit`). Interactive users can still
use `:save` normally.


### `ed.fs-read` (unsafe)

Reads an arbitrary file from disk as UTF-8 text.

- feature: `ed.fs-read`
- option: `cap.fs-read`

This is intentionally constrained:

- disabled by default
- best-effort size limit (currently ~1MB) to avoid accidental huge reads
- optional sandbox root via `cap.fs-root` (relative paths resolve under it; outside paths are denied)


### `ed.fs-list` (unsafe)

Lists directory entries from disk.

- feature: `ed.fs-list`
- option: `cap.fs-list`

This is intentionally constrained:

- disabled by default
- best-effort entry limit (currently 500)
- optional sandbox root via `cap.fs-root` (relative paths resolve under it; outside paths are denied)
- returns portable rows as `[[name kind path] ...]` where `kind` is `dir`|`file`|`other`


### `ed.fs-stat` (unsafe)

Stats a path on disk and returns a small portable map (exists/kind/size/mtime).

- feature: `ed.fs-stat`
- option: `cap.fs-stat`

This is intentionally constrained:

- disabled by default
- optional sandbox root via `cap.fs-root` (relative paths resolve under it; outside paths are denied)
- designed as a *read-only* helper for building pickers and safe workflows


### `ed.persist` (unsafe)

Allows the editor to read/write its own small persistence files (recent-file MRU, prompt history, savecursor state).

- feature: `ed.persist`
- option: `cap.persist`

Optional sandbox root:

- option: `cap.persist-root` (default: `~/.config/micromax`)

Note: persistence features are still separately opt-in (e.g. `recent.persist`, `history.persist` / `savehistory`, `savecursor`).
This capability is an additional safety boundary so scripts/plugins can't
accidentally start writing to disk just by toggling those options.

