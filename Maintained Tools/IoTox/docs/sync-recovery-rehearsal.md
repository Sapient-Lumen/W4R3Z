# Synchronization recovery rehearsal

Status: exact external restore-tree verification, operator provenance labels, retained receipt wrapper, local drill requirements, and bounded node-loss rehearsal implemented.
Updated 2026-09-10.

## What this rehearsal is for

Synchronization answers “which authorized state should the live peers converge on?” A backup
answers “what can the owner recover when those peers, their current state, or the owner's last edit
are wrong?” IoTox history, pins, conflict alternatives, quarantine, and another writable peer are
useful recovery material, but none is independently versioned by definition.

For a backup generation selected by the operator, restore it into a separate empty directory that
is outside every live synchronized namespace. Then compare the backup view with that restored view:

```sh
iotox sync-recovery-verify \
  /absolute/path/to/mounted-backup-generation \
  /absolute/path/to/empty-restore-target
```

For a larger deliberately bounded drill, state the ceilings rather than relying on defaults:

```sh
iotox sync-recovery-verify BACKUP_ROOT RESTORED_ROOT 1073741824 100000
```

For an audit-ready drill, attach the operator-selected backup and restore context directly to the
machine-readable report:

```sh
iotox sync-recovery-verify BACKUP_ROOT RESTORED_ROOT \
  backup-system=restic \
  backup-generation=snapshot-2026-09-10T120000Z \
  backup-failure-domain=external-usb-disk \
  restore-provenance=manual-drill-2026-09-10
```

Exit 0 and `decision=match` mean the two trees had identical relative paths, directories, regular
file bytes, and private owner `r/w/x` modes under the tree-v2 owner-mode-v2 model. The command also
requires the strict ADR 0318 filesystem contract and two stable scans. ADR 0360 additionally records
`root-devices-differ=0|1`, `operator-provenance=present|absent`, and any supplied provenance labels
as hex. Exit 4 means mismatch or refusal; exit 2 means command syntax; exit 3 means output failure.

Resolve or archive every `.iotox-conflicts` tree before the drill. IoTox intentionally excludes that
generated projection from ordinary source publication, so the recovery verifier refuses its
presence instead of silently omitting possible losing values.

To keep a compact receipt for the drill without retaining paths or content, use the wrapper added by
ADR 0361:

```sh
tools/iotox-repo.sh sync-recovery-drill \
  --iotox build/iotox \
  --evidence /outside/live-sync/recovery-drill.json \
  --backup-system restic \
  --backup-generation snapshot-2026-09-10T120000Z \
  --backup-failure-domain external-usb-disk \
  --restore-provenance manual-drill-2026-09-10 \
  --require-operator-provenance \
  --require-different-device \
  /absolute/path/to/mounted-backup-generation \
  /absolute/path/to/empty-restore-target
```

The wrapper runs `iotox sync-recovery-verify`, requires the strict no-live-state/no-overclaim
fields, requires the provenance labels to be present in the verifier report when supplied, and writes
`iotox.sync-retained-recovery-drill.v1`. The JSON receipt contains report and label SHA-256 values,
manifest digests, counts, byte totals, and the root-device observation. It does not store paths,
file names, file contents, Tox state, authority material, or backup credentials.

For a stronger same-host prerequisite when no external backup target is available, use the loopback
drill helper:

```sh
nix develop -c tools/iotox-repo.sh sync-loopback-custody-drill --iotox build/iotox
```

It creates two temporary ext4 loopback filesystems, remounts the selected generation read-only,
restores it onto the second filesystem, and then requires both operator provenance and
`root-devices-differ=1`. Accepted run `run.9xP4yW5T` retained a content-free receipt at
`.sandwurm/exports/sync-recovery-custody/run.9xP4yW5T/retained-recovery-drill.json`; see
`evidence/2026-09-17-sync-loopback-custody.md`. This is still same-host loopback evidence, not
disk-loss, host-compromise, or filesystem-wide corruption protection.

ADR 0366 hardens this wrapper. Rejected command receipts retain failure kind, return code,
stdout/stderr byte counts, and a complete failure hash, but no raw diagnostic text. The optional
`--require-operator-provenance` flag rejects the receipt unless all four provenance labels are
present and bound into the report. The optional `--require-different-device` flag rejects the
receipt unless the verifier reports `root-devices-differ=1`. This is still only a local prerequisite:
different device numbers do not prove off-machine custody, immutability, append-only retention, or
independent administration.

A verifier mismatch is different from an opaque command failure. `sync-recovery-verify` emits a full
`decision=mismatch` report and exits nonzero; the wrapper retains that structured report, including
manifest and count evidence, as a rejected receipt instead of collapsing it into raw failure text.

