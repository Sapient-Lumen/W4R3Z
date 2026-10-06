# Boot try-counters and automatic boot assessment (BLS/systemd-boot lesson)

DeriveBSD already wants **health-gated updates** and **A/B lifecycle semantics** over ZFS boot environments (`docs/112-health-gated-updates.md`, `docs/231-ab-updates-and-recovery-semantics.md`).

See also: `docs/284-bootenv-switching-as-evidence.md` (switch plan + receipt: `spec/bootenv.switch.plan.schema.json`, `spec/bootenv.switch.receipt.schema.json`).

One particularly high-leverage lesson to bake in early is **boot assessment using try-counters**: a bootloader-visible mechanism that automatically falls back when a boot entry repeatedly fails.

This is a small primitive with outsized benefits:
- avoids “soft bricks” where a system loops on a broken generation
- makes rollback behavior deterministic and automatable
- cleanly composes with a policy-defined health gate

## The lesson: tries-left / tries-done counters

The UAPI Boot Loader Specification defines a two-counter mechanism (“tries left” / “tries done”) that the bootloader updates on each boot attempt, enabling automatic fallback when tries are exhausted.

systemd-boot documents using these counters for unattended fallback to older boot entries.

DeriveBSD should steal the *idea*, not a specific implementation: any UEFI-capable boot path can implement a similar “boot attempt ledger” (BLS-style entry naming, EFI variables, or a dedicated small dataset).

## DeriveBSD mapping

### Key objects

- **Boot entry**: a ZFS boot environment (BE) plus its associated loader/kernel/initramfs artifacts.
- **Candidate generation**: the new BE selected by the apply engine.
- **Boot attempt ledger**: a durable place where the bootloader can decrement tries and record failures.

### Required invariants

1. **Attempts are bounded**
   - a candidate BE is tried at most `N` times (policy-defined)
   - if `N` attempts fail to reach the *boot success point*, fall back automatically

2. **Boot success is explicit**
   - the OS must mark a boot as “good” (or “bad”) based on health gates
   - this produces a typed receipt (`boot-bless-receipt`, see `spec/boot.bless.receipt.schema.json`) driven by a gate policy (`spec/boot.health.gate.policy.schema.json`)

3. **Rollback is explainable**
   - when rollback occurs, DeriveBSD emits:
     - `change-receipt` with `status=rolled-back` and a reason
     - an incident bundle (policy-bound) referencing the boot health report and relevant events

## Where to place the counters

DeriveBSD can support multiple backends, but should standardize semantics:

1) **UEFI/BLS-compatible** (preferred when possible)
- store a boot entry descriptor per BE
- encode try-counters as metadata the bootloader updates

2) **EFI variable ledger** (small, robust)
- store try counters and the “pending” BE selector in authenticated variables (when available)

3) **ZFS dataset ledger** (fallback)
- a small ZFS dataset with tight integrity rules and explicit receipts
- bootloader must be able to update it safely (more fragile than (1)/(2))

## Interactions

### A/B updates

The A/B state machine in `docs/231-ab-updates-and-recovery-semantics.md` becomes concrete with try-counters:
- `pending_boot`: candidate BE has tries-left `N`
- `booted_unconfirmed`: first successful boot reached userland, but not yet blessed
- `committed`: boot blessed, tries reset, candidate becomes default
- `rolled_back`: tries exhausted or boot marked bad

### Confirmable change-sets

If a change-set requires confirmation (`spec/change.set.schema.json` has a `confirm` section), boot assessment supplies the automatic revert mechanism.

See: `docs/242-confirmable-change-sets-and-auto-revert.md`.

## Evidence: make boot assessment observable

Boot assessment must not be “mystery state”.

DeriveBSD should emit:
- `boot-health-report` (`spec/boot.health.report.schema.json`)
- `boot-bless-receipt` whenever a boot is blessed good/bad (`spec/boot.bless.receipt.schema.json`)

Official support handoff now has a typed place for that exact decision too: when health-gated finalization or rollback materially shaped an incident, bundles can carry `boot_bless_receipt_digests` instead of making support infer the outcome from loader counters, boot-status text, or dashboard prose.
- optional gate policy digest to make the decision reproducible (`spec/boot.health.gate.policy.schema.json`)
- structured `event.segment` entries linking the boot attempt to the change-set and BE

## Related

- Health gates: `docs/112-health-gated-updates.md`
- Boot assessment in practice (greenboot/systemd): `docs/335-boot-assessment-greenboot-and-health-gated-rollback.md`
- A/B lifecycle semantics: `docs/231-ab-updates-and-recovery-semantics.md`
- Change sets and confirmation: `docs/219-change-sets-and-apply-engine.md`, `docs/242-confirmable-change-sets-and-auto-revert.md`
- Incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`

Last updated: 2026-03-21r363
