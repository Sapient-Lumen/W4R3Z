# ZIP extra-field audit — rev0030

Local and central extra areas are complete TLV streams: two-byte identifier,
two-byte payload length, then exactly that many payload bytes. One shared walker
requires complete headers and in-range payloads while accepting unknown,
well-framed identifiers.

## ZIP64 central fields

A central ZIP64 field is consumed in the conditional order selected by legacy
sentinels:

1. uncompressed size;
2. compressed size;
3. relative local-header offset;
4. start disk.

Every required value must be present exactly once. Duplicate ZIP64 fields,
missing values, trailing values in a required field, a nonzero resolved disk,
and version-needed values below 4.5 are fatal.

## ZIP64 local fields

The local contract differs from placeholder-only central parsing. Whenever
either legacy local size is `0xffffffff`, the ZIP64 field must carry both
64-bit sizes in uncompressed-then-compressed order. Therefore:

- one sentinel plus a complete two-value field is valid;
- the ordinary non-sentinel size must agree with its redundant 64-bit value;
- a one-value field is malformed even when only one legacy field is a sentinel;
- duplicate, missing, incomplete, and trailing-value fields are fatal; and
- a streamed small member using ZIP64 solely for descriptor width must still
  carry one exact local two-size pair.

This audit fixed a placeholder-only interpretation that rejected the valid
one-sentinel/two-value form and could accept malformed one-value records.

## Evidence and nonclaims

Strict tests cover local and central truncation/overrun, unknown fields,
duplicates, every sentinel variant, redundant mismatch, descriptor-only ZIP64,
and complete archive-level ZIP64 fixtures. All 18 representative datacubes pass,
including 2,563 entries carrying local ZIP64 representation.

The parser validates structure and selected ZIP64 semantics. It does not
interpret arbitrary extension meaning, decrypt data, decompress members, or
authenticate payloads.
