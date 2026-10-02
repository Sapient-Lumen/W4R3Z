# ADR 0340: Qualify exchanged-projection open-descriptor retention

- Status: accepted and qualified on founding Sandwurm/KVM/ext4 raw proof
- Date: 2026-09-08

## Context

ADR 0338 changed the projection exchange so that the visible target and the
obsolete staged projection are both validated before the stage is removed.
Rev0051 has deterministic tests for held-descriptor writes immediately before
`RENAME_EXCHANGE` and immediately after it, before either tree is validated.
Those tests prove the in-process algorithm preserves ambiguity, but they do
not establish the real syscall boundary, ext4 inode continuity, controlled
restart, or remount behavior.

The risk is concrete: a pathname user may keep `held.bin` open while IoTox
exchanges its containing projection. The descriptor then names the old inode
at the private staging pathname. A local write must never be discarded merely
because its old name is no longer visible. A correct response is preservation
and explicit forward recovery, not implicit conflict resolution.

## Decision

1. Qualify this boundary only in a source-linked, networkless
   Cloud-Hypervisor/KVM guest with a persistent ext4 node volume. The product
   binary runs without a test seam in the guest.
2. Use an independent helper process to open `held.bin` with `O_RDWR`, record
   its device/inode, retain the descriptor, perform exact same-length writes,
   and report `fsync` results. The helper's ownership of the descriptor must
   be distinct from the Agent process.
3. Use an external ptrace controller to stop the exact target sync worker at
   a validated `renameat2(..., RENAME_EXCHANGE)` boundary. It must bind the
   worker identity, destination and staging paths, the exchange flag, and
   syscall entry/exit phase; sleeps, pathname polling, and a product crash hook
   are not substitutes.
4. Construct two cells from a canonical three-node/six-directed-RW-share
   state. A remote edit to a file other than `held.bin` forces the exchange.

   - **Final-scan-to-exchange selected write:** stop at `renameat2` entry,
     write through the selected-file descriptor, then resume. Require exactly
     one exchange, visible target success, staged old-tree retention,
     descriptor/staging device+inode equality, exact written bytes,
     `protocol_error` with the stable preservation classification, and intact
     pending workspace plus both projection markers.
   - **Post-exchange unselected write through restart/remount:** retain an
     unselected local `held.bin`, stop at successful `renameat2` exit, write
     through the descriptor, then resume. Require the same retained ambiguity.
     Controlled-stop the Agent while the helper remains alive; require an
     attempted read-only ext4 remount to fail busy while that writable
     descriptor exists and leave the descriptor, inode, and bytes unchanged.
     Close the helper, remount read-only then read-write, and require the
     retained stage pathname to keep the same device/inode and bytes. Open a
     second independent helper on that exact retained inode, write and `fsync`
     a second value, close it, and cold-start the Agent. Startup must refuse
     before worker/network exposure and preserve the stage, markers, pending
     workspace, identity, inode, and latest descriptor bytes exactly.
5. Exercise one explicit salvage ceremony after the second cell: copy the
   retained bytes to an owner-private recovery path with file/parent barriers,
   restore the staged old projection to its authenticated baseline, restart
   through ordinary workspace recovery, reapply the salvaged bytes by visible
   pathname, publish normally, converge all three nodes, and repair. This is
   recovery of a demonstrated local edit, not automatic merge policy.
6. Add a closed receipt, strict host verifier, compact exporter, guest
   predicate, CTest self-tests, lab commands, workspace-cleaner scope, and
   content-free evidence record. The receipt must bind source/binary identity,
   networkless KVM/ext4 substrate, ptrace arguments/phase, helper PID/FD and
   inode continuity, hashes for each baseline/mutated/retained/salvaged/final
   value, error classification, marker/workspace state, controlled stop,
   busy-remount refusal, successful closed-descriptor remount results,
   cold-start result, convergence, and repair. The verifier
   must reject a wrong syscall phase/flag/path, inode mismatch, missing stage,
   changed retained bytes, successful ambiguous startup, false remount claim,
   and malformed or non-integral evidence.

## Consequences

This gate qualifies one narrow ordinary-file descriptor class in the real
production path, including post-exchange retention through controlled restart
and an ext4 remount after the descriptor is closed. It does not make the local
writer authoritative; it demonstrates that the bytes are preserved for a
conscious owner merge.

Source-linked Sandwurm/KVM/ext4 run `1fq3WhIY`, bound to commit
`e034311dc4d5843f5650e3194b43879dd5f434a4`, passes the two-cell raw proof and
strict host verification. The selected entry cell observed the real
`renameat2(..., RENAME_EXCHANGE)` as a split strace entry/resume pair; the
unselected exit cell observed it as one line. Both cells bind exactly one
successful exchange to the exact visible and staging paths, return
`protocol_error` from live `sync-repair`, retain the signed pending workspace,
converge all three writers, and repair. The unselected cell additionally
proves ext4's busy read-only-remount refusal while the writable descriptor is
open, closed-descriptor RO/RW remount preservation, cold-start refusal before
control-socket exposure, and explicit `recovered/held.bin` salvage
publication.

The retained compact evidence is
`.sandwurm/exports/sync-projection-descriptor/run.1fq3WhIY`. It contains five
strictly verified content-free records plus `compact-export.json`, totals 7,644
manifested bytes, and replays through the same strict verifier.

The 2026-09-08 founding-host construction probe corrected the original
decision before evidence was accepted: Linux ext4 rejects a read-only remount
with `EBUSY` while a writable descriptor on that mount remains open. Therefore
no honest test can carry the same writable descriptor through an RO/RW remount.
That refusal is a useful kernel safety boundary, and the amended cell proves it
directly instead of weakening the mount or silently closing the descriptor.

This gate must not claim that IoTox revokes writable descriptors or closes all
deletion races. It excludes writes after final obsolete-tree validation begins
and before/during removal, forever-open writers, writable `mmap`, io_uring or
direct I/O, hostile same-UID processes, directory descriptors, hard links,
mount namespaces, non-ext4 filesystems, lying storage, physical power loss,
and independent backup provenance. The remaining final-validation-to-removal
interval remains an architectural decision: application quiescence, durable
retired-projection retention, or a stronger kernel-assisted contract is
required before claiming complete open-descriptor safety.
