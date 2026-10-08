# Bounded project-file picker and filesystem-worker audit

Rev0953 adds a first-class project-file picker and extracts project-root/file
inventory policy from the editor coordinator. This is a flow feature designed
under trust constraints, not a fuzzy prompt wrapped around recursive `glob`.

## Product diagnosis

Micromax had many sophisticated inspection and picker surfaces, but its primary
open-file gesture still asked for a path. Recent-file rows helped only after the
user had already visited a file. That is backwards for a serious project editor:
filename movement is a primary loop, not an advanced command.

The tempting implementation—walk the tree while the user types—would have
created new trust and waste problems:

- unbounded or repeated filesystem traversal;
- UI stalls on remote, cyclic, huge, or hostile trees;
- symlink escape and time-of-check/time-of-use ambiguity;
- plugin-created prompts borrowing later user authority;
- duplicated root discovery and process teardown inside the 29k-line `Editor`;
- another chronology-heavy feature contract future agents must excavate.

The chosen unit is one coherent snapshot per picker open.

## User contract

- `Ctrl-O` opens the project-file picker.
- `filepick [QUERY]` opens the same picker through the command dispatcher.
- Typing fuzzy-filters the captured relative paths.
- Empty browse mode groups root files and top-level directories; query mode uses
  a single `Matches` section.
- Enter opens the selected row only after revalidation.
- Esc closes the picker.
- `Ctrl-E`, then `open PATH`, remains the explicit arbitrary-path path.

Raw text that does not resolve to a captured candidate is a zero-match, not a
fallback open. This prevents a low-friction picker from becoming an accidental
filesystem command surface.

## Root policy

For trusted interactive use, root selection is:

1. nearest ancestor containing `.git`, `.hg`, `.svn`, `pyproject.toml`,
   `package.json`, or `Cargo.toml`;
2. otherwise the active buffer's directory;
3. otherwise the current working directory.

The nearest-marker walk is bounded to eight candidate levels and marker probes
are batched. Results live in a 2-second, size-bounded cache because recent-file
sectioning also asks the same question.

For a script-owned picker, configured `cap.fs-root` wins and is also passed as
the containment root. Without a configured root, the existing capability model
allows the host's normal active-buffer/cwd policy; `cap.fs-list` remains the
explicit grant to enumerate.

Root discovery moved into `ProjectRootLocator` in
`src/micromax_editor/project_files.py`. Compatibility methods in `Editor`
delegate to it so recent-file grouping does not gain a second source of truth.

## Snapshot policy

`scan_project_files()` returns an immutable `ProjectFileScan`:

```text
root
files
files/directories/entries/path-bytes observed
truncated + reason
timed_out
error
```

Public file paths are root-relative POSIX strings, sorted case-insensitively with
a stable original-text tie break. That makes rows deterministic across the
fd-relative POSIX walk and the portable path fallback.

One successful scan is installed in `Prompt.picker_root`,
`Prompt.picker_items`, and `Prompt.picker_meta`. Query edits rank this list in
memory and never touch the filesystem. Reopening is the refresh operation.
Prompt transaction snapshots deep-copy all three fields.

A timeout or scan error installs no picker. A coherent truncated snapshot is
usable and reports which terminal budget ended traversal.

## Resource limits

Default host-owned limits for one snapshot:

| Resource | Default |
| --- | ---: |
| files retained | 4096 |
| directories entered | 2048 |
| descendant depth | 32 |
| directory entries observed | 32768 |
| UTF-8 bytes of observed relative paths | 1,048,576 |
| worker wall time | 1.0 second |

The VM stores these as embedding dials, but malformed, nonpositive, NaN, and
infinite project-picker values fall back to finite defaults. Direct scanner use
also normalizes nonfinite timeout values. A zero direct timeout is retained as a
test/embedder seam for synchronous traversal; the editor-facing effective value
is always positive.

Entry and path-byte accounting occurs before ignore filtering. A directory full
of ignored names therefore still consumes finite observation work instead of
becoming a budget bypass.

