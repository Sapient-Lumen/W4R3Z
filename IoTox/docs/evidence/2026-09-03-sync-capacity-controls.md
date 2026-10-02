# Synchronization capacity control measurements

- Date: 2026-09-03
- Source commit: `c079584ee3a38e087e3abe7faa263ea2b87f6b72`
- Host: IoTox founding x86_64 machine, Linux 6.12.34
- Binary SHA-256: `a3a70c65534e22ff51494ff80d7d4caa46580fb924bc012876bd9ffc5edc3ff3`
- Status: control measurements pass; representative multi-node capacity gate remains open

## Maximum-entry structural control

The existing owned test `tree-v2 scans stores and projects the maximum ordinary tree` creates 4,096
unique small files and drives the production worktree scan, immutable-object installation, signed
branch creation, merge, and complete projection. It was isolated as registry shard `524/831` and
measured with GNU time 1.10:

```sh
nix develop --command nix shell nixpkgs#time --command time -v \
  build/gcc-debug/iotox_tests \
  --mock-toxcore build/gcc-debug/libtoxcore-iotox-mock.so \
  --mock-argon2 build/gcc-debug/libargon2-iotox-mock.so \
  --wordlist third_party/eff_large_wordlist_2016-07-18.txt \
  --shard-index 524 --shard-count 831
```

Result: one selected test passed in 0.37 seconds wall time with 0.20 seconds user CPU, 0.24 seconds
system CPU, 23,592 KiB maximum resident set, zero major faults, and zero filesystem input blocks.
The test's temporary files are small and hot on the host; this is a structural ceiling control, not
a data-volume or storage-throughput measurement. The shard ordinal is evidence for this exact
commit, not a stable public test identifier.

## Mixed-size source and restore control

A separate synthetic tree used 3,616 unique random regular files in five directories:

| Population | Per-file bytes | Logical bytes |
| --- | ---: | ---: |
| 3,072 small files | 1,024 | 3,145,728 |
| 512 medium files | 65,536 | 33,554,432 |
| 32 large files | 524,288 | 16,777,216 |
| **Total** |  | **53,477,376** |

Selected entries totaled 3,621, or 88.4% of the default 4,096-entry ceiling. One tree occupied
61,440 KiB according to `du`; a disjoint exact restored copy used the same shape. Some files used
owner mode 0400 or 0700 and the rest 0600.

The production commands were measured with explicit 64 MiB/4,096-entry recovery bounds:

```sh
iotox sync-doctor SOURCE read-write 30 owner-mode-v2
iotox sync-recovery-verify SOURCE RESTORED 67108864 4096
```

Doctor returned `decision=ready`, 3,616 files, 3,621 entries, 53,477,376 content bytes, and 3,617
estimated objects. It completed in 0.26 seconds wall time, 0.21 seconds user CPU, 0.04 seconds system
CPU, and 9,312 KiB maximum resident set. Recovery returned `decision=match` for all 53,477,376 bytes
after its alternating double scans. It completed in 1.25 seconds wall time, 1.09 seconds user CPU,
0.14 seconds system CPU, and 18,708 KiB maximum resident set.

`/tmp` was a 48 GiB tmpfs and both processes reported zero filesystem input/output blocks. The
synthetic fixtures were deleted after aggregate results were recorded; they contained no user data
and are not recoverable.

## Evidence boundary and next cell

These controls establish bounded source hashing and exact restore comparison at a useful mixed-size
population, plus an end-to-end structural path at the nominal entry ceiling. They do not measure
durable-media latency, cold-cache behavior, object-store disk amplification for 53 MiB, incremental
rescan cost, conflict growth, repair/catch-up, or three-node network transfer. Process maximum RSS
also excludes tmpfs page-cache memory.

The representative-capacity gate remains open until a retained Sandwurm three-writer campaign
measures those missing phases on persistent virtual disks near—but not at—the bounds. No quota,
default, precious-data recommendation, or permanent-GC decision changes from these controls.
