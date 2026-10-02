# ADR 0335: Qualify tree-v2 branch-publication prefixes

- Status: accepted, implemented, and qualified on the founding Sandwurm stack
- Date: 2026-09-08

## Context

ADRs 0332--0334 cut both sides of the workspace exchange and the receive/CAS object pipeline. A
tree-v2 successor still crosses three metadata commits before it can become the current visible
branch:

1. its immutable manifest is written and fsynced as `manifests/.install.tmp`, renamed with
   `RENAME_NOREPLACE`, and followed by a manifest-directory fsync;
2. its signed immutable branch record follows the same sequence through `records/.install.tmp`;
3. `branches/.update.tmp` is written and fsynced, atomically replaces the writer's prior mutable
   branch pointer, and is followed by a branch-directory fsync.

Startup removes only those three exact private regular temporary names and fsyncs the containing
directory. It then authenticates every current branch, referenced manifest, and immutable record.
Unit tests exercise cleanup and rejection, but ordinary timing cannot reliably hit these small
files: a polling observer can see a temporary and still let its rename complete before the host
reacts. A product crash hook would make a convenient test while changing the product being tested.

## Decision

1. Reserve sync power-cut proof v5 for three named boundaries:
   `manifest-install-temporary`, `branch-record-install-temporary`, and
   `branch-pointer-update-temporary`.
2. Discover one successor from the two converged live writers while the third writer is offline.
   Bind the exact manifest, immutable record, successor pointer, and prior pointer by canonical name,
   byte count, and SHA-256. The two live frontiers must agree; the offline writer must contain the
   same writer set with exactly one prior pointer and must not already contain the successor manifest
   or record.
3. Run only the recovering follower beneath qualification-owned `strace -f`. Use `-P` to restrict
   tracing and injection to the exact selected `.install.tmp` or `.update.tmp` pathname, then inject
   a two-second syscall-entry delay into `rename` and `renameat2`. This leaves a fully written and
   file-fsynced temporary in place before the selected commit syscall enters the kernel without
   delaying unrelated Agent/runtime projection renames. The instrumentation is outside IoTox and
   changes timing; it is neither product code nor production configuration.
4. Arm only after proving all of the following twice: the selected temporary is one mode-0600,
   single-link, matching-owner regular file with the exact target bytes; the worktree remains the
   stable prior projection; the durable destination prefix is exact; and exactly one traced IoTox
   worker thread is stopped by ptrace. Deliver `SIGSTOP` to the Agent thread group while the tracer
   remains live, require every Agent task to enter ptrace/group stop while retaining the exact worker
   TID, then stop the tracer and revalidate that the process group contains exactly those two
   processes before emitting the arm receipt. Stopping tracer and tracee simultaneously is invalid:
   it can freeze strace before it propagates group-stop to sleeping Agent threads.
5. The host independently binds and kills the exact task-owned Cloud Hypervisor process. It boots a
   copy of that crash image under a second kernel; no graceful Agent, guest, or VMM shutdown is part
   of the first epoch. Artifact realization/materialization and exact VMM launch have a separate,
   bounded 3600-second prelaunch budget. The 1200-second semantic arm budget begins only after the
   coordinator has resolved the runtime disk and the exact VMM PID, start time, and command; it
   revalidates that identity immediately before the cut. Thus a cold Nix cache cannot consume the
   guest's observation window.
6. Before restarting an Agent, require the selected destination prefix:

   | cut | manifest | immutable record | mutable pointer |
   | --- | --- | --- | --- |
   | manifest install | absent | absent | prior |
   | branch-record install | exact | absent | prior |
   | branch-pointer update | exact | exact | prior |

   The selected file-fsynced temporary may be absent after the crash. If it survives, it must be the
   exact target; every non-selected publication temporary must be absent.
7. Ordinary startup must remove any surviving exact temporary, receive and authenticate the missing
   metadata, advance the pointer to the exact successor, converge the completed projection, restore
   three branches on all three nodes, and pass repair. No malformed, partial, or unrelated temporary
   is accepted as recovery work.
8. Compact proof exports contain receipts and source/launch bindings only. A redacted target object
   carries the three hashed canonical names, exact byte counts and successor SHA-256 values, plus the
   prior pointer's byte count and SHA-256; arm, campaign, and recovery must carry the identical
   object. The export excludes raw names, private node volumes, identities, policy state, tree
   content, and the raw strace log.
9. Treat a locally reusable immutable branch record as authenticated graph input, not as proof that
   its writer pointer already incorporates that record. After a crash between record installation
   and pointer replacement, an authenticated peer inventory must drive the existing successor
   through normal branch acceptance. Already-current and older exact records remain no-op history;
   an orphan successor replaces the pointer only after its complete signed dependency closure and
   manifest have been revalidated. Recovery must not retransmit metadata or CAS content that is
   already exact locally.

The construction commands are:

```sh
./tools/iotox-sandwurm-lab.sh up-sync-power-cut manifest-install
./tools/iotox-sandwurm-lab.sh up-sync-power-cut branch-record-install
./tools/iotox-sandwurm-lab.sh up-sync-power-cut branch-pointer-update
```

## Consequences

The three pre-rename tree-v2 publication prefixes now have semantic whole-VMM targets rather than a
timing-only crash loop. Proof v2/v3 workspace and v4 object-pipeline evidence remain readable and
independently verifiable. The seven exact raw proof parents and shared compact directory are covered
by the guarded workspace cleaner.

The first real pointer-prefix campaign exposed a liveness defect at exactly this boundary: the
follower rebooted with the successor manifest and immutable record but its prior pointer, then
mistook record durability for pointer incorporation and never converged. The subscriber now keeps
those states separate. An owned regression constructs that exact durable prefix, proves zero object
requests, replays the signed successor, advances the pointer, and projects the successor worktree;
the complete direct registry passes 835/835. This is defect-finding and repair evidence, not an
accepted power-cut campaign.

All three repaired-source-linked v5 campaigns now pass from commit `2b2cc85` with one byte-identical
rev0049 binary. Each begins recovery as `[completed, completed, prior]`, observes its exact permitted
metadata prefix, preserves identity, removes all temporaries, converges to branches `[3,3,3]`, and
repairs every node. The accepted compact proofs are `run.l2gckna4`, `run.c9xhj26a`, and
`run._cphu30p`; see
`../evidence/2026-09-08-sync-whole-vmm-branch-publication-power-cut.md`.

This decision does not cover the post-rename/pre-directory-fsync windows, witnessed publication,
corrupt durable records, a second crash during cleanup, remount/open-descriptor behavior, storage
that lies about flushes, physical power removal, independent backup, or precious-data suitability. The syscall delay
intentionally perturbs scheduling, so accepted runs will prove recovery from the selected durable
prefixes, not their natural occurrence frequency.
