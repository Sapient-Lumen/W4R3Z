# Query replace

Query replace is Micromax's headless confirm-each replacement interaction. It
must remain predictable across buffer navigation, rename, plugin cleanup, undo,
and failure—not merely while one prompt is visible.

## Commands and keys

- `qreplace SEARCH VALUE [-l]`
- `queryreplace ...` (alias)
- `-l` selects literal matching; otherwise the search is regular-expression
  based and follows the editor's `ignorecase` option.

| Key | Meaning |
| --- | --- |
| `y` / `Enter` | replace this match and continue |
| `n` | keep this match and continue |
| `a` | replace this and remaining matches up to the response budget |
| `l` | replace this match and finish |
| `q` / `Esc` | finish without replacing the selected match |

The capture keymode consumes otherwise-unbound input, so an answer cannot fall
through to global save, quit, or other bindings.

## Current lifecycle contract

A live session captures a weak `QueryReplaceBufferWitness` for the exact
`EditorBuffer` object and the monotonic `Buffer.version` that produced the
current match. Its display name is diagnostic; neither name reuse nor a later
text generation authorizes the saved coordinates.

- Renaming that object preserves the session and refreshes the display name.
- Switching to another buffer finalizes accepted replacements on the original
  object as one undo step before activation changes.
- Successful plugin group/generation cleanup finalizes accepted replacements and
  removes the plugin-owned interaction.
- Failed plugin cleanup restores both the live interaction and the pre-cleanup
  undo membership. It may not leave one provisional undo row beside a restored
  session.
- Closing the target drops the session before the object leaves the live buffer
  map. Reusing the old name cannot redirect replacement or selection.
- Selection cleanup touches only the witnessed target, never whichever buffer is
  active when cleanup later runs.
- Starting another query-replace first finalizes accepted edits in the old
  session, even when validation of the new request then fails.
- Every replace, skip, all, last, or quit response validates the captured text
  generation before using saved coordinates. Accepted edits refresh the witness.
- Another supported mutating action closes query-replace and clears its transient
  primary selection before the action runs.

Each accepted mutation marks the exact target changed immediately under the
session's captured script authority. Delayed physical input cannot elevate a
plugin-owned query-replace into trusted host authority.

Each accepted match is applied through the shared one-range edit seam. The match
coordinates, primary cursor, and every retained secondary cursor/selection are
interpreted against one witnessed pre-edit range. Variable-length replacement
rebases sidecars through local line/column geometry; the complete-document
simultaneous planner is reserved for genuine multi-range work.

## Immutable planning without a retained joined document

Before capture mode begins, the planner obtains the complete bounded match set
from one session-start source generation. Regex compilation, matching, and
`$...` capture expansion happen once in the killable child; the live interaction
stores one immutable packed replacement plan. `y`, `n`, `a`, and `l` project the
current concrete row and never rematch mutated text, so replacement-created
targets cannot enter the same session.

The delayed source generation is a `QueryReplaceSourceSnapshot`:

- one immutable tuple returned by `Buffer.snapshot_lines()`;
- the canonical character length; and
- one read-only `PackedOffsets` vector containing an unsigned 64-bit start for
  every logical line.

The tuple is detached from future list mutation while complete immutable line
strings stay shared with the live buffer. The session therefore does not retain
`"\n".join(lines)` as a second complete document.

### Literal planning

Literal query-replace scans exact canonical source coordinates through bounded
256 KiB offset windows. Each window materializes only the intersecting line
fragments and complete interior lines. The scanner carries
`len(search) - 1` characters into the next window, enough to find every match
that crosses a window boundary because `re.escape(search)` is a fixed-width
non-empty literal pattern.

The flat scanner remains the executable oracle. Segmented planning preserves:

- Python `re.escape()` literal semantics;
- ordered, non-overlapping `finditer()` rows;
- Python's Unicode `IGNORECASE` behavior without a length-changing lowercase or
  casefold copy;
- source start positions, replace-one/replace-all behavior, and exact offsets;
- pattern, match-count, replacement, and result budgets; and
- failure before capture or mutation.

