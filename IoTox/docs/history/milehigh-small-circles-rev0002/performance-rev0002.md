# rev0002 performance record

## Environment

The canonical package was built in the recorded Linux x86-64 container with GCC 14.2.0 release optimization. Exact compiler, kernel, and dependency output is retained under `artifacts/reports/`.

The benchmark command was:

```sh
./build/gcc-release/iotoxmutorr_bench \
  --nodes 30 --namespaces 200000 --rounds 5
```

## Measured result

```text
nodes=30
namespaces-per-round=200000
rounds=5
cube-build-ns-per-op=2410.07
cube-build-ops-per-second=414925.02
custodian-select-ns-per-op=2204.31
custodian-select-ops-per-second=453656.77
head-evaluate-ns-per-op=43.59
head-evaluate-ops-per-second=22939893.74
checksum=9326512983994446362
```

The placement measurement uses `custodian_indices_into` with a caller-owned three-element array. It includes scoring all 30 members and maintaining the top three candidates, but performs no heap allocation and no full sort per namespace.

The Cube construction measurement includes sorting 30 fixed-size IDs and constructing the flat four-neighbor adjacency. It does not include the diagnostic all-pairs diameter calculation.

## Topology result

```text
members=30
max-degree=4
cube-edges=60
full-mesh-edges=435
edge-reduction-percent=86.21
diameter-hops=8
```

A 4,096-namespace deterministic sample assigned 12,288 total custodian slots across 30 members, with observed per-member load from 374 to 456.

## Interpretation limits

These are microbenchmark results, not end-to-end network throughput. They exclude toxcore iteration, encryption, sockets, gossip queues, signatures, hashing, disk, Merkle traversal, and file transfer. Re-run on target hardware and measure memory, wakeups, traffic, thermal throttling, and power before choosing final defaults.
