# Ship readiness

Status: IoTox sync and Ratox are evidence-gated stable surfaces. The
repository now carries one accepted local all-scope stable dossier, but stable
is not a slogan the binary claims by default: operators must pass its manifest
explicitly so the binary, host/route scope, dataset scope, and owner decision
stay visible. Sync receipt classes are hash-bound and shape-checked so
placeholder prose cannot certify precious-data evidence. Updated 2026-10-01.

The native release gate is:

```sh
iotox ship-check all stable
iotox ship-check sync stable
iotox ship-check terminal stable
```

Stable mode is the “ready to ship without concern?” question. It exits blocked
without a complete stable evidence manifest. That is intentional: the command
is a release brake, not a marketing badge.

The current accepted local dossier pointer is:

```sh
tools/iotox-repo.sh current-stable-evidence
iotox ship-check all stable \
  --evidence-manifest .sandwurm/exports/terminal-soak/run.OjbHRv/all-stable-evidence.service-reality.XOlEdI/stable-evidence.manifest
```

For private founder use and carefully labeled evaluation builds:

```sh
iotox ship-check all founder-preview
tools/iotox-repo.sh release-plan founder-preview
tools/iotox-repo.sh release-check founder-preview --iotox /path/to/iotox
```

That can pass, but only with explicit nonclaims:

- sync is a synchronized working-copy system, not the sole system of record for
  precious originals;
- versioned recovery custody and restore drills remain mandatory;
- Ratox is a profile-bound self-machine control surface, not a universal SSH
  replacement;
- sudo remains disabled by default and belongs to a reviewed profile plus the
  host sudo/PAM policy;
- Tor/I2P route labels are evidence scopes, not anonymity or reliability
  guarantees; and
- support bundles and readiness output are content-free operator evidence, not
  remote attestation.

## Current release table

| Surface | Founder-preview channel | Stable/no-concern channel |
| --- | --- | --- |
| Sync | Allowed as `working-copy-with-versioned-recovery-custody` | Accepted for the current local dossier; blocked without complete manifest |
| Precious-data sync | Blocked | Accepted only for datasets covered by the supplied dossier plus operator signoff |
| Ratox terminal | Allowed as `self-owned-profile-bound-daily-driver-candidate` | Accepted for the current local dossier; blocked without complete manifest |
| Sudo through Ratox | Explicit profile only | Evidence-gated; requires sudo/PAM review record |
| Tor/I2P route privacy | Bounded route evidence only | Evidence-gated route scope, not anonymity certification |
| Backup/disaster recovery/host survival | Not an IoTox goal | Stable sync requires recovery practice evidence, but backups, disk-loss survival, host-compromise survival, filesystem-wide corruption recovery, and media certification remain outside the IoTox product contract |
| Fleet/kernel/media certification | Not an IoTox goal | IoTox can record bounded host/service evidence, but it does not certify fleets, kernels, disks, controllers, firmware, write caches, or power-loss behavior |

## Release command trail

`iotox ship-check` owns the product claim. `tools/iotox-repo.sh` owns the
repository command trail around that claim:

```sh
tools/iotox-repo.sh release-plan founder-preview
tools/iotox-repo.sh release-check founder-preview --iotox /path/to/iotox
tools/iotox-repo.sh datacube --seed
```

The release check requires a clean worktree, `git diff --check`, shell syntax
for the release scripts, an executable IoTox binary, and a passing ship gate
for the selected channel. Founder-preview is allowed only with explicit
nonclaims; stable is allowed only with a supplied evidence manifest. The check
does not itself package artifacts and does not run hidden storage or hardware
proofs; the seed datacube command packages the already-checked clean source
state plus a one-commit cloneable bundle as the recommended public handoff
object. Use `tools/iotox-repo.sh datacube --upload` only when full local Git
history is intentionally part of the handoff.

Stable has a separate evidence-dossier path:

```sh
tools/iotox-repo.sh stable-evidence-plan
tools/iotox-repo.sh current-stable-evidence
iotox evidence dossier-plan \
  --dataset /dataset \
  --out /proof/stable \
  --terminal-root ~/.local/state/iotox \
  --peer alias:desktop
iotox evidence dossier-status /proof/stable \
  --scope all \
  --manifest /proof/stable/stable-evidence.manifest
iotox ship-check all stable --evidence-manifest stable-evidence.manifest
tools/iotox-repo.sh release-check stable \
  --iotox /path/to/iotox \
  --evidence-manifest stable-evidence.manifest
```

