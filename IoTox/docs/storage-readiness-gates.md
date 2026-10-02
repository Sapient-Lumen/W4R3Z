# Storage readiness gates

Status: same-host storage substrate and live-Agent production transaction-prefix
replay are accepted. IoTox does not certify storage media, disk survival, host
integrity, or filesystem-wide corruption recovery because those are not IoTox
product goals. Precious-data readiness is therefore gated only on the
sync-layer discipline IoTox can own: software storage science, versioned
recovery custody outside normal IoTox sync mutation, restore drills, and an
operator recovery runbook. Updated 2026-10-01.

The executable status command is:

```sh
tools/iotox-repo.sh storage-readiness
iotox ship-check sync stable
```

That report is content-free. It verifies retained storage receipts and then
fails closed unless every graduation class below has accepted evidence. For
external proof intake, verify the custody receipt first and then point the
combined readiness report at the accepted run directory or JSON file:

```sh
tools/iotox-repo.sh sync-precious-data-gates-plan --json
tools/iotox-repo.sh sync-precious-data-gates-plan \
  --dataset /dataset \
  --write-templates /proof/templates
tools/iotox-repo.sh sync-backup-custody-verify /proof/run/backup-custody.json
tools/iotox-repo.sh storage-readiness \
  --backup-custody-proof /proof/run
```

`sync-precious-data-gates-plan` is the safe porch before the custody work. It
does not format, mount, unmount, certify devices, or read file contents. It
names backup/restore capabilities, writes invalid-by-default backup-custody and
recovery-runbook templates to an explicit directory, and says
`storage-media-qualification=not-an-iotox-goal`.

For one candidate dataset, the native operator porch is:

```sh
iotox sync trust-plan /dataset read-write 30

iotox sync backup plan /dataset read-write 30

iotox sync backup verify /dataset read-write 30 \
  backup-root=/backup/dataset restored-root=/restore-drill/dataset \
  backup-system=borg backup-generation=gen001 \
  backup-failure-domain=external-ssd restore-provenance=drill

iotox sync backup receipt /dataset read-write 30 \
  backup-root=/backup/dataset restored-root=/restore-drill/dataset \
  backup-system=borg backup-generation=gen001 \
  live-failure-domain=live.host backup-failure-domain=external-ssd \
  restored-failure-domain=restore.host restore-provenance=drill \
  custody-class=same-host-versioned immutable-or-versioned=1 \
  operator-rehearsal-repeatable=1 --out /proof/backup

iotox sync runbook plan /dataset read-write 30

iotox sync runbook receipt /dataset read-write 30 \
  --runbook /proof/recovery-runbook.md \
  --reviewer owner --accept-reviewed-runbook \
  --out /proof/recovery-runbook.receipt

iotox sync retention set photos \
  --keep-days 90 --min-revisions 8 --delete-grace-days 14 \
  --out /proof/retention.receipt

iotox sync-dataset-readiness /dataset read-write 30 \
  backup-root=/backup/dataset restored-root=/restore-drill/dataset \
  backup-system=borg backup-generation=gen001 \
  backup-failure-domain=external-ssd restore-provenance=drill \
  verify-recovery=1

iotox sync graduation-check /dataset read-write 30 \
  --evidence local-preflight=doctor \
  --evidence storage-readiness=repo.storage \
  --evidence recovery-custody=backup.receipt \
  --evidence restore-drill=restore.drill \
  --evidence recovery-runbook=runbook.review

iotox evidence collect sync /dataset read-write 30 --out /proof/sync \
  --storage-readiness /proof/storage-readiness.json \
  --long-soak /proof/long-soak.json \
  --backup-custody /proof/backup/backup-custody.json \
  --restore-drill /proof/backup/restore-drill.json \
  --recovery-runbook /proof/recovery-runbook.receipt \
  --retention-policy /proof/retention.receipt

iotox evidence manifest /proof/sync --out /proof/stable-evidence.manifest
iotox sync precious-status /dataset read-write 30 --evidence-dir /proof/sync
iotox sync precious-signoff /dataset read-write 30 \
  --evidence-dir /proof/sync --reviewer owner \
  --accept-operator-responsibility \
  --out /proof/precious-signoff.receipt
```

