# Tree-v2 post-rename directory-durability power cuts — 2026-09-08

## Result

The three proof-v6 post-rename/pre-parent-directory-fsync cells pass on the founding
Sandwurm/Cloud-Hypervisor/KVM/ext4 stack:

| boundary | run | offline selected destination | surviving exact temporary | recovery | campaign |
| --- | --- | --- | --- | ---: | ---: |
| manifest directory fsync | `dbgtc3ip` | manifest absent | 1 × 1,981 bytes | 19,432 ms | 588,515 ms |
| immutable-record directory fsync | `jznfzx52` | record absent | 1 × 472 bytes | 21,172 ms | 447,787 ms |
| mutable-pointer directory fsync | `ia70ljmf` | prior pointer | 1 × 472 bytes | 18,535 ms | 446,119 ms |

All three runs are source-linked to commit
`0686cba5e0169a5b58a045945abee23617f0c812`, product rev0049, and binary SHA-256
`f63a92434bb0fa2f4f47e81c63cf5679a0300420e7a7e29d4990ce764411268c`. Each first
epoch reached an exact semantic arm, the host sent `SIGKILL` to the independently bound task-owned
Cloud Hypervisor process, and a second kernel booted a copy of that exact crash image. Both launches
were networkless.

Every crash recovered the old side of its selected directory transaction rather than the live
post-rename side. This is useful coverage, not a weakness: it directly exercises the reason the
parent-directory barrier exists. In every cell the worktrees initially classified
`[completed, completed, prior]`; the offline follower retained only the exact selected temporary and
the permitted earlier metadata prefix. Normal startup removed the temporary, authenticated or
reused exact dependencies, advanced the pointer, and finished at:

- manifest `exact`, immutable record `exact`, pointer `successor`;
- zero manifest, record, or pointer temporaries;
- branches `[3,3,3]` and three repair-verified nodes;
- 18 files, one directory, and 33,619,995 bytes;
- tree digest `e1c1515d0faf3e669849a3913cd0fcb3faddb689ae911eedf2d9cee9e6e9bd2d`;
- unchanged Tox identities and stable principals.

This closes ADR 0336's founding-stack qualification gate. Synthetic v6 fixtures separately accept
the permitted new-side recovery for each selected directory entry, reject corrupt prefixes, and
retain verifier compatibility with proof v2--v5. The real campaigns observed old-side recovery only;
they do not claim an empirical new-side crash observation.

## Method

The two converged live writers produced one exact successor while the third writer remained at the
prior pointer. A private marker bound the successor manifest, immutable record, successor pointer,
and prior pointer. Receipts export only SHA-256 canonical-name commitments, exact byte counts, and
content hashes.

Only the recovering follower ran beneath qualification-owned `strace -f`. The trace used `-P` for
the exact selected `manifests`, `records`, or `branches` parent and injected a two-second entry delay
only into `fsync`. The live observer required the selected rename already visible, its exact
temporary absent, stable workspace phase byte 1, the active prior projection, no projection stage,
and the complete expected metadata prefix. It then stopped every Agent task while ptrace remained
live, retained the exact traced worker TID, stopped the tracer, and required the process group to
contain exactly those two processes before writing the arm receipt.

The host had a separate 3,600-second artifact/prelaunch budget and started the 1,200-second semantic
budget only after resolving the runtime disk and exact VMM identity. It revalidated PID, proc start
time, and command immediately before `SIGKILL`. Recovery copied the crash disk, inspected its three
private ext4 node volumes before Agent restart, rejected every prefix outside ADR 0336's bounded
old-or-new set, and then ran ordinary startup/convergence/repair. The strict verifier independently
cross-bound the arm, recovery, source/binary identity, VMM launch records, distinct boot IDs,
crash-image lineage, final tree, and exact compact file allowlist.

Reproduce the three cells with:

```sh
./tools/iotox-sandwurm-lab.sh up-sync-power-cut manifest-directory-fsync
./tools/iotox-sandwurm-lab.sh up-sync-power-cut branch-record-directory-fsync
./tools/iotox-sandwurm-lab.sh up-sync-power-cut branch-pointer-directory-fsync
```

## Defect-finding and optimization

The first record-directory campaign, `run.pjo_92d4` from pre-optimization commit `1fe20c0`, failed
closed before arming. Read-only `debugfs` extraction from its retained outer crash disk found 134
delayed record-directory `fsync` calls. `TreeV2BranchStore::prepare()` had unconditionally fsynced
all three metadata directories, `tree-v2`, and the namespace root on every frontier read, even when
it created no directory. The two-second qualification delay serialized those unrelated steady-state
barriers and exhausted the guest observation window.

Commit `0686cba` changed preparation to report actual directory creation. It now fsyncs each newly
created child, then `tree-v2` if the tree or any child was created, then the namespace root only if
`tree-v2` itself was created. Publication's file fsync, atomic rename, and parent-directory fsync are
unchanged. The complete development-shell CTest surface passed 59/59 with five cgroup tests skipped
by their environment gate; its owned registry passed all 835 cases. `nix flake check --no-build`
also passed. The repaired record cell then armed and passed without shortening the two-second fence.

Earlier pre-optimization manifest proof `run.et453axl` passed before the store-barrier change, but is
superseded for this final same-source set. It is not cited as qualification evidence.

The pointer recovery epoch logged a nonfatal Sandwurm attempt to re-realize its toolchain from the
mutable Sandwurm source tree; Nix could not read one Rust incremental lock owned by another context.
The already-realized immutable toolchain nevertheless launched the actual second VMM. The strict
proof binds that real Cloud Hypervisor argv/process, normal recovery-epoch exit control, guest
receipt, and source-linked binary. This warning does not alter the IoTox result, but it remains
visible in the raw diagnostic root.

## Compact evidence

The content-free compact roots are:

| run | manifested bytes | campaign SHA-256 | compact-manifest SHA-256 |
| --- | ---: | --- | --- |
| `.sandwurm/exports/sync-power-cut/run.dbgtc3ip` | 146,311 | `a70079123668048490bcc4013db468e4c04521bed6ebd86252b84fadbf1e6727` | `cdea0c99f049ef022ddc04e3b2ecb1750f473a35b5887f73da342cecc70c87c8` |
| `.sandwurm/exports/sync-power-cut/run.jznfzx52` | 147,428 | `5c104e4e195c7d3867770816f8e8c647f58202fbc9672f131174abf8103a4fa9` | `f0f59da19b5b3479867eb16bfa066e8438bb0b8731372da7583cbe4c09321a1e` |
| `.sandwurm/exports/sync-power-cut/run.ia70ljmf` | 147,011 | `78bc7b696ea040148df29d837ff6f9ce0e5fd9b48c21a52fe03c031f375206aa` | `01c102561166e60eeada300716d726fd7d1351a4f09096f3d2a79659e2b571aa` |

Each compact manifest covers ten files and omits raw names, identities, node volumes, policy state,
tree content, private logs, and the strace stream. All three compact roots passed strict replay after
export.

## Nonclaims and next gate

This evidence covers one honest Cloud-Hypervisor/KVM/ext4 crash-consistency stack with externally
perturbed scheduling. It does not establish natural boundary frequency, a physical power pull,
storage firmware that lies about flushes, another filesystem/kernel/hypervisor, a second cut during
cleanup, corrupt durable records, witnessed publication, projection/remount open-descriptor behavior,
independent backup, or precious-data suitability.

The next abrupt-storage frontier is durable-record corruption, starting with explicit classification
and fail-closed recovery for workspace state, manifest, immutable branch record, mutable pointer, and
projection marker families. Lying-storage and physical-power claims remain later independent gates.
