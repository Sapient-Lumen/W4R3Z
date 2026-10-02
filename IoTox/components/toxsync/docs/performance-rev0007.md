# Performance notes — rev0007

## Changes intended to reduce CPU, syscall, and allocator pressure

- reusable v1 and v2 workspaces retain page-rounded buffers across jobs;
- `pread`/`pwrite` replace cursor movement and stream object churn on large paths;
- index and manifest processing are batched;
- v1 uses one bit per current batch block;
- v2 never retains a chunk-count-sized C++ container;
- content-store chunks are no-replace hard-linked from private temporary files;
- IoTox range send/receive keeps the original transfer descriptor alive instead of
  duplicating and closing it for every Tox chunk;
- content-authenticated ranges omit two per-chunk metadata syscalls while ordinary file
  transfer retains source-stability checks;
- caller-visible counters report read/write calls, workspace bytes, and growth events.

## Recorded release medians

Seven independent GCC release processes used a 128 MiB fixture per engine. Raw runs and
minimum/maximum values are retained under
`artifacts/reports/benchmarks-rev0007/`.

```text
v1 bounded large path
  index construction:                 1,125.750 MiB/s
  verified aligned synchronization:   1,075.150 MiB/s
  index explicit workspace:           1,114,096 bytes
  sync explicit workspace:            1,060,896 bytes
  target bytes reused:                 134,090,752
  target bytes fetched:                    126,976
  coalesced source ranges:                      31

v1 adaptive in-memory path
  index construction:                   914.893 MiB/s
  adaptive planning:                   4,331.672 MiB/s
  verified reconstruction:              385.015 MiB/s
  index resident storage:                786,504 bytes
  plan resident storage:                 327,848 bytes
  planner temporary arena:             1,048,576 bytes
  process peak RSS:                       10,860 KiB

v2 content-store preview, 12,345-byte prefix insertion
  basis build:                           373.794 MiB/s
  target build:                          419.919 MiB/s
  verified reconstruction:              628.546 MiB/s
  target-byte reuse:                      99.901 percent
  retained explicit workspace:         1,376,256 bytes
  process peak RSS:                       10,568 KiB
```

The bounded-v1 sync range was sensitive to host scheduling/page cache in one of seven runs
(315.150 MiB/s minimum, 1,096.580 MiB/s maximum); the median is reported rather than the
best run. The v2 reconstruction range was 443.872–657.782 MiB/s.

## Interpretation boundary

These are local, generally page-cached virtual-host measurements with final data `fsync`
disabled inside the benchmark. They compare implementations; they do not predict Tox
throughput, cold-flash behavior, write endurance, relay performance, radio energy, thermal
throttling, or target-board RSS. Real lane selection must use verified network goodput and
retry/stall feedback, not these filesystem numbers.
