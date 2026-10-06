# Block decoder contract audit

rev0021 audits the active C++20 translation at the boundary where an untrusted
BZ3v1 block descriptor becomes transform work. The encoded-byte contract for
valid upstream blocks is unchanged; malformed inputs now fail before they can
turn inconsistent metadata into ambiguous output.

## Findings repaired

- Negative compressed sizes are malformed. A compressed size that is valid but
  larger than the caller's supplied buffer is reported separately as
  `BZ3_ERR_DATA_SIZE_TOO_SMALL`.
- The raw-block form (`bwt_idx == -1`) must contain 0–64 literal bytes and that
  literal count must exactly equal the frame descriptor's original size.
- A successful raw encode or decode now clears a stale prior error. Previously,
  a caller could receive valid bytes while `bz3_last_error()` still described an
  older failure.
- Regular blocks reject negative primary indexes other than `-1`, unknown model
  bits, empty-output descriptors, incomplete variable headers, and fewer than
  four arithmetic-coder bytes.
- Arithmetic input exhaustion is recorded rather than silently substituting
  unlimited `0xff` bytes; truncated entropy payloads return
  `BZ3_ERR_TRUNCATED_DATA`.
- LZP and RLE intermediate sizes must be positive and bounded by the codec
  state's transform capacity. The BWT primary index must fit the selected
  intermediate size.
- LZP output is checked against the destination capacity and, when RLE follows,
  against the declared RLE intermediate size.
- Success requires the final decoded size to equal `orig_size`, not merely to
  remain below the state block size. The low-level function returns that exact
  count.
- The high-level decoder accepts legal compressed expansion up to
  `bz3_bound(block_size)` rather than incorrectly capping payloads at the
  uncompressed block size. It uses subtraction-safe input and output range
  checks and verifies the low-level returned count before copying.
- Negative encode sizes are rejected before checksum work, and `bz3_free(NULL)`
  is explicitly harmless.
- Signed 32-bit wire values are serialized through unsigned bit patterns and
  `std::bit_cast`, avoiding implementation-dependent signed shifts/conversions.

## Layering

The C++ frame scanner validates the complete descriptor and transform envelope
before allocating a workspace or invoking a sink. The low-level decoder repeats
critical block-local checks because it remains a public API and cannot assume
that callers used the frame scanner.

CRC, inverse BWT, LZP, and mRLE failures can still occur only after entropy
work begins. This is why streaming decode is a prefix-producing operation and
filesystem publication is staged atomically.

## Regression coverage

The strict test matrix covers raw sizes 0, 1, and 63; the historical 64-byte raw
form; regular blocks; stale-error reset; raw descriptor mismatch; unknown model
bits; negative BWT indexes; truncated entropy payloads; undersized buffers;
negative compressed sizes; exact return counts; moved-from workspace guards; and high-level reconstruction.
The pristine upstream C tree remains a separately compiled valid-stream oracle.

## rev0029 terminal completion

rev0021 made arithmetic underflow observable, but the inherited reader still
returned `-1` as a synthesized byte and the model continued toward the full
declared output. rev0029 closes that remaining work-bound gap: the first missing
bootstrap or renormalization byte stops the decoder. It also replaces permissive
LZP and modified-RLE reconstruction with exact-input/exact-output grammars and
moves the low-level block decoder onto the same parsed `BlockEnvelope` used by
all frame preflights.

Regular BWT indices are now explicitly one-based, structural transform failures
map to `BZ3_ERR_MALFORMED_HEADER`, and checksum failure is reserved for a
structurally complete output. See `ENTROPY_TRANSFORM_AUDIT.md` for the malformed-work
witness and exact terminal rules.
