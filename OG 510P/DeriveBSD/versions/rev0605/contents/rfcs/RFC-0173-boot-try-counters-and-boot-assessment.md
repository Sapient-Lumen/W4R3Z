# RFC-0173: Boot try-counters and automatic boot assessment

Status: Draft  
Last updated: 2026-02-25

## Problem

DeriveBSD’s update story relies on atomic switching + rollback (`docs/112-health-gated-updates.md`, `docs/231-ab-updates-and-recovery-semantics.md`).

Without a bootloader-visible “try counter” primitive, the system is vulnerable to:
- boot loops on broken generations
- inconsistent rollback behavior across platforms
- ad-hoc scripts that can’t be audited or tied to receipts

## Goals

- Standardize a **bounded boot attempt** mechanism for candidate boot environments.
- Require that boot success is **explicitly blessed** and produces typed evidence.
- Make boot rollback decisions **explainable** via receipts and event references.
- Keep the mechanism implementable across multiple boot paths (UEFI/BLS, EFI vars, ZFS ledger).

## Non-goals

- Mandating systemd-boot or a Linux-oriented boot stack.
- Replacing ZFS boot environments as the core “slot” mechanism.

## Proposal

### 1) Candidate boot entries have bounded attempts

When the apply engine selects a candidate BE, it MUST set:
- `tries_left = N` (policy-defined)
- `tries_done = 0`

On each boot attempt, the bootloader (or a boot-time ledger component) updates:
- decrement `tries_left`
- increment `tries_done`

If `tries_left == 0` before the OS blesses the boot “good”, the bootloader MUST fall back to a previous known-good entry.

### 2) Boot success is explicit and receipted

Define a new evidence object:

- `boot-bless-receipt` (`spec/boot.bless.receipt.schema.json`)

Emitted by the OS when it decides:
- `decision="good"` (commit)
- or `decision="bad"` (do not retry; trigger immediate fallback when possible)

The bless receipt MUST reference:
- generation digest
- boot environment name/id
- current try-counter state
- the boot health report digest (when available)

### 3) Incident bundle integration

Extend incident bundle include knobs and includes to optionally reference:
- `boot_bless_receipt_digests`

This allows automatic rollback events to be exported with the minimal but sufficient evidence.

## Data contract changes

- Add `spec/boot.bless.receipt.schema.json` and example.
- Update `spec/incident.bundle.schema.json` to include boot bless receipts.

(Existing schemas remain compatible; change-set confirmation uses `change-receipt(status=pending-confirm)`.)

## Rollout plan

1) Introduce the schema and examples.
2) Update the apply engine to:
   - set try counters when staging a candidate BE
   - record the ledger backend used (meta)
3) Add a small “boot bless” component in early userland to:
   - run required boot health checks
   - emit the bless receipt
   - commit or fail the entry

## Risks / tradeoffs

- Some platforms may not support robust bootloader-side updates; a ZFS ledger fallback exists but is more fragile.
- If the boot success point is set too early, we can “bless” broken generations. The health gate needs to be strict and policy-defined.

## Related

- `docs/241-boot-try-counters-and-boot-assessment.md`
- `docs/112-health-gated-updates.md`
- `docs/231-ab-updates-and-recovery-semantics.md`
- `docs/216-incident-snapshots-and-support-bundles.md`
