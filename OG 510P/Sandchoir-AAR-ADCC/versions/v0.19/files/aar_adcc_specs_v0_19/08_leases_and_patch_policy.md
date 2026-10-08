# 08 — Leases + Patch Policy (v0.19)

Goal: prevent silent collisions in shared engineering work with minimal overhead.

## Default: soft leases + patch-shaped exports
- Leases are advisory in Gatekeeper, enforced in Jailer.
- One writer per file at a time (lease scope is file or component tag).
- Non-owners submit P# proposals (diffs) or REQ#.

## Lease events
- grant/revoke/expire are mandatory deltas (always shown when relevant)

## Patch discipline
- Any canonical change requires P# with:
  - touch set
  - summary
  - diff pointer or inline diff (prefer pointer)
  - verify intent
  - rollback note

## Escalation path (only if needed)
1) Soft leases
2) Hard leases (Jailer)
3) PatchOnly mode
4) Nested sandboxes (per-agent mutable workdirs) — expensive; use only if collisions persist
