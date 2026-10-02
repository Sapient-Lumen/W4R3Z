# Whole-VMM tree-v2 power-cut evidence — 2026-09-04

## Result

One corrected, source-linked, networkless Sandwurm campaign passed a real Cloud Hypervisor
`SIGKILL` after observing raw signed workspace phase byte 2 (`pending-exchange`), then booted a copy
of that exact crash image under a second kernel. Before any recovering Agent started, the two
up-to-date writers exposed the exact successor and the interrupted writer exposed the exact prior
tree. Its journal still carried raw byte 2 and no staging path survived. No hybrid was admitted.
Normal startup preserved identities, converged the successor, retained all writer branches, and
passed repair.

This is one bounded whole-VMM cut. It is not a complete power-cut matrix, a dishonest-storage test,
a physical-host power loss, or permission to use IoTox as the only copy of precious data.

## Reproduction

From a clean checkout on the prepared Sandwurm host:

```sh
./tools/iotox-sandwurm-lab.sh up-sync-power-cut
./tools/iotox-sandwurm-lab.sh verify-sync-power-cut \
  .sandwurm/lab/sync-power-cut/run.4hto8rll
./tools/iotox-sandwurm-lab.sh export-sync-power-cut \
  .sandwurm/lab/sync-power-cut/run.4hto8rll
./tools/iotox-sandwurm-lab.sh verify-sync-power-cut \
  .sandwurm/exports/sync-power-cut/run.4hto8rll
```

The runner creates two independent Sandwurm live-chain proof epochs. It never searches for a VMM by
name alone: the candidate must descend from epoch one's launcher and its argv must contain the exact
task-owned writable runtime disk. PID, `/proc` start time, and NUL-delimited argv SHA-256 are bound
to Sandwurm's final launch receipt.

## Bound identities

```text
source Git commit:  3dcc675a3be41ed8620021762bedc359bbff7d21
product:            IoTox 0.47.0 rev0047
binary SHA-256:     8e62c38c7a042e6f5f1be4126dd20d9b9c5b5d697fcf25efd6b404022157a81e
substrate:          Cloud Hypervisor / KVM, 2 vCPU, 2 GiB, network class none
root image:         24-GiB sparse task-owned disk
first VMM PID:      1275667
first VMM start:    1842639 Linux clock ticks
first VMM exit:     137; ch-remote exit control false
second VMM PID:     1276776
second VMM exit:    0; ch-remote exit control true
copy method:        cp-reflink-always-sparse-auto
campaign elapsed:   435628 ms
```

The boot-ID values are retained only as SHA-256 digests. They differ, proving that recovery crossed a
kernel boot boundary.

## Tree and journal result

The first boot durably recorded both admissible states before arming:

```text
prior:               17 files, 1 directory, 65563 bytes
prior SHA:           f678f55be7b21ee7d42771ec16d07e22203978f463a70f54d294a476b0343a88
completed:           18 files, 1 directory, 33619995 bytes
final SHA:           e1c1515d0faf3e669849a3913cd0fcb3faddb689ae911eedf2d9cee9e6e9bd2d
arm transition:      pending-workspace
arm raw phase:       2 (stable=1,pending-exchange=2)
offline views:       completed, completed, prior
recovered journal:   pending, raw phase 2
recovered stage:     absent
recovery:            1973 ms; branches 3/3/3; repairs 3
```

The first-boot marker was fsynced on the guest disk before the interrupted follower started. The v2
arm crossed virtiofs only after the exact signed-record header decoded to raw byte 2; it did not
request another guest-root flush. Epoch two's runtime-root receipt names epoch one's task-owned
runtime disk as its source, and both Sandwurm launch receipts prove no virtual NIC was attached.

## Compact proof

The raw proof contains sparse disks and private guest state and is not distribution material. The
strict exporter retained ten content-free JSON records totaling 135,819 manifested bytes, plus its
manifest:

```text
proof:             .sandwurm/exports/sync-power-cut/run.4hto8rll
allocated bytes:   217088
campaign SHA-256:  dc7a62c2722df5c58323e08a2606f457cd2cc31cbdcd42e876754166a39d3284
manifest SHA-256:  33b5ae2a0c1bec039059292db0519550f36fcccf49d275caf052dc1cc5520128
contains secrets:  false
```

The independent verifier checks the exact file set and every digest, v2 arm/recovery shape, raw phase
byte and encoding, old-or-new classification, identity and binary binding, VMM PID/start-time/argv
binding, noncooperative first exit, networkless launches, distinct boot IDs, crash-image preseed
lineage, normal second exit, and compact-manifest closure.

## Invalidated predecessor and harness correction

Earlier run `wjlem1i2` crossed a real VMM restart and passed offline-tree, identity, convergence,
branch, and repair checks, but its v1 observer mapped byte 1 to pending and byte 2 to stable, opposite
the C++ enum and signed codec. It therefore armed on stable state. Its workspace-exchange claim and
compact proof were withdrawn; current tooling rejects all v1 proof. The compact artifact was moved
recoverably out of the active evidence tree.

Harness v2 decodes the exact ten-byte signed-record prefix as `stable=1` and
`pending-exchange=2`, includes raw phase byte 2 and that encoding in the arm/campaign, requires a
pending journal even when a stage directory is observed, and cross-checks the recovery label against
its raw phase. Deterministic tests prevent byte 1 from arming. The corrected run above is the first
accepted whole-VMM workspace result.

The first diagnostic attempt also exposed a separate harness dependency: the disposable DHT
bootstrap's key files were zero-length after the cut, so recovery stopped before inspecting IoTox.
Recovery now uses a fresh boot-ID-scoped rendezvous directory while every node disk and identity
remains on the exact crash lineage.

## Remaining boundary

ADR 0333 now qualifies the paired post-exchange side. Repeat the mechanism across the other named
tree-v2 transaction families and their valid old/new linearizations, randomized timing, cold and
near-ceiling populations, sustained write load, and host reset where practical. Separately inject
authenticated-record corruption, exercise open descriptors across remount/exchange, and model
devices that violate flush ordering. Independent backup provenance and restore drills remain
necessary even after those gates pass.