## What to retain with the result

Record outside the synchronized namespace:

- backup system and immutable/version identifier;
- when the backup was created and when the restore was performed;
- physical or administrative failure domain of the backup;
- exact verifier command, ceilings, complete v1 report, and IoTox build identity;
- who selected the generation and confirmed that both paths were external to live IoTox state; and
- any excluded data, resolved conflicts, or filesystem transformations.

The historical report deliberately says `backup-independence=not-assessed` and
`restore-provenance=not-assessed` even when provenance labels are present. In
current ADR 0405 terms, those labels name the operator's selected
backup/restore evidence; they do not prove recovery custody, correct generation
choice, append-only retention, disk-loss protection, or media honesty. A second
directory on the same disk can exercise the verifier, but it does not satisfy
the versioned recovery-custody gate.

## Implemented bounded node-loss ceremony

The Sandwurm three-writer gate now invokes `tools/run-sync-recovery-rehearsal.py`. It reconstructs
one erased writer as a fresh device, then erases all live node roots and reconstructs a new
three-writer mesh from one restored ordinary tree. It never copies Tox savedata, device identity,
authority ledger, namespace store, sync object database, or a branch record into a replacement.

Writer retirement is ordered and deliberately non-magical:

1. run `sync-writer-cutoff` on every survivor;
2. separately revoke the departed principal's synchronization capability;
3. remove the departed Tox friendship;
4. restart/re-prove the surviving authority sessions and exchange every cutoff checkpoint without
   skipping a writer generation;
5. run `sync-checkpoint` on each survivor after the cutoff frontier is shared, then exchange those
   graph floors; and
6. only then admit a fresh replacement that never trusted the obsolete writer.

The two checkpoint barriers matter. A cutoff checkpoint proves the retired writer's terminal
history to existing members. The later graph floor removes that historical writer from the current
observation dependency so a genuinely new member can validate the live frontier without being
silently granted trust in the obsolete principal.

The bounded direct source-linked gate passes 33 files / 131,099 bytes, one empty-node replacement,
total live-node loss, six repair checks, and four exact restore comparisons. A clean retained
2-vCPU/2-GiB Sandwurm run first passes the 512-file capacity and 24-cycle persistent lifecycle, then
repeats that recovery in 97.238 seconds with zero watchdog restarts. The final harness establishes
all six policy edges while the namespace is empty and only then installs the ordinary restore tree;
it never weakens the Agent's refusal to mutate membership during an active pull. See ADRs 0323--0324
and `evidence/2026-09-03-sync-node-loss-recovery.md`.

ADR 0361 also makes the recovery rehearsal pass concrete same-VM drill provenance labels in the
Sandwurm follow-up path. Those labels are bound into all four restore-verifier report hashes and
retained in the merged three-writer receipt, while `backup-independence=not-assessed` and
`restore-provenance=not-assessed` remain mandatory.

ADR 0362 fixes the terminal-cutoff replay bug found by the first soak-smoke recovery run. After a
writer is retired, its exact terminal record is still valid history and can be retained below
`tree-v2/retired-branches/`, but it must not become a live branch pointer again. Compact proof
`.sandwurm/exports/three-writer/run.UFBCMzt9` passes the repaired same-host KVM/ext4 short soak,
retained recovery-provenance follow-up, and storage-fault follow-up.

## What remains before precious data

Run this ceremony on representative noncritical data first. ADR 0360 makes provenance recordable in
the verifier output and ADRs 0361/0362 now provide a short same-host soak/recovery proof, but a
deployment still needs an actually independent, immutable/versioned backup with recorded retention
evidence; repeated generation selection and restore exercises; an actual retained 24-hour writable
soak; near-ceiling capacity; the remaining abrupt-power,
broader record-corruption, and projection/remount open-descriptor matrix; and explicit conflict
review. ADR 0325 now proves a bounded real-ENOSPC/read-only/abrupt-Agent slice on separate ext4
volumes, and ADR 0328 proves the narrower post-scan source-descriptor mutation refusal. ADR 0337
adds one-bit corruption/refusal and operator-supplied exact restoration for the five present live
signed tree-v2 metadata families. Source-linked run `mixJ9VUp` qualifies that
exact cell on the founding networkless KVM/ext4 stack; see
`evidence/2026-09-08-sync-tree-v2-metadata-corruption.md`. It does not prove which backup generation should be selected,
authenticate its provenance, exercise simultaneous or valid-old-state corruption, cut during
restoration, or cover other durable-record families. None of these gates removes host power or
assesses dishonest storage. Keep independent versioned backups after
promotion. One matching drill does not make future generations safe, and IoTox is not yet
recommended as the sole recovery path for precious originals.
