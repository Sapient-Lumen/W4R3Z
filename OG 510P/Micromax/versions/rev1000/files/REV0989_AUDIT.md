# Rev0989 audit — sparse query-replace history and local one-range rebasing

The deep implementation, measurement, research, and residual-risk record is
`docs/946-sparse-query-replace-history.md`.

## Heart of the mission

Confirm-each replacement is ordinary editing. A few-character accepted match
should not copy and rescan a million-character document several times, and one
coherent interaction should remain one exact Undo action. Rev0989 fixes that
measured loop without adding a transaction registry or changing the bounded
match-planning contract.

## Severe corrected waste

The reproduced rev0988 answer path performed `5N - 2` whole-document
materializations for `N` accepted matches and retained complete before/after
history generations. In the permanent 1,100,000-character, 128-match witness:

- answer-time complete materializations fall from 638 to 0;
- materialized answer characters fall from 701,677,312 to 0;
- accounted retained text falls from 2,199,616 B to 771 B (99.965%);
- full-document callback generations fall from 2 to 0;
- traced current Python allocations fall 95.650%; and
- traced peak Python allocations fall 72.542%.

Both paths retain one user-visible row and pass exact full Undo and Redo. Timing
is recorded only as local context.

## Shipped change

A query-replace session now keeps one immutable planning source, initial
sidecars, monotonic source/current mapping state, and exact accepted old/new
slices in source/final coordinate spaces. Ordinary answers validate the existing
identity/version lease plus one local old-text range. Selection advances through
bounded source spans without copying unchanged gaps or materializing the live
buffer.

Finalization emits one `SimultaneousEditWitness`. Undo and Redo validate every
slice before one result commit, preserve unrelated same-width text outside the
addressed ranges, and refuse stale rows without moving history membership.
Exceptional stale/post-hoc boundaries reconstruct the session-owned result from
the source plus sparse witness rather than retaining an owned full generation on
every answer.

## Audit and refactor findings

- One-range edits in multi-cursor buffers still entered the complete-document
  simultaneous planner. They now use one witnessed buffer replacement plus a
  local line/column sidecar mapper; the full planner is reserved for genuine
  multi-range work.
- Advancing between distant planned matches initially sliced the unchanged source
  gap. The cursor helper now uses bounded newline scans and allocates no gap
  copy.
- A retained-history test expected ten independent keystroke rows even though
  rev0988 intentionally groups them. Its injected clock now crosses the grouping
  boundary so it continues to test independent compact-row retention rather than
  disabling product behavior.
- A final adversarial read covered delayed finalization, stale generation paths,
  post-hoc recorded edits, equal replacements, sidecar-only rows, multiline
  mapping, and atomic replay. No broader owner or registry was needed.

## Online evidence

CodeMirror keeps inverse construction tied to the pre-change document;
ProseMirror represents old-to-new position maps; Scintilla groups coherent
editing work into undo actions; and Emacs's `perform-replace` consumes answers
per selected match. Rev0989 adopts those narrow directions while retaining
Micromax-specific bounded planning, identity/version leases, authority, local
old-text validation, and all-slice atomic replay. URLs and retrieval details are
in the deep record.

## Executed evidence

Focused query-replace, simultaneous-edit, cursor-mapping, retained-history, and
measurement tests cover live whole-buffer materialization traps, exact sparse
retention, stale later-slice refusal, unrelated same-width preservation,
multiline/Unicode/skip/delete/equal geometry, 257 mixed decisions, and seeded
local-versus-full-planner differential mapping. Another seeded lane executes 160
complete sessions from randomized nonzero source origins with multiline and
Unicode gaps, skips, deletions, variable-length replacements, and secondary
selection state. The permanent measurement tool reproduces the rev0988 call
shape and rejects either path unless exact Undo and Redo pass.

Final publication validation is recorded by the generated context, structural
audit, effect/resource contracts, doctor lanes, compilation/lint gates, package
policy, and exact archive verifier.

## Missing or still risky

- Initial planning retains one complete source generation.
- Sparse replay constructs one complete current/result generation at Undo/Redo
  time.
- Exact dirty tracking can still hash small documents after accepted mutations.
- Length-changing unrelated edits before recorded offsets fail sparse replay
  closed.
- Touched aggregate rows and specialized line-plan history remain broader.
- Very long logical-line mutation is now the highest-value editing hot path to
  measure.
- `tracemalloc` and logical `undobytes` are not RSS, allocator, native-memory, or
  portable-latency guarantees.
- Signed/hermetic provenance and explicit platform support remain incomplete.

## Highest-value next work

Measure sustained editing in a very long logical line with exact product and
reference oracles. Do not select a rope, piece table, or other text-engine change
before the measurement distinguishes mutation rebuilding from dirty tracking,
rendering geometry, and replay construction.
