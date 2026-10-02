# ADR 0334: Make object-pipeline recovery durable and directly cuttable

- Status: accepted, implemented, and whole-VMM qualified on the construction host
- Date: 2026-09-08

## Context

ADRs 0332--0333 qualify both semantic sides of the tree-v2 workspace directory exchange. They do
not cover the earlier receive and immutable-object pipeline. That pipeline has three distinct names
and authorities:

1. the generic file manager writes an authenticated transfer into private
   `tree-v2/incoming/.iotox-.receive-<request>.part.part-<random>` staging;
2. only after full length, file `fsync`, and link publication does the canonical
   `.receive-<request>.part` name appear;
3. the subscriber gives the completed canonical file to the quota- and digest-verifying CAS importer;
4. the importer copies it into the digest fanout as `.install.tmp`, fsyncs the file, renames it with
   `RENAME_NOREPLACE`, and fsyncs the fanout before the object can support branch effects.

Startup already rejected unsafe temporaries and removed canonical stale ones. Two cleanup removals,
however, lacked their own directory durability barrier: incoming staging removal and CAS install
temporary recovery. This could not authenticate bad bytes as a digest-named object, but a closely
following crash could resurrect cleanup work and consume space repeatedly.

Timing is a second problem. A CAS copy temporary may exist for milliseconds. A guest can truthfully
observe it, write an arm receipt, and nevertheless let the Agent publish a branch before the host
notices that receipt and kills the VMM.

## Decision

1. Persist receive cleanup. Startup recognizes both exact canonical `.receive-*` names and the
   generic transfer manager's exact six-base62-suffix temporary grammar. Single staging removals
   fsync their parent; startup, cancellation,
   failure, peer-loss, and completed file-window paths batch all unlink operations behind one
   incoming-directory fsync. The batching preserves ADR 0330's removal of per-object CAS work.
2. When object-store inventory removes a safe recovered `.install.tmp`, fsync that exact fanout
   before accepting its remaining digest-named inventory.
3. Reserve power-cut proof v4 for object-pipeline cuts. The accepted v2/v3 workspace proof grammar
   and verifier compatibility remain unchanged.
4. Name two v4 targets: `receive-staging-partial` observes the generic private transport temporary
   between 8 MiB and the 32 MiB object size; `cas-install-temporary` observes the private temporary in the
   expected digest fanout while the final name is absent.
5. Both observations additionally require stable workspace phase byte 1, the active canonical
   projection marker, no projection stage, mode 0600, one link, matching owner, and an absent
   digest-named final object.
6. Immediately after the double-stat observation, send `SIGSTOP` to the follower process group and
   prove the process entered the kernel stopped state. The host then independently identifies and
   sends `SIGKILL` to the one task-owned Cloud Hypervisor process. `SIGSTOP` is a qualification
   scheduler fence, not a product crash hook or a graceful shutdown.
7. On the second boot, inspect all canonical incoming and CAS temporaries before starting an Agent.
   Permit the expected digest-named object to be only absent or byte-exact; reject partial or corrupt
   final names. The worktree must still be exactly prior on the follower and completed on both live
   writers. Normal startup must leave no temporary, install the exact object, converge the completed
   projection, restore three branches on every node, and pass repair.
8. Export only content-free receipts. Test payload bytes, node images, identities, and policy state
   remain outside the compact proof.

The explicit commands are:

```sh
./tools/iotox-sandwurm-lab.sh up-sync-power-cut receive-staging
./tools/iotox-sandwurm-lab.sh up-sync-power-cut cas-install
```

## Consequences

The gate now distinguishes transfer staging, CAS installation, branch publication, and projection
exchange rather than calling them one crash boundary. An absent temporary after reboot is valid:
the arm proves it existed in the running kernel, while power loss is allowed to discard data that
was not yet made durable. A surviving digest-named object is valid only when its complete size and
SHA-256 match.

Two corrected source-linked campaigns now pass and their strict content-free compact proofs are
retained. This decision does not yet cut manifest installation, immutable branch-record installation,
mutable branch-pointer replacement, witness transitions, or a second crash immediately after
cleanup. It assumes the block device honors flushes and `fsync`; lying-storage and physical-power
qualification remain separate.

The first source-linked v4 attempt, `run.s_2l5lii` at commit `898c04b`, rejected because it searched
for a partial canonical `.receive-*` file. Read-only inspection of its retained crash disk confirmed
the subscriber still had the prior 17-file tree and lacked the successor object, while both live
writers held the exact 32-MiB CAS object. Source inspection then established that the generic file
manager publishes the canonical name only after completion. The attempt is diagnostic provenance,
not accepted power-cut evidence; the corrected observer targets the real transport-temporary grammar.

Corrected source-linked run `1e05ayp9` at commit `885f104` stopped the follower with 8,393,262
transport-temporary bytes. After the VMM cut, the private inode survived with zero bytes, the final
object remained absent, and startup durably removed it before exact convergence. Run `jtiyspp_`
stopped at a 61,440-byte CAS install temporary. After reboot, that copy was absent while the complete
33,554,432-byte canonical incoming file survived; startup re-imported it into the exact digest name
and removed all staging. Both runs began offline as `[completed, completed, prior]`, preserved
identity, converged the 18-file/33,619,995-byte successor, restored three branches per node, and
passed repair on all nodes. Their compact proofs independently verify. See
`../evidence/2026-09-08-sync-whole-vmm-object-pipeline-power-cut.md`.
