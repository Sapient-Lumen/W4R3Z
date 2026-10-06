# Frame-envelope and decoder-workspace contraction audit

## Scope

rev0027 audits the boundary between a validated BZ3v1 frame declaration and the
actual `bz3_state` retained to decode it. A frame's 32-bit block-size field is an
upper bound, not proof that every block needs declaration-sized codec state.
Before this revision, the public high-level C decoder had one private
block-envelope validator and a conservative contraction rule, while the C++
scalar/parallel frame path had a second validator and charged the declaration
for every decoder lane.

That split was a drift risk and made an overdeclared but otherwise valid frame
unnecessarily expensive or impossible under a reasonable workspace budget.

## One shared no-throw envelope contract

`src/frame_envelope.cpp` now owns the constant-metadata rules consumed by:

- the public `bz3_decompress` preflight;
- C++ frame inspection and scalar decode;
- one-shot and retained parallel decode;
- serial and parallel encoders when they report `FrameInfo`.

For each block it validates the raw/regular distinction, model bits, model-header
length, LZP and mRLE intermediate sizes, and BWT primary index. The validator
requires at most the first 17 payload bytes and allocates nothing.

The result separates two capacities that had previously been conflated:

- `block_extent`: bytes constrained directly by `bz3_state::block_size`, namely
  the original decoded block size;
- `bound_extent`: bytes constrained by `bz3_bound(block_size)`, namely the
  compressed payload and LZP/mRLE/BWT intermediates.

This distinction matters because `bz3_bound(n) = n + floor(n / 50) + 32`.
Requiring the state block size itself to be at least every compressed or
intermediate extent is safe but not minimal.

## Exact smallest legal state

After the complete envelope pass, the selector chooses the smallest legal state
size `n` satisfying all of the following:

1. `65 KiB <= n <= declared_block_size`;
2. `n >= maximum original block size`;
3. `bz3_bound(n) >= maximum payload/intermediate extent`.

The third condition is solved with a bounded binary search over the monotonic
per-block bound. Unsatisfiable requirements return zero and are rejected; they
are never silently clamped to the declaration.

The selected size controls both the internal `bz3_state` and its external
scratch buffer. `FrameInfo::decoder_block_size` and
`FrameInfo::decoder_workspace_bytes` expose the resulting per-lane plan.
Empty frames retain zero decoder workspace.

## Scalar, C, and parallel behavior

- Scalar C++ inspection and decode use the contracted state after a complete
  O(1)-metadata scan and before output publication.
- The public high-level C decoder uses the same validator and selector before
  allocating state or mutating output.
- One-shot parallel decode scans first, applies activation policy, and creates
  only contracted lane workspaces.
- `ParallelFrameDecoder` retains its original declaration-sized constructor for
  compatibility and adds an explicit `(declared_block_size,
  decoder_block_size, policy)` constructor. A frame whose validated plan exceeds
  that retained capacity is rejected before the first sink callback.
- Serial and parallel encoders feed their generated block envelopes through the
  same requirements accumulator, so returned `FrameInfo` agrees with a later
  independent inspection without a second payload pass.

The second descriptor pass and low-level block decoder remain defensive. If a
range source changes after preflight, compact workspaces fail safely rather than
trusting stale metadata.

## Deterministic witness

A representative 17,821,567-byte regular-datacube ZIP was framed as seventeen
1 MiB blocks, then only the legal frame declaration was raised to 64 MiB. The
encoded payload remained 15,883,582 bytes and reconstructed exactly.

- declaration-sized rev0026 per-lane workspace contract: `411,904,598` bytes;
- rev0027 selected block size: `1,048,576` bytes;
- rev0027 per-lane workspace contract: `7,615,634` bytes;
- deterministic contract reduction: `404,288,964` bytes, or `98.151117%`;
- four contracted lanes: `30,462,536` bytes, accepted under a 64 MiB aggregate
  budget;
- the declaration-sized predecessor is rejected under that same budget.

These numbers describe checked allocation/budget capacity, not committed RSS.
Allocator laziness and page demand can make physical residency much smaller.
No throughput, compression-ratio, or universal memory claim is made.

## Regression coverage

The strict suite proves:

- exact inverse-bound selection and one-byte predecessor boundaries;
- impossible direct and bounded extents return no plan;
- model 0, 2, 4, and 6 envelopes select and decode through the shared planner;
- scalar C++, public high-level C, one-shot parallel, and compact retained
  parallel decoding reconstruct exactly;
- a one-byte-too-small workspace budget rejects before output;
- a retained decoder smaller than the validated plan rejects before callbacks;
- encoder-reported and independently inspected plans agree;
- valid encoded bytes remain identical to rev0026 on the representative cohort.
