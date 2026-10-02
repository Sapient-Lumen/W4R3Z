# ADR 0413: Add resident services and messenger readiness polish

Status: accepted.

## Context

IoTox had enough durable sync/Ratox/person machinery to run continuously, but
operators still had to assemble the continuous-running shape from separate
pieces:

- the Agent ran through `iotox run --config`;
- Ratox had a terminal-specific `service plan|render|receipt` porch;
- the person messenger had a native `background-run` loop, but no shared
  resident-service command;
- device receipts could prove device receipt, but there was no local human-read
  state; and
- transcripts and groups had signed stores/envelopes, but no direct operator
  summary for convergence or group health.

That left two kinds of friction. First, “make it run all the time” was not an
ordinary command. Second, person multidevice had raw pieces but not enough
daily-lived vocabulary for “did my devices converge?” or “did I read it here?”

## Decision

Add a top-level resident-service porch:

```sh
iotox service plan|render|receipt \
  --target agent|person|all \
  --manager systemd-user|nixos-user|nixos-system|monsternix
```

`agent` renders the long-lived Agent/sync/Ratox service around
`iotox run --config ROOT/agent.conf`. `person` renders the person messenger
background worker around `iotox person background-run`. `all` renders both.

The renderer emits systemd-user, NixOS-user, NixOS-system, or MonsterNix
adapter shapes. The receipt is content-free and hashes the reviewed root,
binary path, and rendered artifact. It records operator review, not service
manager state.

ADR 0414 later adds the separate `service status-plan|status-receipt` path for
operator-observed service-manager state. That keeps this render/review receipt
honest while giving stable dossiers a stronger service-supervision artifact.

Add person messenger polish commands:

```sh
iotox person read-mark READ_STATE MESSAGE_ID_HEX ...
iotox person read-status READ_STATE ...
iotox person transcript-convergence LOCAL_TRANSCRIPT [PEER_TRANSCRIPT...]
iotox person group-status GROUP ...
```

`read-mark`/`read-status` define local human-read UX state, separate from
delegated device receipts. `transcript-convergence` compares signed message
identity and payload-digest sets across transcript stores while explicitly
refusing to claim global total order. `group-status` summarizes signed group
membership, local group transcript entries, group device receipts, and local
group human-read marks while explicitly refusing to claim Tox groupchat
identity.

## Consequences

- Running IoTox continuously is now a binary-native workflow rather than a
  shell-script convention.
- Sync, Ratox, and person messenger can share one service porch while keeping
  Ratox's terminal-specific service-supervision evidence receipt available for
  terminal activation/graduation gates.
- Person messaging has ordinary local UX for reads, receipt rollups, group
  summaries, and transcript convergence.
- The new receipts and summaries keep their nonclaims explicit:
  - no automatic installation;
  - no proof the service manager is active;
  - no route, sync health, cgroup, sudo, or person-read proof from a service
    receipt;
  - no remote human-read proof from local read marks; and
  - no global transcript total order from convergence checks.

## Verification

The human CLI regression suite covers:

- `iotox service plan|render|receipt` for resident agent/person service shapes,
  including raw systemd output, MonsterNix adapter output, and explicit
  operator acceptance for receipts;
- idempotent `person read-mark` and `read-status` expected-reader summaries;
- `person transcript-convergence` over matching transcript stores; and
- `person group-status` over a signed group, local group transcript, aggregate
  receipt store, and read-state file.
