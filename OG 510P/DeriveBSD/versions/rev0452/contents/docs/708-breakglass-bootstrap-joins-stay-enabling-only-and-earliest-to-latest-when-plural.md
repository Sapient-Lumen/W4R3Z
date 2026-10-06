# Breakglass bootstrap joins stay enabling-only and earliest-to-latest when plural

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate

`docs/707-breakglass-bootstrap-joins-stay-exact-receipt-typed-and-pre-session-only.md` already fixed the first important split: pre-session recovery history joins through exact upstream receipts instead of notes or adapter folklore.

This follow-on cut fixes the next ambiguity:
**if more than one bootstrap receipt is present, what exactly belongs in that array, and in what order?**

## Accepted boundary

- `breakglass.receipt.evidence.bootstrap_receipt_joins[]` stays an **enabling-only** surface.
- When plural, those joins are listed in **earliest-to-latest** causal order.
- `breakglass.receipt.evidence.bootstrap_join_sequence_posture` fixes that rule to `earliest-to-latest-pre-session-enabling-only`.
- denied attempts, failed dead ends, superseded experiments, and adapter breadcrumbs do **not** belong in the canonical bootstrap join array.
- Post-entry repair truth still stays on `repair_outcome.authoritative_receipt_digests`.

## Why this matters

Without this cut, the archive would still have a quiet portability leak.
Two implementations could both claim to support exact bootstrap joins while meaning very different things:

- one could list only the receipts that actually enabled entry,
- another could append denied boot attempts and failed resets because they happened earlier,
- and a third could keep the right receipts but serialize them in dashboard order instead of causal order.

That would make support, policy review, and later automation rediscover the real sequence from prose.

## Practical rule

Think of `bootstrap_receipt_joins[]` as the **pre-session enabling chain**, not the whole incident timeline.

Good:

- a reviewed `boot.override.receipt` that selected the next maintenance boot,
- followed by a reviewed `reset.receipt` that actuated that selection,
- listed earliest to latest.

Not good:

- denied boot attempts,
- failed reset experiments that never yielded the real session,
- duplicate/superseded exploratory steps,
- BMC UI breadcrumbs or virtual-media attachment state when the exact typed receipts already exist.

## First spec cut

- add `evidence.bootstrap_join_sequence_posture = earliest-to-latest-pre-session-enabling-only` to `spec/breakglass.receipt.schema.json`
- update `bootstrap_receipt_joins[]` descriptions so they say enabling-only and earliest-to-latest when plural
- update the canonical example so the array exercises a real ordered pair: `boot.override.receipt` then `reset.receipt`
- add a guardrail so this ordering/selection boundary cannot drift back into timeline scrapbook behavior

## Wiring surfaces

- ADR: `adrs/ADR-0298-breakglass-bootstrap-joins-stay-enabling-only-and-earliest-to-latest-when-plural.md`
- prior exact-join cut: `docs/707-breakglass-bootstrap-joins-stay-exact-receipt-typed-and-pre-session-only.md`
- breakglass lane: `docs/236-breakglass-and-recovery-mode.md`
- breakglass workflows: `docs/250-breakglass-and-recovery-workflows.md`
- breakglass recording posture: `docs/618-breakglass-recording-detail-and-export-posture-by-profile.md`
- schema: `spec/breakglass.receipt.schema.json`
- example: `spec/examples/breakglass.receipt.json`
- guardrail: `tools/check_breakglass_bootstrap_sequence_boundary.py`

## References

- DMTF Redfish Resource and Schema Guide (`ComputerSystem.BootSourceOverrideTarget`, `ComputerSystem.Reset`): https://redfish.dmtf.org/schemas/v1/DSP2046_2025.2.html
- DMTF Redfish schema index (`VirtualMedia`): https://redfish.dmtf.org/redfish/schema_index

This now has one more concrete rule too: when the enabling chain includes both a one-time maintenance boot selection and the reset that consumed it, serialize `boot.override.receipt` before the later `reset.receipt` rather than reversing selection and actuation. `docs/709-breakglass-bootstrap-joins-keep-boot-override-before-reset-when-both-participate.md` locks that paired-case order down.

Last updated: 2026-03-23r440
