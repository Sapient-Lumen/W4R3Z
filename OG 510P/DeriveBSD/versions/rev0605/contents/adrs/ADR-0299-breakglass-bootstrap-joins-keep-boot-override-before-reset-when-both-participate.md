# ADR-0299: Breakglass bootstrap joins keep boot override before reset when both participate

- Status: Accepted
- Date: 2026-03-23

## Context

`ADR-0297` made pre-session recovery-path joins exact and typed, and `ADR-0298` made plural joins enabling-only and earliest-to-latest.
That fixed the big portability leak, but one smaller implementation detail was still fuzzy:

**what is the canonical order when a one-time maintenance boot selection and a reset both materially enabled the eventual breakglass session?**

The current archive example had drifted into one plausible-but-wrong story: `reset.receipt` before `boot.override.receipt`.
That is not the right portable default for the reviewed one-time boot path.

Redfish separates these surfaces cleanly:

- boot-source override is used to select the next boot target,
- reset/power-cycle actions are what actuate that next boot,
- serial/console surfaces are separate again,
- and virtual media is manager-provided media/boot plumbing rather than the breakglass session method itself.

Vendor implementations tell the same story in operator-facing terms: one-time boot / boot-on-next-reset is selected first, then the server is rebooted or reset to consume that setting.

Without one more boring rule, two implementations could both claim `earliest-to-latest-pre-session-enabling-only` while disagreeing on the most common paired sequence.
That would make the exact join surface portable in theory but still require human reinterpretation in practice.

## Decision

1. `breakglass.receipt.evidence.bootstrap_receipt_joins[]` remains ordered by the joined receipts' own timing.

2. When the enabling chain includes **both** a reviewed `boot.override.receipt` and a reviewed `reset.receipt` for the same maintenance/recovery entry path, the canonical order is:
   - `boot.override.receipt`
   - then `reset.receipt`

3. The reason is semantic, not cosmetic:
   - `boot.override.receipt` records the exact next-boot selection,
   - `reset.receipt` records the later actuation that consumes that selection.

4. `reset.receipt` may still appear alone when reset/reprovision itself is the enabling path, and `boot.override.receipt` may still appear alone when the reviewed recovery path does not require a typed reset receipt.
   The new rule only constrains the paired case.

## Consequences

Good:

- the canonical example now matches the reviewed one-time-boot semantics,
- support/export tooling gets one boring paired sequence instead of vendor-by-vendor folklore,
- and plural bootstrap joins stay causally readable without inventing a richer adapter taxonomy.

Costs:

- nearby docs and guardrails need one more explicit sentence,
- the previous example order must be corrected,
- and richer per-adapter timelines remain follow-on work instead of piggybacking on the authoritative join array.

## Follow-on

Still open as implementation detail:

- exact same-host/subject correlation mechanics across the joined receipt families,
- exact rendering of adapter breadcrumbs when they exist as supplementary evidence,
- and exact redaction/export posture for BMC / virtual-media / console metadata beyond the accepted breakglass baseline.
