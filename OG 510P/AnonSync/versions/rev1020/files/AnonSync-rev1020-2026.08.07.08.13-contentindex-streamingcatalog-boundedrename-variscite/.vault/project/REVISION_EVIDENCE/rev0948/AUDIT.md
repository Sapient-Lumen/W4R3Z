# Rev0948 audit record

## Selected product correction

Rev0947's fair scan segment was bounded only by classified bytes. A valid
zero-byte or tiny-file namespace could therefore deliver up to the whole
100,000-entry traversal ceiling, retain one acknowledgement string per path,
and publish one correspondingly large scan-journal transaction.

Rev0948 composes an independent internal 4,096 delivered-regular-file frontier
with the existing byte and whole-walk entry bounds. The check occurs before the
next eligible callback. Successful effects alone advance the in-memory cursor;
all opened directories and the retained root are re-proved before the result
returns; the owner stages paths only after committed effects and publishes the
bounded journal segment once.

## Audit/refactor

The idle fast path no longer allocates and sorts duplicate observed and catalog
path vectors. Per-path unique `File` membership plus complete-traversal
cardinality proves file-set equality; tombstone paths remain explicitly
inspected.

## Runtime evidence

- observer zero-byte continuation: `2 + 2 + 1`, exact cursors and skipped prefix;
- directory substitution at a one-file count frontier fails during rooted unwind;
- folder owner survives reconstruction between zero-byte segments;
- first two-path segment traces two journal INSERTs and one progress UPDATE;
- zero path limit fails before catalog mutation;
- unchanged compatibility and process paths remain covered by the full suite.

## Nonclaims

The count frontier does not bound complete per-directory basename retention,
repeated root-prefix metadata classification, path-local durable-state cost,
namespace mutation into a point-in-time snapshot, or target-scale latency.

The full authority analysis is in
`BOUNDED_SCAN_SEGMENT_FRONTIER_AUDIT_rev0948.md`.
