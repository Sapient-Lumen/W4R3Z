# Performance notes — rev0008

Seven independent GCC release processes ran the native paged-fabric benchmark with a 128 MiB
basis, a 12,345-byte insertion before the reused basis, a 4,096-chunk scheduler window, and
16 synthetic peers. Every run reconstructed and verified the target.

The scheduler measurement uses the production `ContentFabricSession` storage mode: the
scheduler borrows the already-decoded bounded manifest window instead of copying 4,096
`ContentChunkRef` records. Exact peer availability is transposed into one 32-bit mask per
active chunk, and a fixed-capacity min-heap retains rarest-first order. Rebuilding the heap
uses bottom-up linear heap construction.

Median results on the available virtualized x86-64 host:

```text
basis paged-store build:             376.270 MiB/s
target paged-store build:            437.912 MiB/s
verified reconstruction:             606.918 MiB/s
target bytes reused:                  99.945 percent
exact inventory:                     510,854 chunks/s
scheduler issue+complete:          2,196,649 assignments/s
availability-filter insertion:    50,788,799 items/s
availability-filter probes:       68,584,814 probes/s
explicit content workspace:          655,360 bytes
4,096-chunk/16-peer scheduler:        135,696 bytes
availability sketch:                   1,024 bytes
process peak RSS median:               10,084 KiB
```

Observed min/max ranges and all raw process/time reports are retained in the parent cube under
`artifacts/reports/benchmarks-rev0008/`.

These are local, generally page-cached host measurements with benchmark fsync disabled. The
process also owns fixture-generation and benchmark structures. Results are not evidence of
Tox goodput, cold-flash behavior, relay performance, target-board RSS, radio energy, thermal
limits, or the useful number of concurrent Tox file lanes.
