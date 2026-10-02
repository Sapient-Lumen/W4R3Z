# ADR 0409: Add operator watch/freeze, terminal readiness, and messenger background plans

Status: accepted
Date: 2026-09-27

## Context

IoTox had enough stable evidence machinery, Ratox profile checking, sync
status, and person outbox/card-floor primitives to support daily operator
porches, but humans still had to remember how to compose them. Four gaps kept
showing up:

- the accepted local stable dossier was real, but not discoverable as one
  current pointer;
- sync operators needed a small watch surface and an emergency local brake;
- Ratox operators needed one stale-profile/rescue readiness view before trying
  to daily-drive SSH-like work; and
- person messaging needed timer-friendly retry/card-freshness plans without
  pretending IoTox had a built-in background daemon.

## Decision

Add native, content-free operator porches:

- `tools/iotox-repo.sh current-stable-evidence` prints the accepted local
  stable manifest, expected SHA-256, and exact ship/release commands.
- `iotox sync-watch NAMESPACE` and grouped `iotox sync watch NAMESPACE` print
  live/offline sync status, namespace job counts when the Agent is reachable,
  and any local freeze record.
- `iotox sync-freeze`, `sync-unfreeze`, and `sync-freeze-status` maintain a
  durable local operator freeze record. They deliberately state that Agent
  enforcement is not wired yet and remote peers are not stopped.
- `iotox terminal readiness` checks local shell/sudo/rescue profile records,
  executable pins, toolbox pins, and prints daily-driver commands while keeping
  binding, service, route, and sudo/PAM policy separate.
- `iotox person outbox-retry-plan`, `card-refresh-plan`, and
  `background-plan` print exact one-shot retry/freshness commands for an
  external timer.

## Consequences

The ordinary human path is easier to find without hiding authority:

- stable release rehearsal can point at the accepted manifest without copying a
  long path from memory;
- sync has a reversible local brake and watch output useful even when the Agent
  is offline;
- Ratox profile staleness is visible before a remote shell attempt; and
- person messaging can be supervised by systemd/cron/Monsternix-style timers
  using native commands.

The remaining boundaries stay explicit. The sync freeze record is not yet an
Agent-enforced automation stop. `terminal readiness` is profile payload
readiness, not service, binding, route, or sudo/PAM proof. Person background
plans are one-shot command plans, not durable offline all-device delivery,
aggregate receipts, or transcript consensus.