### Regex planning

The isolated Python regex worker still consumes one `str`, but regex begin no
longer creates that complete value in the editor process or embeds it in the
worker's JSON/stdin body. The planner emits canonical bounded chunks from the
shallow line snapshot into one exclusively created exact-text file inside a
private temporary directory. The request carries only a versioned path, byte,
and character descriptor. The child validates the opened regular file, exact
size, inode witness, UTF-8 `surrogatepass` decode, and character count before it
constructs the one `str` required by Python `re` and applies the existing
deadline, match, result, and Linux memory-headroom policy.

The file is removed after success, timeout, startup or worker failure, staging
failure, and interruption under ordinary Python cleanup. The transport removes
complete parent source/JSON/UTF-8 request copies; it does not claim zero-copy,
total cgroup memory, immunity to same-UID tampering, or cleanup after `SIGKILL`
or host loss. The temporary file can consume filesystem and page-cache bytes.

### Packed match plan

`ReplacementEdits` exposes the established read-only sequence of concrete
`ReplacementEdit(start, end, new)` rows over a narrower retained owner:

- one interleaved private `array('Q')` of source start/end coordinates;
- one shared replacement string for literal plans and regex plans whose expanded
  outputs are all equal; or
- one replacement reference per match only when regex capture expansion varies.

Indexing or iteration projects short-lived row objects for existing consumers.
The delayed session itself retains no Python edit object or coordinate integer
per match. The plan is complete and exposes no mutator before capture begins, so
plugin/runtime deep-copy snapshots share the same immutable owner while mutable
session, authority, capture, source, accepted-history, and provisional-Undo
state remain under their existing rollback owners.

The 100,000-match rev0998 witness records 1,600,000 coordinate bytes and reduces
traced retained allocation from 12,792,104 to 1,694,286 bytes relative to the
rev0997 object-row shape. This is still O(matches), and architecture-specific
`array.itemsize` rather than a universal heap bound owns the exact byte figure.

### Monotonic navigation

For each planned row the session:

1. maps source offsets to line/column coordinates with `bisect_right()` over the
   packed starts;
2. advances current geometry through the unchanged source gap from the previous
   mapped boundary;
3. checks that current offsets equal source coordinates plus the accepted-length
   delta;
4. materializes only the exact planned source slice; and
5. verifies that slice against `Buffer.get_range_text()` before mutation.

Under fast-dirty operation, ordinary answers, next-match selection, and
finalization do not materialize the complete live buffer after planning.

## Sparse grouped Undo

Every text-changing accepted row appends one exact splice:

- old start/end offsets in the immutable session source;
- new start/end offsets in the final accepted result;
- exact old source text; and
- normalized replacement text.

Rows must remain monotonic in both coordinate spaces. Equal-text accepted rows
retain no document payload, though the final interaction may still record a
sidecar-only action.

When the session finishes, navigation finalizes it, or successful lifecycle
cleanup removes it, accepted work becomes one `SimultaneousEditWitness` plus
exact before/after sidecars. Undo and redo validate every addressed slice against
one immutable current line generation before constructing and committing one
result. A stale later row cannot leave an earlier row half-applied, and unrelated
same-width text outside the addressed ranges is preserved.

An ordinary interleaving action finalizes the replacement row first and records
its own edit second, so undo reverses the later edit before the earlier
replacement. Commands and hostcalls that record only after mutation are split at
their pre-edit snapshot by the central undo recorder.

If `Buffer.version` changed without a trackable boundary, the session is canceled
and every delayed response returns false. A grouped replacement undo is emitted
only when the session-owned result can still be authenticated. Exceptional
stale/post-hoc paths replay accepted sparse splices against the shallow
session-start line generation and compare canonical line vectors directly; they
do not flatten the source or live buffer merely to decide ownership. An
untracked interleaving edit is not silently absorbed.

The witness is session-local, not a persistent document revision. Raw
Python/native mutation can bypass supported ownership. Sparse Undo/Redo still
constructs one complete result line vector before one commit. Dense plans retain
O(matches) packed coordinates, at 16 coordinate bytes per match on the measured
interpreter, and varying regex capture expansion retains one string reference per
match.

