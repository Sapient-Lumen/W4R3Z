# Rev0997 audit — shallow query-replace source and segmented literal planning

## Priority chosen

Rev0996 named delayed query-replace's complete immutable planning source as the
next locally measurable risk. That source survived for the full confirm-each
interaction even though ordinary literal answers needed only stable coordinates,
one exact current slice, monotonic line geometry, and a stale-boundary oracle.
Rev0997 reproduced the retained duplicate, removed it, and audited the adjacent
coordinate/search and plugin-cleanup paths. It does not add a rope, piece tree,
registry, watcher, background index, or second document model.

## Severe waste corrected

The permanent three-sample case uses 16,777,279 characters over 258,112 lines
with exactly one literal match. The rev0996 complete-string reference retains all
16,777,279 source characters and records 16,777,903 bytes traced current and
16,778,847 bytes traced peak. The product path retains no complete source string,
shares every original line object, avoids `Buffer.get_text()`, and records
4,224,717 bytes traced current and 5,306,573 bytes traced peak.

That is a 100% reduction in retained complete-source characters, 74.820% lower
traced retained allocation, and 68.373% lower traced peak. The exact edit row is
unchanged. These are local CPython `tracemalloc` facts, not RSS, native heap,
allocator-arena, or portable latency bounds.

## Correction

- `QueryReplaceSourceSnapshot` retains the exact shallow immutable line tuple,
  canonical length, and one packed unsigned-64-bit line-start vector.
- Literal planning scans exact canonical coordinates in bounded 256 KiB windows
  with `len(search)-1` overlap. It preserves Python `re.escape`, `finditer`, and
  Unicode `IGNORECASE` semantics without a full joined source.
- Regex planning keeps the current killable worker and may flatten once
  temporarily, but the delayed session retains only the shallow source witness.
- Initial and next-match geometry project through the witnessed packed starts;
  query-replace no longer performs a redundant live-buffer prefix walk and
  materializes only the exact planned match text.
- Exceptional sparse-history authentication replays and compares line vectors;
  it no longer flattens the session source or live buffer.
- The existing compact read-only `PackedOffsets` owner moved from `search.py` to
  the shared `textpos.py` coordinate layer and remains the same public search
  type.

Development profiling also rejected two superficially cleaner variants. One
Python-level chunk per line was about five times slower under the evidence
harness, while exact-size packed-array preallocation saved only about 90 KiB and
roughly doubled planning time. The final fixed-window/append-built design follows
the measured product path.

## Evidence

The rev0997 focused union covers query-replace lifecycle, stale generation and
local-slice authority, sparse undo/redo, plugin cleanup rollback, search
navigation/authority, replacement budgets, and text-position helpers. New tests
add randomized Unicode differential scanning down to one-character chunks,
patterns spanning many chunks and line breaks, mutable-vector detachment,
shared-object/deepcopy shape, regex temporary-source disposal, literal
no-flattening, stale-boundary no-flattening, and executable measurement checks.

The behavioral union passes 175 tests. The living-doc/context contract passes
32 tests, the structural-audit file passes 4, and the revision-archive contract
passes 53. The finite health lane also passes generated context/effects, lint,
172 portability cases, and the bounded doctor preflight. These are focused and
finite checks, not a completed 3,545-test full-suite claim.

The permanent artifact is `.artifacts/rev0997-qreplace-source.json`, SHA-256
`e951139453caeba28448e99b7ee037356db27b77044b3b6d83f25884d6047b19`.
Full implementation rationale, primary online sources, tradeoffs, and residuals
are in `docs/955-segmented-query-replace-shallow-source-audit.md`.

## Residual risk and next work

- The configured hosted release/attestation lane still needs an executed run,
  retained-subject download, and consumer verification; Windows/macOS receipts
  remain unproved.
- The source witness remains O(lines): about 2.06 MiB for tuple pointers and 2.06
  MiB for packed starts in the measured 258,112-line case.
- Regex begin still creates one temporary complete source for the worker.
- Dense query-replace still retains one planned edit object per match up to its
  ceiling.
- Aggregate history also retains O(lines) shallow generations, and one huge
  changed logical line remains O(line length).

The next query-replace change should follow measured regex-begin or dense-plan
pressure, not conceptual completeness. The next project-level finish line is
executed hosted provenance, not more publication doctrine.
