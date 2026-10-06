# RFC-0165: A/B update lifecycle on ZFS boot environments (update_engine semantics)

Status: Draft  
Last updated: 2026-02-25

## Problem

DeriveBSD wants health-gated updates and rollback (`docs/112-health-gated-updates.md`), but we don’t yet have a precise, tested *lifecycle contract* for:
- staging an update while the system is running
- selecting the next boot target
- recording “boot success” as an explicit fact
- limiting retries and rolling back safely
- generating bounded incident evidence when things go wrong

Without a clear lifecycle, we risk a fragile shell-script ecosystem around boot environments.

## Goals

- Define an explicit A/B-style lifecycle for BE-based updates.
- Make every transition receipted and queryable (evidence spine).
- Integrate with:
  - health gates (policy-driven checklists)
  - anti-rollback / rollback floors (optional lane)
  - incident bundles (privacy-safe defaults)
- Keep the updater small: policy comes from Derive, lifecycle is enforced centrally.

## Non-goals

- Designing a new delta payload format (we can reuse existing artifact distribution choices).
- Replacing FreeBSD bectl semantics (we build on it).

## Proposal

### 1) Lifecycle state machine (`update.lifecycle.state`)

Persist a small state record (and mirror it in receipts):

- `staged` → `pending_boot` → `booted_unconfirmed` → (`committed` | `rolled_back`)

Transitions are driven by:
- the apply engine (when staging)
- the boot hook / health gate runner (when booted)
- policy (required checks, retry limits, rollback policy)

### 2) Retry tracking and rollback

- Maintain a bounded retry counter per staged update.
- If boot fails N times or the health gate fails:
  - roll back to the prior BE
  - emit a failure receipt
  - optionally generate an incident bundle

### 3) Evidence objects

Add two small evidence objects (schemas to be added in follow-up RFC or extended existing ones):

- `boot.health.report` (already referenced in `docs/112`):
  - checks run + results
  - evidence digests used
  - pointer to the staged change id / generation id

- `boot.commit.record`:
  - decision: commit/rollback
  - reason
  - retry counter state
  - policy digest

### 4) Storage locations / resilience

Retry state must survive partial boots and be hard to corrupt.
Options:
- EFI variables (with care)
- a tiny dedicated dataset with strict integrity rules
- a small bootloader-readable record

DeriveBSD should pick one and test power-loss scenarios.

### 5) Anti-rollback integration (optional)

If rollback indices are enabled:
- BE selection must respect rollback floors.
- State migrations and firmware updates must be staged such that rollback remains feasible (or explicitly disallowed by policy).

## Alternatives considered

- “Treat BEs like snapshots and do it with a couple scripts” (brittle, not auditable).
- “Use OSTree/rpm-ostree wholesale” (not BSD-native; still useful as inspiration).

## References

- ChromeOS / Android update_engine README (A/B lifecycle, rollback behavior, policy separation): https://chromium.googlesource.com/aosp/platform/system/update_engine/+/HEAD/README.md
- Android A/B updates overview: https://source.android.com/docs/core/ota/ab

## Related work in this archive

- `docs/231-ab-updates-and-recovery-semantics.md`
- `docs/112-health-gated-updates.md`
- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/137-anti-rollback-rollback-index.md`
- `docs/17-secure-activation.md`
