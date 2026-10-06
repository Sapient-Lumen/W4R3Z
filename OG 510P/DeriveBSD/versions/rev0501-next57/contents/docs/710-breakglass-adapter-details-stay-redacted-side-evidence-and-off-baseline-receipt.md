# Breakglass adapter details stay redacted side evidence and off baseline receipt

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, supply-chain  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`docs/706` through `docs/709` already did the hard narrowing work:

- breakglass session methods stay concrete,
- pre-session bootstrap history joins through exact upstream receipts,
- plural joins stay enabling-only and earliest-to-latest,
- and the common paired one-time-boot case is `boot.override.receipt` then `reset.receipt`.

This follow-on cut answers the next tempting implementation shortcut:
**should the baseline breakglass receipt start carrying rich BMC / KVM / SOL / virtual-media runtime detail?**

## Accepted boundary

No.

The baseline `breakglass.receipt` stays adapter-thin.
The canonical portable story is still:

- `session.method = console | serial | ssh`
- `evidence.bootstrap_receipt_joins[]` when exact reviewed pre-session boot/reset receipts materially enabled entry
- `evidence.tty_recording_digests[]` when the stronger interactive evidence lane participated
- `repair_outcome.authoritative_receipt_digests[]` when post-entry repair truth needs exact derived-operation proof

That is the portable truth surface.

## What stays out of the baseline receipt

Do **not** treat these as first-class baseline `breakglass.receipt` fields:

- vendor/product-specific BMC console metadata
- remote console launch URLs, ports, session ids, cookies, or tokens
- copied `ConsoleEntryCommand` / hotkey display strings
- virtual-media image locators or proxy/legacy/browser transport detail
- screenshots, crash-video captures, or dashboard breadcrumbs
- ticket prose that reconstructs adapter/runtime detail instead of pointing at reviewed typed receipts

Those details may exist, and sometimes they matter.
But they are adapter/runtime evidence, not the portable authority story.

## Why this is the right boring answer

The primary management sources already separate these surfaces rather than collapsing them into one noun:

- Redfish separates graphical console, serial console, and virtual media.
- Serial-console surfaces can publish client hints such as `ConsoleEntryCommand` and `HotKeySequenceDisplay`, which are useful operator/runtime details rather than portable authority proof.
- OpenBMC virtual media documents multiple implementation modes (browser proxy vs BMC-managed remote image mounting).
- Vendor remote consoles add plugin choices, port settings, concurrent-session behavior, and video/crash-log capture.

That is precisely the kind of detail that becomes privacy-toxic, vendor-specific, and hard to redact if it silently joins the baseline breakglass receipt.

The archive already has a better pattern for this class of problem: keep the portable typed receipt small and exact, and keep richer helper/runtime material as explicit stronger side evidence.

## First spec cut

The implementation-shaped cut is intentionally small:

- keep `breakglass.receipt.session` and `breakglass.receipt.evidence` closed-world instead of adding adapter/runtime fields by convenience
- teach the schema descriptions that adapter launch/runtime detail stays redacted side evidence
- teach `breakglass.receipt.notes` that it is not a loophole for live locators, session secrets, or copied console-launch data
- add a guardrail so future edits cannot quietly widen the baseline receipt with adapter-specific keys or wording

## What this does *not* forbid

This cut does **not** say adapter detail is never worth keeping.
It says the detail belongs in an explicit stronger lane.

Still allowed as follow-on work:

- a dedicated adapter-side-evidence artifact family
- redacted support-bundle members for adapter/runtime investigation
- profile-shaped export rules for those richer artifacts
- UI rendering that shows redacted adapter provenance without laundering it into portable authority truth

## Related docs

- ADR: `adrs/ADR-0300-breakglass-adapter-details-stay-redacted-side-evidence-and-off-baseline-receipt.md`
- concrete session methods: `docs/706-breakglass-session-methods-stay-concrete-and-oob-adapters-project-into-them.md`
- exact bootstrap joins: `docs/707-breakglass-bootstrap-joins-stay-exact-receipt-typed-and-pre-session-only.md`
- enabling-only ordered joins: `docs/708-breakglass-bootstrap-joins-stay-enabling-only-and-earliest-to-latest-when-plural.md`
- paired boot-override/reset order: `docs/709-breakglass-bootstrap-joins-keep-boot-override-before-reset-when-both-participate.md`
- breakglass lane: `docs/236-breakglass-and-recovery-mode.md`
- breakglass workflows: `docs/250-breakglass-and-recovery-workflows.md`
- product defaults: `docs/618-breakglass-recording-detail-and-export-posture-by-profile.md`
- guardrail: `tools/check_breakglass_adapter_detail_boundary.py`

## References

- DMTF Redfish Property Guide (`ConsoleEntryCommand`, `HotKeySequenceDisplay`, `VirtualMedia`, `VirtualMediaConfig`): https://redfish.dmtf.org/schemas/v1/DSP2053_2025.2.pdf
- DMTF Redfish release history (remote console / serial console / virtual media updates on `ComputerSystem`): https://redfish.dmtf.org/schemas/Redfish_Release_History.pdf
- DMTF Redfish schema index (`VirtualMedia`): https://redfish.dmtf.org/redfish/schema_index
- OpenBMC virtual-media design (browser proxy mode vs BMC-managed remote image mounting): https://github.com/openbmc/docs/blob/master/designs/virtual-media.md
- Dell iDRAC virtual console (plugin/runtime/session behavior, crash/video capture): https://www.dell.com/support/manuals/en-us/idrac9-lifecycle-controller-v4.x-series/idrac9_4.00.00.00_ug_new/configuring-and-using-virtual-console?guid=guid-1607d2bc-0ed1-4487-84e1-272357a474ae&lang=en-us

Last updated: 2026-03-23r441
