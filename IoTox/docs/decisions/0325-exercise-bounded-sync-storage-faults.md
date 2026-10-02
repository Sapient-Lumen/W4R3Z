# ADR 0325: Exercise bounded synchronization storage faults

- Status: accepted and implemented
- Date: 2026-09-03

## Context

The persistent three-writer and node-loss cells proved ordinary ext4 operation, process-restart
reconciliation, and reconstruction from an ordinary tree. They did not force a live filesystem to
return `ENOSPC`, prove read-only startup refusal without durable mutation, or interrupt an Agent
while a large tree-v2 exchange had a signed pending workspace. Those cases are materially different
from a cooperative stop or an in-memory fault injection.

They also must not be confused with a whole-VM power cut. A process `SIGKILL` exercises IoTox's
durable join logic against the kernel/filesystem state that has already become visible; it cannot
prove that a device, controller, or dishonest medium honors an acknowledged flush.

## Decision

Add `tools/run-sync-storage-fault-rehearsal.py` to the retained three-writer Sandwurm gate. The
rehearsal creates three separate 192-MiB loop-backed ext4 filesystems inside the guest and places
one fresh IoTox node root on each. It then runs three bounded scenarios:

1. stop one live writer, durably edit its ordinary worktree, fill that node's filesystem until a
   real write returns `ENOSPC`, resume the writer, require an explicit checkpoint mutation to fail
   with no-space, kill the Agent abruptly, reclaim only the exact filler, restart, converge, and
   repair all nodes;
2. stop a different Agent cleanly, hash its durable state excluding runtime and logs, remount its
   exact filesystem read-only, require Agent startup to fail, require the durable hash to remain
   unchanged, remount read-write, restart, converge, and repair; and
3. stop the third Agent, create a deterministic 32-MiB successor on a remote writer, restart it,
   observe either signed `pending-workspace` state or the projection staging boundary, kill that
   Agent with `SIGKILL`, then restart, reconcile, converge, and repair.

The normal capacity/lifecycle and node-loss recovery phases run first in the same source-linked VM.
The receipt is content-free and states whether whole-power loss or dishonest storage was assessed.
The verifier requires those fields to remain false for this gate.

## Consequences

The accepted cell observed live `ENOSPC` after 178,147,328 filler bytes, an explicit no-space
mutation refusal, and an abrupt exit of `-9`. Read-only startup refused with exit 3 and did not
change the durable state digest. The 32-MiB interrupted exchange was killed at the signed
`pending-workspace` side and recovered. All three repaired views then matched 19 files in one
directory, 33,620,017 bytes, and canonical tree SHA-256
`444795f5a52d94a9301bececa30987cc907b650551f11b562f76ac6b4f360b93`.

This closes a first bounded real-filesystem slice of the abrupt-storage campaign. It does not close
the full gate: no VM or host power was cut, no cold boot from an arbitrarily interrupted disk image
was exercised at every named transition, no durable-record corruption family was injected, no open
descriptor was held across remount, and no lying controller/device was assessed. It remains
same-host construction evidence and does not make synchronization a backup or justify precious-only
storage.
