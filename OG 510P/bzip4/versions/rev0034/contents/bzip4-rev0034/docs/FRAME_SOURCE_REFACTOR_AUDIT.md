# Frame-source parser refactor audit

rev0024 removes the second independent BZ3v1 envelope parser from the parallel
decoder design. Scalar inspection, scalar decode, vector decode, and retained-
parallel decode now consume one internal `frame_source` module.

## Shared parser boundary

`scan_frame_source()` accepts only a declared source size and exact random-
access callback. It performs a complete constant-metadata pass before decoding:

- exact five-byte `BZ3v1` magic and legal 65 KiB through 511 MiB block size;
- a block-count feasibility bound derived from the minimum legal record size;
- checked per-workspace memory policy for every non-empty frame;
- signed descriptor decoding, compressed/original block bounds, and source
  range containment using subtraction-safe arithmetic;
- raw-block length agreement and regular-block model-bit validation;
- bounded LZP/RLE intermediate sizes, BWT primary-index shape, and a required
  arithmetic-coded payload prefix;
- checked cumulative decoded bytes, encoded payload bytes, and output budget;
- explicit trailing-byte accounting and policy.

The scan reads one 13-byte frame header and one at-most-25-byte descriptor/model
probe per block. It retains only `FrameInfo`; memory does not grow with an
attacker-controlled block count.

## Second-pass cursor

`FrameBlockCursor` is the sole descriptor replay mechanism. It retains the
current source offset, output offset, encoded total, and block ordinal. Each
`next()` rereads one descriptor, rechecks local bounds, and refuses any shape
that would exceed the totals established by the scan. `require_complete()`
requires exact block count, cumulative encoded and decoded sizes, final cursor,
and trailing-byte agreement.

The cursor does not authenticate an arbitrary callback or preserve a per-block
snapshot. The public range contract therefore requires stable source bytes.
This is explicit rather than hidden: constant metadata and arbitrary mutable
callbacks cannot simultaneously provide snapshot identity without another
trusted capability or an additional full-source digest/pass. Filesystem tools
supply that capability with descriptor pinning and post-read fingerprint
verification before atomic publication.

## Refactor invariants

The extraction keeps format constants and source-offset conversion in one
place. Scalar and parallel paths cannot independently drift on signed sizes,
model probes, intermediate transform bounds, trailing policy, or aggregate
accounting. Span input is adapted through `span_reader()` and follows the same
source code as range-backed input.

The regression matrix exercises malformed magic and counts, truncated
records/payloads, negative and oversized descriptors, raw/model/intermediate
shape errors, output/workspace budgets, trailing policy, thousands of tiny
records without proportional parser metadata, and a descriptor mutation
between scan and cursor. Parallel output and output-budget failures are required
to produce zero sink callbacks when rejected by the complete scan or the first
collected descriptor batch.

## rev0027 envelope-plan consolidation

rev0027 moves block-envelope validation out of this scanner into the allocation-
free `frame_envelope` module shared with the public high-level C API and the
encoders. The scanner now accumulates separate direct block-size and
`bz3_bound` capacities, derives the exact smallest legal decoder state, and
applies the workspace budget to that state rather than the frame declaration.
The O(1)-metadata and second-pass cursor contracts are unchanged.
