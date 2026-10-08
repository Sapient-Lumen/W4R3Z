# Rev0997 audit: segmented query-replace over a shallow source generation

## Why this was the next cut

The heart of Micromax is not a small VM in isolation. It is a calm editor whose
configuration, macros, and plugins remain understandable because effects,
authority, failure, and retained state have narrow owners. The highest-value
work is therefore the place where an ordinary editor loop still violates that
shape, not another registry or policy layer.

Rev0996 explicitly left one measured candidate: delayed query-replace retained a
complete LF-joined immutable source for the full confirm-each interaction. That
source was useful during planning, but ordinary literal answers only needed:

- stable original coordinates;
- exact text for the current planned match;
- line/column geometry across the next unchanged source gap; and
- an authoritative session-start generation for exceptional sparse-history
  authentication.

Retaining every source character in a second joined string was much broader than
those needs. A long-lived interaction could therefore pin a complete duplicate
of a large many-line document even after planning had finished.

## Reproduced waste

`tools/measure_qreplace_source.py` constructs one canonical many-line buffer with
exactly one literal match, initializes the live editor before tracing, and then
compares two retained planning shapes:

1. the rev0996 shape: call `Buffer.get_text()`, scan it, and retain that complete
   joined source with the compact edit plan; and
2. the rev0997 product path: begin an ordinary literal query-replace and retain
   only its shallow line generation, packed starts, and compact edit plan.

The permanent three-sample 16 MiB-class witness contains 16,777,279 characters
across 258,112 logical lines. Its medians are:

| Shape | Retained complete source | Traced current | Traced peak | Planning elapsed |
| --- | ---: | ---: | ---: | ---: |
| Rev0996 complete-string reference | 16,777,279 chars | 16,777,903 B | 16,778,847 B | 0.013877 s |
| Rev0997 shallow-line product | 0 chars | 4,224,717 B | 5,306,573 B | 0.185105 s |

The plans are byte-for-byte coordinate-equivalent. Every one of the 258,112
source line objects is shared with the live buffer, and the product path makes no
`Buffer.get_text()` call. Relative to the reference this removes 100% of the
retained complete source, reduces traced retained allocation by 74.820%, and
reduces traced peak allocation by 68.373%.

The remaining retained source shape is intentionally visible:

- the shallow tuple occupies 2,064,936 bytes in this interpreter; and
- 258,112 packed unsigned 64-bit line starts occupy 2,064,896 bytes.

These are CPython `tracemalloc` attribution facts on this machine, not RSS,
allocator-arena, native-heap, portable latency, or total-memory bounds. The
artifact is `.artifacts/rev0997-qreplace-source.json`, SHA-256
`e951139453caeba28448e99b7ee037356db27b77044b3b6d83f25884d6047b19`.

## Product correction

### 1. One shallow immutable source witness

`QueryReplaceSourceSnapshot` owns:

- the exact tuple returned by `Buffer.snapshot_lines()`;
- the canonical character length; and
- one read-only `PackedOffsets` owner containing each logical line start in an
  `array('Q')` cell.

The tuple is detached from future list mutation while its strings remain shared.
When an accepted replacement changes a live line, Python creates replacement
strings and the snapshot continues to own the immutable original line object.
Deep-copying editor/plugin interaction state returns the same frozen snapshot
rather than recursively copying data intended to be shared.

Flat source offsets project to line/column coordinates with `bisect_right()` over
the packed starts. The first query-replace offset is derived from that same
witness instead of redundantly walking the live buffer prefix. One planned match
materializes only its exact source slice. Monotonic navigation advances from
source-coordinate pairs, so it no longer counts or searches newlines in a
retained full-document string.

### 2. Segmented literal planning

Literal query-replace no longer calls `Buffer.get_text()`. It scans exact
canonical `"\n".join(lines)` coordinates through fixed 256 KiB offset windows.
Each window is assembled from only the intersecting line fragments and complete
interior lines. The scanner carries `len(search) - 1` characters into the next
window, which is sufficient because an escaped non-empty literal has fixed
character width under Python's regular-expression engine.

The existing semantics remain the oracle:

- `re.escape()` protects every literal metacharacter;
- `Pattern.finditer()` supplies ordered, non-overlapping matches;
- `re.IGNORECASE` preserves Python's Unicode case-insensitive behavior without a
  length-changing `lower()` or `casefold()` coordinate copy; and
- match, pattern, replacement, and result budgets fail before mutation with the
  same public messages as the flat scanner.

Randomized differential tests cover empty and multiline documents, every tested
chunk size down to one character, patterns longer than a chunk, newline-spanning
matches, start positions beyond the source, replace-one/replace-all, and Python's
special Unicode ignore-case characters.

An early implementation assembled one chunk per logical line. It removed the
retained string but made the 258,112-line witness spend roughly 0.90 seconds in
Python-level chunk handling under the tracing harness. Fixed offset windows over
the same packed index brought that exploratory figure to roughly 0.18 seconds.
A second experiment preallocated the exact packed array size; it saved only about
90 KiB of peak traced allocation while roughly doubling planning time, so it was
rejected. The shipped append-built index is the measured tradeoff, not the most
ornamental implementation.

### 3. Regex flattening is temporary, not denied by rhetoric

