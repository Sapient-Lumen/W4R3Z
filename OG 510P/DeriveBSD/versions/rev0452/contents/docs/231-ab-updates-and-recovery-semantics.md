# Seamless A/B updates + recovery semantics (ChromeOS / Android update_engine lessons)

DeriveBSD already wants health-gated, rollbackable updates (`docs/112-health-gated-updates.md`).
A big greenfield advantage is to *codify* the “A/B update lifecycle” as a first-class system contract—so we don’t end up with a brittle set of scripts around boot environments.

ChromeOS (and Android’s A/B model) formalized this as:
- stage updates to an **inactive slot**
- reboot into the new slot
- only “commit” after **boot success is explicitly recorded**
- automatically **roll back** after boot failure
- keep policy centralized, keep payload formats stable, and preserve backward compatibility in the updater

## Mapping to DeriveBSD (ZFS boot environments as “slots”)

We can implement A/B semantics on top of ZFS BEs:

- **Slot** ≈ ZFS BE (plus any paired state datasets that must match)
- **Inactive slot** ≈ “next boot” BE
- **Commit** ≈ mark BE as default + clear rollback counters + emit `boot.commit.record`
- **Rollback** ≈ boot back to previous default + emit a failure record + bundle incident evidence

## Proposed primitives (conceptual)

### 1) `update.lifecycle.state`

A tiny state machine persisted in a safe place (and mirrored in evidence objects):
- `staged` (new BE created, not selected)
- `pending_boot` (next boot will attempt it)
- `booted_unconfirmed` (booted, but not yet declared healthy)
- `committed` (declared healthy)
- `rolled_back` (failed, reverted)

### 2) Retry counters + bounded attempts

A/B systems typically allow N boot attempts before automatic rollback.
DeriveBSD should:
- store retry state in a resilient location (e.g., EFI var or a small ZFS dataset with tight integrity rules)
- emit receipts for every attempt and decision

See also: `docs/241-boot-try-counters-and-boot-assessment.md`.

### 3) Health gate = policy-driven checklist

Same as `docs/112-health-gated-updates.md`, but with explicit lifecycle wiring:
- required services up
- `derive verify-host` ok
- required receipts present (config/state/pki/time/storage/fault/resource)
- optional remote attestation verifier receipt present (if required)

## Why add ChromeOS’s update_engine mindset?

ChromeOS’s updater docs are unusually explicit about:
- lifecycle and rollback behavior
- policy management separation
- delta vs full payloads
- “do not break backward compatibility”

Those are exactly the failure modes we want to preempt in DeriveBSD’s updater.

## Interactions with anti-rollback and measured boot

- If we enable rollback indices (`docs/137-anti-rollback-rollback-index.md`) we must ensure:
  - “rollback to previous BE” does not violate the rollback floor,
  - state migrations and firmware updates respect floors and are receipted.
- If we enable measured boot:
  - each slot attempt can produce an attestation receipt for admission control (secrets, workloads) and for incident bundles.

## Related

- Health-gated updates + rollback: `docs/112-health-gated-updates.md`
- Secure activation: `docs/17-secure-activation.md`
- Anti-rollback / rollback indices: `docs/137-anti-rollback-rollback-index.md`
- Incident bundles (on rollback): `docs/216-incident-snapshots-and-support-bundles.md`

Last updated: 2026-02-25
