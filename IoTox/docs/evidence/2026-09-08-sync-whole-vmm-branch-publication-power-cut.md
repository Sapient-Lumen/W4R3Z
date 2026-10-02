# Whole-VMM tree-v2 branch-publication power-cut evidence — 2026-09-08

## Result

Three source-linked, networkless Sandwurm campaigns passed real Cloud Hypervisor `SIGKILL` cuts at
the three pre-rename tree-v2 metadata-publication boundaries: immutable manifest installation,
immutable signed branch-record installation, and mutable writer-pointer replacement. All three used
one repaired source commit and byte-identical IoTox binary.

Before each host cut, a qualification-owned, exact-path-filtered `strace` delay held the selected
sync-worker rename at syscall entry. The guest proved the selected temporary was complete, fsynced,
private, singly linked, and owned by the Agent; stopped every Agent task while ptrace remained live;
then stopped the tracer and emitted the arm receipt. The host independently rebound the exact
task-owned writable disk and Cloud Hypervisor PID/start-time/argv before killing that VMM.

A second kernel booted a copy of each exact crash image. Before any recovering Agent started, A and
B exposed the completed tree and C exposed the exact prior tree. The durable metadata prefixes were
exactly the expected absent/exact combinations. Ordinary startup removed the surviving selected
temporary, authenticated or reused the missing metadata and content, advanced C to the successor,
preserved all identities, converged the same 18-file tree, restored three writer branches per node,
and passed repair on all three nodes.

This closes ADR 0335's three pre-rename source-linked cells on the founding Sandwurm/KVM stack. It
does not qualify the post-rename/pre-directory-fsync sides, a second cut during cleanup, witnessed
publication, corrupt durable records, dishonest storage, physical power removal, independent backup,
or precious-data sole-copy use.

## Reproduction

From a clean checkout on the prepared Sandwurm host:

```sh
./tools/iotox-sandwurm-lab.sh up-sync-power-cut manifest-install
./tools/iotox-sandwurm-lab.sh up-sync-power-cut branch-record-install
./tools/iotox-sandwurm-lab.sh up-sync-power-cut branch-pointer-update

./tools/iotox-sandwurm-lab.sh verify-sync-power-cut \
  .sandwurm/exports/sync-power-cut/run.l2gckna4
./tools/iotox-sandwurm-lab.sh verify-sync-power-cut \
  .sandwurm/exports/sync-power-cut/run.c9xhj26a
./tools/iotox-sandwurm-lab.sh verify-sync-power-cut \
  .sandwurm/exports/sync-power-cut/run._cphu30p
```

Artifact realization has a separate 3,600-second prelaunch budget. The 1,200-second semantic budget
begins only after the coordinator resolves the runtime receipt, task-owned disk, and exact VMM
identity. This prevents cold Nix construction from consuming the observation window.

## Bound build and common result

```text
source Git commit:    2b2cc85429b322a47c671c1a6ab23c28a112fd7b
product:              IoTox 0.49.0 rev0049
binary SHA-256:       0f1dbb1a1fb88ead500a49d2ba91a23f4d589276e0776ee7f189ee5efa0b735e
substrate:            Cloud Hypervisor / KVM, 2 vCPU, 2 GiB, network class none
root image:           24-GiB sparse task-owned disk
scheduler fence:      strace-path-filtered-delay-enter+sigstop
workspace at arm:     stable raw byte 1; active projection; no stage
offline views:        completed, completed, prior
final projection:     18 files, 1 directory, 33,619,995 bytes
final tree SHA-256:   e1c1515d0faf3e669849a3913cd0fcb3faddb689ae911eedf2d9cee9e6e9bd2d
recovery result:      no temporaries; exact metadata; branches 3/3/3; repairs 3
identity preserved:   true
```

The boundary-specific observations were:

| boundary | proof | campaign ms | offline manifest/record/pointer | surviving selected temporary | recovery ms |
| --- | --- | ---: | --- | --- | ---: |
| manifest install | `run.l2gckna4` | 697,556 | absent / absent / prior | 1 × 1,981 bytes | 26,043 |
| branch-record install | `run.c9xhj26a` | 636,245 | exact / absent / prior | 1 × 472 bytes | 26,708 |
| branch-pointer update | `run._cphu30p` | 549,210 | exact / exact / prior | 1 × 472 bytes | 19,762 |