`iotox sync trust-plan` is the ordinary non-mutating runbook command. It runs
the same local sync-doctor inspection, prints the exact
`sync-dataset-readiness` command shape, names the repository storage-readiness
and backup-custody verifier commands, prints the matching
`sync graduation-check` shape, and keeps `precious-data-default=blocked`.

`iotox sync-dataset-readiness` runs the local sync-doctor inspection, prints the
exact `sync-recovery-verify` command when backup/restore roots are supplied,
and can run that strict restore comparison inline with `verify-recovery=1`.
Even then it keeps `precious-data-repo-certified=0`. It is a human readiness
porch, not an accepted storage-science receipt.

`iotox sync backup verify` is the native restore-drill porch. It runs the same
tree-v2 recovery comparison and reports whether the restored tree matches the
backup tree. `iotox sync backup receipt` is stricter: it writes
`backup-custody.json`, `restore-drill.json`, and the raw recovery report only
when the restore matches, custody labels are explicit, the operator declares a
supported `custody-class`, the generation is immutable or versioned, and the
rehearsal is repeatable. Distinct root devices are recorded as useful metadata,
not required. Same-host custody can pass when it is versioned and outside normal
IoTox sync write/delete/GC mutation; it still is not disk-loss,
host-compromise, or filesystem-wide corruption protection, because those are
different layers of responsibility.

`iotox sync runbook receipt` is the native recovery-runbook porch. It reads a
reviewed local recovery document, hashes it, binds the receipt to the hashed
dataset selector, requires explicit `--accept-reviewed-runbook`, and writes a
content-free line record. The receipt does not contain the runbook text or the
literal dataset path. Minimal hand-authored runbook records no longer satisfy
the stable gate; accepted records must carry reviewer, runbook hash, dataset
selector hash, nonzero runbook byte count, and the stop/restore/verify/retire/
rehearse coverage flags.

`iotox sync retention set` writes a reviewed content-free retention policy:
keep-days, minimum revisions, delete grace, guarded delete propagation, and
GC requiring backup custody. `iotox sync precious-status` requires that policy
in addition to storage-readiness, long-soak, backup-custody, restore-drill, and
runbook receipts before it says `precious-data=operator-signable`. It still
prints `repo-certified=0`: signable means the operator has a complete evidence
trail for a working copy, not that IoTox is the only archive.

`iotox evidence collect sync` copies only receipts that match their native
shape checks into a bounded evidence directory and writes a sync stable
manifest when all six stable sync gates are present. `iotox evidence manifest`
can regenerate that manifest from the directory.

For the long-soak slot, the current accepted repository proof is
`.sandwurm/exports/three-writer/run.2nPKtCoX`. Mint the native stable-gate
receipt with:

```sh
tools/iotox-repo.sh current-sync-long-soak-receipt --out /PROOF/long-soak.json
```

The generated verifier receipt has SHA-256
`6e88a2efcf33b268ff82cf0fdaaa99e8c45be612f50c9e77dc0714ab2d6759a0` and closes
the same-host sync long-soak gate. The raw guest receipt inside the compact
proof has SHA-256
`687b4ace878465ba733399a722d009a8d99afc616fe244ad7f2721443263356b`; it is lab
evidence, not the native stable-gate input. Neither file closes a specific
dataset's versioned recovery-custody or restore-runbook gates.

`iotox sync precious-signoff` is the final native human porch. It is not a new
upstream certification gate; it writes only after `precious-status` would say
`operator-signable`, requires explicit `--accept-operator-responsibility`, and
persists a content-free receipt that binds the stable evidence manifest hash,
the reviewed retention-policy hash, the other receipt hashes, and a hashed
dataset selector. It deliberately avoids storing file content, dataset
entries, or the literal dataset path.

