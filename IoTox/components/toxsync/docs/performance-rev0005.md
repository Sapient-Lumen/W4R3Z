# toxsync 0.2.0 / rev0005 performance record

## Method

The comparison uses the packaged rev0004 `toxsync_bench` binary and the final rev0005 portable release build. Seven runs were interleaved and pinned to logical CPU 0. Artifact size was 64 MiB with 4 KiB blocks. In the normal fixture every tenth basis block differed, leaving approximately 90% aligned reuse. Final `fsync` was disabled by both paths; files were local and generally page-cached.

Final rev0005 configuration:

```text
compiler:                       GCC 14.2 release + LTO
SHA-256 backend:                OpenSSL 3.5.5 EVP
rolling-checksum initialization: x86-64 SSE2
index buffer:                    64 KiB
adaptive aligned buffer:          1 MiB
rolling scan buffer:            256 KiB
apply buffer:                    256 KiB
```

## Seven-run medians

```text
operation                       rev0004       rev0005       ratio
index construction             220.846 MiB/s 1105.580 MiB/s  5.006x
planning, exhaustive rolling   297.802 MiB/s  789.944 MiB/s  2.653x
planning, adaptive aligned     297.802 MiB/s 5288.362 MiB/s 17.758x
verified reconstruction        227.042 MiB/s 1247.896 MiB/s  5.496x
```

The adaptive fixture reused 60,395,520 bytes and fetched 6,713,344 bytes. It required 64 basis reads for planning, no rolling pass, and 256 output writes during reconstruction.

## Shifted-basis recovery

A second fixture inserted a 37-byte prefix before an otherwise identical 64 MiB basis. No block remained aligned. The adaptive probe determined that its 85% aligned-reuse threshold was impossible after a bounded prefix, stopped, and entered exhaustive rolling search.

Seven-run median:

```text
planning throughput:            2929.543 MiB/s
aligned bytes examined:         10,485,760
aligned probe aborted early:    yes
rolling passes:                 1
reused bytes:                   67,108,864
missing bytes:                  0
final verification:             passed
```

This demonstrates that the fast path does not remove arbitrary-offset recovery.

## Explicit memory accounting

For 16,384 target blocks:

```text
index resident bytes:             393,288
plan resident bytes:              164,008
adaptive temporary peak:        1,048,576
apply buffer:                      262,144
```

The rolling planner's measured temporary peak on the same fixture was 462,847 bytes because it uses the rolling window buffer plus the temporary weak-checksum table instead of the 1 MiB aligned buffer.

The rev0004 benchmark retained two complete 64 MiB fixture vectors and reported a median process high-water RSS of 136,144 KiB. rev0005 streams fixture creation and reported 10,264 KiB. That process-level change mostly reflects the benchmark harness and must not be presented as a direct library-RSS ratio.

## Backend comparison

The project-owned fallback remains format-identical and tested:

```text
backend                                      index       adaptive plan  apply
OpenSSL EVP + SSE2, portable release         1105.580    5288.362       1247.896 MiB/s
built-in C++ SHA-256 + SSE2                    250.192    5285.589        252.963 MiB/s
built-in C++ SHA-256 + scalar rolling          234.855    5337.234        256.738 MiB/s
```

Planning is governed by the 128-bit discovery hash and rolling/aligned logic, so complete-artifact SHA-256 backend choice mainly affects index creation and verified apply.

A five-run `-march=native` experiment did not produce a general win: index and apply moved only slightly, while adaptive planning was slightly slower than the portable build. The packaged release therefore remains portable; native tuning stays opt-in.

## Buffer tuning

A small buffer sweep showed that larger apply buffers can occasionally raise cached-file throughput, but the runs were noisy and buffers above 1 MiB introduced larger outliers or additional RSS. The 256 KiB default remains the bounded-memory choice; callers can tune it per device and workload. The 64 KiB index buffer and 1 MiB aligned buffer were near the useful plateau on this host.

## Boundaries

These results measure algorithm execution on one virtualized x86-64 host. They do not measure c-toxcore, framing, encryption, packet loss, radio airtime, network latency, flash wear, thermal throttling, or final IoT hardware. The AArch64 NEON source path compiled conditionally but was not executed on this x86-64 host. Raw output, run order, tuning sweeps, tool versions, and `/usr/bin/time -v` records are packaged under `artifacts/reports/`.