The selected temporary was permitted to disappear after the crash because its directory entry had
not crossed a directory barrier. On this host all three complete, file-fsynced temporaries survived
ext4 recovery. No non-selected publication temporary survived. After ordinary Agent startup every
selected temporary was absent and every final manifest, record, and pointer was exact.

## Defect found and repaired

The first genuine pointer-prefix attempt, `run.021hhqac`, made the intended host cut and passed the
second boot's offline-prefix inspection, then timed out before convergence. C held the complete
successor CAS object, manifest, and immutable record, but its mutable writer pointer remained prior.
The subscriber loaded the local record as “durable” and excluded it from the branch-acceptance loop,
thereby confusing immutable-byte presence with incorporation into the live frontier.

Commit `2b2cc85` separates those states. A locally exact record is reusable authenticated graph input
but remains unincorporated until the current frontier proves it is already history or normal branch
acceptance validates its dependency closure and replaces the pointer. The deterministic regression
constructs the exact orphan manifest/record/CAS prefix beside a prior pointer, requires zero object
requests, advances the successor, and verifies its projection and generation. The direct registry
passes 835/835. The accepted pointer campaign above then reproduced and recovered the real prefix.

The rejected pointer run is defect-finding provenance, not qualification evidence.

## Harness corrections before acceptance

Three earlier manifest attempts were also rejected rather than weakened:

- `run.y4ar7t0h` coupled a 1,200-second coordinator timeout to cold Nix realization. The image took
  about 16 minutes to build, leaving only 239 seconds for the guest. No semantic arm or cut occurred.
  Prelaunch and semantic budgets are now separate.
- `run.566zrhfl` injected a two-second delay into every Agent `rename`, including 159 unrelated
  runtime projection renames, so sync publication could not begin before the guest deadline. No arm
  or cut occurred. `strace -P` now scopes observation and injection to the exact selected temporary.
- `run.lfqd31o8` caught the target syscall, but stopping tracer and multithreaded tracee
  simultaneously froze the tracer before sleeping Agent threads entered group stop. No arm or cut
  occurred. The fence now stops and verifies every Agent task while ptrace remains live, then stops
  and revalidates the tracer.

These attempts improved the measurement without adding a product crash hook. They establish neither
product failures nor accepted power-cut cells.

## Compact proofs

The raw campaigns each allocate about 3.1 GiB and contain sparse disks and private guest state. The
retained content-free compact proofs are:

```text
manifest proof:         .sandwurm/exports/sync-power-cut/run.l2gckna4
manifested files/bytes: 10 / 144,287
campaign SHA-256:       34c919561840f86763f3e606b8324447756b487b94aaecf74ef73b0a2e6757c6
manifest SHA-256:       377c3428613b1f51a65c5175f63fb1522fd68c0e00c973e34dcf8b309a0a2414

record proof:           .sandwurm/exports/sync-power-cut/run.c9xhj26a
manifested files/bytes: 10 / 144,758
campaign SHA-256:       e1ec8cfaea7b133dcd27d4256d6c2c68d2f56a67ad1685e7963fdf8274245a5f
manifest SHA-256:       91c2fe92b875b926877b6b8f3a54939050e51823dcf19ea032a17f481a9ebc69

pointer proof:          .sandwurm/exports/sync-power-cut/run._cphu30p
manifested files/bytes: 10 / 145,425
campaign SHA-256:       215e200da12587eb16d50da324902994ba6937aa6d948808d1f23a91003d4cb9
manifest SHA-256:       c059a3010e19b4b8acc8a01f0343760f5463ae7b0be777a1b8360223f3ab8ae8

contains secrets:       false (all three)
```

The strict v5 verifier checks exact file-set and digest closure; source, product, and binary identity;
the redacted target commitment; exact-path scheduler fence; every stopped Agent task and traced
worker; exact VMM ownership; genuine host cut; networkless launches; distinct boot IDs; crash-image
lineage; boundary-specific offline metadata; absent-or-exact temporary grammar; identity survival;
final projection, branches, and repair; and normal second exit. It retains explicit v2--v4 read
compatibility for the accepted workspace and object-pipeline proofs.

## Next boundary

The next abrupt-storage work is the other half of these commits: cut after each rename but before its
parent-directory `fsync`, then repeat cleanup interruption, corrupt every durable record family, and
exercise remount/open-descriptor behavior. Capacity/soak and actually independent backup restoration
remain separate trust-graduation gates.
