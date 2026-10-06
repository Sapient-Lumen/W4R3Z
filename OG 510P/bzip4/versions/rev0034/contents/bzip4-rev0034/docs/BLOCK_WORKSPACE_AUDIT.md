# Block workspace ownership and initialization audit

## Scope

rev0025 audits the lowest compatible block boundary: where a completed BZ3v1
block resides, how long that storage remains valid, and which codec scratch
ranges actually require initialization. The wire format and public bzip3 C ABI
remain unchanged.

The production C++ `Workspace` previously called the public in-place C block
functions. Those functions must always return their result in the caller's
buffer, so transform models whose final bytes naturally reside in the retained
swap arena paid a final `memcpy`. The internal codec now returns a
`Bz3BlockView`; the public C wrappers still copy when required, while
`Workspace` publishes the workspace-owned span directly.

## Borrowed-view contract

`src/codec_core.hpp` is an internal, non-installed contract. A successful view
contains a non-null pointer and exact signed block length. Its storage is one of:

- the caller buffer; or
- the codec state's retained swap buffer.

The view is valid only until the next operation on the same state. Callers must
consume or copy it before state reuse. Public `bz3_encode_block` and
`bz3_decode_block` retain their historical in-place behavior and never expose
this lifetime.

The transform parity is deterministic for ordinary coded blocks:

| model | transforms | final internal location | borrowed from state |
|---:|---|---|---|
| 0 | BWT only | caller buffer | no |
| 2 | LZP + BWT | retained swap buffer | yes |
| 4 | mRLE + BWT | retained swap buffer | yes |
| 6 | mRLE + LZP + BWT | caller buffer | no |

Strict tests force all four models, compare exact encoded bytes with the
independently compiled pristine bzip3 1.5.3 oracle, verify the public in-place
boundary, and reuse one encoder and decoder across three complete model cycles.

## Initialization audit

The audit separated three superficially similar clears:

1. **State-construction suffix-array clear.** Encoding treats the libsais array
   as output/workspace, and decoding initializes its active inverse-BWT range
   immediately before use. The full allocation clear in `bz3_new` was redundant
   and is removed.
2. **Inverse-BWT output clear.** libsais writes all `n` output bytes on success.
   Clearing the destination before `libsais_unbwt` was redundant and is removed.
3. **Inverse-BWT pointer-table clear.** This clear is required. The vendored
   inverse BWT uses one-based pointer entries spanning `[1, n]` and deliberately
   leaves the sentinel link at zero. Removing the clear exposed a malformed-
   descriptor crash in the existing corruption sweep. rev0025 therefore does
   not erase this dependency; it narrows the clear from the whole configured
   `BWT_BOUND(block_size)` allocation to exactly `n + 1` entries.

The distinction matters: "libsais overwrites its workspace" is true for forward
BWT, but is not a valid blanket statement for inverse BWT.

## Poison proof configuration

`-DBZIP4_POISON_CODEC_WORKSPACE=ON` fills the retained byte arena and complete
suffix-array allocation with non-zero patterns before forward BWT and inverse
BWT. Immediately before inverse BWT, only the required `n + 1` pointer-table
prefix is reset to zero; its allocation tail and the output destination remain
poisoned.

The complete strict suite passes in this configuration. This proves that:

- forward BWT does not depend on zero-initialized suffix-array storage;
- inverse BWT does not read the allocation tail beyond `n + 1`;
- inverse BWT overwrites every published output byte; and
- state reuse across models does not depend on stale zeros.

The poison option is a diagnostic gate, not a production performance mode.

## Representative accounting

Across the 18 external regular-datacube type specimens used for validation,
1 MiB framing produced 104 blocks. Models 2 and 4 occurred in 47 blocks. On one
encode plus decode pass, internal borrowed publication avoids:

- 44,246,088 encoded bytes of final block copying; and
- 49,283,072 decoded bytes of final block copying.

For one decode pass, the old explicit clears wrote 521,489,632 bytes. The exact
active-prefix clear writes 338,019,488 bytes, avoiding 183,470,144 clear bytes
(35.18%). A newly constructed 1 MiB workspace also avoids a 4,278,828-byte
full suffix-array clear.

These figures are deterministic operation accounting, not measured bandwidth
or elapsed-time claims. Five balanced atomic-file decode pairs on each of two
representative specimens did not establish a speed gain: rev0025 medians were
9.62% and 6.56% slower on this host. The optimization is therefore promoted as
an ownership and memory-traffic refactor, not as a universal or specimen-level
throughput improvement.

## Rejected adjacent experiment

A generation-tagged LZP reset prototype was not promoted. Its extra tag lookup
sat in the match hot path, and initial local measurements did not establish a
net gain. The roadmap keeps sparse/reset alternatives open, but requires a
representative compatible-byte and timing gate before source promotion.
