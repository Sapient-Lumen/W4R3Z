# Editor command bar and picker contract

Rev0955 keeps the compact contract and adds collision-safe untitled-buffer
creation. The complete chronology-heavy
pre-rev0953 body remains preserved at
`docs/history/55-editor-command-bar-through-rev0952.md`.

## Purpose

Micromax uses one prompt substrate for commands, search, file/buffer/help
pickers, completion, history, confirmations, and query-replace transitions. The
substrate should feel consistent without pretending every prompt has the same
authority or submit semantics.

The command bar is an explicit text command surface. A picker is a bounded set
of candidates. That distinction is part of trust:

- a command may intentionally parse an arbitrary path or argument;
- a picker may submit only a candidate in the interaction's captured inventory;
- typing into a picker filters or ranks; it does not silently become a command.

## Opening common prompts

- `Ctrl-E` — command bar.
- `Ctrl-O` — bounded project-file picker.
- `Ctrl-Space` — command/action palette.
- `Ctrl-B` — buffer picker.
- `Ctrl-F` — literal find prompt.
- `Ctrl-G` — help picker.
- `Alt-G` — binding picker.
- `Ctrl-R` — command bar prefilled with `replace `.
- `Alt-%` — command bar prefilled with `qreplace `.

The host owns these shipped bindings. A plugin-created binding or mode retains
its plugin authority when the key is pressed later.

## Prompt editing and navigation

While a prompt is active:

- printable input inserts at the prompt cursor;
- Left/Right, Home/End, Backspace/Delete edit the prompt;
- Up/Down move through visible suggestions, falling back to history when the
  prompt has no picker result to consume;
- PageUp/PageDown move by a suggestion page;
- Alt-Up/Alt-Down jump between visible sections;
- Ctrl-Home/Ctrl-End select the first/last suggestion;
- Tab completes/cycles forward; Shift-Tab cycles backward;
- Ctrl-Y copies the selected prompt row when that interaction supports it;
- Enter submits; Esc closes or cancels the active interaction.

Suggestion selection is stable only for the current `suggest_base`. Editing the
query refreshes rows and resets selection through the shared prompt-refresh
helpers.

## Prompt state

`src/micromax_editor/commandbar.py:Prompt` owns text editing, cursor position,
history position, suggestion rows, selected index, paging, and lightweight
interaction metadata. Product-specific candidate construction and effects stay
with the relevant editor owner/coordinator.

Picker interactions may capture immutable input state. The project-file picker
uses:

- `picker_root` — the resolved root whose relative paths are meaningful;
- `picker_items` — the captured candidate paths;
- `picker_meta` — bounded scan counts/truncation facts.

Prompt lifecycle snapshots deep-copy these fields. Reload/rollback must not
retain aliases to a live inventory list or metadata dictionary.

## Command bar

The `command` prompt submits through the command dispatcher. Commands are
registered centrally and have explicit argument grammars. Examples:

```text
open path/to/file.txt
filepick src
new
new "project notes"
save
write path/to/new-name.txt
bufferpick
find needle
replace old new
qreplace old new
help topic
showoption filepicker.hidden
set filepicker.hidden true
```

`open PATH` is the deliberate raw-path route. It remains available even though
Ctrl-O now opens a project picker. This separation keeps keyboard flow fast
without hiding arbitrary filesystem authority behind fuzzy matching.

`new [NAME]` is the deliberate untitled-buffer route. It accepts at most one
parsed name, never replaces a live buffer, and chooses `*scratch-2*` or
`name<2>` when the preferred label is occupied. The matching `NewBuffer` action
is palette/binding vocabulary but has no shipped default key. Script context is
denied until retained buffer creation has a finite capability/lifecycle
contract.

Command completion may expose commands, actions, known options, recent files,
paths, docs, plugins, marks, macros, and other registered inventories. Each
provider must apply its own scan/input/result budgets before rows reach the
shared VM result boundary.

## Project-file picker

`Ctrl-O` and `filepick [QUERY]` invoke the same headless path:

1. select the nearest project marker root, active-buffer parent, cwd, or script
   `cap.fs-root`;
2. build one bounded deterministic snapshot;
3. install relative paths and scan metadata in the prompt;
4. filter/rank that list in memory as the query changes;
5. submit only a snapshot member;
6. re-resolve and re-stat it before opening.

An empty query groups root files first and nested paths by top-level directory.
A non-empty query uses the shared picker ranking and shows a `Matches` section.
Rows carry `[relative path, projectfile, status, parent]`, where status is
`file`, `open`, or `modified` according to currently readable buffers.

The picker does not accept an unmatched typed path. Use `open PATH` for that.
Files created after the snapshot are absent until the picker is reopened. Files
deleted or changed into symlinks/directories after the scan are rejected at
submit with a visible message.