Without that complete manifest, stable remains blocked. With it, the native
gate can pass for the selected scope while binding every required gate to a
content-free receipt or review-record file and SHA-256. ADR 0398 additionally
shape-checks every sync receipt class (`sync-doctor`, storage-readiness,
long-soak, backup-custody, retained restore drill, and recovery
runbook) so the stable gate rejects placeholder notes before anyone mistakes
them for precious-data evidence. See
[`docs/stable-release-evidence.md`](stable-release-evidence.md).
`evidence dossier-plan` and `evidence dossier-status` keep the whole path
discoverable from the binary: the first prints the exact command trail, and
the second reports per-gate accepted/missing/blocked status plus the final
manifest/ship-check commands.

The founder-preview release recipe and required nonclaim label live in
[`docs/founder-preview-release.md`](founder-preview-release.md). The repository
datacube contract remains in
[`docs/revision-packaging.md`](revision-packaging.md) and
[`docs/conversation-datacubes.md`](conversation-datacubes.md).

## Why stable blocks by default

Stable/no-concern sync needs more than local correctness, so the native gate
blocks unless the operator supplies a complete accepted manifest. The sync side
needs:

- an accepted long-running sync soak for the writer shape being claimed;
- immutable/versioned recovery custody outside normal IoTox sync write/delete/GC
  mutation;
- repeated restore drills;
- a reviewed retention/undelete/GC policy for the namespace;
- clear operator recovery runbooks; and
- enough user-facing guardrails that “sync” cannot be mistaken for “backup.”

Stable/no-concern Ratox needs more than a working remote PTY. The terminal side
needs:

- daily-driver long soaks across the routes the operator intends to use;
- route-loss proof for direct, Tor, and I2P where claimed;
- sudo/PAM policy review on the target host;
- service-manager and cgroup behavior across the deployment families we name;
- independent security review; and
- explicit owner activation, because root-capable interactive shells are never
  a silent default.

## Commands that close local operator checklists

These do not make the stable release pass by themselves, but they are the
ordinary local gates:

```sh
tools/iotox-repo.sh sync-precious-data-gates-plan \
  --dataset /dataset \
  --write-templates /proof/templates

iotox sync backup plan /dataset read-write 30
iotox sync backup verify /dataset read-write 30 \
  backup-root=/backup/dataset restored-root=/restore-drill/dataset \
  backup-system=borg backup-generation=gen001 \
  backup-failure-domain=external restore-provenance=drill
iotox sync runbook receipt /dataset read-write 30 \
  --runbook /proof/recovery-runbook.md \
  --reviewer owner --accept-reviewed-runbook \
  --out /proof/recovery-runbook.receipt
iotox sync retention set dataset \
  --keep-days 90 --min-revisions 8 --delete-grace-days 14 \
  --out /proof/retention.receipt

iotox sync graduation-check /dataset read-write 30 \
  --evidence local-preflight=doctor \
  --evidence storage-readiness=repo.storage \
  --evidence recovery-custody=backup.receipt \
  --evidence restore-drill=restore.drill \
  --evidence recovery-runbook=runbook.review

iotox evidence collect sync /dataset read-write 30 --out /proof/sync \
  --storage-readiness /proof/storage-readiness.json \
  --long-soak /proof/long-soak.json \
  --backup-custody /proof/backup-custody.json \
  --restore-drill /proof/restore-drill.json \
  --recovery-runbook /proof/recovery-runbook.receipt \
  --retention-policy /proof/retention.receipt
iotox sync precious-status /dataset read-write 30 --evidence-dir /proof/sync
iotox sync precious-signoff /dataset read-write 30 \
  --evidence-dir /proof/sync --reviewer owner \
  --accept-operator-responsibility \
  --out /proof/precious-signoff.receipt

iotox terminal graduation-check --root ~/.local/state/iotox --peer alias:desktop \
  --evidence daily-control=local.gate \
  --evidence profile-freshness=profile.check \
  --evidence service-supervision=terminal.service.systemd-user \
  --evidence reconnect-continuity=cli.reconnect \
  --evidence cgroup-delegation=nixos.cgroup \
  --evidence route-loss=tox.loss \
  --evidence long-soak=soak.24h \
  --evidence tor-route-loss=tor.operator \
  --evidence i2p-route-loss=i2p.fronts \
  --evidence sudo-policy=host.sudo \
  --evidence security-review=review \
  --evidence activation-decision=owner

iotox terminal soak-plan --root ~/.local/state/iotox --peer alias:desktop
iotox terminal soak-run --root ~/.local/state/iotox --peer alias:desktop \
  --route native \
  --seconds 86400 \
  --sample-every 300 \
  --out ./terminal-24h.receipt
iotox terminal soak-verify ./terminal-24h.receipt
iotox service status-plan --target all --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit-prefix iotox-self \
  --binary /usr/bin/iotox
iotox service status-receipt --target all --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit-prefix iotox-self \
  --binary /usr/bin/iotox \
  --service-manager-state active \
  --enabled-state enabled \
  --log-state reviewed \
  --health-state passed \
  --upgrade-state passed \
  --accept-operator-responsibility \
  --out /proof/terminal-service-supervision.receipt
iotox evidence collect terminal \
  --root ~/.local/state/iotox \
  --peer alias:desktop \
  --out /proof/stable \
  --service-reality /proof/terminal-service-supervision.receipt \
  --long-soak ./terminal-24h.receipt \
  --evidence daily-control=local.gate \
  --evidence profile-freshness=profile.check \
  --evidence reconnect-continuity=cli.reconnect \
  --evidence cgroup-delegation=nixos.cgroup \
  --evidence route-loss=tox.loss \
  --evidence tor-route-loss=tor.operator \
  --evidence i2p-route-loss=i2p.fronts \
  --evidence sudo-policy=host.sudo \
  --evidence security-review=owner.review \
  --evidence activation-decision=owner.decree

iotox person graduation-check --root ~/.local/state/iotox \
  --evidence background-delivery=service.loop \
  --evidence offline-retry-expiry=outbox.retry \
  --evidence receipt-summary=receipts.rollup \
  --evidence human-read-semantics=read.policy \
  --evidence transcript-convergence=transcripts.checked \
  --evidence group-semantics=groups.reviewed \
  --evidence service-supervision=systemd.user \
  --evidence route-policy=route-set.v2 \
  --evidence operator-review=owner

iotox person tox-bridge-graduation-check \
  --bridge-store ~/.local/state/iotox/tox.bridge \
  --evidence toxic-native=toxic.default \
  --evidence toxic-forced-tcp=toxic.tcp \
  --evidence inbound-fanout=lab.inbound \
  --evidence outbound-send=lab.outbound \
  --evidence identity-boundary=review \
  --evidence bridge-store=content-free \
  --evidence transcript-commit=transcript \
  --evidence route-nonclaims=routes \
  --evidence operator-review=owner

iotox route-qualification-check --scope toxic \
  --evidence toxic-native=toxic.default \
  --evidence toxic-forced-tcp=toxic.tcp \
  --evidence toxic-tor=tor.route \
  --evidence toxic-i2p=i2p.route \
  --evidence route-nonclaims=review \
  --evidence operator-review=owner
```

