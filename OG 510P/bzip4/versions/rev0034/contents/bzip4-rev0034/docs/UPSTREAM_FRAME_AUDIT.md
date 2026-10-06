# Upstream high-level frame audit

## Two containers share the BZ3v1 magic

bzip3 1.5.3's command-line program and high-level C API do not use identical
outer envelopes:

- the CLI writes `BZ3v1`, a 32-bit block size, and then block records until EOF;
- `bz3_compress()` writes the same fields plus a 32-bit block count before the
  records.

bzip4 adopts the second, 13-byte count-bearing envelope. The explicit count is
part of its complete-envelope, cumulative-output, and bounded-work preflight.
Consequently, a native upstream CLI file and a bzip4 file are not directly
command-line interchangeable despite sharing the magic and codec. For the same
partition, inserting or removing the count field aligns the record stream; the
rev0033 direct-binary witness verified complete byte identity after that
normalization across 522 blocks.

The phrase “BZ3v1-compatible” in this project therefore means pristine block
codec identity and use of upstream's count-bearing high-level frame semantics,
not transparent acceptance of both upstream outer containers. A future CLI-
stream compatibility command would need an explicit parser and profile rather
than guessing between the ambiguous same-magic envelopes.

## Exact-multiple final-block defect

The bzip3 1.5.3 high-level compressor computes the block count as ceiling
input-size division. Inside the block loop it then assigns the final block size
as `in_size % block_size` unconditionally.

For a nonempty input that is an exact multiple of the selected block size, the
remainder is zero. The final full block is therefore encoded as an empty block,
and the input offset does not advance across that block.

The rev0021 regression witness uses:

```text
block size:       66,560 bytes (65 KiB)
input size:       133,120 bytes
upstream blocks:  2
upstream decoded: 66,560 bytes
safe decoded:     133,120 bytes
```

Every normal rev0026 encoder, including the public `bz3_compress` C entry point,
uses remaining-byte splitting:

```text
size = min(block_size, input_size - offset)
```

The upstream-exact behavior is independently reproduced only under the explicit
name `compress_frame_upstream_exact`. It is an isolated compatibility witness,
not a call through the public C API and not a safe encoder.

## Whole-frame capacity

`bz3_bound(n)` is a low-level per-block expansion bound. A multi-block BZ3v1 frame also
contains a 13-byte frame header and an 8-byte descriptor per block, while each
block has its own expansion allowance. `frame_bound(input_size, block_size)`
performs checked arithmetic over every block and descriptor rather than using a
single whole-input low-level bound. rev0026 exposes the equivalent checked
calculation to C callers as `bz3_frame_bound(block_size, input_size)` and makes
`bz3_bound` saturate at `SIZE_MAX` on overflow.

## Decoder envelope

The rev0021 parser validates before allocation or block decoding:

- exact BZ3v1 magic;
- legal block size;
- a block count that can fit in the actual bytes at a minimum legal record size;
- nonnegative descriptor sizes;
- per-block compressed and original bounds;
- complete payload ranges and block-local model/header envelopes;
- cumulative output budget;
- estimated codec-state plus scratch workspace budget;
- optional rejection of trailing bytes.

The default decoder workspace budget is 512 MiB. A zero-block frame requires no
codec state regardless of its declared block capacity. The scan stores no descriptor vector, so metadata memory is independent of block
count. Low-level CRC and inverse-transform execution remain the codec's
responsibility and can still fail after an earlier streamed block was emitted.

The legacy public C decoder now performs the same class of structural and
output-capacity preflight before allocation or output mutation, but intentionally
continues to accept trailing bytes and exposes no caller workspace budget. It
contracts its state to the largest validated block extent where safe; the C++
decoder remains the preferred untrusted-input interface.
