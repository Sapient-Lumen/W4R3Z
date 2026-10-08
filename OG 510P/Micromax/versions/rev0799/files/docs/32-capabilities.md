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
set cap.fs-require true   (allow scripts to load/evaluate Micromax source files)
set cap.fs-chdir true    (allow scripts to change process cwd)
set cap.buffer-discard true   (allow scripts to force-discard dirty editor buffers)
set cap.history-clear true    (allow scripts to clear editor history/evidence registers)
set cap.undo-redo true        (allow scripts to replay trusted undo/redo history)
set cap.fs-root ./   (optional sandbox root)
```

Notes:

- `cap.clipboard-write` gates *system* clipboard exports triggered from script
  context for both `clipboard=terminal` (OSC 52) and `clipboard=external`
  (wl-copy/xclip/etc). Rev799 also uses it as the explicit override for
  script-origin writes to a trusted or other-origin internal clipboard register.
  Interactive copy/cut remains allowed.
- `cap.clipboard-read` gates *system* clipboard imports triggered from script
  context (via `ed.clipboard-import` or scripted Paste). Rev799 also uses it
  as the explicit override for script-origin reads of a trusted or other-origin
  internal clipboard register. Interactive Paste remains allowed.

Or at runtime:


```text
set cap.open-url true
toggle cap.shell
```

When you change a `cap.*` option from trusted user/config code or an interactive
command, the editor refreshes `host.features` so `host.feature?` reflects the
new state. Script-originated command/prompt/action-chain/deferred callbacks may
inspect options, but rev772/rev773 block them from mutating `cap.*` options;
otherwise a script could grant itself filesystem, shell, code-load, or clipboard
authority and immediately call back into a host API. Rev778 also makes several
capability-denied hostcalls fail before consuming their operation argument, so
denied script requests remain inspectable after the error.

Rev773 also extends `cap.fs-require` to the core VM loader words while they run
inside editor script context: `include`, `require`, `reload`, and `unrequire`
now share the editor's code-load capability and `cap.fs-root` policy instead of
using ambient VM filesystem access.

## Current capabilities

### `ed.open-url` (unsafe)

Opens an external URL via the host system browser.

- feature: `ed.open-url`
- option: `cap.open-url`

Used by the docs browser: following an external link will only open it when
this capability is enabled. Rev778 keeps the dispatch boundary narrow: only
`http`, `https`, and `mailto` URLs are handed to the host opener. Unsupported
schemes such as `file:` are refused before browser/desktop dispatch, even when
`cap.open-url` is enabled.

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

Rev799 also uses this option as the explicit override that lets script-origin
code overwrite a trusted or other-origin internal clipboard register. It does
not block interactive copy/cut.


### `ed.clipboard-import` (unsafe-ish)

Allows scripts/plugins to **read/import** the system clipboard via external
tools (when `clipboard=external`).

- feature: `ed.clipboard-import`
- option: `cap.clipboard-read`
- hostcall: `ed.clipboard-import` ( -- ok text err )

This does **not** affect interactive paste (Ctrl-v) for humans, but blocks
script-originated clipboard reads by default. Rev799 also applies the same
read capability to the internal clipboard register, so script-origin `ed.clipboard`,
`ed.clipboard-items`, and fallback Paste cannot read trusted or other-origin
clipboard rows without the override.

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


### `ed.chdir` (unsafe)

Changes the process current directory from script-originated command execution.

- feature: `ed.chdir`
- option: `cap.fs-chdir`
- command surface: scripted `cd PATH` via `ed.command`, `ed.run`, or prompt submission

When `cap.fs-root` is set, relative paths resolve under that root and the final
directory target is rechecked with the contained fd-backed access seam where the
host supports it.  Interactive users can still use `cd` normally.


### `ed.buffer-discard` (unsafe)

Allows script-originated forced commands to discard unsaved in-memory buffer
changes.

- feature: `ed.buffer-discard`
- option: `cap.buffer-discard`
- command surfaces: scripted `close!`, `closeall!`, `only!`, `quit!`, `revert!`

This is intentionally separate from filesystem write capabilities: a script can
lose user data by discarding dirty editor buffers even if it never writes to
disk.


### `ed.history-clear` (unsafe)

Allows script-originated code to clear protected editor history/evidence registers
that it does not own, including message-log rows, recent-file MRU rows, and
jumplist rows. Same-origin script rows remain clearable without this capability.

- feature: `ed.history-clear`
- option: `cap.history-clear`
- command/host surfaces: `ed.clear-messages`, `ed.pop-message`, `ed.recent-clear`, `ed.recent-clear-count`, `ed.clear-jumps`, `recent clear`

This is intentionally separate from filesystem, shell, clipboard, persistence,
and dirty-buffer discard authority. Clearing evidence can make automation harder
to diagnose even when it never touches the host filesystem.


### `ed.undo-redo` (unsafe)

Allows script-originated code to replay protected undo/redo history entries that
it does not own. Same-origin script edits remain undoable/redoable without this
capability.

- feature: `ed.undo-redo`
- option: `cap.undo-redo`
- command/action surfaces: scripted `undo`, `redo`, `Undo`, `Redo`

This is intentionally separate from history-clear and dirty-buffer discard
authority. Undo/redo entries are executable recovery state: replaying a trusted
entry can erase or reapply user edits long after the script that triggered it
has returned.


### `ed.persist` (unsafe)

Allows the editor to read/write its own small persistence files (recent-file MRU, prompt history, savecursor state).

- feature: `ed.persist`
- option: `cap.persist`

Optional sandbox root:

- option: `cap.persist-root` (default: `~/.config/micromax`)

Note: persistence features are still separately opt-in (e.g. `recent.persist`, `history.persist` / `savehistory`, `savecursor`).
This capability is an additional safety boundary so scripts/plugins can't
accidentally start writing to disk just by toggling those options. Rev772 moves
recent/history/savecursor reads and writes onto contained persistence I/O: reads
are byte-capped by `persist.maxbytes`, and writes use `persist.atomic` plus a
late `cap.persist-root` containment recheck before committing.



### `ed.require` / core loader words (unsafe)

Allows scripts to load and evaluate Micromax source from disk.

- feature: `ed.require`
- option: `cap.fs-require`
- hostcall: `ed.require` ( path -- )
- core words in editor script context: `include`, `require`, `reload`, `unrequire`

When `cap.fs-root` is set, relative code loads are resolved under the same
script filesystem root and final reads use the contained read seam.
