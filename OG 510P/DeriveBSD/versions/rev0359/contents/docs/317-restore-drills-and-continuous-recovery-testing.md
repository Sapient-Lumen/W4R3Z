# Restore drills and continuous recovery testing

Backups are only valuable if restores are **routine**.
Most fleets fail here: backups exist, but the restore path is undocumented, key material is missing, or the resulting system is subtly broken.

DeriveBSD treats restore testing as **continuous recovery testing**: a scheduled workflow that produces evidence.

## Design stance

- A restore drill is a **test** of:
  - data availability (the bytes exist)
  - key availability (crypto policy can decrypt/unseal)
  - procedure correctness (apply steps work)
  - service correctness (the restored service passes health checks)

- Drills must be **safe by default**:
  - restore into a quarantine namespace (quarantine dataset / isolated microVM)
  - no outbound network by default
  - no ambient secrets; only policy-issued credentials

- Drills produce **typed receipts** so incidents can answer: “when was this backup last restored successfully, and what was checked?”

## `restore.drill.receipt`

A `restore.drill.receipt` is emitted by a drill runner.
It references the `backup.receipt` (or snapshot set) under test, records the environment in which the drill ran, and includes the checks performed.

Schema: `spec/restore.drill.receipt.schema.json`

This object intentionally stays small:
- digest links instead of embedding large logs
- optional pointers to support bundles (export-governed) when deeper artifacts are needed

Restore drills now supplement, rather than replace, the official restore apply lane: `restore.plan` / `restore.receipt` are standardized, ordinary restore stays quarantine-first, and any later `replacement-target` apply should usually point back to a prior verified restore receipt instead of pretending a drill receipt alone is arbitrary replacement authority. See `docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md`.

## Practical drill patterns

1) **Mount-only drill** (fast, frequent)
- fetch backup bytes
- decrypt/unpack
- verify snapshot digests
- mount datasets read-only

2) **Cold-start drill** (moderate)
- restore into a new microVM instance
- start services
- run health checks / smoke tests

3) **Full recovery rehearsal** (slow, periodic)
- restore into an isolated staging topology
- validate dependencies (e.g., schema migrations)
- verify RTO/RPO expectations

## Policy hooks

- Authority budgets should cap:
  - how often drills can access sensitive backups
  - how much detail a drill receipt may retain
  - whether drill artifacts can be exported off-host

- Secrets and key management:
  - drill workflows should exercise the real key paths (crypto portal / sealed secrets lane), not bypass with file keys.

See: `docs/223-secrets-and-key-management-as-evidence.md`, `docs/306-crypto-operations-portal-and-split-keys.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`, `docs/464-backup-and-restore-posture-by-profile.md`, `docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md`.

Last updated: 2026-03-21r350
