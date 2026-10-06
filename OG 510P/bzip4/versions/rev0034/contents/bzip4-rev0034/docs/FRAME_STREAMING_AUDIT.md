# Frame streaming and metadata audit

rev0021 introduced ordered sink APIs to remove full output-frame
materialization. rev0022 completed the production path with stable
random-access input, so the CLI materializes neither the complete source nor the
complete result. rev0024 moves the security-sensitive frame-source parser into
one internal module shared by scalar and parallel decode.

## Encoding

`Workspace::encode_frame_to` and `compress_frame_to` adapt spans to the same
range-backed implementation used by `encode_frame_from` and
`compress_frame_from`. The encoder emits:

1. the 13-byte frame header;
2. one 8-byte descriptor per block;
3. the corresponding encoded payload.

All shape arithmetic, block-count representability, and the whole-frame bound
are checked before the first callback. Each source block is read directly into
reusable codec scratch. Each payload span aliases that scratch and is valid only
during its callback. Tests require byte identity between vector, span-sink,
range-sink, and compatible retained-parallel forms.

## Decoding

Both scalar and retained-parallel decoding deliberately perform two passes over
stable random-access bytes through `detail::scan_frame_source` and
`detail::FrameBlockCursor`:

1. validate magic, block size/count, descriptor signs and bounds, all payload
   ranges, every model prefix, cumulative output, workspace budget, and
   trailing-byte policy;
2. reread descriptors, reconcile the validated aggregate shape, decode bounded
   payload batches, and publish in exact block order.

The first pass uses one 13-byte header read and one at-most-25-byte contiguous
probe per block. No descriptor vector proportional to attacker-controlled block
count is allocated. The minimum legal record size bounds iteration from actual
frame length, and a 4,096-empty-block regression confirms parser metadata memory
is a function of block size rather than block count.

The scalar decoder retains one descriptor and one payload workspace. The
parallel decoder retains at most one descriptor and one codec workspace per
retained lane, waits for a complete bounded batch, and synchronously publishes
each workspace view before reusing it. The complete envelope is known before
the first decoded callback.

A later checksum, source-stability, or transform error can nevertheless occur
after earlier blocks were delivered. Callers needing all-or-nothing publication
must stage callbacks and commit only after decoder success and source
revalidation.

## Current boundary

The generic range callback is a contract, not an authenticated snapshot. It
must fill every requested span and expose stable bytes. Concurrent parallel
calls also require concurrent exact-read support unless the serialized-reader
adapter is selected. The filesystem CLI provides the stronger practical
boundary by retaining one `O_NOFOLLOW` descriptor, using positional reads,
rechecking size/mtime/ctime, and committing a same-directory temporary only
afterward.

## rev0027 metadata agreement

Serial and parallel encoders now accumulate decoder requirements directly from
each generated block envelope. Returned `FrameInfo` therefore reports the same
smallest legal decoder state as an independent later scan, without rereading the
payload or changing emitted bytes. The `bzip4_codec inspect` JSON schema is v2
and includes `decoder_block_size` beside the declared `block_size`.
