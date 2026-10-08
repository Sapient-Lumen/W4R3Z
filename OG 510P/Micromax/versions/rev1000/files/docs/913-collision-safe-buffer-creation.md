# Collision-safe buffer creation and explicit ownership (rev0955)

## Why this mattered

`Editor.new_buffer(name, ...)` used to assign directly into `Editor.buffers`.
Because the dictionary key is also used by marks, authority sidecars, MRU state,
help history, and recovery code, a duplicate name did not merely replace a
label. It could orphan a dirty live buffer and make name-keyed metadata appear
to refer to the replacement. No warning, capability, or discard confirmation
ran first.

That was a trust-model inversion: the lowest-level creation helper silently
performed the most destructive possible collision policy, while higher-level
rename and save-as paths already refused to clobber another open buffer.

Rev0955 makes the two legitimate intentions explicit:

- **strict creation** requests an exact unused name and fails before any state
  changes when that name is live;
- **human-facing creation** requests a preferred display name and deterministically
  chooses a nearby unused label.

There is no public replacement primitive. Replacement is a destructive action
and should never be smuggled through creation.

## Contract

### Strict owner

`Editor.new_buffer(name, ...)` is now the sole ordinary insertion primitive.
It:

1. normalizes and rejects an empty name;
2. checks the live buffer dictionary;
3. raises `BufferNameCollisionError` on collision;
4. only then allocates cursor identity, constructs the buffer, records authority,
   activates it, and captures any disk signature;
5. returns the exact created name.

The guard precedes cursor allocation and every mapping/sidecar mutation. A
failed duplicate request therefore leaves active buffer, dirty text, marks,
mark authority, buffer authority, MRU order, and cursor-id allocation unchanged.

### Unique-name owner

`src/micromax_editor/buffer_names.py:unique_buffer_name()` owns deterministic
label allocation:

- `notes`, `notes<2>`, `notes<3>`, ... for ordinary names;
- `*scratch*`, `*scratch-2*`, `*scratch-3*`, ... for internal/untitled names;
- the first available suffix is chosen, so holes are reused predictably;
- the search is bounded by the current occupied-name count rather than using an
  unbounded retry loop.

`Editor.new_buffer_unique()` delegates to that owner and then to strict
`new_buffer()`. It does not duplicate construction logic.

### File and help identity

`open_file()` and `open_help_doc()` first reuse an already-open buffer by
normalized path. If no path-backed buffer owns the target but a pathless buffer
already uses the preferred display name, they preserve that buffer and create a
uniquely labelled path-backed buffer.

This separates two concepts that had been accidentally conflated:

- **file identity** is the normalized path attached to a buffer;
- **display/lookup name** is a unique label inside the current editor session.

Reopening the same file switches to the existing path-backed buffer even when
its display name has a suffix.

## Product surface

The command bar now exposes:

```text
new
new NAME
new "project notes"
```

Repeated `new` creates `*scratch*`, `*scratch-2*`, and so on. Repeated custom
names use the ordinary `<N>` form. More than one parsed argument is rejected as
`usage: new [NAME]` before state changes.

The public core action `NewBuffer` creates the same default untitled buffer and
is available to the command/action palette or trusted user bindings. No shipped
key was displaced: terminal key vocabularies are scarce, and the existing
`Ctrl-N` search meaning remains intact.

## Authority boundary

Untitled buffer creation is interactive/trusted only in this revision.
`Editor.create_untitled_buffer()` rejects script context, and both the `new`
command and `NewBuffer` action route through it.

This is intentionally stricter than adding a boolean `cap.buffer-create` today.
A script-visible create primitive is an unbounded retained-memory effect unless
its contract also defines at least:

- maximum live script-created buffers;
- maximum initial text/result bytes;
- ownership and cross-origin visibility;
- unload/rollback behavior;
- whether creation is durable, recoverable, or merely session-local;
- how later close/save/rename authority is derived.

Plugins can still provide editing behavior through already-bounded surfaces.
Expose script creation only when a real plugin journey justifies a finite,
reviewable contract.

## Audit and refactor

The change audits both single-key writes and whole-registry replacement. Rev0955
leaves three explicit single-key owners:

1. `new_buffer()` — guarded strict creation;
2. `_restore_buffer_identity()` — synchronous rollback to a captured save-as
   snapshot;
3. `rename_buffer()` — identity-preserving move that refuses a live destination.

The broader AST pass found a fourth, different ownership path: macro and
`ed.with-undo` rollback rebuilt the whole registry with
`self.buffers = restored`. That restored values correctly but silently replaced
the public mapping object. An embedder, inspector, or test retaining
`registry = ed.buffers` would then observe stale state forever. Marks had the
same avoidable identity break in several restore paths.

`_restore_macro_replay_snapshot()` now clears and updates the existing buffer and
mark mappings in place. Aborted macro playback and successful transaction
undo/redo remove or restore entries without invalidating retained registry
references. The refactor does not preserve buffers created after the captured
snapshot; it preserves the registry object and the pre-existing `EditorBuffer`
objects that the transaction contract owns.

