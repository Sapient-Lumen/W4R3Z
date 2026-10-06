# Secure activation and rollback

Activation is security-sensitive: it changes the running system.

## Principles

- activation is idempotent and minimal
- switching is atomic; rollback remains available
- verify signatures/hashes of target closure before switching

## ZFS boot environment integration

- each generation corresponds to a BE snapshot/clone
- activation creates new BE, sets boot target, updates pointer
- rollback selects previous BE + pointer

## Service jails pointer

See `docs/86-host-activation-rcd-and-service-jails.md` for service-jail hardening and the rc.d activation backend.


Last updated: 2026-02-23
