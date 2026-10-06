# Compatible checksum-fusion audit

## Scope

BZ3v1 stores a bzip3-specific reflected Castagnoli checksum for the original
block. Before rev0026, every normal encode performed a complete checksum scan
and then immediately performed a second complete mRLE analysis scan. Decode
reconstructed the final bytes and then scanned them again for CRC regardless of
which final transform produced them.

rev0026 removes only passes that are provably redundant. It does not change the
polynomial, initial state (`1`), update order, transform selection, model bits,
block headers, or encoded bytes.

## Encode path

Every block of at least 64 bytes already enters mRLE analysis before optional
LZP, BWT, and entropy coding. The analysis reads every source byte exactly once
to score symbol runs. `mrlec_with_crc` now applies the existing table update to
that same byte before the analysis state advances and returns both encoded mRLE
size and CRC.

The CRC is therefore available even when mRLE is rejected, and the old
standalone `crc32sum` pass is unnecessary for all normal models 0, 2, 4, and 6.
Blocks below 64 bytes bypass mRLE and retain the small raw-path scan.

## Decode path

The final output producer depends on the model:

| Model | Final producer | rev0026 CRC behavior |
| --- | --- | --- |
| 0 | inverse BWT output | retained final scan |
| 2 | LZP reconstruction | fused byte-by-byte update |
| 4 | mRLE reconstruction | fused byte-by-byte update |
| 6 | mRLE reconstruction after LZP | fused byte-by-byte update |
| raw | literal move | retained small scan |

The templated LZP decoder instantiates tracked and untracked paths, so model 6
does not waste CRC work on its intermediate RLE stream. mRLE publishes its CRC
only when the requested original byte count is reconstructed. Size and model
validation still precede the final checksum comparison.

## Correctness gates

- Independent pristine-C oracle identity for valid encoded blocks.
- Exact model 0/2/4/6 round-trip.
- Deliberate checksum corruption rejected as `BZ3_ERR_CRC` for every model.
- Workspace poison, ASan/UBSan, ThreadSanitizer, GCC, and Clang gates.
- Full 18-archive type cohort byte-identical to rev0025 and exactly decoded.

## Representative operation accounting

The 18-archive cohort contains 98,376,644 bytes in 104 normal blocks. Encoding
avoids a CRC-only scan of all those bytes. Models 2, 4, and 6 account for
83,696,580 decoded bytes, so decode avoids the standalone final scan for
85.077694% of cohort output. The 14 model-0 blocks account for the retained
14,680,064-byte scan.

These figures count calls no longer made over logical bytes. They do not claim
an equal reduction in cache misses, memory traffic, wall time, energy, or RSS.
BWT and entropy work dominate many blocks, and no speed promotion is made.
