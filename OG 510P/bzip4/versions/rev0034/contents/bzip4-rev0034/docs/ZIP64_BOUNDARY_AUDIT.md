# ZIP64 boundary audit — rev0030

rev0030 completes bounded single-disk ZIP64 admission and repairs the local
size-pair interpretation. It resolves structure needed for local-record
inspection without allocating from untrusted 64-bit member sizes or extracting
payloads.

## End-record chain

A terminal classic EOCD is located with exact comment coverage. When sentinels
require ZIP64, the immediately adjacent 20-byte locator must reference a
readable ZIP64 EOCD ending exactly at that locator. A ZIP64 end record without
legacy sentinels is accepted only when the referenced record is structurally
plausible, adjacent, and single-disk; this prevents a locator-signature
coincidence in an ordinary comment from selecting ZIP64.

The ZIP64 EOCD contract includes:

- signature, minimum 56-byte record, and checked 64-bit arithmetic;
- complete declared record and bounded extensible-data sector;
- locator and end-record adjacency;
- disk zero, one total disk, and equal per-disk/total entry counts;
- version needed to extract of at least 4.5;
- agreement with every populated legacy EOCD field; and
- an exact central-directory end anchor.

`max_zip64_eocd_bytes` defaults to 1 MiB and includes the extensible-data sector.
Split and spanned archives remain unsupported.

## Central sentinel resolution

Central field `0x0001` is consumed only for legacy placeholders and in this
order: uncompressed size, compressed size, local-header offset, start disk.
Missing, duplicate, trailing, nonzero-disk, and low-version representations are
fatal. All resolved sizes and offsets remain 64-bit through aggregate, method,
range, and overlap accounting.

## Local two-size rule

When either 32-bit local size is a placeholder, the local ZIP64 field contains
both 64-bit sizes. rev0030 accepts either one-sentinel variant when its complete
pair agrees with the redundant ordinary value. It rejects the former
placeholder-only one-value interpretation, redundant mismatch, duplicate
fields, incomplete pairs, and trailing values.

## Data descriptors

Unsigned and signature-bearing descriptors are checked. Ordinary members use
12/16-byte forms; ZIP64 representation uses 20/24-byte forms. ZIP64 extra-field
presence selects the wide form even when logical sizes fit in 32 bits. If an
unsigned descriptor CRC equals `0x08074b50`, both interpretations are evaluated
and the unsigned form is selected with a nonfatal ambiguity note only when both
fully match.

## Regression evidence

The strict `zip_preflight` group covers complete and prefix-truncated ZIP64
fixtures, both descriptor signatures, offset-only central representation,
one-sentinel/two-value local records, malformed one-value fields, redundant
mismatch, bounded extensible sectors, low versions, missing or bad locator/end
records, metadata disagreement, impossible entry counts, descriptor mismatch,
and ordinary-comment locator collisions.

A separately generated 65,536-entry archive uses a real 56-byte archive-level
ZIP64 EOCD and passes bzip4 preflight and independent ZIP integrity checking. A
force-ZIP64 one-entry archive also passes. Across the 18 representative cubes,
2,563 entries use per-entry ZIP64 representation in one archive; all 20,677
entries pass with zero issues.

## Nonclaims

This audit does not support split archives, encrypted central directories,
central-directory compression, payload decompression, CRC recomputation,
authentication, or filesystem extraction. It establishes bounded structural
admission and metadata agreement only.
