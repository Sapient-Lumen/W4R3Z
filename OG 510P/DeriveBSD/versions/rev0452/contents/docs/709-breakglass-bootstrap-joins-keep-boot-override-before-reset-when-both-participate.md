# Breakglass bootstrap joins keep boot override before reset when both participate

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`docs/707-breakglass-bootstrap-joins-stay-exact-receipt-typed-and-pre-session-only.md` made the bootstrap join exact.
`docs/708-breakglass-bootstrap-joins-stay-enabling-only-and-earliest-to-latest-when-plural.md` made plural joins enabling-only and earliest-to-latest.

This follow-on cut fixes the next smaller ambiguity:
**when both a one-time maintenance boot selection and a reset materially enabled the session, which receipt comes first?**

## Accepted boundary

When `breakglass.receipt.evidence.bootstrap_receipt_joins[]` includes both of these reviewed kinds for the same pre-session recovery path:

- `boot.override.receipt`
- `reset.receipt`

…the canonical earliest-to-latest order is:

1. `boot.override.receipt`
2. `reset.receipt`

That ordering is now the reviewed baseline for the paired case.

## Why this is the right boring answer

The one-time maintenance boot story has two different jobs:

- select the *next* boot target
- then actually make the machine boot

Those are not the same event.

`boot.override.receipt` is the reviewed proof that the next boot target was selected.
`reset.receipt` is the later proof that the machine was reset/rebooted and actuated that selection.

So when both receipts materially participated, `boot.override.receipt` belongs earlier in the enabling chain and `reset.receipt` belongs later.

This matches the underlying management split too:

- Redfish models boot-source override separately from reset actions,
- VirtualMedia is manager-provided media/boot plumbing rather than the breakglass session surface,
- and vendor one-time-boot flows describe selecting the next boot target first and rebooting/resetting afterward.

## What this does *not* mean

This is **not** a claim that every bootstrap path needs both receipts.

Still valid:

- only `reset.receipt`, when reset/reprovision itself is the enabling pre-session path
- only `boot.override.receipt`, when the reviewed recovery path does not also expose a typed reset receipt

The new rule only hardens the paired case so support/export tooling does not reverse the most common one-time-boot sequence.

## First spec cut

- keep `bootstrap_join_sequence_posture = earliest-to-latest-pre-session-enabling-only`
- tighten the sequence language so paired `boot.override.receipt` + `reset.receipt` joins are serialized as selection-then-actuation
- correct the canonical example to demonstrate `boot.override.receipt` before `reset.receipt`
- add a small guardrail so future edits do not drift back into reversed one-time-boot folklore

## Related docs

- ADR: `adrs/ADR-0299-breakglass-bootstrap-joins-keep-boot-override-before-reset-when-both-participate.md`
- exact bootstrap joins: `docs/707-breakglass-bootstrap-joins-stay-exact-receipt-typed-and-pre-session-only.md`
- enabling-only ordered joins: `docs/708-breakglass-bootstrap-joins-stay-enabling-only-and-earliest-to-latest-when-plural.md`
- breakglass lane: `docs/236-breakglass-and-recovery-mode.md`
- breakglass workflows: `docs/250-breakglass-and-recovery-workflows.md`
- boot override authority: `docs/482-boot-code-admission-and-constrained-overrides.md`
- reset authority: `docs/483-destructive-reprovisioning-and-reset-authority.md`
- guardrail: `tools/check_breakglass_bootstrap_actuation_boundary.py`

## References

- DMTF Redfish Resource and Schema Guide (`BootSourceOverrideEnabled`, `BootSourceOverrideTarget`, reset actions): https://redfish.dmtf.org/schemas/v1/DSP2046_2025.2.html
- DMTF Redfish schema index (`VirtualMedia`, `SerialInterface`): https://redfish.dmtf.org/redfish/schema_index
- Dell iDRAC virtual console / next boot menu: https://www.dell.com/support/kbdoc/en-us/000176919/using-virtual-console-idrac7
- HPE iLO one-time boot status: https://support.hpe.com/hpesc/public/docDisplay?docId=sd00005342en_us&docLocale=en_US&page=one-time-boot-options.html

Last updated: 2026-03-23r440