Default scan budgets are 4096 files, 2048 directories, depth 32, 32768 observed
entries, 1 MiB of relative-path text, and one second. A truncated coherent
snapshot remains usable and reports the terminal budget. A timeout or scan error
opens no prompt.

## Other picker families

- `buffer` submits a visible buffer row, not arbitrary text.
- `recent` and `recentdir` submit only remembered recent targets; no raw-open
  fallback is granted.
- `palette` searches commands/actions plus bounded contextual rows.
- `topic`, `doc`, `helplink`, `helpoutline`, and `helpnav` navigate help models.
- `binding`, `mark`, `jump`, and `plugin` expose corresponding inventories.

Each family owns its row schema, section labels, submit effect, and authority.
Shared UI behavior does not erase those distinctions.

## Find and replace

The `find` prompt updates incremental search when `incsearch` is enabled. Literal
and regex paths remain explicit; risky regex work must stay inside its bounded
worker contract.

`replace` is a command with explicit source/replacement arguments. `qreplace`
enters a confirmation mode whose host-owned keys are:

- `y` or Enter — replace this match;
- `n` — skip;
- `a` — replace all remaining;
- `l` — replace this match and stop;
- `q` or Esc — quit.

Query-replace state is an interaction with its own rollback/failure behavior,
not merely a text prompt. Preserve selection/cursor truth and visible counts.

## Destructive repeat confirmation and headless exit

`quit`, `close [NAME]`, `closeall`, and `only` warn before discarding dirty
buffers. The warning is evidence about one exact operation scope, not a sticky
permission bit:

- the first request captures live target identity, mutation version, dirty bit,
  path, and any retained `only` buffer identity;
- an unchanged second request confirms;
- an edit, open, rename, target/context change, or same-name object replacement
  refreshes the warning and requires another request;
- an unrelated command clears the pending witness;
- `quit!`, `close!`, `closeall!`, `only!`, and the corresponding `-f` forms are
  explicit one-shot force choices.

Prompt previews show `armed` only while the current state still matches the
witness. They must never display a stale remembered boolean.

The headless REPL uses `:q` for normal policy and `:q!` for explicit force. EOF
also attempts normal quit, but never counts as the second confirmation. Dirty
terminal EOF clears the witness and returns to the prompt; dirty exhausted
non-interactive input reports the refusal and exits with status 2. Clean or
successfully autosaved EOF exits normally.

## History and persistence

Prompt history is partitioned by prompt kind and carries authority/provenance for
plugin cleanup and read policy. Persisting history is a host option/capability,
not automatic ambient storage. Plugin unload/reload removes or restores rows by
origin/generation through the existing lifecycle transaction.

History navigation must not reveal a lower-authority row to a script that cannot
read it. A physical keypress does not elevate the prompt's captured origin.

## Failure behavior

A prompt failure should answer three questions in one short message:

1. which interaction failed;
2. whether no candidate matched, a capability denied the effect, or host work
   failed/timed out;
3. what stable state remains.

Examples include `filepick: 0 project file(s)`, `disabled for scripts
(cap.fs-open)`, `file disappeared since scan`, and explicit bounded-snapshot
notices. Do not collapse these into generic `(none)` or silently fall back to a
more powerful operation.

## Extension rules

When adding a new prompt or picker:

1. define its authority at creation and submission;
2. define a finite candidate/traversal budget before VM result materialization;
3. choose snapshot versus live inventory deliberately;
4. specify row shape, ranking, sectioning, and zero-match language;
5. preserve captured state in prompt snapshot/restore;
6. reject raw fallback unless arbitrary input is the explicit command contract;
7. test keyboard navigation, exact submit, stale candidate, denial, and failure;
8. add it to shared maps only after those semantics exist.

Do not create a second prompt framework for visual convenience. Do not force a
new effect through a generic picker submitter if its revalidation or authority is
different.

## Test and audit anchors

Primary implementation anchors:

- `src/micromax_editor/commandbar.py`
- `src/micromax_editor/editor.py`
- `src/micromax_editor/prompt_refresh.py`
- `src/micromax_editor/prompt_suggestions.py`
- `src/micromax_editor/command_dispatcher.py`
- `src/micromax_editor/project_files.py`
- `src/micromax_editor/discard_guard.py`
- `src/micromax_editor/startup.py`
- `src/micromax_editor/__main__.py`
- `src/micromax_editor/default_keybindings.py`

Primary current startup/discard evidence is
`tests/test_editor_startup_discard_trust.py`; project-picker evidence is
`tests/test_editor_project_file_picker.py`. Cross-cutting prompt, history,
authority, navigation, completion, and query-replace behavior remains distributed
across the focused `tests/test_editor_prompt_*`, command-bar, keymap, capability,
and lifecycle suites. `tools/mxaudit.py` pins the release-visible owner, finite
budgets, prompt snapshot fields, queue-drain policy, startup/discard ownership,
headless exit policy, capability checks, commands, actions, options, and the
default-key mirror.