## Replacement and resource safety

- Empty searches and zero-width matches are rejected because every candidate
  must be visible and advancing.
- Unknown flags, deeply nested/invalid patterns, timeouts, worker failures, and
  invalid replacement templates fail before capture or edit.
- Raw backslashes remain literal except for Micromax's documented `$...`
  replacement syntax; Python's replacement-template dialect is not exposed.
- Read-only targets fail before mutation.
- `qreplace.max` bounds one `all` response (default `10000`; `0` is an explicit
  unlimited opt-in). Reaching the budget leaves the session at the next match.
- Literal planning owns bounded temporary windows but retains O(lines) tuple
  pointers and packed line starts. Delayed match plans retain O(matches) packed
  spans; varying regex output retains per-match string references. Regex planning
  stages bounded canonical chunks in one private exact-text file, sends only a
  strict descriptor from the parent, and still owns one complete child `str` plus
  filesystem/page-cache bytes.
- No-match and error exits clear only session-owned capture/selection state.

## Implementation and evidence

- `src/micromax_editor/query_replace.py` — weak identity/version witness,
  shallow source snapshot, offset projection, exact source slices, and source
  line/column advancement.
- `src/micromax_editor/textpos.py` — shared read-only packed coordinate owner.
- `src/micromax_editor/replace_plan.py` — bounded segmented literal planning,
  child-backed concrete regex expansion, and the packed read-only match-plan
  owner.
- `src/micromax_editor/simultaneous_edits.py` — source/final sparse witness,
  atomic line-vector replay, and local one-range cursor mapping.
- `src/micromax_editor/editor.py` — immutable-row interaction, authority,
  monotonic navigation, mutation, selection, sparse finalization, lifecycle,
  navigation, rename, close, and undo owner.
- `src/micromax/regex_runtime.py` / `regex_worker_child.py` — flat and
  file-backed request policy, exact source descriptor validation, compile/match/
  expansion timeout, result ceilings, and cleanup owner.
- `src/micromax_editor/plugin_runtime.py` — scoped interaction and provisional
  undo snapshot/restore during plugin cleanup transactions.
- `tools/measure_qreplace_regex_transport.py`
- `tools/measure_qreplace_source.py`
- `tools/measure_qreplace_dense_plan.py`
- `tools/measure_qreplace_history.py`
- `.artifacts/rev0999-regex-transport.json`
- `.artifacts/rev0998-qreplace-dense-plan.json`
- `.artifacts/rev0997-qreplace-source.json`
- `tests/test_rev0999_file_backed_regex_transport.py`
- `tests/test_rev0998_packed_qreplace_plan.py`
- `tests/test_rev0997_qreplace_source_snapshot.py`
- `tests/test_qreplace_sparse_history.py`
- `tests/test_editor_query_replace.py`
- `tests/test_editor_qreplace_interaction_boundary.py`
- `tests/test_query_replace_buffer_witness.py`
- `tests/test_qreplace_generation_journey.py`
- `tests/test_editor_interaction_authority.py`
- `tests/test_plugin_runtime_group_policy.py`
- `tests/test_search_navigation_journey.py`

The interaction is intentionally familiar to Emacs query-replace and Vim's
confirming substitute, while Micromax keeps its own bounded planner, source
witness, sparse history, command, and capture model:

- <https://www.gnu.org/software/emacs/manual/html_node/emacs/Query-Replace.html>
- <https://vimhelp.org/change.txt.html>

The file-backed regex transport, process-tree measurement, Python/Linux
primary-source research, and residual risks are in
`docs/957-file-backed-regex-query-replace-transport-audit.md`. The packed-plan
landing remains in `docs/956-packed-query-replace-plan-audit.md`; the shallow
source and segmented literal landing remains in
`docs/955-segmented-query-replace-shallow-source-audit.md`; sparse accepted
history remains documented in `docs/946-sparse-query-replace-history.md`.
