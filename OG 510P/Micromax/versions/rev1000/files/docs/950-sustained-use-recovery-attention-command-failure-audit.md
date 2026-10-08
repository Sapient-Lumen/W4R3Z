# Sustained-use recovery attention and truthful command failure (rev0993)

## Why this became the priority

Rev0992 removed the clearest remaining aggregate-history allocation cliff. The
highest risk then moved from another isolated hot path to the lived loop: could a
person start the editor, move through a project, edit and search, survive a failed
plugin command, review an interrupted save, and finish with an honest screen?

A new 100x24 sustained-use journey exercised that complete chain. It found three
connected trust failures:

1. The startup recovery warning was transient. Ordinary messages could replace
   it while the unresolved private record still existed, so crash-recovery work
   effectively became invisible.
2. A transactional plugin command could emit a message and return false. Correct
   rollback restored editor state including that message, but the command layer
   then left the *previous* success message visible. The command failed while the
   screen still looked successful.
3. Opening a recovery in an existing clean buffer put text in ordinary history
   but left recovery authority outside that history row. Undo could restore the
   old text while retaining the journal entry id; a later ordinary save could
   retire recovery data the user had not actually reviewed.

The third defect was the severe one. It crossed text history, dirty truth, save
baselines, and durable journal ownership. More local undo tuning would not have
found it.

## Shipped correction

### Persistent, render-safe recovery truth

`Editor` now owns one cached filename-presence model refreshed at event
boundaries: journal configuration, startup, explicit inventory/recovery actions,
checkpoint creation, dismissal/repair, and successful save cleanup. Rendering
never scans or decodes the recovery store.

The status model exposes:

- `recovery_configured`
- `recovery_record_count`
- `recovery_record_truncated`
- `recovery_record_known`
- `recovery_warning`
- `recovery_error`
- `recovery_summary`

The default right status format ends in `$(recovery)`, producing
`[recovery:N]`, `[recovery:N+]` for a bounded lower bound, or `[recovery:?]` when
the configured store has not yet been inventoried or its latest refresh failed.
The token is deliberately at the end because narrow status rows preserve the
end of the right segment.

This is standing attention, not a modal interruption. The badge remains until
records are resolved, and repaint remains filesystem-free.

### One truthful failure message

`CommandDispatcher.exec()` now records the visible-message witness before a
command. If the command returns false and no new message survives, it emits one
fallback: `command NAME: failed`. Commands that already supplied a specific
failure keep it; no duplicate generic message is added.

This repairs the plugin rollback case without inventing a parallel diagnostic
registry. The command boundary simply guarantees that false cannot silently
leave stale success looking current.

### Recovery-open is one atomic user decision

For an existing clean buffer, opening interrupted-save content now records one
history row over:

- a shallow immutable line-vector generation;
- that generation's content signature, distinct from any saved baseline;
- cursors, selections, cursor ids, and primary cursor;
- recovery-relevant local encoding/file-format/filetype options;
- autosave and script-dirty provenance;
- the save recovery id; and
- interrupted-save entry id, target authority, and force-save requirement.

Text installation splits the journal payload once, reuses equal prefix/suffix
line strings from the live generation, and publishes one line vector. It does
not join complete source and result documents on the measured fast-dirty path.
Metadata-only recovery of an identical empty document retains no line vectors
and creates no synthetic text version.

Undo and Redo intentionally do **not** restore historical dirty flags, versions,
or saved signatures. They mutate monotonically and derive dirtiness against the
*current* saved baseline. This matters when a save occurs after recovery-open:
Undo to older text must be dirty; Redo to the saved recovered text must be clean.
The row therefore retains each text generation's BLAKE2 content signature and
compares it with the buffer's current save signature during replay. A
`fastdirty` buffer gets exact clean/dirty truth without joining or rehashing the
complete document at Undo/Redo time.

History also cannot recreate a retired journal filename. Before restoring
interrupted-save authority, it performs one exact bounded no-follow presence
check requiring a regular record below the journal read ceiling. The check does
not decode the private payload or inspect its target. A successfully saved,
dismissed, non-regular, or oversized record is not resurrected. A transient
inspection error is handled conservatively as possible continued authority.

Aggregate macro/`ed.with-undo` snapshots now carry the same recovery sidecars,
so wider rollback cannot detach journal authority from the buffer either. The
recovery inventory, review, repair, cleanup, and disposition commands are exact
nonrecordable macro boundaries. A successful `recover` therefore retains its
specialized current-save-baseline-aware history row instead of being flattened
into an aggregate macro snapshot that could later replay under another disk
baseline.

## Research comparison

The implementation stays Micromax-sized, but established editors reinforce the
underlying product rules:

- VS Code shows unsaved indicators and keeps backups restorable after unexpected
  closure. Its Hot Exit design explicitly treated backups that still exist but
  are no longer discoverable as a product failure.
