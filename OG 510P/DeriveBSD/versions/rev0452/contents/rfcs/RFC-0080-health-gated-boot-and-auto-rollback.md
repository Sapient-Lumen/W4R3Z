# RFC-0080: Health-gated boot and automatic rollback

Status: Draft

## Summary

Add a **health gate** to host generation switching so that a new ZFS boot environment is only committed after passing policy-governed checks.

Inspired by A/B update semantics where new slots are marked successful only after health confirmation.

References:
- Android A/B updates: https://source.android.com/docs/core/ota/ab
- Transactional snapshot updates: https://documentation.suse.com/sles/15-SP7/html/SLES-all/cha-transactional-updates.html

## Goals

- Fail-safe updates for remote-managed hosts.
- Health checks are explicit, minimal-TCB, and policy-controlled.
- Generate a structured `boot.health.report` object bound to the generation digest.

## Design sketch

1) `derive switch --tentative` activates a BE for next boot only.
2) Early boot runs `derive health-probe` (or equivalent):
   - verify artifacts + signatures
   - check required services are up
   - optional: check network policy compliance
3) On success: mark BE committed.
4) On failure: rollback to previous BE.

See: `docs/112-health-gated-updates.md`.
