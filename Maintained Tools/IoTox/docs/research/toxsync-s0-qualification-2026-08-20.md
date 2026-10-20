# toxsync S0 qualification evidence

Date: 2026-08-20

Scope: preserved `components/toxsync` 0.7.0, still not linked into the IoTox daemon.

## Source matrix

`tools/build-toxsync-matrix.sh` passed on the founding bare-metal host with:

- GCC 15.3 debug;
- GCC 15.3 release;
- GCC 15.3 portable release using builtin C++ SHA-256 and scalar rolling checksums;
- Clang 21.1.8 debug;
- Clang 21.1.8 ASan/UBSan.

Each lane ran both native CTest routes. The component registry remains 121 native checks per lane.
The retained marker was:

```text
toxsync-source-matrix=pass
```

## Fuzz smoke

The same script now builds a dedicated Clang ASan/UBSan fuzzer lane and ran each target for 5,000
units:

```text
toxsync_wire_fuzzer:     cov=427 ft=615 rss=176MiB
toxsync_metadata_fuzzer: cov=424 ft=645 rss=59MiB
toxsync_files_fuzzer:    cov=313 ft=393 rss=191MiB
```

Coverage routes:

- wire: mutable HEAD summary/query/receipt, range requests/responses, content inventory, exact
  availability, range indexes, and reconnect capability records;
- metadata: signed index records and conservative content-availability records;
- files: flat manifests, paged manifests, treepack records, index files, and pin journals.

This is a bounded smoke gate, not long-running fuzz qualification. It proves the decoders survive the
current corpus and mutation surface under sanitizers for the configured budget.

## Measurement

The current positive bulk evidence favors the content-addressed paths:

```text
flat content-v2, 8 MiB:
  basis-build-mib-per-second=329.924
  target-build-mib-per-second=572.506
  reconstruct-mib-per-second=801.683
  target-reuse-percent=98.421
  workspace-resident-bytes=1376256
  peak-rss-kib=10432

large range-index smoke, 8 MiB:
  index-mib-per-second=836.193
  sync-mib-per-second=659.545
  sync-fetched-bytes=8192
  sync-source-ranges=2

flat content-v2, 16 MiB:
  basis-build-mib-per-second=223.829
  target-build-mib-per-second=270.550
  reconstruct-mib-per-second=486.538
  target-reuse-percent=99.210
  workspace-resident-bytes=1376256
  peak-rss-kib=10176

large range-index smoke, 16 MiB:
  index-mib-per-second=732.634
  sync-mib-per-second=509.159
  sync-fetched-bytes=16384
  sync-source-ranges=4

paged content-v2 fabric, 16 MiB, 16 peers:
  reconstruct-mib-per-second=399.181
  target-reuse-percent=99.561
  inventory-chunks-per-second=164051.980
  scheduler-assignments-per-second=2548904.301
  scheduler-completed-bytes=268435456
  scheduler-resident-bytes=295520
  availability-adds-per-second=41049240.407
  availability-probes-per-second=45740318.946
  availability-estimated-fpr=0.001
  peak-rss-kib=9968
```

The older `toxsync_bench` delta lane timed out without producing a completed result at 1 MiB, 8 MiB,
and 16 MiB under the bounded harness used for this report. Treat that as a current S0 finding:
content-v2 and large range-index paths have usable positive smoke evidence, while the legacy delta
bench is not yet a bulk qualification path and must be isolated, redesigned, or replaced before it can
support product limits.

## Nonclaims

This report does not claim:

- IoTox daemon integration;
- synchronization protocol framing;
- remote HEAD acceptance;
- authority-ledger sync capability enforcement;
- power-loss recovery of IoTox sync state;
- Sandwurm two-node convergence;
- production throughput under Tox file transfer;
- long-duration fuzz coverage.

S0 is closed for keeping the preserved component independently green. S1 remains responsible for
IoTox-owned namespace policy, durable accepted state, authority binding, and restart recovery.