- GNU Emacs recovery is review-first: it shows original/auto-save information,
  asks for confirmation, opens selected recovered files in buffers, and changes
  the actual files only when the user subsequently saves.
- Vim keeps warning while a swap file remains, tells users to verify recovered
  content before overwriting or deleting the swap, and historically fixed a bug
  where recovered text was not marked modified because `:x`/`ZZ` could otherwise
  lose the visible work.
- Scintilla defines modified state by the undo position relative to the current
  save point, reinforcing that history traversal must honor the latest saved
  boundary rather than restore an old dirty bit.

Micromax therefore treats an unresolved record as a standing obligation,
recovery-open as an atomic text-plus-authority decision, and save as a baseline
boundary that history may not rewrite.

Sources retrieved 2026-07-29:

- VS Code Basic Editing: https://code.visualstudio.com/docs/editing/codebasics
- VS Code, Hot Exit Comes to Insiders: https://code.visualstudio.com/blogs/2016/11/30/hot-exit-in-insiders
- GNU Emacs Manual, Recovering Data from Auto-Saves: https://www.gnu.org/software/emacs/manual/html_node/emacs/Recover.html
- Vim recovery reference: https://vimhelp.org/recover.txt.html
- Vim crash-recovery user manual: https://vimhelp.org/usr_11.txt.html
- Vim version history recovery/modified fix: https://vimhelp.org/version7.txt.html
- Scintilla documentation, Undo and Redo / save point: https://www.scintilla.org/ScintillaDoc.html

## Permanent evidence

New focused evidence covers:

- silent false versus command-specific failure feedback;
- the full startup/project/edit/search/save/plugin-failure/recovery/save journey;
- persistent status attention without a repaint-time journal scan;
- bounded and failed recovery presence refreshes;
- recovery-open Undo/Redo over text, metadata, dirty truth, and authority;
- save between recovery-open and history traversal;
- exact pre-save and post-save clean/dirty replay in a `fastdirty` large buffer,
  with complete live-document joins trapped;
- metadata-only recovery with zero retained text and no version fabrication;
- prevention of journal-authority resurrection after save, explicit dismissal,
  and known unusable record replacement;
- direct no-decode exact-entry checks for absent, oversized, non-regular, and
  untrusted-root cases; and
- large 4,096-line recovery with complete-text joins trapped, unchanged line
  identities shared, and retained-byte accounting below two full documents; and
- successful recovery review remaining outside aggregate macro recording.

Focused command/status/journey tests pass, the atomic recovery-history tests
pass, and the explicit save-failure/restart/recover/save path passes. The full
3,456-test monolithic run did not complete under the cloudtainer's 30-minute
supervisor. A pre-existing command-source-column assertion also fails identically
at the rev0992 baseline worktree (expected 36, observed 31). Rev0993 therefore
claims bounded targeted evidence, not a fresh complete-suite release receipt.

## Audit/refactor judgment

The most important refactor was deletion of a false model: recovery text was not
just another edit whose dirty/version snapshot could be replayed verbatim.
Recovery is a decision whose authority must travel with text, while dirtiness
must remain relative to the current disk baseline. Separating those concepts
removed the dangerous save/Undo interaction without adding a general recovery
registry, watcher, or second document model.

The follow-on audit removed a subtler false shortcut: `fastdirty` cannot be
allowed to turn recovery replay into permanently sticky dirtiness. Each recovery
generation carries its own content signature, while the saved signature remains
live buffer truth. That is enough for O(1) baseline comparison during replay and
does not create a second document snapshot.

The status cache is similarly narrow. It replaces repeated rediscovery with one
small event-refreshed truth object; it does not become a filesystem observer.
The command fallback is one boundary invariant, not a new error bus.

## Remaining risk

1. Presence is event-refreshed, not cross-instance live. Another Micromax process
   can change the journal without immediately updating this process's badge.
2. `[recovery:?]` is truthful but compact; it does not yet include a direct
   command hint on the status row.
3. Line-vector recovery history still copies O(number of lines) pointers, and one
   changed recovery computes one O(document bytes) generation signature at open;
   one enormous changed logical line remains one monolithic Python string.
4. Query-replace still owns one complete delayed planning source.
5. The fallback failure message cannot preserve a plugin's rolled-back specific
   text; a structured diagnostic channel is justified only by a reproduced need.
6. Cross-instance journal races remain under a single-writer assumption.
7. Signed/hermetic release evidence and explicit Windows/platform claims remain
   incomplete.

## Risk-ordered next work

1. Reproduce a user-visible huge-line mutation cliff beyond automatic
   `fastdirty`, then prototype only the smallest representation needed by the
   measured geometry.
2. Complete signed/hermetic release evidence and narrow platform claims to
   executed receipts.
3. Revisit delayed query-replace planning only if interaction measurements make
   its complete source owner visible.
4. Add cross-instance recovery refresh only after a real stale-badge journey is
   reproduced; do not add a watcher by anticipation.
