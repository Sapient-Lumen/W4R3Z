Rev0961 note: restricted plugin package authority is content-bound. Explicit approval captures immutable package bytes; package-local lifecycle and deferred source reads use that snapshot, while ordinary script filesystem loads still require `cap.fs-require`.

Rev0953 note: a script-owned project-file picker separates enumeration (`cap.fs-list`) from delayed opening (`cap.fs-open`) and obeys `cap.fs-root`.

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

## Project-file picker authority

The shipped `FilePicker` action is ordinary host-owned interactive editor behavior.
A trusted user pressing Ctrl-O does not need script filesystem capabilities.

When a plugin/script creates the interaction, authority remains attached to the
prompt across later physical navigation:

- `cap.fs-list` is required to enumerate and create the snapshot;
- `cap.fs-root`, when configured, is the inventory and containment root;
- `cap.fs-open` is checked again when the selected snapshot member is submitted;
- a later physical Enter does not promote plugin authority;
- unmatched typed text never falls back to arbitrary path opening.

The scan itself has finite host-owned file/directory/depth/entry/path-byte/time
limits. The selected path is re-resolved, containment-checked, symlink-checked,
and stat-checked before open. See
`docs/911-bounded-project-file-picker.md`.

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
set cap.buffer-read true      (allow scripts to inspect trusted/other-origin inactive buffer metadata)
set cap.buffer-switch true    (allow scripts to switch into trusted/other-origin inactive buffers)
set cap.history-clear true    (allow scripts to clear editor history/evidence registers)
set cap.undo-redo true        (allow scripts to replay trusted undo/redo history)
set cap.cursor-restore true   (allow scripts to replay trusted/persisted savecursor landings)
set cap.macro-read true       (allow scripts to inspect trusted/other-origin macros)
set cap.macro-play true       (allow scripts to replay trusted/other-origin macros under script authority)
set cap.mark-read true        (allow scripts to inspect trusted/other-origin named marks)
set cap.mark-jump true        (allow scripts to jump to trusted/other-origin named marks)
set cap.search-read true      (allow scripts to inspect trusted/other-origin active search state)
set cap.search-replay true    (allow scripts to replay or replace trusted/other-origin active search state)
set cap.message-read true      (allow scripts to inspect trusted/other-origin message-log rows)
set cap.prompt-read true       (allow scripts to inspect trusted/other-origin active prompt state)
set cap.prompt-write true      (allow scripts to submit trusted/other-origin active prompts)
set cap.option-read true       (allow scripts to inspect protected option values)
set cap.command-read true      (allow scripts to inspect trusted/other-origin command metadata)
set cap.action-read true       (allow scripts to inspect dynamic trusted action metadata/source)
set cap.action-run true        (allow scripts to directly run dynamic trusted actions under script authority)
set cap.word-read true         (allow scripts to inspect trusted/other-origin VM word metadata/source)
set cap.plugin-read true       (allow scripts to inspect protected plugin metadata and load errors)
set cap.hook-read true         (allow scripts to inspect protected hook handlers and source spans)
set cap.hook-fire true         (allow scripts to explicitly fire protected hook handlers under script authority)
set cap.timer-fire true        (allow scripts to explicitly pump protected timers under script authority)
set cap.keybinding-read true   (allow scripts to inspect trusted/other-origin keybinding specs)
set cap.keybinding-press true  (allow scripts to synthesize protected keybinding replay under script authority)
set cap.recent-read true       (allow scripts to inspect trusted/persisted recent-file paths)
set cap.fs-root ./   (optional sandbox root)
```

Notes:

- Full CLI/TUI startup installs the shipped keymap as trusted host policy before
  any plugin source is evaluated. Physical default Ctrl-O, Ctrl-S, Ctrl-Z,
  clipboard, buffer-picker, and palette actions are therefore ordinary
  interactive editor behavior and do not require the matching script
  capabilities.
- `plugins/core/init.mx` is an exact readable mirror of those public defaults.
  Its lower-authority repeats are idempotent no-ops; a third-party binding still
  captures plugin authority, and pressing it does not grant the plugin ambient
  user authority. Trusted user init or interactive commands can intentionally
  rebind defaults after plugin loading.
- A bare embedded `Editor()` keeps only the small internal modal bootstrap. Hosts
  that want the full interactive product map call
  `Editor.install_default_keybindings()` before loading plugins.
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
new state. Script-originated command/prompt/action-chain/deferred callbacks
cannot mutate `cap.*` options (rev772/rev773), and rev810 also redacts direct
reads of capability values plus host-adjacent option values unless
`cap.option-read` is enabled. Scripts should probe available capabilities with
`host.feature?` / `host.capabilities` instead of scraping raw configured roots
or command strings. Rev778 also makes several capability-denied hostcalls fail
before consuming their operation argument, so denied script requests remain
inspectable after the error.

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


Note: this gate is enforced for **script-originated** requests (hostcalls and
scripted command execution via `ed.command` / `ed.prompt-submit`, including
palette-driven opens via `ed.command-palette` + `ed.prompt-submit`). Interactive
users can still use `:open` or the host-owned Ctrl-O prompt normally. A
plugin-created keybinding remains script-originated even when a user presses it.


### `ed.save` (unsafe)

Saves the current buffer to disk.

- feature: `ed.save`
- option: `cap.fs-save`

When `cap.fs-root` is set, the save target must remain within it.


Note: this gate is enforced for **script-originated** requests (hostcalls and
scripted command execution via `ed.command` / `ed.prompt-submit`). Interactive
users can still use `:save` or the host-owned Ctrl-S binding normally. A
plugin-created save binding remains capability-scoped.


### `ed.fs-read` (unsafe)

Reads an arbitrary file from disk as UTF-8 text.

- feature: `ed.fs-read`
- option: `cap.fs-read`

This is intentionally constrained:

- disabled by default
- VM-tunable pre-read byte limit (default ~1MB) to avoid accidental huge reads before byte loading
- final fd-bound read check repeats the size, kind, and containment validation so late file growth or swaps fail closed
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
changes and to close protected inactive clean buffers that belong to trusted/user
or other script origins.

- feature: `ed.buffer-discard`
- option: `cap.buffer-discard`
- command surfaces: scripted `close NAME`, `close!`, `closeall!`, `only!`, `quit!`, `revert!`

This is intentionally separate from filesystem write capabilities: a script can
lose user data by discarding dirty editor buffers or erasing open-buffer session
state even if it never writes to disk.


### `ed.buffer-read` (unsafe)

Open-buffer rows are live session metadata: names, paths, dirty/protected state,
positions, picker rows, and line counts. Script-origin callers can read the
active buffer they were invoked on and same-origin buffers they created, but
trusted/user or other-origin inactive buffers are hidden by default.

- feature: `ed.buffer-read`
- option: `cap.buffer-read`
- host/UI surfaces: `ed.buffers`, buffer inventory/detail/section rows, `buffers`, `showbuffer`, `bufferpick`, and buffer-picker completion rows

`cap.buffer-read` does not grant navigation replay. A script that can inspect a
protected inactive buffer still needs `cap.buffer-switch` to switch into it.


### `ed.buffer-switch` (unsafe)

Allows script-originated code to switch into trusted/user or other-origin
inactive buffers. Same-origin script-created buffers and the active ambient
buffer do not need this override.

- feature: `ed.buffer-switch`
- option: `cap.buffer-switch`
- host/command surfaces: `ed.set-active-buffer`, `ed.with-buffer`, scripted `buffer NAME`, scripted `prevbuf`, and buffer-picker submit

`cap.buffer-switch` is intentionally separate from `cap.buffer-read`: switching
turns the target into the active/ambient buffer, but it does not reveal unrelated
inactive protected buffers.


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


### `ed.cursor-restore` (unsafe)

Allows script-origin code to replay trusted/user or persisted `savecursor` rows.

- feature: `ed.cursor-restore`
- option: `cap.cursor-restore`
- command/action surfaces: scripted file opens that would otherwise restore a saved cursor

Rev801 treats saved-cursor rows as delayed navigation state. Scripts may replay
their own same-origin rows by default, but not trusted/user rows, rows restored
from persistence, or rows owned by another script. This capability is a replay
override only: it does not let scripts overwrite protected saved-cursor rows as
an incidental side effect of switching or closing buffers.

### `ed.macro-read` / `ed.macro-play` (unsafe)

Saved macros are delayed executable editor state. Script-origin code can create,
inspect, and replay its own same-origin macro slots, but trusted/user macro slots
and slots created by another script or plugin generation are protected by
default.

- feature: `ed.macro-read`
- option: `cap.macro-read`
- host/command surfaces: `ed.macro-get`, `ed.macro-names`, `ed.macro-inventory-rows`, `ed.macro-detail-row`, `showmacro`, `macro list`, `macro status`

- feature: `ed.macro-play`
- option: `cap.macro-play`
- host/command surfaces: script-origin `ed.macro-play` and scripted `macro play`

`cap.macro-play` permits the script to trigger replay of a protected slot, but
it does not make the replay trusted: steps still run inside script authority, so
`cap.*` self-escalation remains blocked.


### `ed.mark-read` / `ed.mark-jump` (unsafe)

Named marks are delayed navigation and evidence state. Script-origin code can
create, inspect, and jump to marks it owns, but trusted/user marks and marks
created by another script or plugin generation are protected by default.

- feature: `ed.mark-read`
- option: `cap.mark-read`
- host/command surfaces: `ed.marks`, `ed.mark-inventory-rows`, `ed.mark-detail-row`, `ed.mark-section-rows`, `ed.mark-section-summary-rows`, `marks`, `showmark`, `showmarkgroups`, mark-pickers/completion rows

- feature: `ed.mark-jump`
- option: `cap.mark-jump`
- host/command surfaces: script-origin `ed.mark-jump`, scripted `markjump`, and scripted mark-pickers

`cap.mark-jump` allows the navigation replay, but it does not imply
`cap.mark-read`; a script can be granted the ability to jump to a protected mark
without also inventorying names, buffers, positions, and line previews.


### `ed.search-read` / `ed.search-replay` (unsafe)

The active search query is a small but sensitive register: it appears in status
and search-row models, drives highlighting, and powers later `findnext` /
`findprev` navigation. Script-origin code can use an active search it created
itself, but trusted/user searches and searches created by another script or
plugin generation are protected by default.

- feature: `ed.search-read`
- option: `cap.search-read`
- host/UI surfaces: `ed.status`, `ed.statusline-model`, `ed.search-rows`, search-position summaries, and search-highlight row models

- feature: `ed.search-replay`
- option: `cap.search-replay`
- host/command surfaces: script-origin `ed.find`, `ed.find-next`, `ed.find-prev`, `findnext`, `findprev`, and search-mode changes that would replace or retag a protected active search

`cap.search-read` does not grant navigation replay, and `cap.search-replay` does
not reveal another authority's query through status/search-row models. Denied
`ed.find` calls preflight before consuming the query operand.


### `ed.message-read` (unsafe)

Message rows are recovery and audit evidence. Script-origin code can emit and
read rows it owns, but trusted/user messages and messages from another script or
plugin generation are hidden by default.

- feature: `ed.message-read`
- option: `cap.message-read`
- host/UI surfaces: `ed.messages`, `ed.last-message`, `ed.capture-messages`, and statusline `last_message`

`cap.message-read` is intentionally separate from `cap.history-clear`: it grants
inspection only, not destructive pop/clear authority.


### `ed.prompt-read` / `ed.prompt-write` (unsafe)

The active prompt is delayed interaction state. It may contain command text, a
search query, path fragments, completion rows, or picker previews. Script-origin
code can read and answer prompts it created itself, but trusted/user prompts and
prompts created by another script/plugin generation are protected by default.

- feature: `ed.prompt-read`
- option: `cap.prompt-read`
- host/UI surfaces: `ed.prompt-text`, `ed.prompt-kind`, prompt suggestion/current-row/window/display/panel hostcalls, status prompt fields, and the shared interaction model

- feature: `ed.prompt-write`
- option: `cap.prompt-write`
- host/command surfaces: direct script-origin `ed.prompt-submit` for protected prompts

`cap.prompt-read` does not grant submit authority. `cap.prompt-write` lets a
script submit a protected prompt under script authority; it does not make the
submitted command trusted, so `cap.*` self-escalation remains blocked by the
ordinary script option policy.


### `ed.recent-read` (unsafe)

Recent-file rows are host path history and recovery/navigation evidence. Script-origin code can read rows it created itself, but trusted/user, persisted, and other-origin rows are hidden by default.

- feature: `ed.recent-read`
- option: `cap.recent-read`
- host/UI surfaces: `ed.recent`, recent inventory/detail/section/prompt rows, command-palette Recent Files rows, and recent-sourced path completion candidates

`cap.recent-read` is intentionally separate from `cap.history-clear`: it grants path-history inspection only, not destructive MRU clearing authority.


### `ed.option-read` (unsafe)

Allows scripts to inspect protected option values, including capability bits,
capability roots, external-command configuration, persistence file paths, URL
confirmation policy, and save-safety knobs. Without this capability, option
rows keep names/docs discoverable but redact protected values, and `ed.opt-get`
refuses protected reads before consuming the option name.

- feature: `ed.option-read`
- option: `cap.option-read`

### `ed.command-read` (unsafe)

Allows scripts to inspect dynamic trusted/user or other-origin command names,
docs, groups, and source spans. Without this capability, command registry
hostcalls, `showcmd`, command-palette rows, and command completion expose only
built-in core commands plus same-origin script/plugin commands while running in
script context.

- feature: `ed.command-read`
- option: `cap.command-read`

### `ed.action-read` (unsafe)

Allows scripts to inspect dynamic trusted/user action names, docs, and Python
source spans. Built-in core actions remain public editor vocabulary. Without
this capability, script-origin action inventory/detail, `showaction`,
command-palette action rows, help/topic action rows, and action-spec completion
show only built-in core actions.

- feature: `ed.action-read`
- option: `cap.action-read`

### `ed.action-run` (unsafe)

Allows scripts to directly run dynamic trusted/user Python actions. Built-in core
actions remain runnable under script authority for compatibility. This capability
does not make the caller trusted; editor-side script capability and option guards
remain active while the action callback runs.

- feature: `ed.action-run`
- option: `cap.action-run`

### `ed.word-read` (unsafe)

Allows scripts to inspect dynamic trusted/user or other-origin Micromax word
metadata, source spans, and source text. Without this capability, `showword`,
`ed.word-detail-row`, word rows in help/topic discovery, and word-name
completion expose only built-in/core words plus same-origin dynamic definitions
while running in script context.

- feature: `ed.word-read`
- option: `cap.word-read`

### `ed.plugin-read` (unsafe)

Allows scripts to inspect trusted/user, other-plugin, candidate-only, or broken
plugin metadata, dependency state, and load errors. Without this capability,
script-origin plugin inventory/detail/section rows, `plugin.list`,
`plugin.errors`, `showplugin`, plugin picker rows, and plugin-name completion
show only the currently executing loaded plugin's own row. Denied exact
`ed.plugin-detail-row` calls keep the plugin-name operand on the VM stack.

- feature: `ed.plugin-read`
- option: `cap.plugin-read`

### `ed.hook-read` (unsafe)

Allows scripts to inspect trusted/user or other-origin hook-handler names,
groups, and source spans. Hook event names remain public so command-prompt and
`hooks` discovery can still show the available event API, but protected handler
rows are hidden from `ed.hook-*`, `showhook`, `showhooks`, `hook-rows`,
`hook-detail`, and `hook-groups` unless this capability is enabled.

- feature: `ed.hook-read`
- option: `cap.hook-read`

### `ed.hook-fire` (unsafe)

Allows scripts to explicitly fire trusted/user or other-origin hook handlers.
Without this capability, script-origin execution of a hook word runs only
same-origin script/plugin handlers. With the capability enabled, protected
handlers are still executed under the caller's script authority or the handler's
captured script/plugin callback context; the capability does not make the caller
trusted. `hook@` is also governed by this fire policy because it returns
executable handler tokens.

- feature: `ed.hook-fire`
- option: `cap.hook-fire`

### `ed.timer-fire` (unsafe)

Allows scripts to explicitly pump trusted/user or other-origin due timer callbacks
through `ed.pump-timers`. Without this capability, script-origin timer pumping
runs only same-origin script/plugin timers and leaves protected due timers
pending. With the capability enabled, protected timers may be triggered, but
callback execution still uses captured script/plugin authority where applicable;
the capability does not make the script trusted. Script-origin timer pumping does
not run editor autosave maintenance.

- feature: `ed.timer-fire`
- option: `cap.timer-fire`

### `ed.keybinding-read` (unsafe)

Allows scripts to inspect trusted/user or other-origin keybinding action specs,
groups, descriptions, and source spans. Without this capability, script-origin
binding inventories, binding prompts, `showkey`/`showbindings`/`whichkey`, and
`ed.resolve-key` expose only same-origin bindings. Denied exact hostcalls keep
the key operand on the VM stack.

- feature: `ed.keybinding-read`
- option: `cap.keybinding-read`

### `ed.keybinding-press` (unsafe)

Allows scripts to synthesize replay of trusted/user or other-origin keybindings
through `ed.press-key`. Without this capability, `ed.press-key` can trigger only
same-origin script/plugin bindings. With the capability enabled, the target
binding's action spec is still executed under the caller's script authority; it
does not borrow the target binding's trusted authority.

- feature: `ed.keybinding-press`
- option: `cap.keybinding-press`

### `ed.persist` (unsafe)

Allows the editor to read/write its own small persistence files (recent-file MRU, prompt history, savecursor state).

- feature: `ed.persist`
- option: `cap.persist`

Optional sandbox root:

- option: `cap.persist-root` (default: `~/.config/micromax`)

Note: persistence features are still separately opt-in (e.g. `recent.persist`, `history.persist` / `savehistory`, `savecursor`, `plugin.cleanup-log.persist`).
This capability is an additional safety boundary so scripts/plugins can't
accidentally start writing to disk just by toggling those options. Rev772 moves
recent/history/savecursor reads and writes onto contained persistence I/O: reads
are byte-capped by `persist.maxbytes`, and writes use `persist.atomic` plus a
late `cap.persist-root` containment recheck before committing. Rev801 also
stamps persisted savecursor rows as lower-authority state so `cap.persist` does
not double as permission for scripts to replay the user's old cursor landings.



### `ed.require` / core loader words (unsafe)

Allows scripts to load and evaluate Micromax source from disk.

- feature: `ed.require`
- option: `cap.fs-require`
- hostcall: `ed.require` ( path -- )
- core words in editor script context: `include`, `require`, `reload`, `unrequire`

When `cap.fs-root` is set, relative code loads are resolved under the same
script filesystem root and final reads use the contained read seam. Editor-owned
VMs also apply executable source-load budgets: rev0905 added per-file source byte
and nested eval-step budgets, and rev0906 added dependency-graph depth and
cumulative-byte budgets shared by `ed.require` and nested core loader words.

## rev0819 keymode-read

`cap.keymode-read` / `ed.keymode-read` allows scripts to inspect trusted/user or other-origin active and known keymode names/state. It is intentionally narrower than `cap.keybinding-read`: enabling keymode reads reveals modal state, but protected key/action specs, descriptions, groups, and source spans remain behind the keybinding-read policy.
