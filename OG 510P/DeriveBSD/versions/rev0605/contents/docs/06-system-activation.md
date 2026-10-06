# System generations and activation

## Goals

- Atomic activation of a new system closure
- Fast rollback to a previous generation
- Clear separation: build vs activate

## Model

- A “system” is just another closure type:
  - base/world/kernel (later)
  - configs
  - services
  - packages
  - activation script (idempotent)

## BSD leverage

- On ZFS:
  - each generation can map to a boot environment
  - rollback is a BE selection + profile pointer

See: `docs/404-zfs-boot-environments-as-system-generations.md`.

## rc.d backend pointer

See `docs/86-host-activation-rcd-and-service-jails.md` (RFC-0056, ADR-0027) for rc.d + service-jail orchestration and activation invariants.


Last updated: 2026-02-27r117