`iotox sync graduation-check` is the stricter fail-closed porch for a single
working copy. With no labels it exits blocked and prints every gate that still
needs evidence: local preflight, repository storage-readiness, recovery
custody, restore drill, and recovery runbook. With all five labels it can say
`working-copy-graduation=operator-attested`. It still says
`precious-data-readiness=blocked` and `repo-certified=0`; labels are custody
references, not cryptographic proof and not permission to delete every other
versioned recovery path.

`iotox ship-check sync stable` is stricter again: it answers the release
question and remains blocked for no-concern shipping. When a stable evidence
manifest is supplied, the binary rejects wrong-shape sync receipts before
accepting the manifest: storage-readiness, long-soak, backup-custody,
restore-drill, and recovery-runbook files must match their content-free receipt
class instead of being ordinary prose. The bounded release channel remains
`iotox ship-check sync founder-preview`, meaning a working copy with versioned
recovery-custody evidence and explicit precious-data nonclaims.

## Current gate state

| Gate | Current state | Accepted evidence | What it means |
| --- | --- | --- | --- |
| Same-host dishonest-storage matrix | Accepted | `.sandwurm/exports/sync-dishonest-storage/run.qGwEvF17` | ext4+btrfs detect/refuse valid-old rollback, cross-family rollback, torn manifest, and masked `dm-flakey` writes across six IoTox-shaped families. |
| Same-host exact block-prefix replay | Accepted | `.sandwurm/exports/sync-log-writes-prefix/run.90LCC7ra` | ext4+btrfs replay exact `dm-log-writes` marks for older-valid, mixed manifest/record, and complete-current prefixes. |
| Live Agent production transaction-prefix replay | Accepted | `.sandwurm/exports/sync-production-prefix/run.HYXJnDzI` | Real Agent `sync-create` and `sync-publish` transactions replay from ext4+btrfs `dm-log-writes` prefixes and match the marked production inventory. |
| Storage media certification | Not an IoTox goal | none | IoTox does not certify disks, controllers, firmware, write caches, or power-loss behavior as a product gate. |
| Versioned recovery custody | Blocked by default | `backup-custody.json` verifier exists | Requires a content-free receipt proving a matched restore from immutable/versioned custody outside normal IoTox sync mutation; this is sync-layer recovery practice, not disk-loss, host-compromise, or filesystem-wide corruption protection. |
| Native recovery runbook receipt | Implemented | `iotox sync runbook receipt` | Hash-binds a reviewed runbook and dataset selector without storing the runbook content or dataset path. |
| Native retention policy | Implemented | `iotox sync retention set` | Records guarded delete propagation and GC requiring backup custody as a reviewed content-free policy. |
| Native evidence collection | Implemented | `iotox evidence collect sync` | Gathers shape-checked receipts into a stable sync manifest directory; missing/placeholder receipts do not pass. |
| Dataset precious-status | Implemented and fail-closed | `iotox sync precious-status PATH ...` | Reports `operator-signable` only when storage, soak, backup, restore, runbook, and retention evidence are all accepted. |
| Operator precious-data signoff | Implemented and fail-closed | `iotox sync precious-signoff PATH ...` | Writes a content-free local acceptance receipt only after all precious-status gates pass and the operator accepts responsibility. |
| Precious-data readiness | Blocked by default | none | IoTox sync is not recommended as the sole trusted path for irreplaceable originals until the backup/restore/runbook gates are genuinely closed. |

## Production transaction-prefix replay

ADR 0381 accepts the first live-Agent production-prefix adapter. The accepted
receipt, `.sandwurm/exports/sync-production-prefix/run.HYXJnDzI`, starts the
real Agent with sync enabled, writes the durable Agent state, source directory,
and sync-policy root through `dm-log-writes`, runs ordinary `sync-create`,
`sync-publish`, and `sync-repair` commands, and replays exact block prefixes at
two transaction boundaries.

An accepted production-prefix receipt must name:

- IoTox binary SHA-256 and source revision;
- filesystem and block interposer;
- namespace/configuration class without exposing paths or content;
- the exact transaction family and boundary;
- the selected replay prefix, mark, or entry number;
- production `sync-repair` verification result;
- replayed-prefix comparison against the marked production inventory; and
- `contains_secrets=false`.

