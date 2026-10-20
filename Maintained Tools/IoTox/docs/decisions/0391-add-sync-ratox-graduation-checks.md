# 0391 — Add sync and Ratox graduation checks

Date: 2026-09-20

Status: accepted

## Context

The project has working operator porches for the two largest remaining
day-to-day trust fronts:

- `iotox sync trust-plan` and `iotox sync-dataset-readiness` explain how to
  preflight a candidate sync directory, run backup/restore drills, and keep the
  precious-data boundary explicit; and
- `iotox terminal daily-status` and `iotox terminal activation-check` explain
  how to turn Ratox into an SSH-shaped daily control surface without silently
  enabling root or widening route claims.

Those commands made the work understandable, but they did not give operators a
single fail-closed graduation target for the checklist itself. The result was a
soft boundary: humans could read the plan, but scripts and support bundles did
not have one ordinary command that said “these named pieces of evidence have
been supplied” while still refusing overclaims.

## Decision

Add two native, content-free graduation commands.

`iotox sync graduation-check PATH [one-writer|read-write] [INTERVAL_SECONDS]
[--evidence NAME=LABEL...]` runs the local sync doctor, prints the trust-plan,
dataset-readiness, repository storage-readiness, and backup-custody verifier
commands, then requires these evidence labels:

- `local-preflight`;
- `storage-readiness`;
- `recovery-custody`;
- `restore-drill`; and
- `recovery-runbook`.

Without every label it exits blocked. With every label it reports
`working-copy-graduation=operator-attested`. It always reports
`precious-data-readiness=blocked` and `repo-certified=0`.

`iotox terminal graduation-check [--root PATH] [--store PATH] [--peer PEER]
[--profile PROFILE] [--sudo-profile PROFILE] [--evidence NAME=LABEL...]`
prints the daily-plan, activation-check, doctor, service, session, reconnect,
profile-freshness, sudo-profile-freshness, cgroup, direct route-loss,
impairment, Tor, and I2P proof commands, then requires these evidence labels:

- `daily-control`;
- `profile-freshness`;
- `service-supervision`;
- `reconnect-continuity`;
- `cgroup-delegation`;
- `route-loss`;
- `long-soak`;
- `tor-route-loss`;
- `i2p-route-loss`;
- `sudo-policy`;
- `security-review`; and
- `activation-decision`.

Without every label it exits blocked. With every label it reports
`daily-driver-graduation=operator-attested` and
`production-activation=operator-attested`. It always reports `repo-certified=0`.

Both commands accept only short, non-space, content-free labels. They are
native binary surfaces, not wrapper scripts.

## Consequences

The two frontiers now have ordinary, automatable graduation porches:

- sync can distinguish “this working copy has an operator-labeled evidence
  trail” from “this is safe as the sole precious-data system of record”;
- Ratox can distinguish “this host/route set has an operator-labeled daily
  driver evidence trail” from “Ratox is universally certified like OpenSSH”;
- `sync trust-plan` and `terminal daily-status` point directly at the stricter
  graduation commands; and
- support bundles can include the graduation output without leaking dataset
  contents, secrets, or message text.

The nonclaims remain deliberate:

- evidence labels are not cryptographic proof;
- a working-copy graduation is not precious-data readiness;
- a daily-driver graduation is host, route, kernel, sudo-policy, and operator
  specific;
- Tor/I2P labels describe the operator's collected route evidence, not an
  anonymity or reliability SLA; and
- recovery custody still requires accepted receipts before the project should
  invite irreplaceable data. ADR 0400 later removed storage-media
  certification from IoTox scope; ADR 0405 narrowed current custody language to
  sync-layer versioned recovery custody.

## Validation

The human CLI regression now covers both commands in blocked and fully labeled
states:

- `sync graduation-check` exits blocked with no evidence, then reports
  `working-copy-graduation=operator-attested`,
  `precious-data-readiness=blocked`, and `repo-certified=0` with all six labels.
- `terminal graduation-check` exits blocked with no evidence, then reports
  `daily-driver-graduation=operator-attested`,
  `production-activation=operator-attested`, and `repo-certified=0` with all
  twelve labels.

The commands share the existing local source/profile/route runbook commands
rather than minting a parallel proof system.
