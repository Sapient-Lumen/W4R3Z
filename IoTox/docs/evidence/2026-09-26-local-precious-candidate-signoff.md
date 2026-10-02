# 2026-09-26 local precious-candidate signoff pass

This is a local workstation evidence note, not a product-wide release
attestation. The receipt bundle lives under ignored `.sandwurm` storage:

```text
.sandwurm/exports/precious-candidate.20260926T032238Z.yCLIPcSI/
```

The dataset was a tiny disposable "precious-candidate" tree created only to
exercise the native signoff path. It is not user data and contains no secrets.

## Sync result

The native sync evidence path completed end-to-end:

```text
accepted-sync-stable-gates=6/6
precious-data=operator-signable
ship-decision=allowed-with-evidence-manifest
stable-evidence=accepted
sync-precious-data=accepted
```

The bundle was produced with native commands:

```sh
iotox sync backup plan PATH read-write 30
iotox sync backup verify PATH read-write 30 backup-root=... restored-root=...
iotox sync backup receipt PATH read-write 30 backup-root=... restored-root=... \
  custody-class=same-host-versioned immutable-or-versioned=1 \
  operator-rehearsal-repeatable=1 --out PROOF/sync-backup
python3 tools/qualify-storage-readiness.py --backup-custody-proof PROOF/sync-backup
tools/iotox-repo.sh current-sync-long-soak-receipt --out PROOF/long-soak.json
iotox sync runbook receipt PATH read-write 30 --runbook PROOF/recovery-runbook.md \
  --reviewer owner --accept-reviewed-runbook --out PROOF/recovery-runbook.receipt
iotox sync retention set precious-candidate --keep-days 90 --min-revisions 8 \
  --delete-grace-days 14 --out PROOF/retention-policy.receipt
iotox evidence collect sync PATH read-write 30 --out PROOF/sync-evidence ...
iotox sync precious-status PATH read-write 30 --evidence-dir PROOF/sync-evidence
iotox sync precious-signoff PATH read-write 30 --evidence-dir PROOF/sync-evidence \
  --reviewer owner --accept-operator-responsibility --out PROOF/precious-signoff.receipt
iotox ship-check sync stable --evidence-manifest PROOF/sync-evidence/stable-evidence.manifest
```

Content-free retained hashes:

```text
stable-evidence.manifest sha256=28204d3a19d0e6fa20d214cd1437fb22e19a636150f855fac10524b1d6a5d5f7
precious-signoff.receipt sha256=99b480be713bfe08ff0cbdb7f903c39b935de17043086e115d0f02c7d6195a1f
```

## Ratox daily-driver result

The same pass collected a Ratox daily-driver porch bundle under:

```text
PROOF/terminal-daily-driver/
```

Observed results:

```text
pidfd=live-proved
landlock=live-proved
cgroup-v2=available
sudo-default=disabled-until-sudo-profile-and-host-policy-are-explicit
production-activation=requires-terminal-activation-check
executable-state=present
payload-ready=1
production-activation=operator-attested
daily-driver-graduation=operator-attested
repo-certified=0
```

The short terminal soak smoke receipt verified at 60 seconds and correctly
failed the stable 86,400-second floor:

```text
accepted=1
accepted=0
blocker=terminal long-soak receipt is shorter than required
```

Retained hashes:

```text
terminal-smoke-soak.receipt sha256=9b7faeb0c90c5d1327424e9948143e709d050fc6f9d7b9f887f2cd01d229cd9d
ship-check-all-stable.out sha256=29e335c1020b2b55dac50c2a8651ff000ef0604e86e9032540edd7ff25272cd6
```

## Release boundary

`iotox ship-check all stable --evidence-manifest PROOF/sync-evidence/stable-evidence.manifest`
remained blocked because the manifest intentionally contains only sync stable
evidence. The missing gates were the 12 Ratox stable gates:

```text
terminal.daily-control
terminal.profile-freshness
terminal.service-supervision
terminal.reconnect-continuity
terminal.cgroup-delegation
terminal.route-loss
terminal.long-soak
terminal.tor-route-loss
terminal.i2p-route-loss
terminal.sudo-policy
terminal.security-review
terminal.activation-decision
```

That is the desired boundary. Sync can be operator-signed for a specific
working copy when the evidence exists. Ratox daily-driver setup can be
operator-attested. Full `all stable` must still wait for a real terminal stable
evidence manifest, especially a real 24-hour terminal long soak receipt.

