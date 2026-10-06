# High-level C frame API audit

## Findings

The inherited bzip3 1.5.3 high-level functions had several contracts that were
unsafe or incomplete for a production datacube boundary:

1. The final block used `input_size % block_size` unconditionally, losing a full
   block whenever nonempty input was an exact multiple.
2. `bz3_bound` is a per-block expansion formula, not a whole-frame capacity.
   It omits the frame header, per-block descriptors, and independent expansion
   allowances.
3. The compressor trusted a coarse capacity check and then published records
   without checking each addition.
4. The decompressor allocated from the untrusted declared block maximum before
   proving that the declared records could even fit in the input.
5. It decoded and copied early blocks before discovering later structural or
   output-budget failures.
6. High-level encode/decode copied completed blocks through the public low-level
   in-place compatibility boundary even when the internal result already lived
   in retained codec storage.
7. Null `out_size` and related pointer combinations were not guarded.

## rev0026 compressor contract

`bz3_frame_bound(requested_block_size, input_size)` applies the same effective
block-size rule as `bz3_compress`, computes a representable ceiling block count,
and adds with overflow checks:

```text
13-byte frame header
+ full_block_count * (8-byte descriptor + bz3_bound(full_block_size))
+ optional remainder descriptor and remainder bound
```

It returns zero for an invalid request, an unrepresentable BZ3v1 block count, or
size arithmetic overflow. `bz3_bound` itself now saturates at `SIZE_MAX` rather
than wrapping.

`bz3_compress` splits by `min(block_size, input_size - offset)`, checks every
complete record against the caller's remaining capacity before publication,
serializes unsigned frame fields without signed conversion, and consumes the
internal encoded block view directly. Empty input emits exactly the 13-byte
zero-block frame without constructing codec state.

The intentionally defective upstream behavior is no longer reachable through
the public C function. It is reproduced independently only by
`bzip4::compress_frame_upstream_exact` so the oracle regression remains durable.

## rev0026 decoder preflight

Before allocation or output mutation, `bz3_decompress` performs a constant-
metadata scan over the declared records. It checks:

- exact BZ3v1 magic and legal declared block size;
- block count against the minimum 16-byte record size;
- signed descriptor fields, compressed bound, original bound, and payload end;
- raw literal length and descriptor agreement;
- regular model byte, supported model bits, complete model header and entropy
  tail, positive bounded LZP/RLE intermediates, and BWT primary index;
- subtraction-safe cumulative output capacity.

Trailing bytes after the declared block count remain accepted to preserve the
legacy C entry point. The C++ frame APIs reject trailing bytes by default.

Structural and capacity failures leave `*out_size == 0` and do not touch the
output. CRC, entropy, BWT, LZP, or mRLE failures occur during the second pass and
may follow already emitted earlier blocks; callers requiring atomic filesystem
publication should use the bzip4 atomic CLI/library path.

## Descriptor-derived workspace

The declared frame block size is an upper bound, not proof that every block
needs that workspace. During preflight, rev0026 records the largest validated
payload, original size, and transform intermediate. It chooses at least 65 KiB,
uses that validated extent when it is below the declaration, and falls back to
the declared size when a legal expanded payload exceeds the nominal block size.

This preserves every low-level bound while preventing a tiny valid record under
a 511 MiB declaration from forcing a declaration-sized state. The regression
suite decodes a one-byte raw block with that maximum declaration and also proves
that a zero-block maximum declaration allocates no state.

This legacy C API still has no caller-supplied workspace budget. The C++ frame
APIs remain the preferred untrusted-input boundary because they expose explicit
output and workspace budgets, optional trailing-byte rejection, and streaming
or atomic sinks.

## Compatibility and limits

- Non-exact valid public-C frames remain byte-identical to the pristine bzip3
  oracle.
- Exact multiples now match the corrected C++ encoder and reconstruct fully.
- The low-level public C block API remains in-place.
- Input/output overlap is not supported.
- No format, ratio, or automatic parallelism change is introduced.

## rev0027 shared envelope and exact workspace plan

The high-level decoder no longer owns a private copy of the raw/model envelope
rules. It consumes the same no-throw validator as C++ inspection and parallel
decode. Its workspace selector now distinguishes the original-size floor from
payload/intermediate extents covered by `bz3_bound`, and chooses the exact
smallest legal state instead of conservatively treating every extent as a direct
block-size requirement. C ABI, valid bytes, trailing-byte compatibility, and
pre-output structural gating are unchanged.
