# Repeated search wrap, one source match set, and truthful viewport projection

Rev0969 follows the first repeated navigation loop selected after rev0968:

```text
find -> next -> next -> previous -> inspect status/highlight
```

The loop looked complete because Micromax already had `find`, `findnext`,
`findprev`, an `i/n` status summary, and visible `hlsearch`. In ordinary use it
was not coherent. Reaching the final or first occurrence terminated repetition
with “not found.” Newline-starting matches could be rediscovered instead of
advanced. Navigation, count, and highlight used different algorithms, so they
disagreed on overlap, Unicode case transformations, and zero-width regexes. The
renderer then ran the pattern again on each visible row fragment, changing regex
meaning after softwrap or horizontal scrolling and hiding real cross-line
matches.

This is a trust failure in a high-frequency loop, not missing polish. The cursor,
status, and highlighted text must describe the same target.

## The repaired loop

For `one two one`, starting on the first occurrence:

1. `findnext` moves to the second occurrence and reports `2/2`;
2. the next invocation moves to the first and reports `1/2 [wrapped to top]`;
3. `findprev` moves to the second and reports `2/2 [wrapped to bottom]`;
4. if the buffer contains only one occurrence, next/previous return false and
   report `[only match]` without claiming cursor movement;
5. the status summary and visible current/all-match cues are derived from the
   same resolved span set used for movement.

Initial `find` also wraps to the first occurrence when the cursor is after the
last target and names that crossing when feedback is requested. The behavior is
fixed rather than configurable. No `wrapscan` option was introduced.

## Severe semantic fractures found by the audit

### Endpoint repetition terminated the task

The old next/previous commands stopped at the buffer boundary. The user had to
restart the search or move manually even though the active query and earlier
matches remained valid. Worse, an endpoint “not found” looked like query failure
rather than the end of one traversal.

### Cursor-column increment was not a source-offset successor

Forward repetition tried to avoid rediscovering the current match by constructing
`Cursor(line, col + 1)`. Buffer clamping can collapse that position back onto the
same end-of-line cursor. A literal newline match beginning at that cursor could
therefore be found again, returning success without progress.

### Three surfaces implemented three match policies

- navigation used `str.find`/`rfind` or regex search from a cursor offset;
- status counting used non-overlapping whole-buffer matches and case-folded
  copies for literals;
- highlight re-ran literal/regex discovery against each rendered row fragment.

That produced observable contradictions:

- `aaa` searched for literal `aa` could navigate to overlapping position 1 while
  count/highlight reported only the non-overlapping position 0;
- `.lower()` and `.casefold()` can change Unicode matching behavior and string
  length, so an index from transformed text is not necessarily an index in the
  original buffer;
- zero-width regexes could move or “succeed” in navigation while count/highlight
  deliberately omitted them;
- a cross-line pattern could be navigable but invisible because neither row
  fragment contained the complete pattern.

### Rendered fragments changed regex meaning

A soft-wrapped continuation or horizontally clipped suffix is not a new source
line. Running `^foo` against a visible fragment beginning with `foo` invented a
match that did not exist at the logical line start. Conversely, a real `b\nc`
match disappeared when the two source portions were searched independently.
Display geometry had accidentally become search semantics.

### Screen assembly repeated whole-buffer work

Status calculation scanned the buffer for `i/n`, then visible highlighting
scanned again. Each visible row could then walk matches from the beginning.
The first refactor draft added span-boundary bisection but still sliced the
trailing tuple per row, copying all remaining matches. That hidden cost was
removed before packaging.

## One ordered source-coordinate match set

`src/micromax_editor/search.py` now owns one policy:

- empty or invalid patterns produce no targets;
- literal search escapes the query and uses the same regex traversal machinery;
- ignore-case search leaves the source text unchanged and uses `re.IGNORECASE`;
- only non-empty matches are retained;
- `finditer` order and non-overlap define the stable target sequence;
- every span is an offset into the original normalized buffer text.

The policy deliberately excludes zero-width regex matches. Micromax currently
has no visible width, advancing cursor contract, or replacement interaction for
such a target. Counting one while refusing to paint it, or repeatedly returning
the same cursor, would be less truthful than excluding it. This can change only
with a concrete interaction design and matching evidence.

Using `re.IGNORECASE` preserves source coordinates and aligns literal and regex
case policy, but it does not claim full Unicode case-fold equivalence. For
example, searching `strasse` does not claim that `Straße` is an equivalent
literal. Full case folding would require an explicit source-offset mapping and a
clear user contract; silently indexing a length-changing transformed copy is not
acceptable.

## Navigation resolves before mutation

`navigate_search()` receives the exact match snapshot, a source cursor,
direction, inclusion rule, and wrap rule. It uses binary search over match starts
to return a `SearchNavigation` row containing:

- target cursor and exact source span;
- 1-based match index and total;
- whether the boundary was crossed.

`Editor` owns active-search authority, cursor mutation, and public messages. It
commits the resolved row and reuses its exact `i/n` summary rather than rescanning
after movement. A sole match resolves back to the current source offset; the
editor reports `[only match]` and returns false.

