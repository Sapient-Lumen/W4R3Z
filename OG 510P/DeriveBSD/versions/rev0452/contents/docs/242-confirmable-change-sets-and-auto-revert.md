# Confirmable change-sets and auto-revert (generalized “commit confirmed”)

DeriveBSD already treats configuration changes and multi-step transitions as **typed artifacts** with **receipts** (`docs/218-configuration-transactions-and-receipts.md`, `docs/219-change-sets-and-apply-engine.md`).

A greenfield advantage is to add a single, coherent primitive that prevents lockouts and soft-bricks:

> **A change can require confirmation within a timeout, or it is automatically reverted.**

This is the generalization of the networking world’s “commit confirmed” pattern (apply a risky change; if you don’t confirm, it rolls back).

## The goal

Make “commit confirmed” work for *any* change-set category, not just config files:
- firewall/routing changes
- SSH/console policy
- boot chain changes
- service graph refactors
- secrets delivery policy

…and do it in a way that is:
- explicit in the change-set
- reflected in receipts
- compatible with health-gated updates and A/B boot semantics

## Surface area

### 1) Change-set intent

`spec/change.set.schema.json` already has an optional `confirm` section.
This doc tightens the semantics:

- `confirm.required=true` means the apply engine may finish with **pending confirmation**.
- `confirm.timeout_sec` defines the maximum time window.
- `confirm.authority` (optional) binds confirmation to a grant/capability.

### 2) Receipts and evidence

Two receipts matter:

1) `change-receipt` ends with `status=pending-confirm` when the change is applied but not committed.

2) A separate `change-confirm-receipt` is emitted when a human or controller confirms.

This allows incident bundles to include:
- what was applied
- what remained unconfirmed
- who confirmed (and under what authority)

## The auto-revert mechanism

If a change impacts bootability, network reachability, or control-plane access, the safest revert mechanism is:

- **A/B style boot semantics over BEs** (candidate BE + try counters)
- boot assessment determines whether the new generation is *good*
- on failure (or missing confirmation), automatically revert the default boot target

This composes cleanly with:
- `docs/112-health-gated-updates.md`
- `docs/231-ab-updates-and-recovery-semantics.md`
- `docs/241-boot-try-counters-and-boot-assessment.md`

### Confirmation windows: time vs boots

DeriveBSD should support two equivalent windows:

- **time window**: confirm within `timeout_sec`
- **boot window**: confirm within N successful boots (useful when RTC/time are not trustworthy yet)

The implementation can still store a single deadline, but the *policy decision* may choose which input is authoritative.

## Suggested apply-engine behavior (normative)

1) Apply the change-set into a **candidate BE** (or a staging area) when possible.
2) Switch next-boot to the candidate, with **try-counters** set.
3) Reboot.
4) On boot:
   - run boot health checks
   - if required checks pass, emit `boot-health-report`
   - if confirmation is required:
     - keep the system in `pending-confirm` state
     - emit `change-receipt(status=pending-confirm)`
   - if confirmation is not required:
     - bless boot good and commit immediately
5) If confirmation arrives in time:
   - emit `change-confirm-receipt`
   - bless/commit the candidate as default
6) If confirmation does not arrive:
   - auto-revert to the previous default BE
   - emit `change-receipt(status=rolled-back)` and an incident bundle

## Why bake this in early?

Most ecosystems add this as bespoke glue:
- config managers implement their own “revert” logic
- operators invent manual rollback playbooks
- supervisors can’t reliably connect “the change” to “the revert”

DeriveBSD already has the missing ingredients (receipts + BEs + health gates). This doc makes it a single standardized contract.

## Related

- Config transactions: `docs/218-configuration-transactions-and-receipts.md`
- Change sets + apply engine: `docs/219-change-sets-and-apply-engine.md`
- Boot assessment: `docs/241-boot-try-counters-and-boot-assessment.md`
- A/B lifecycle: `docs/231-ab-updates-and-recovery-semantics.md`
- Breakglass lane (confirm as a capability): `docs/236-breakglass-and-recovery-mode.md`

Last updated: 2026-02-25