For the combined elapsed campaign, use the repository soak porch:

```sh
tools/run-massive-soak.py plan
tools/run-massive-soak.py preflight
tools/run-massive-soak.py smoke
tools/run-massive-soak.py launch-long \
  --include sync --include terminal --include person --include toxic
tools/run-massive-soak.py status
tools/run-massive-soak.py watch --samples 12 --interval 300
```

That runner records exact commands, logs, PIDs, and native receipt paths under
`.sandwurm/massive-soak/`. It does not manufacture operator evidence labels
for the stable manifest; it keeps the long sync, terminal, person, Toxic
bridge, service, and route evidence reviewable from one retained campaign
root. See [`docs/massive-soak.md`](massive-soak.md).

The stable manifest also needs `sync.long-soak=accepted` with a native
verifier receipt path and matching SHA-256; it is not part of the per-dataset
`sync graduation-check` label set. The current accepted sync long-soak proof is
`.sandwurm/exports/three-writer/run.2nPKtCoX`; generate the stable receipt with:

```sh
tools/iotox-repo.sh current-sync-long-soak-receipt --out /PROOF/long-soak.json
```

That generated receipt has SHA-256
`6e88a2efcf33b268ff82cf0fdaaa99e8c45be612f50c9e77dc0714ab2d6759a0`.

`iotox evidence collect terminal` is the native terminal-side manifest porch.
It writes content-free `iotox.terminal-stable-evidence.v1` receipts for the
ordinary operator-attested Ratox gates, copies a checked
`iotox.service-reality.v1` receipt for `terminal.service-supervision`, and
refuses to copy a `terminal.long-soak` receipt unless
`iotox terminal soak-verify` would accept it at the 86,400 second stable
floor. Short smoke receipts remain useful, but they do not enter the stable
manifest.

The person and route graduation checks are not part of the historical
sync/Ratox stable manifest. They are now the ordinary operator checklists for
the lived multidevice messenger, normal Toxic bridge, and Tor/I2P route claims.
They preserve the same release discipline: complete labels can make the
installation `operator-attested`, but they still print `repo-certified=0`,
`anonymity-certified=0`, or the relevant identity nonclaim where appropriate.

The release rule is blunt:

```text
If stable/no-concern lacks a complete evidence manifest, say blocked.
If founder-preview is shipped, ship it with the nonclaims attached.
```