The active-search provenance model is unchanged. Scripts still require the
existing read/replay capabilities when the query belongs to another authority,
and denied operations preserve their previous argument/state behavior.

## Exact transient snapshots, not a cache subsystem

A `SearchSnapshot` binds:

- the exact `Buffer` object;
- its monotonic text version;
- query, literal/regex flavor, and case policy;
- source text length and line-start offsets;
- ordered spans plus start/end indexes.

Supplying a snapshot from another same-version buffer is rejected. Supplying one
after mutation is rejected. The caller transparently rescans the live buffer.
Exact object identity matters because version numbers are local witnesses, not
global document identities.

The snapshot is transient. A composed screen creates at most one when status or
`hlsearch` needs search truth, passes it to both surfaces, and then drops it. No
persistent cache, invalidation registry, background worker, or lifecycle owner
was added. Pattern compilation likewise relies on direct local compilation
rather than a new project-owned cache.

## Viewport projection preserves whole-buffer meaning

The edit-window model already exposes source line, start column, visible source
length, and renderer-owned display offset. Search highlighting now intersects
whole-buffer spans with those source fragments:

- a cross-line match appears on every visible source portion it intersects;
- softwrap continuation indentation is display-only and never enters match
  coordinates;
- horizontal clipping changes projection, not pattern meaning;
- the current target is identified by the whole match's source start, so all
  visible pieces of one cross-line current match receive the current cue.

Projection bisects monotonic match-end offsets to start at the first possible
intersection, then indexes spans until their start passes the fragment end. It
does not rescan the prefix and does not slice/copy the trailing match tuple.
This keeps work proportional to boundary lookup plus intersecting/nearby spans
for each visible row.

The public `micromax.screen.v1` shape is unchanged. Existing search cue tokens
receive more accurate spans; the independent consumer and highlight precedence
remain intact.

## Audit/refactor result

The revision removes rather than multiplies semantic owners:

- the editor-local row-fragment `search_match_spans()` implementation is gone;
- compatibility imports now delegate to the shared search module;
- navigation no longer owns separate literal and regex loops;
- status lookup uses binary search over the same match starts;
- screen status and highlight share one snapshot;
- no option/schema/registry/pane/indexer was added.

A late exact-identity audit found that a snapshot initially checked version,
query, and options but not buffer object identity. Two buffers can legitimately
share version zero, so the stale set could be accepted across buffers. The
snapshot now retains the exact transient buffer object and a regression test
pins the rejection. The same audit found tuple slicing in projection despite
bisection; indexed iteration removed that remaining per-row copy.

## Primary-source research reviewed on 2026-07-18

Vim documents wrapping search as ordinary repeated-search behavior when
`wrapscan` is enabled and makes boundary crossing visible. Sublime Text's
official API likewise exposes a `WRAP` flag for search. The common useful lesson
is not that Micromax needs another option. It is that repetition can remain a
loop while the boundary is explicitly reported.

- Vim pattern/search documentation: https://vimhelp.org/pattern.txt.html
- Vim options documentation: https://vimhelp.org/options.txt.html
- Sublime Text API reference: https://www.sublimetext.com/docs/api_reference.html

Micromax chooses a fixed wrapping loop because the transcript showed a broken
ordinary path, not competing user requirements. A toggle would add state,
documentation, completion, persistence, tests, and disagreement between users
without repairing any additional observed failure.

## Evidence

Focused journeys cover:

- forward/backward and initial-find wrapping with exact messages;
- sole-match no-op truth;
- newline-starting progression;
- overlap agreement;
- original-coordinate Unicode behavior;
- adjacent regex and zero-width policy;
- cross-line current/all-match projection;
- softwrap and horizontal-scroll anchor integrity;
- mutation-stale and cross-buffer snapshot rejection;
- one search scan for status plus highlight in a composed screen.

Adjacent editor-core, active-search authority, plugin containment, TUI highlight,
selection precedence, screen-layout, contract, and independent-consumer slices
also pass. Structural/effect audits and compilation pass. `mypy` is unavailable
in the offline cloudtainer, so no typecheck pass is claimed. No complete
repository-suite claim is made.

## Residual risk and next speculation

- Direct editor regex evaluation is synchronous Python `re`. A catastrophic
  expression can still block navigation or screen assembly. The VM hostcall
  layer already demonstrates worker/time-budget containment, but putting process
  work into an every-screen path would be expensive. First capture and measure a
  real editor stall, then choose among a safer engine, explicit regex budget,
  worker, or refusal threshold.
- Newline-only matches have no dedicated visible cell. Their adjacent source
  fragments can be projected, but a pure newline has zero printable row width.
- Coordinates remain Python code points rather than grapheme clusters or
  terminal cells.
- Ignore-case literal search is coordinate-preserving but not full Unicode
  case-fold equivalence.
- Search remains active-buffer navigation, not workspace/project results.
- The active query remains editor-global across buffer switches. That may be
  correct, but the next buffer/recent/project transcript should test whether the
  query, cursor target, and return path remain understandable.

The next likely high-value product risk is movement among open buffers, recent
files, and the bounded project picker. Capture that loop before adding workspace
search, result panes, watchers, symbols, or indexing.