`tools/mxaudit.py` now reports a separate `buffer_creation` section. It parses
the `Editor` AST to verify that the duplicate-name guard occurs before cursor
allocation and insertion; inventories buffer subscript stores/deletes,
whole-registry assignments, insertion/removal calls, and clears; inventories
mark-registry replacement plus every restore-time clear/update owner; permits
whole-registry assignment only in `__init__`; and pins unique routing,
interactive surfaces, script denial, and focused regressions. This is more useful
than a broad grep because a future `self.buffers = ...`, `update()`, `pop()`,
`del self.buffers[...]`, or direct key write becomes a review event.

The giant `Editor` coordinator remains a pressure surface. Moving name policy to
`buffer_names.py` is deliberately small: it extracts one pure decision without
creating a second buffer model or speculative manager hierarchy.

## Adjacent archive and discovery audit

The broader command/help lane exposed an inherited archive defect rather than a
buffer defect. Living docs deliberately put short `Rev####` or `Latest ...
rev####` provenance paragraphs near their title. The catalog's old “first
non-heading line” rule treated those breadcrumbs as the document summary. That
made help rows, docs pickers, command completion, and LLM-oriented scans churn on
every revision while hiding the durable subject of central documents.

`docs_index._first_summary_line()` now recognizes only bounded revision-banner
forms and skips the banner's whole Markdown paragraph, including wrapped lines.
It does **not** skip arbitrary text beginning with `Latest`; a revision marker is
required. Focused tests cover wrapped `Rev0955` notes, `Latest ... (rev955)`
landings, and an ordinary durable `Latest ...` sentence that must remain visible.

The same audit found two central references with misleading catalog titles:
`docs/10-research-notes.md` began at a dated level-two heading, and
`docs/66-editor-micromax-commands.md` did not reach a level-one heading until a
historical `TODO rev682` block. Both now have truthful top-level titles and
stable introductory summaries. Existing fuzzy apropos coverage was also made
order-insensitive: it proves the intended word is present without pretending the
global first result can never change as useful documents are added.

The context lane exposed a related handoff failure: once rev0954 was no longer the
newest revision, `discard_guard.py` fell out of the rolling revision-code window
even though it remains the central startup/discard trust owner. It is now a
permanent curated `mxcontext` entrypoint. Future sessions therefore retain the
policy boundary instead of seeing only whichever files changed most recently.

The residual risk is intentionally narrow: a real document whose first durable
paragraph literally begins `Revision 2 ...` will be treated as a provenance
banner. That is preferable to a broad heuristic, and a future syntax change
should be driven by a concrete misclassification test rather than more guessing.

## Prior art and judgment

The implementation borrows conventions, not architecture:

- GNU Emacs [`create-file-buffer`](https://www.gnu.org/software/emacs/manual/html_node/elisp/Subroutines-of-Visiting.html)
  appends `<2>`, `<3>`, and so on when a preferred name is occupied.
- GNU Emacs [`make-indirect-buffer`](https://www.gnu.org/software/emacs/manual/html_node/elisp/Indirect-Buffers.html)
  signals an error when asked for an already-live name. This supports separate
  strict and convenience lanes rather than silent replacement.
- Vim documents a stable unique buffer number independent of its display name
  in [`windows.txt`](https://vimhelp.org/windows.txt.html). Micromax does not add
  numeric IDs yet, but this is the strongest likely future direction if rename,
  marks, persistence, or recovery keep making names carry too much identity.
- VS Code adds folder context when editor labels collide in
  [multi-root workspaces](https://code.visualstudio.com/docs/editing/workspaces/multi-root-workspaces).
  That is useful taste guidance for future same-basename file labels, but it is
  not needed for Micromax's current full-path file names.

The small-editor lesson is: preserve the object first, disambiguate the label
second, and never make a collision policy destructive by default.

## Tests

Focused regressions cover:

- deterministic ordinary and internal-name allocation, including holes;
- side-effect-free strict duplicate failure;
- preservation of dirty text, marks, authority, MRU state, and cursor identity;
- pathless same-name drafts when opening a real file;
- pathless `help:topic` notes when opening protected help;
- normalized-path reuse after a suffixed display name is allocated;
- repeated and quoted `new` commands;
- command/action denial in script context, delayed script-origin binding denial,
  and trusted user-init binding provenance;
- failed macro rollback plus transaction undo/redo preserving the public buffer
  and mark registry objects;
- legacy/corrupted same-name object replacement still re-arming exact discard
  confirmation.

## Residual risk and next pressure

Names still act as lookup keys across several editor sidecars. Strict no-clobber
semantics remove the dangerous replacement path, and rename updates known
name-keyed state, but names are not a permanent identity architecture.

Do not introduce a global buffer-ID migration merely for elegance. Reconsider a
stable immutable ID when one of these concrete pressures appears:

- persisted marks or recovery records must survive renames robustly;
- multiple views/indirect buffers share text;
- same-basename file labels become common enough to need contextual display
  names distinct from lookup identity;
- plugin APIs need durable references that cannot be confused by close/reopen.

The next product work should return to complete visible failure journeys and a
restrained highlight hierarchy, while the remaining fork-first worker migration
continues as a bounded infrastructure audit.
