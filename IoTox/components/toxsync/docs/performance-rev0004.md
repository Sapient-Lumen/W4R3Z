# rev0004 performance record

The bundled microbenchmark creates a 16 MiB target, derives a related basis, builds a 4 KiB-block index, plans reuse, and reconstructs through `FileRangeSource`.

Recorded GCC release result on the available virtualized x86-64 host:

```text
index throughput: 211.255 MiB/s
basis scan:       264.976 MiB/s
apply:            204.808 MiB/s
reused bytes:      15,097,856
fetched bytes:      1,679,360
missing ranges:           410
verified:                   1
```

The observed process peak RSS was 37,172 KiB because the benchmark itself retained both 16 MiB synthetic input vectors while measuring. It is not a library-only RSS figure. For 4,096 blocks, the central decoded-index/planner structures are approximately 195 KiB before allocator and stream-buffer overhead; artifact contents are streamed.

These measurements are an algorithm smoke baseline, not target-device, Tox, flash, radio, thermal, power, or multi-peer results. Re-run under the pinned Nix environment on each intended IoT class and record CPU cycles, peak RSS, bytes read/written, transfer bytes, startup latency, and interrupted-resume behavior.
