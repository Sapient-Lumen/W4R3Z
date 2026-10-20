# Whole-VMM tree-v2 object-pipeline power-cut evidence — 2026-09-08

## Result

Two source-linked, networkless Sandwurm campaigns passed real Cloud Hypervisor `SIGKILL` cuts in
the tree-v2 object pipeline. One stopped the interrupted follower during a partial authenticated
generic transport receive; the other stopped it during the digest-fanout CAS install copy. Both
observers proved the exact temporary was private, singly linked, owned by the Agent, below the final
name, and paired with a stable prior workspace before stopping the Agent process group. The host then
independently found and killed the exact task-owned VMM.

A second kernel booted each crash image. Before any recovering Agent started, A and B were exactly
completed, C was exactly prior, and the expected digest-named object was absent. Normal startup
removed every surviving temporary, installed the exact object, preserved all identities, converged
the 18-file successor, restored three writer branches per node, and passed repair on all nodes.

These are two bounded virtual power-cut results on the construction machine. They do not qualify
manifest/branch publication, every old/new linearization, a second cut after cleanup, dishonest
storage, physical power loss, independent backup, or precious-data sole-copy use.

## Reproduction

From a clean checkout on the prepared Sandwurm host:

```sh
./tools/iotox-sandwurm-lab.sh up-sync-power-cut receive-staging
./tools/iotox-sandwurm-lab.sh up-sync-power-cut cas-install
./tools/iotox-sandwurm-lab.sh verify-sync-power-cut \
  .sandwurm/exports/sync-power-cut/run.1e05ayp9
./tools/iotox-sandwurm-lab.sh verify-sync-power-cut \
  .sandwurm/exports/sync-power-cut/run.jtiyspp_
```

The harness records a durable campaign marker before the interrupted follower begins. At the exact
semantic observation it double-stats the temporary and stable workspace, sends `SIGSTOP` to the
follower Agent process group, verifies `/proc/<pid>/status` reports a stopped task, and emits the arm
receipt. The host accepts only a Cloud Hypervisor descendant of the epoch launcher whose argv names
the exact writable runtime disk; PID, process start time, and NUL-delimited argv digest are bound in
the proof before `SIGKILL`.

## Bound build and result

Both campaigns used:

```text
source Git commit:    885f1045daad243e5a81f01e04b1fc968ddd7c8c
product:              IoTox 0.48.0 rev0048
binary SHA-256:       1e404de0f55db6fd4ed156f58870359cbb66738e3870db81716efce6f1a68b09
substrate:            Cloud Hypervisor / KVM, 2 vCPU, 2 GiB, network class none
root image:           24-GiB sparse task-owned disk
object:               33,554,432 bytes
object SHA-256:       c30702112c5524364699ccb618f16b5fa682744e3c5f1b59eea9906ab5a57803
workspace at arm:     stable raw byte 1; active projection; no stage
final projection:     18 files, 1 directory, 33,619,995 bytes
final tree SHA-256:   e1c1515d0faf3e669849a3913cd0fcb3faddb689ae911eedf2d9cee9e6e9bd2d
```

The receive-staging result was:

```text
proof ID:                    run.1e05ayp9
arm transition:              transport-receive-staging
arm boundary:                receive-staging-partial
temporary bytes at arm:      8,393,262
temporary mode/links/owner:  0600 / 1 / match
final object at arm:          absent
Agent stopped at arm:         true
first VMM PID/start:          625283 / 32421318 clock ticks
first VMM argv SHA-256:       c73ea3d793ee2489dcc4491348f320679fbe87babae39d61afad5a8567e3835c
campaign elapsed:             559,862 ms
offline views:                completed, completed, prior
offline incoming temporary:   one inode, 0 bytes
offline CAS temporary/final:  zero / absent
recovery elapsed:             29,891 ms
recovery result:              no temporaries; exact object; branches 3/3/3; repairs 3
```

The partial transport inode survived ext4 journal replay but its uncommitted payload did not. That is
permitted: the arm receipt proves the running-kernel state, while the recovered filesystem may lose
data that had not crossed its durability boundary. Startup removed the zero-length orphan durably.

