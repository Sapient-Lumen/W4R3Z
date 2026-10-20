# ADR 0336: Cut post-rename directory-durability windows

- Status: accepted, implemented, and qualified on the founding Sandwurm stack
- Date: 2026-09-08

## Context

ADR 0335 qualifies the three tree-v2 metadata-publication prefixes immediately before their rename
commit. A successful `rename` is atomic to live observers, but it does not by itself prove that the
directory entry will survive abrupt power loss. IoTox therefore follows each manifest install,
immutable branch-record install, and mutable branch-pointer replacement with `fsync` of the exact
parent directory.

That leaves three adjacent failure windows: the rename has completed in the running kernel, the
selected final pathname is exact and its temporary is absent, but the parent-directory `fsync` has
not entered the kernel. After a whole-VMM cut, honest crash recovery may expose either the old or new
directory state. Both must be safe. A timing loop cannot establish which `fsync` was selected, while
a product crash hook would change the binary under test.

## Decision

1. Reserve sync power-cut proof v6 for
   `manifest-install-directory-fsync`, `branch-record-install-directory-fsync`, and
   `branch-pointer-update-directory-fsync`. Proof v2--v5 remain readable and retain their original
   meaning.
2. Reuse ADR 0335's exact successor discovery and redacted commitments. Arm, campaign, and recovery
   bind the manifest, immutable record, successor pointer, and prior pointer by hashed canonical
   name, byte count, and SHA-256 without exporting identities or content.
3. Run only the recovering follower beneath qualification-owned `strace -f`. Restrict the trace
   with `-P` to the exact `manifests`, `records`, or `branches` directory and inject a two-second
   entry delay only into `fsync`. The traced worker must be stopped at that exact delayed syscall;
   unrelated filesystem barriers do not qualify.
4. At the live arm, require stable workspace phase 1, active prior projection, no projection stage,
   the selected final file equal to its committed target, the selected temporary absent, and the
   following exact live prefix:

   | cut | manifest | immutable record | mutable pointer |
   | --- | --- | --- | --- |
   | manifest-directory fsync | exact | absent | prior |
   | record-directory fsync | exact | exact | prior |
   | pointer-directory fsync | exact | exact | successor |

5. Keep ptrace live while stopping the Agent thread group. Require every Agent task stopped, the
   exact traced worker TID retained, and the process group to contain exactly the tracer and Agent;
   stop the tracer only after those facts hold. The host then independently binds and `SIGKILL`s the
   exact task-owned Cloud Hypervisor process and boots a copy of its crash image under a second
   kernel.
6. Before any Agent restart, accept only the selected honest old-or-new namespace outcome:

   | cut | manifest | immutable record | mutable pointer |
   | --- | --- | --- | --- |
   | manifest-directory fsync | absent or exact | absent | prior |
   | record-directory fsync | exact | absent or exact | prior |
   | pointer-directory fsync | exact | exact | prior or successor |

   The selected temporary may be absent or one exact committed target; every non-selected
   publication temporary must be absent. No partial, malformed, unrelated, or out-of-order metadata
   state is admissible.
7. Normal startup must remove any surviving exact temporary, authenticate or reacquire every
   missing dependency, advance to the exact successor, converge the completed projection, restore
   branches `[3,3,3]`, and pass repair on all three nodes. The initial worktree remains the prior
   projection because the cut precedes completion of the reconciliation transaction, even when the
   mutable pointer's rename survived.
8. The strict verifier must test both permitted old and new directory outcomes for every v6 boundary,
   reject corrupt prefixes, cross-bind arm/campaign/recovery commitments, and preserve source,
   binary, two-boot, crash-image, VMM, and networkless-launch evidence. The compact exporter retains
   only that content-free allowlist.

The construction commands are:

```sh
./tools/iotox-sandwurm-lab.sh up-sync-power-cut manifest-directory-fsync
./tools/iotox-sandwurm-lab.sh up-sync-power-cut branch-record-directory-fsync
./tools/iotox-sandwurm-lab.sh up-sync-power-cut branch-pointer-directory-fsync
```

## Consequences

The harness can distinguish "rename has not entered the kernel" from "rename is visible but its
directory barrier has not entered the kernel" without modifying IoTox. The three outcomes are
separate cells because a later metadata step cannot stand in for durability of an earlier parent
directory.

The first record-directory attempt, `run.pjo_92d4`, timed out before arming. Its retained syscall
trace showed 134 delayed record-directory barriers from `TreeV2BranchStore::prepare()`, which
had unconditionally fsynced all three metadata directories, `tree-v2`, and the namespace root on
every frontier read even when no structure changed. Preparation now reports actual directory
creation and emits child-to-parent barriers only for those structural mutations. This removes a
steady-state metadata bottleneck without removing any publication barrier; the rejected run is
diagnostic, not qualification evidence.

All three repaired-source-linked campaigns now pass from commit `0686cba` and one byte-identical
rev0049 binary. Runs `dbgtc3ip`, `jznfzx52`, and `ia70ljmf` each recovered the old directory state
with the exact selected temporary, preserved the prior worktree and identity, then cleaned staging,
converged exact/exact/successor, restored branches `[3,3,3]`, and repaired all nodes. Their compact
proofs pass strict replay; see
`../evidence/2026-09-08-sync-whole-vmm-directory-durability-power-cut.md`.

This covers one founding
Cloud-Hypervisor/KVM/ext4 stack and an honest flush contract. It does not prove dishonest storage,
physical power removal, a second cut during cleanup, corrupt durable records, witnessed publication,
projection/remount descriptor behavior, independent backup, or precious-data suitability.
