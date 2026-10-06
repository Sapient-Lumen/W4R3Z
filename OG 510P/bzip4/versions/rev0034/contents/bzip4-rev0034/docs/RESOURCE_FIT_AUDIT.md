# Allocation-free resource fitting audit — rev0033

## Purpose

Large BZ3v1 blocks and high lane counts can each be individually legal while
their product is inappropriate for a cloudtainer. rev0033 adds an allocation-
free planning API and opt-in command paths that fit scheduling concurrency to an
explicit codec-workspace budget before any codec state or worker thread exists.

This does not silently change block size. Block size changes serialized bytes
and remains the caller's explicit parameter. Only lane count is reduced, and
lane count is scheduling-only for BZ3v1.

## API

`include/bzip4/resource_plan.hpp` exposes:

```cpp
ParallelResourcePlan plan_parallel_resources(...);
CompressionResourcePlan plan_parallel_compression(...);
ParallelResourcePlan plan_parallel_decompression(...);
```

A plan reports:

- requested and effective block size;
- validated block count and logical bytes;
- requested lanes;
- useful lanes after the block-count limit;
- per-lane workspace bound;
- strict workspace for all useful requested lanes;
- lane capacity under the supplied budget;
- selected lanes and selected workspace;
- whether work or workspace caused the reduction; and
- whether at least one lane fits.

The planner uses checked multiplication, enforces the retained-pool safety limit
of 257 total lanes, and calls the same `workspace_memory_bound()` and frame-bound
logic used by production codec paths. Empty frames require zero lanes and zero
codec workspace.

## Command surface

```text
bzip4_codec plan INPUT_SIZE BLOCK_SIZE LANES [MAX_WORKSPACE_BYTES]

bzip4_codec compress-fit INPUT OUTPUT BLOCK_SIZE LANES \
    MAX_WORKSPACE_BYTES [SERIALIZE_READS(0|1)]

bzip4_codec decompress-fit INPUT OUTPUT MAX_OUTPUT_BYTES \
    MAX_WORKSPACE_BYTES LANES [SERIALIZE_READS(0|1)]
```

`plan` prints schema `bzip4.compression-resource-plan.v1` as one JSON object.
It performs no input I/O and allocates no codec state.

`compress-fit` computes the complete frame shape first. `decompress-fit`
validates the complete frame envelope with fixed-size reads first, obtains the
smallest legal decoder block size, and then fits lanes. Both commands reject the
operation before creating the atomic destination if one lane does not fit.

The pre-existing `compress` and `decompress` commands remain strict. When the
caller explicitly requests lanes that exceed the workspace budget, those paths
fail rather than silently changing policy. This preserves a clear distinction
between strict admission and realization-local fitting.

## Workspace frontier

Measured exact per-lane bounds include codec state and scratch:

| Block size | Per-lane workspace |
|---:|---:|
| 128 KiB | 2,000,518 bytes |
| 256 KiB | 2,802,676 bytes |
| 512 KiB | 4,406,998 bytes |
| 1 MiB | 7,615,642 bytes |
| 2 MiB | 14,032,930 bytes |
| 4 MiB | 26,867,500 bytes |
| 8 MiB | 52,536,640 bytes |
| 16 MiB | 103,874,920 bytes |
| 32 MiB | 206,551,480 bytes |
| 64 MiB | 411,904,606 bytes |
| 128 MiB | 822,610,852 bytes |
| 256 MiB | 1,644,023,350 bytes |
| 511 MiB | 3,280,431,052 bytes |

A nominal three-gigabyte ceiling cannot admit even one maximum-size lane. More
importantly, a responsible embedding budget must reserve memory for Datacube,
thread stacks, allocator metadata, descriptors, input/output staging, page
cache, and concurrent operations. `max_workspace_bytes` charges only bzip4
codec arenas; it is not a whole-process or whole-cloudtainer cap.

## Exact-byte fitting witness

On the 546,406,400-byte combined current-session stream, 64 MiB blocks and eight
requested lanes require 3,295,236,848 charged bytes for all eight lanes. Under a
2,800,000,000-byte codec budget the planner selected six lanes and charged
2,471,427,636 bytes.

`compress-fit` produced 30,279,230 bytes exactly identical to an explicit
six-lane encoding. `decompress-fit` reconstructed the source exactly. The
measured process RSS was about 1.20 GiB in each direction; this lower observed
RSS does not weaken the conservative preallocation charge.

A budget of 411,904,605 bytes—one byte below the 64 MiB one-lane requirement—
failed with codec error `BZ3_ERR_DATA_TOO_BIG` and published no destination.

## Datacube policy guidance

Do not compile “3 GB” into semantic codec law. Datacube already distinguishes
environment observation, operator policy, and effective policy. The embedder
should calculate a codec-workspace allowance after its reserve and aggregate
heavy-operation limits, then pass that number to the planner.

For the current speed profiles, a conservative 128 MiB codec budget admits:

- eight 256 KiB lanes: 22,421,408 bytes;
- eight 512 KiB lanes: 35,255,984 bytes;
- eight one MiB lanes: 60,925,136 bytes; and
- eight two MiB lanes: 112,263,440 bytes.

This avoids consuming the cloudtainer ceiling merely because it exists. Larger
blocks should be explicit ratio experiments with a separately approved budget.

## Safety and nonclaims

The planner does not measure current RSS, discover cgroups, reserve address
space, or promise that the operating system can satisfy an allocation. It is a
checked codec-workspace admission calculation. The embedder remains responsible
for process-wide and aggregate policy.

Machine-readable regression evidence is in
`evidence/resource-fit-regression.json`. Dedicated unit tests cover empty input,
work-limited lanes, workspace-limited lanes, impossible budgets, lane-limit
validation, decoder workspace consistency, and contracted decoder planning.
