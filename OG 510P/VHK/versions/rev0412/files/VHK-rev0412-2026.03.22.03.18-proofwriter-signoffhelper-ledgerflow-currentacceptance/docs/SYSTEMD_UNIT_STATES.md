# Systemd unit state steps

VHK now has first-class runtime steps for Linux-native unit lifecycle checks:

- `GetSystemdUnitState`
- `WaitForSystemdUnitState`

They are intentionally smaller than the richer doctor/install-lane probes. The
goal is to let a macro ask the common question directly: **what state is this
unit in right now, and has it reached the state I need yet?**

## Why this exists

A lot of Linux desktop automation eventually turns into *service orchestration*:
wait for a socket-activated helper, a user service, a timer-triggered exporter,
or a VHK-owned bridge unit to be ready before doing the next desktop action.

Systemd already exposes that state through `systemctl show` and the D-Bus API
fields it mirrors (`LoadState`, `ActiveState`, `SubState`, `UnitFileState`).
VHK now keeps that vocabulary intact instead of forcing every project to shell
out and parse ad-hoc text.

## `GetSystemdUnitState`

```yaml
- type: GetSystemdUnitState
  unit: vhk-busd-demo.service
  scope: user
```

Outputs:

- `systemd_unit` (dict)
- `systemd_status`
- `systemd_scope`
- `systemd_active_state`
- `systemd_sub_state`
- `systemd_load_state`
- `systemd_unit_file_state`
- `systemd_fragment_path`
- `systemd_description`

`systemd_status` is VHK's lighter summary (`ok`, `inactive`, `failed`,
`activating`, `deactivating`, `loaded`, `unit_missing`,
`manager_unavailable`, `probe_tool_missing`, `probe_failed`).

## `WaitForSystemdUnitState`

```yaml
- type: WaitForSystemdUnitState
  unit: vhk-busd-demo.service
  scope: user
  active_state: active
  sub_state: running
  timeout_ms: 15000
```

You can match on any combination of:

- `status`
- `load_state`
- `active_state`
- `sub_state`
- `unit_file_state`

Each matcher accepts either one string or a list of acceptable strings.

Example:

```yaml
- type: WaitForSystemdUnitState
  unit: vhk-busd-demo.service
  scope: user
  active_state: [active, reloading]
  sub_state: running
```

## Honesty rule

These steps currently use `systemctl show` probing, not a long-lived D-Bus
subscription. That is deliberate:

- it matches how VHK already probes service state in doctor/install/dossier lanes
- it works for the common macro-time question without forcing raw bus plumbing
- it avoids claiming that every systemd-related workflow should start from a
  hand-managed `Subscribe()` / `PropertiesChanged` flow

For high-rate service event streams, `WaitForDbusSignal` remains the lower-level
escape hatch.
