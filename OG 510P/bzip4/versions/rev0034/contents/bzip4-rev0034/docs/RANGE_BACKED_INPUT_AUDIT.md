# Range-backed input and frame-source audit

rev0022 removes the complete input vector from the production codec path while
retaining rev0021's ordered sinks, complete envelope gate, output budgets, and
atomic publication boundary.

## Source contract

`RangeReader(offset, output)` must fill the complete output span or throw. The
frame APIs validate requested ranges against the separately supplied source
size before invoking it. Bytes must remain stable for the duration of a call.
The generic callback cannot prove that stability; filesystem callers use
`PinnedFile` and recheck its descriptor fingerprint before committing output.

The range API is intentionally random-access rather than a forward-only stream.
BZ3v1 decompression needs a complete envelope pass before the first decoded
callback and a second pass that reads payloads. Random access preserves that
security contract without storing attacker-proportional descriptor metadata.

## Encoding path

`Workspace::encode_block_from` fills reusable codec scratch directly and
encodes in place. `encode_frame_from` invokes it once per logical block and
emits the existing 13-byte header, 8-byte block descriptor, and encoded payload
through the ordered sink. It does not allocate either:

- a vector containing the whole source; or
- a separate caller-side vector for the current block.

The vector-returning and span-backed APIs collect or adapt the same range path,
and the regression oracle requires byte identity among them.

## Inspection and decoding path

The first pass performs fixed-size reads:

1. one 13-byte frame header;
2. one contiguous probe per block containing the 8-byte descriptor and up to
   17 bytes of model prefix.

The 25-byte maximum covers every legal combination of model byte, LZP size, and
RLE size. Descriptor signs, block bounds, payload ranges, model bits,
intermediate sizes, aggregate output, workspace budget, and trailing-byte
policy are all validated before the first decoded callback.

The second pass rereads each 8-byte descriptor, reconciles cumulative original
and compressed totals with the validated frame shape, loads only that block's
payload into reusable workspace, and decodes it. This preserves metadata memory
independent of block count and rejects descriptor drift that violates the
validated cumulative or final shape. Shape-preserving source changes remain a
violation of the stable-source contract; filesystem callers additionally rely
on the pinned fingerprint check, while payload corruption is subject to the
low-level block checksum and decoder checks.

## Publication boundary

A generic sink may receive a valid prefix before a later payload, source, or
sink failure. The CLI therefore writes through `AtomicFileWriter`, calls
`PinnedFile::require_unchanged()`, and renames only after complete success.
Mutation of the opened inode during range encoding is covered by a regression
that leaves an existing destination byte-identical and removes the temporary.

Descriptor fingerprinting is not cryptographic authentication. It detects
ordinary in-place changes through size, mtime, and ctime; it does not establish
author identity or defend against a privileged adversary able to subvert those
filesystem semantics.

## Measured witness

On one external 17,616,777-byte representative ZIP using 1 MiB blocks, rev0021
and rev0022 produced the same 3,028,312-byte stream. Five alternating local
runs measured these medians:

| operation | rev0021 elapsed | rev0022 elapsed | rev0021 RSS | rev0022 RSS |
| --- | ---: | ---: | ---: | ---: |
| compress | 1.86 s | 1.81 s | 30,860 KiB | 13,424 KiB |
| decompress | 1.83 s | 1.82 s | 17,388 KiB | 14,192 KiB |

The RSS reductions are 56.5% and 18.4%. This is a single-host specimen witness;
it is not a universal memory or throughput claim.
