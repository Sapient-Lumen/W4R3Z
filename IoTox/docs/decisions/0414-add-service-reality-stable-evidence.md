# ADR 0414: Add service reality receipts for stable evidence

Status: accepted.

## Context

ADR 0413 made resident services ordinary: one binary can render Agent/sync/Ratox
and person-messenger service shapes for systemd-user, NixOS user/system, and
MonsterNix adapters. That solved the “what should I install?” problem, but the
receipt was deliberately only a reviewed-shape receipt. It correctly said
`not-service-manager-state-proof=1`.

Stable release evidence needed one stronger seam: `terminal.service-supervision`
should be able to point at an observed service-manager proof, not only a safe
operator label. At the same time, IoTox must not pretend to remotely attest the
host or collapse unrelated proof into one artifact.

## Decision

Add a top-level resident status porch:

```sh
iotox service status-plan \
  --target agent|person|all \
  --manager systemd-user|nixos-user|nixos-system|monsternix

iotox service status-receipt \
  --target agent|person|all \
  --manager systemd-user|nixos-user|nixos-system|monsternix \
  --service-manager-state active \
  --enabled-state enabled|static|managed \
  --log-state reviewed \
  --health-state passed \
  --upgrade-state passed \
  --accept-operator-responsibility \
  --out service-reality.receipt
```

`status-plan` prints the exact active/enabled/log/health/upgrade checks for
the selected service manager and target. `status-receipt` writes
`iotox.service-reality.v1` only when the operator supplies accepted states and
explicit responsibility. The receipt hashes the root, binary path, and rendered
service artifact, records `stable-evidence-key=terminal.service-supervision`,
and keeps nonclaims for cgroup delegation, route proof, sync folder health, and
person read semantics.

`iotox evidence collect terminal` now accepts:

```sh
--service-reality service-reality.receipt
```

When present, that receipt is copied and shape-checked as the
`terminal.service-supervision` stable gate. Legacy
`iotox.terminal-stable-evidence.v1` service-supervision labels remain accepted
for old dossiers, but the native dossier plan prefers service reality.

## Consequences

- Stable evidence can distinguish a reviewed service shape from a running,
  enabled/static/managed, log-reviewed, health-checked, upgrade-checked
  service observation.
- The resident service porch becomes a complete operator loop:
  render, review, install externally, check status, write receipt, collect
  stable evidence.
- The receipt is portable and testable because it records an operator/test
  harness observation rather than shelling out to a particular service manager.
- The receipt still does not prove service-manager state by remote attestation,
  host integrity, route survivability, cgroup delegation, sudo/PAM policy, sync
  folder health, or human read semantics.

## Verification

The human CLI regression suite covers:

- `iotox service status-plan` command generation for Agent/person units;
- accepted `iotox service status-receipt` output and receipt schema;
- fail-closed rejection when the observed service state is not active;
- `iotox evidence collect terminal --service-reality ...`; and
- `iotox ship-check terminal stable --evidence-manifest ...` accepting the
  generated service reality receipt as `terminal.service-supervision`.

