# Breakglass bootstrap joins stay exact receipt-typed and pre-session-only

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

## What changed

Breakglass now has an official way to say **which earlier recovery-path receipt materially got the machine into this emergency session**.

- `breakglass.receipt.evidence.bootstrap_receipt_joins[]` is the optional canonical join surface
- the first reviewed join kinds are `boot.override.receipt` and `reset.receipt`
- `breakglass.receipt.evidence.bootstrap_join_posture` fixes the meaning of that join to `pre-session-recovery-path-only`

## Why this matters

`ADR-0296` already decided that breakglass session methods stay concrete (`console`, `serial`, `ssh`) and that generic `oob` is too blurry.
But the archive still needed one more hard decision:

**how does a breakglass receipt explain the boot or reset path that happened *before* the operator reached that concrete session?**

Without an exact answer, support and forensics fall back to screenshots, BMC breadcrumbs, or ticket prose about “we used virtual media” or “we bounced into maintenance mode”.
That is not a stable implementation target.

## Accepted boundary

### 1) Use exact upstream receipts, not adapter folklore

If the emergency session materially depended on an earlier recovery-path step, the breakglass receipt should join the exact reviewed receipt that already explained that step.

The first reviewed join kinds are:

- `boot.override.receipt`
- `reset.receipt`

### 2) The join is only for pre-session recovery path

`bootstrap_receipt_joins[]` is not a second repair log and not a place to stuff later mutation receipts.
Its meaning is deliberately narrow:

- it explains **how the machine got into the emergency session**
- it does **not** explain repairs performed after the session opened

That boundary is explicit through:

- `evidence.bootstrap_join_posture = pre-session-recovery-path-only`

### 3) Post-entry repair truth stays where it already belongs

Once breakglass has opened, actual repair work still proves itself through the normal authoritative receipts plus:

- `breakglass.receipt.repair_outcome`
- `breakglass.receipt.repair_outcome.authoritative_receipt_digests`

This avoids collapsing “booted into maintenance” and “successfully repaired the problem” into one mushy story.

### 4) Virtual media and BMC UI are not the authority object

Virtual media, BMC KVM, and similar remote-presence features are still real adapters.
But in this first cut they do not get to replace typed recovery-path receipts.

If virtual media only helped reach a maintenance boot that is already explained by `boot.override.receipt` or `reset.receipt`, the breakglass receipt should join **that** receipt instead of turning dashboard state into the portable truth.

## First spec cut

The first implementation-shaped cut is intentionally small:

- add optional `evidence.bootstrap_receipt_joins[]` to `spec/breakglass.receipt.schema.json`
- keep the first join vocabulary to `boot.override.receipt` and `reset.receipt`
- add `evidence.bootstrap_join_posture = pre-session-recovery-path-only`
- update the example and nearby breakglass docs so pre-session recovery no longer disappears into notes

That is enough to make recovery-path evidence portable without inventing a full BMC provenance subsystem.

## Follow-on narrowing

The next quiet drift after exact pre-session joins is to turn the array into a scrapbook of every attempted recovery step. `docs/708-breakglass-bootstrap-joins-stay-enabling-only-and-earliest-to-latest-when-plural.md` closes that loophole by keeping plural joins enabling-only and earliest-to-latest instead of mixing in denied attempts or failed dead ends. `docs/709-breakglass-bootstrap-joins-keep-boot-override-before-reset-when-both-participate.md` then tightens the common paired one-time-boot case so selection stays before actuation when both receipts are joined.

## Related docs

- ADR: `adrs/ADR-0297-breakglass-bootstrap-joins-stay-exact-receipt-typed-and-pre-session-only.md`
- concrete method split: `docs/706-breakglass-session-methods-stay-concrete-and-oob-adapters-project-into-them.md`
- breakglass lane: `docs/236-breakglass-and-recovery-mode.md`
- breakglass workflows: `docs/250-breakglass-and-recovery-workflows.md`
- installation / recovery posture: `docs/473-installation-and-recovery-posture-by-profile.md`
- boot override authority: `docs/482-boot-code-admission-and-constrained-overrides.md`
- destructive reset authority: `docs/483-destructive-reprovisioning-and-reset-authority.md`
- risk register: `docs/266-open-questions-and-risk-register.md`
- guardrail: `tools/check_breakglass_bootstrap_join_boundary.py`
- follow-on sequence cut: `docs/708-breakglass-bootstrap-joins-stay-enabling-only-and-earliest-to-latest-when-plural.md`

## References

- DMTF Redfish schema index (`VirtualMedia`): https://redfish.dmtf.org/redfish/schema_index
- DMTF Redfish Resource and Schema Guide (`ComputerSystem.BootSourceOverrideTarget`, manager `SerialInterfaces`): https://redfish.dmtf.org/schemas/v1/DSP2046_2025.2.html

Last updated: 2026-03-23r440
