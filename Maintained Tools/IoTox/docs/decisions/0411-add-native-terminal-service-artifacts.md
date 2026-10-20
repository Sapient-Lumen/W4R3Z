# ADR 0411: Add native terminal service artifacts

Status: Accepted.

## Context

Ratox daily-driver use needs a boring service-manager shape: a reviewed
`iotox run-check --config ...` preflight, a long-running `iotox run --config
...`, restart policy, and owner-private defaults. Before this decision, IoTox
documented systemd and NixOS sketches, while the binary only pointed at those
docs. That made the daily-driver gate weaker than the rest of the project:
operators had to reconcile prose, service files, and evidence labels by hand.

## Decision

IoTox adds a native grouped porch:

```sh
iotox terminal service plan
iotox terminal service render
iotox terminal service render --raw
iotox terminal service receipt
```

The renderer emits conservative `systemd-user`, `nixos-user`, and
`nixos-system` service shapes. The receipt records a content-free,
operator-reviewed service-supervision fact and prints a stable evidence label
such as:

```text
service-supervision=terminal.service.systemd-user
```

The receipt binds the root/config/binary strings by SHA-256 and records the
manager and unit name. It deliberately does not claim that the service manager
is active, cgroups are delegated, routes survive impairment, or sudo policy is
correct.

## Consequences

- `terminal daily-plan`, `terminal daily-status`, `terminal activation-check`,
  and `terminal graduation-check` now point at the native service porch.
- Deployment docs prefer generated artifacts over hand-copied snippets.
- The service-supervision gate has a native label and receipt trail, but
  service-manager state, cgroup delegation, route loss, long soak, and sudo
  policy remain independent gates.
- `render --raw` exists so install automation can write only the service file,
  while plain `render` stays self-describing for review and tests.
