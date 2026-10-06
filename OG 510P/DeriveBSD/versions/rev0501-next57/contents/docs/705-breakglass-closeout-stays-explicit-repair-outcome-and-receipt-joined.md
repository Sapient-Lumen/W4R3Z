# Breakglass closeout stays explicit, repair-outcome-shaped, and exact receipt-joined

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt  

## What changed

Emergency-session closeout now has a typed truth surface instead of hiding the result in operator prose.

`breakglass.receipt` now carries `repair_outcome`, and that object says whether the emergency session was:

- `observation-only`,
- `repair-pending-confirmation`,
- `repair-confirmed`,
- `repair-rolled-back`, or
- `repair-failed`.

If the session materially attempted a repair, the breakglass receipt must also carry exact `repair_outcome.authoritative_receipt_digests`. Those digests point at the authoritative derived-operation receipts (for example `config.receipt`) that actually prove the repair or rollback attempt.

## Why this matters

Before this cut, the archive could tell you:

- who opened breakglass,
- when it started and expired,
- whether attestation materially gated the emergency lane,
- and, for interactive shell/console sessions, which exact terminal recording artifact belonged to the session.

But it still could not say in typed form whether the emergency work ended as observation-only, pending confirm, confirmed repair, rollback, or failure. That pushed the most operationally important closeout fact back into notes, dashboards, and incident-ticket folklore.

That is not enough for any of the four product shapes.

## Boundary

The boundary is now:

- `breakglass.grant` / `breakglass.receipt` remain the emergency authority artifacts,
- derived operations executed under breakglass still prove themselves through their own receipts,
- `repair_outcome` is the typed closeout summary that joins the emergency session to those authoritative repair receipts,
- and ordinary post-breakglass authority still follows the separate fresh-attestation resumption rule.

So: **ending the emergency session is not the same thing as proving the repair succeeded**.

## Canonical example

The accepted example keeps a narrow, realistic story:

- breakglass opened through the console,
- interactive recording started at session open before the first prompt,
- a derived configuration repair ran under the lease,
- that repair is still `repair-pending-confirmation`,
- and the breakglass receipt carries the exact digest of the authoritative `config.receipt` that proved the attempted repair.

The rejected observation-only example now says exactly that too: `repair_outcome.status = observation-only`, with no fake repair-receipt digests attached.

## Files

- ADR: `adrs/ADR-0295-breakglass-closeout-stays-explicit-repair-outcome-and-receipt-joined.md`
- schema: `spec/breakglass.receipt.schema.json`
- examples: `spec/examples/breakglass.receipt.json`, `spec/examples/breakglass.receipt.rejected.json`, `spec/examples/config.receipt.json`
- guardrail: `tools/check_breakglass_repair_outcome_boundary.py`

Last updated: 2026-03-23r436
