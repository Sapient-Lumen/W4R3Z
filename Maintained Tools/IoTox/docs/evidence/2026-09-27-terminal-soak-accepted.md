# 2026-09-27 — Native terminal long-soak accepted

Status: accepted terminal stable evidence.

The native terminal long-soak runner started on 2026-09-26 completed cleanly
and produced an accepted `iotox.terminal-long-soak-receipt.v1` receipt.

Run directory:

```text
.sandwurm/exports/terminal-soak/run.OjbHRv
```

Verifier result:

```text
iotox-terminal-long-soak-verify-v1
receipt=.sandwurm/exports/terminal-soak/run.OjbHRv/terminal-24h.receipt
minimum-seconds=86400
stable-evidence-key=terminal.long-soak
accepted=1
mutated=0
boundary=receipt-shape-and-duration-check-only; real-soak-custody-remains-operator-evidence
```

Runner summary:

```text
result=accepted
interrupted=0
observed-seconds=86400
samples=289
max-sample-gap-seconds=300
accepted=1
```

Terminal stable evidence was collected into:

```text
.sandwurm/exports/terminal-soak/run.OjbHRv/terminal-stable-evidence.5VjwlW
```

Terminal stable ship-check accepted that manifest:

```text
ship-decision=allowed-with-evidence-manifest
stable-without-concern=accepted
stable-evidence=accepted
terminal-stable=accepted
terminal-fleet-certification=evidence-attested
```

The terminal receipts were then combined with the retained sync stable receipts
from:

```text
.sandwurm/exports/precious-candidate.20260926T032238Z.yCLIPcSI/proof/sync-evidence
```

Combined stable evidence directory:

```text
.sandwurm/exports/terminal-soak/run.OjbHRv/all-stable-evidence.ydZbjn
```

Combined manifest:

```text
manifest=.sandwurm/exports/terminal-soak/run.OjbHRv/all-stable-evidence.ydZbjn/stable-evidence.manifest
manifest-sha256=5d38312c8c419077a0667a675de56ffa607a9fe27994e8ae8809f8965df71977
```

`iotox ship-check all stable` accepted the combined manifest:

```text
ship-decision=allowed-with-evidence-manifest
stable-without-concern=accepted
stable-evidence=accepted
sync-stable=accepted
sync-precious-data=accepted
terminal-stable=accepted
terminal-fleet-certification=evidence-attested
```

The repository release check also accepted the stable path:

```text
iotox-release-check-v1
channel=stable
commit=97bbb7b085207334c2f87bfd7c0024883526b891
git-clean=1
diff-check=pass
shell-syntax=pass
ship-check=pass
stable-brake=passed-with-evidence-manifest
decision=stable-release-path-ready
```

Boundary: this graduates the terminal stable evidence gate for this local
host/route/operator evidence set and allows the current repository stable
release path to pass with a complete evidence manifest. It does not turn the
operator labels into cryptographic proof and it does not claim every future
host, route, sudo policy, or fleet deployment has been qualified.

## Service-reality dossier refresh

Later on 2026-09-27, the combined all-scope dossier was refreshed so
`terminal.service-supervision` uses the native `iotox.service-reality.v1`
receipt shape from `iotox service status-receipt` instead of the legacy
generic `iotox.terminal-stable-evidence.v1` label. The sync receipts,
terminal long-soak receipt, and other terminal evidence receipts remain the
same retained scope.

Refreshed combined stable evidence directory:

```text
.sandwurm/exports/terminal-soak/run.OjbHRv/all-stable-evidence.service-reality.XOlEdI
```

Refreshed manifest:

```text
manifest=.sandwurm/exports/terminal-soak/run.OjbHRv/all-stable-evidence.service-reality.XOlEdI/stable-evidence.manifest
manifest-sha256=1dfef328a55c91259d479134d71606d78f8bcf7f05a40ef136c7b0eb810d9006
```

Both of these commands accepted the refreshed dossier:

```sh
iotox evidence dossier-status \
  .sandwurm/exports/terminal-soak/run.OjbHRv/all-stable-evidence.service-reality.XOlEdI \
  --scope all \
  --manifest .sandwurm/exports/terminal-soak/run.OjbHRv/all-stable-evidence.service-reality.XOlEdI/stable-evidence.manifest

iotox ship-check all stable \
  --evidence-manifest .sandwurm/exports/terminal-soak/run.OjbHRv/all-stable-evidence.service-reality.XOlEdI/stable-evidence.manifest
```