The isolated Python regex worker still consumes one `str`, and arbitrary regex
state cannot be made chunk-local by carrying only pattern width. Regex
query-replace therefore materializes one complete source temporarily while its
killable worker produces concrete expanded rows, then drops that string before
capture mode begins. The delayed session retains the shallow snapshot only.

This closes the long-lived duplication problem without pretending the initial
regex peak has disappeared. A streaming regex protocol or alternate engine would
need its own compatibility, timeout, memory, and cross-boundary evidence.

### 4. Exceptional history authentication stays line-vector-native

Ordinary answers use the O(1) object/version lease. At an exceptional stale or
post-hoc boundary, the editor now replays accepted sparse splices against the
snapshot's line tuple and compares canonical line vectors directly. It does not
flatten either the original generation or the live buffer merely to decide
whether one grouped Undo row is still authentic.

### 5. Shared coordinate-owner refactor

Search already had the needed compact read-only offset owner, but it lived in
`search.py`. Rev0997 moves `PackedOffsets` into `textpos.py`, validates ownership
transfer type codes, and reuses it from both search and query-replace. This
removes a likely duplicate container without creating a generic registry or a
second coordinate model. Search navigation, span projection, and its 100,000-row
storage shape remain covered by their existing tests.

## Correctness and failure audit

The focused union covers query-replace interaction lifecycle, buffer identity and
generation, sparse history, plugin cleanup rollback, search authority/navigation,
replacement planning, and shared text-position helpers. The rev0997 additions
also prove:

- mutable input line lists are detached while immutable strings stay shared;
- snapshot offset/cursor/range geometry matches the flat source oracle at every
  bounded pair;
- segmented literal edit rows exactly match the flat scanner across randomized
  Unicode inputs and adversarial chunk boundaries;
- budget failures remain equivalent;
- literal begin cannot materialize snapshot text;
- regex begin retains no `source_text` field after planning;
- stale-boundary authentication cannot call `Buffer.get_text()`; and
- the permanent measurement itself is executable and shape-checked.

The interaction still validates exact local live old text before every accepted
edit, refreshes the generation witness after its own mutation, rejects stale or
zero-width coordinates, and records one sparse atomic Undo row. The memory
change does not weaken authority or rollback behavior.

## Primary-source research and what it changed

Research was limited to implementation facts and mature-editor lessons rather
than using precedent as permission for a rewrite:

- Python `re` documents Unicode string matching, `re.escape`, ordered iterator
  APIs, optional start positions, and Unicode `IGNORECASE` behavior:
  <https://docs.python.org/3/library/re.html>
- Python `array` documents compact homogeneous numeric storage and the minimum
  eight-byte unsigned long long `Q` cell used by the coordinate owner:
  <https://docs.python.org/3/library/array.html>
- Python `bisect` documents logarithmic insertion-point lookup over a sorted
  sequence and specifically recommends precomputed keys for repeated searches:
  <https://docs.python.org/3/library/bisect.html>
- Python `copy` explicitly notes that deep copying may copy too much when data is
  intended to be shared and provides `__deepcopy__` for user-defined control:
  <https://docs.python.org/3/library/copy.html>
- VS Code's text-buffer reimplementation describes both the string-concatenation
  trap and the metadata/access tradeoffs of a piece tree, then emphasizes that
  real-world profiling—not assumed hot methods—must choose the design:
  <https://code.visualstudio.com/blogs/2018/03/23/text-buffer-reimplementation>
- The interaction remains intentionally recognizable beside GNU Emacs
  query-replace and Vim's confirming substitute:
  <https://www.gnu.org/software/emacs/manual/html_node/emacs/Query-Replace.html>
  and <https://vimhelp.org/change.txt.html>.

The concrete conclusion is conservative. VS Code's piece-tree work supports
avoiding giant concatenations, but it also shows that a representation migration
introduces line-access and metadata complexity. Micromax's reproduced problem
was one delayed duplicate, not a general inability to edit its current line-list
model. A shallow generation plus compact coordinates corrects that problem with
far less blast radius.

## What remains at risk

1. **Hosted provenance is still the largest external finish line.** The exact
   release lane is configured but not executed and consumer-verified here.
2. **The shallow witness remains O(lines).** A many-million-line file may make
   the tuple and packed starts user-visible even when characters are shared.
3. **Regex planning still has one temporary full source.** It is no longer
   retained across keypresses, but initial peak remains proportional to document
   size.
4. **The complete match plan is retained.** Literal and regex sessions still own
   one `ReplacementEdit` row per planned match up to the configured ceiling;
   dense matches may make row/object overhead the next qreplace pressure.
5. **A huge single logical line is one immutable string.** The source snapshot
   shares it, but mutation of that line remains O(line length).
6. **Out-of-band native/Python mutation is outside the supported owner model.**
   Version and local-slice witnesses fail closed only for mutations that update
   or contradict observable buffer truth.

## Next cuts, in order

- Execute and externally verify the hosted release lane before adding more
  release architecture.
- Measure regex begin peak or dense planned-row retention only from a real
  query-replace journey before changing that protocol.
- Measure shallow O(lines) generations only with a many-million-line product
  transcript.
- Add a rope, piece tree, gap buffer, watcher, background index, or persistent
  revision system only if those measurements show the current narrow owners
  cannot meet the lived editor loop.