The first accepted marks are `sync-create-generation-1` and
`sync-publish-generation-2` on both ext4 and btrfs. Passing means IoTox either
observes a permitted current state or detects that a replayed state is older
than the acknowledged floor. Passing does not mean the underlying disk,
firmware, VM, host, or backup system is trustworthy.

This gate is intentionally transaction-boundary coverage. It does not yet cut
every internal rename/fsync subtransaction inside `sync-create` or
`sync-publish`; that deeper interleaving campaign remains optional follow-up
science rather than a replacement for backup-custody gates.

## Storage media certification is out of scope

IoTox will not run or require destructive physical-media qualification. The
project tests its own sync logic, receipt handling, rollback refusal, replay
behavior, and recovery ceremonies. It does not certify a particular disk,
controller, firmware stack, write cache, power-loss behavior, or filesystem
deployment as safe.

That boundary is deliberate. The way IoTox becomes safe enough for important
working sets is not “trust this disk because IoTox blessed it.” The way forward
is:

- local storage-science receipts that prove IoTox detects the failure classes
  it claims to detect;
- immutable/versioned recovery custody outside normal IoTox sync write/delete/GC
  mutation;
- restore drills that compare backup and restored inventories before live
  mutation resumes; and
- an operator runbook that says how to stop writers, restore, verify, retire
  obsolete writers, and rehearse again.

## Versioned recovery custody

Synchronization is not a recovery story until restore can succeed from a
versioned or immutable source that normal IoTox sync mutation cannot rewrite,
delete, or garbage-collect. That is the scope of IoTox's custody gate. It is
not a claim about surviving a lost disk, compromised host, or filesystem-wide
corruption. An accepted custody receipt must prove:

- versioned or immutable recovery storage outside the live sync root and
  outside normal IoTox sync mutation;
- explicit live, custody, and restore-drill failure-domain labels;
- exact generation/provenance labels;
- byte-exact verification of the restored sync evidence before live mutation;
- an operator rehearsal that can be repeated; and
- no reliance on undisclosed paths, secrets, or live cluster state.

Same-host custody can close this gate if it is versioned/immutable and outside
normal IoTox sync mutation. It is still a sync-layer recovery gate, not disaster
recovery.

The verifier for that intake is `tools/verify-sync-backup-custody.py`. It
accepts a content-free `iotox.sync-backup-custody.v1` receipt only when the
record names a supported `custody_class`, says the generation is
immutable/versioned, reports a matching restore, records whether the roots were
on distinct devices, is repeatable, is content-free, and carries the required
nonclaims for disk loss, host compromise, filesystem-wide corruption, storage
media certification, and content custody.

`iotox sync-dataset-readiness` can record operator-supplied custody labels,
render the matching `sync-recovery-verify` command, and run the restore drill
inline with `verify-recovery=1`. A matched drill can upgrade the dataset report
to `precious-data-candidate=restore-verified-operator-attested`; it still does
not close the recovery-custody gate without accepted custody evidence.

## Precious-data readiness

Precious-data readiness is deliberately last. It requires accepted local
storage science, versioned recovery custody, restore drills, and operator
documentation saying how to run, verify, restore, and stop before damage
spreads. Native `precious-status` adds the missing human ergonomics: retention
policy and stable evidence collection must also be present before the local
dataset becomes operator-signable.

The daily-use safety rails inside IoTox's scope are now native too:
`iotox sync folder-status` is the content-free folder dashboard, local freeze
records make native sync mutator commands fail closed for that namespace, and
`iotox sync safe-delete` moves a reviewed target into delete quarantine with a
receipt instead of purging it. These do not make IoTox a backup system; they
make ordinary operator mistakes more recoverable before a signed tombstone,
GC, or retention decision spreads.

Until then the honest product sentence is:

```text
IoTox sync is a useful, increasingly well-tested synchronized working copy.
It is not yet the sole system of record for irreplaceable data.
```