Depth exhaustion is advisory: it skips that descendant but continues useful
siblings. File, directory, entry, and path-byte exhaustion is terminal. The
audit found and corrected a subtle state bug where an earlier `depth` reason
could prevent a later hard cap from stopping sibling traversal. `_ScanState`
now tracks `hard_exhausted` independently and promotes the visible reason when a
terminal boundary actually ends the snapshot.

## Ignore and symlink policy

Hidden names are excluded by default. `set filepicker.hidden true` reveals
ordinary dotfiles, but not VCS administrative names or known generated/cache/
dependency directories:

```text
.git .hg .svn .cache .mypy_cache .nox .pytest_cache .ruff_cache
.tox .venv __pycache__ build dist node_modules target venv
```

The policy is intentionally small and deterministic. Rev0953 does not parse
`.gitignore`, global ignore files, nested negations, or tool-specific ignore
formats. Those semantics may be valuable later, but only with explicit parse,
file-count, byte, recursion, and failure contracts.

On POSIX, traversal prefers directory file descriptors, `scandir(fd)`, and
`openat`-style child opens with `O_DIRECTORY`, `O_CLOEXEC`, and `O_NOFOLLOW`
when available. Symlink directory entries and non-regular/non-directory entries
are skipped. Platforms without fd-relative support use a contained path
fallback and never intentionally follow a symlink.

The snapshot itself is not authorization to open. Submit:

1. accepts only a clean relative snapshot member;
2. resolves the captured root strictly;
3. resolves the nominal target strictly;
4. proves it remains under root;
5. rejects any `resolved != nominal` path (symlink traversal/change);
6. performs a bounded contained stat;
7. requires a regular file;
8. opens through the contained file path.

Deletion, directory replacement, root escape, and post-scan symlink swaps fail
visibly while the current buffer remains stable.

## Authority model

Trusted interactive invocation needs no script capability: it is a normal
host-owned editor action, just like save or undo.

A script/plugin-owned interaction is different:

- creation requires `cap.fs-list`;
- configured `cap.fs-root` bounds enumeration;
- prompt origin is stamped at creation and survives physical navigation;
- submission requires `cap.fs-open` under that captured origin.

A plugin may bind `FilePicker` to a key, but the later physical keypress does not
convert the picker into trusted user authority. Tests exercise creation allowed
with list only and submission denied without open.

This mirrors the rev0952 default-key repair: product defaults are host policy,
while arbitrary plugin registrations remain capability-scoped delayed work.

## Worker lifecycle audit

The filesystem tree walk must be killable because ordinary OS calls can block on
unusual filesystems. The audit exposed two independent multiprocessing hazards.

### Multithreaded fork

CPython documents that safely forking a multithreaded process is problematic;
newer Python releases warn or choose `forkserver` by default on POSIX. A curses
editor may have active threads, so a child created with raw `fork` can inherit
locks in an inconsistent state.

`isolated_filesystem_worker_context()` now prefers:

1. `forkserver`;
2. `spawn`;
3. platform default only when neither explicit method exists.

New project inventory and root-marker batch work use this context. Existing
short filesystem workers still use the legacy fork-preferring helper because
some tests/embedders rely on in-process doubles. That is explicit migration debt,
not an endorsement of the old default.

### Queue-before-join

`multiprocessing.Queue` uses a feeder thread and pipe. A large result can fill the
pipe; if the parent joins the producer before reading, the child may wait for
its feeder to flush while the parent waits for child exit. A healthy result then
looks like a timeout or deadlock.

Both project scans and batched marker stats now poll/drain the queue under the
same deadline before joining. On timeout or failure they terminate, then kill if
necessary. Cleanup calls `cancel_join_thread()` before closing the queue so a
killed producer's partially written payload cannot hang parent teardown.

`terminate_filesystem_worker()` was also hardened for processes that failed
before `start()` or were already reaped; cleanup no longer masks the original
filesystem error with process-state assertions.