The CAS-install result was:

```text
proof ID:                    run.jtiyspp_
arm transition:              cas-install
arm boundary:                cas-install-temporary
temporary bytes at arm:      61,440
temporary mode/links/owner:  0600 / 1 / match
final object at arm:          absent
Agent stopped at arm:         true
first VMM PID/start:          664393 / 32459038 clock ticks
first VMM argv SHA-256:       4de70722b585d5d408f5cf2a48f86fcbd08cec82c70c08e3b37ef9e7db6c41fe
campaign elapsed:             336,559 ms
offline views:                completed, completed, prior
offline incoming temporary:   one complete canonical file, 33,554,432 bytes
offline CAS temporary/final:  zero / absent
recovery elapsed:             30,753 ms
recovery result:              no temporaries; exact object; branches 3/3/3; repairs 3
```

Here the partial CAS copy disappeared after remount while the complete, previously fsynced canonical
receive survived. Startup re-imported that file and then removed its incoming name durably.

## Compact proofs

Raw campaigns contained sparse disks and private guest state. After strict export and independent
verification, their multi-gigabyte raw roots were removed from the active workspace under the
repository retention policy. The retained content-free proofs are:

```text
receive proof:          .sandwurm/exports/sync-power-cut/run.1e05ayp9
manifested files/bytes: 10 / 141,171
campaign SHA-256:       08477e21f8b6142410bbc105d0c9cbd4b0efe14181cd83e6044c8995f8678e2b
manifest SHA-256:       dcd2b46db3e3bc3c625dd523b9e173c28abc1528980f5b2b916e1300eaaab9cb
contains secrets:       false

CAS proof:              .sandwurm/exports/sync-power-cut/run.jtiyspp_
manifested files/bytes: 10 / 140,176
campaign SHA-256:       dd8ee6936b47cc3f0c72f2fd7847048ce27c9a207df4422ae09f71e760d27c39
manifest SHA-256:       a0949961f942aea878681b5ed78a8b8f2ac2f96efd4b1355cab31bd0e4532bc8
contains secrets:       false
```

The strict v4 verifier checks exact file-set and digest closure, source and binary identity, semantic
temporary class, stable workspace/orientation, process stop, exact VMM ownership, noncooperative
first exit, networkless launches, distinct boot IDs, crash-image lineage, old-or-new offline state,
bounded temporary grammar, exact final object, identity survival, convergence, branches, repair, and
normal second exit. The same verifier retains explicit v2/v3 compatibility for the two accepted
workspace-exchange proofs.

## Rejected predecessor and product correction

The first source-linked receive attempt, `run.s_2l5lii` at commit `898c04b`, timed out closed because
it searched for a partial canonical `.receive-<request>.part`. Source and read-only, no-journal-replay
disk inspection established that this state is impossible: the generic file-transfer manager first
writes `.iotox-.receive-<request>.part.part-<six-base62>` and link-publishes the canonical name only
after exact length and file `fsync`.

That rejection exposed a real product gap. Tree-v2 startup cleaned canonical staging but did not
recognize the generic manager's interrupted private temporary, so a power cut could retain orphaned
transfer bytes indefinitely. Rev0048 now recognizes only the exact grammar, removes it alongside
canonical staging, and follows each bounded cleanup batch with one incoming-directory `fsync`.
Recovered safe CAS `.install.tmp` removal likewise fsyncs its exact fanout. Tests prove exact stale
names disappear while unrelated files remain. The rejected run is diagnostic provenance, not
qualification evidence.

## Next boundary

The next whole-VMM family is metadata publication: immutable manifest installation, immutable branch
record installation, and mutable branch-pointer replacement. Each needs a semantic observer and all
valid old/new recovery outcomes without adding a product crash hook. After that come witnessed
publication, second-cut cleanup idempotence, authenticated-record corruption, remount/open-descriptor
cases, cold and near-ceiling repetitions, sustained writes, and storage that violates flush ordering.
