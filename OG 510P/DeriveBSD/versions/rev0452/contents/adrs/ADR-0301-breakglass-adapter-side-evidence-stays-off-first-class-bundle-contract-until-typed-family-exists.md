# ADR-0301: Breakglass adapter side evidence stays off first-class bundle contract until typed family exists

- Status: Accepted
- Date: 2026-03-23

## Context

`ADR-0300` already fixed the baseline `breakglass.receipt` to stay adapter-thin:

- concrete `session.method` stays the portable authority surface,
- exact bootstrap joins explain reviewed pre-session recovery paths,
- exact TTY joins explain reviewed interactive evidence,
- and adapter launch/runtime detail stays redacted side evidence instead of widening the baseline receipt.

That still leaves one nearby support/export seam expensive to leave fuzzy:

**what should the official incident/support bundle contract do with richer breakglass adapter/runtime detail when it materially matters to an investigation?**

The archive already has one narrow, portable answer for emergency authority participation:
`incident.bundle.includes.breakglass_receipt_digests` points to the exact `breakglass.receipt` objects that prove emergency authority was exercised.

But implementations could still drift in two bad directions:

1. minting premature first-class bundle fields for BMC / KVM / SOL / virtual-media runtime detail before the archive even has a dedicated typed artifact family for that material, or
2. pretending that because richer adapter detail might matter, the typed bundle contract should weaken back into collector-private folklore hidden under `extra`, ticket prose, or ad hoc attachments.

Both are costly. The first grows a weak cross-vendor contract too early. The second destroys the authority-first support story the archive already paid for.

## Decision

1. Official support handoff for breakglass stays **authority-first**.
   The first-class typed bundle proof remains `incident.bundle.includes.breakglass_receipt_digests` pointing at exact `breakglass.receipt` objects.

2. Richer adapter/runtime side evidence does **not** get new first-class `incident.bundle` fields in v0 merely because some investigations may need it.
   Examples include:
   - BMC / KVM / SOL launch/runtime records
   - virtual-media session/runtime diagnostics
   - console-launch URLs, ports, or client/runtime hints
   - screenshots, crash videos, or other adapter-specific operator artifacts

3. If that richer material is exported at all before a dedicated typed family exists, it remains **supplementary side evidence** only:
   - optional `incident.bundle.includes.extra[]` evidence digests, and/or
   - external case attachments under explicit support/export policy.

4. `includes.extra[]` is not a substitute for typed authority proof.
   Breakglass participation still becomes official support truth through `breakglass_receipt_digests`, not through ad hoc extra evidence.

5. A future dedicated adapter-side-evidence family remains allowed, but it must arrive RFC-first / ADR-backed instead of being inferred from provisional support-bundle convenience.

## Consequences

Good:

- official support handoff keeps one portable answer to “which exact emergency authority record participated?”
- richer adapter/runtime material can still travel under stronger policy without pretending the archive already standardized it
- the bundle contract avoids cross-vendor schema sprawl while still leaving room for future exact artifacts
- and detached support review remains stable because typed authority proof does not move around when richer side evidence is absent, redacted, or case-managed elsewhere

Costs:

- some investigations will still need supplementary evidence or case attachments in addition to the typed bundle contract
- `incident.bundle.includes.extra[]` stays intentionally second-class for this material, which means clients must not over-interpret it as portable typed truth
- and future richer adapter-side-evidence work must define its own artifact family, joins, and export/redaction posture explicitly

## Follow-on

Still open as a later design cut:

- whether a dedicated breakglass adapter-side-evidence artifact family is worth standardizing
- which redacted adapter/runtime facts would be portable enough to review across vendors
- whether support bundles should later gain a typed pointer family for those artifacts once the family itself exists