## Refactor boundary

The extraction is deliberately narrow.

`project_files.py` owns:

- root marker names, depth, cache, and batched observation;
- inventory exclusions and scan resource policy;
- fd/path traversal;
- worker creation/result/teardown;
- typed immutable scan results.

`Editor` still owns:

- active buffer/cwd/script context;
- capability checks and messages;
- prompt entry, row status (`file`/`open`/`modified`), ranking, and sections;
- delayed interaction authority;
- submit revalidation and opening;
- key/action/command integration.

This removes coherent filesystem policy from the coordinator without building a
parallel editor, service locator, or background index.

## Adversarial evidence

`tests/test_editor_project_file_picker.py` covers:

- deterministic ordering;
- hidden and generated-directory policy;
- symlink refusal;
- file, directory, depth, entry, and path-byte limits;
- depth followed by a terminal cap;
- isolated context preference;
- timeout termination and queue cleanup;
- consuming a large result before join;
- nearest marker root and no rescan while typing;
- raw-path fallback rejection;
- deleted files and post-scan symlink swaps;
- script list/open capability separation;
- plugin-bound delayed authority;
- prompt snapshot detachment;
- malformed, nonpositive, NaN, and infinite limit fallback.

Existing default-key and recent-file tests pin Ctrl-O integration and the
extracted root-locator compatibility. `tools/mxaudit.py` treats the owner,
finite limits, nonfollowing flags, hard-exhaustion state, queue-drain cleanup,
VM attributes, prompt fields, capabilities, submit containment, action, command,
option, default binding, plugin mirror, and adversarial test file as one
release-visible structural contract.

## Research notes

The design follows established editor expectations without copying a large
indexing architecture:

- Helix presents file and buffer pickers as first-class navigation and exposes
  picker options such as hidden/ignored-file behavior:
  <https://docs.helix-editor.com/pickers.html>
  <https://docs.helix-editor.com/editor.html#editorfile-picker-section>
- Zed treats the file finder as primary project navigation:
  <https://zed.dev/docs/migrate/vscode#file-navigation>
- ripgrep's guide is a useful reference for how quickly ignore semantics become
  a real language of precedence, hidden files, parents, and overrides; Micromax
  intentionally postpones that complexity:
  <https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md>
- CPython's multiprocessing documentation explains start methods, the
  multithreaded-fork hazard, queue feeder behavior, and join/deadlock warnings:
  <https://docs.python.org/3/library/multiprocessing.html>
- micro's default key documentation reinforces that opening/searching files is a
  core editor loop, though Micromax separates project picking from raw open:
  <https://github.com/zyedidia/micro/blob/master/runtime/help/defaultkeys.md>

These references inform product expectations and process safety. Micromax keeps
its own smaller, testable contract rather than importing another editor's exact
semantics.

## Intentional omissions

Rev0953 does not add:

- background indexing, watchers, incremental rescans, or cancellation UI;
- `.gitignore` or arbitrary ignore glob parsing;
- previews, file icons, content search, symbols, diagnostics, or multi-root
  workspaces;
- persistence of project snapshots;
- a script-visible raw inventory hostcall;
- a claim that the in-process capability boundary contains malicious native or
  Python code.

The picker should earn complexity through lived project use. The likely next
flow primitive is bounded project text search or symbols, but trust journeys and
legacy worker migration are higher priority.

## Recommended next work

1. Turn startup/open/edit/undo/save/conflict/recovery/close into complete trusted
   and restricted product journeys.
2. Inventory every legacy `_fs_worker_context()` call, preserve its observable
   timeout/error behavior, then migrate it to isolated contexts with focused
   process-lifecycle tests.
3. Observe whether built-in exclusions are insufficient before designing a
   bounded ignore-file parser.
4. Define a small visual hierarchy for picker query, section, selected row,
   status, and inactive detail so the flow feature gains taste without noise.
5. Add bounded in-project text or symbol navigation only after the filename
   picker is used enough to expose the next real friction point.
