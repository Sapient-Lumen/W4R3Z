# ADR-0297: Breakglass bootstrap joins stay exact receipt-typed and pre-session-only

- Status: Accepted
- Date: 2026-03-23

## Context

`ADR-0296` deliberately kept breakglass session methods concrete: `console`, `serial`, and `ssh`.
That stopped generic `oob` from hiding what the operator actually used.

But one nearby seam was still soft: how a breakglass receipt should explain the **pre-session recovery path** that got the machine into that emergency session in the first place.

Without an exact join, responders fall back to the wrong evidence:

- ticket prose about “booted via recovery media”,
- BMC dashboard breadcrumbs,
- virtual-media screenshots,
- or later shell notes that try to retell an earlier boot/reset step.

That is the same kind of folklore leak the archive has been removing elsewhere.
The recovery path already has typed authority/evidence objects:

- `boot.override.receipt` explains approved mutable boot selection,
- `reset.receipt` explains destructive reset/reprovision authority and what was observed.

Breakglass should join those exact objects when they materially enabled the session, instead of inventing a new remote-presence object family or asking support to reconstruct recovery boot history from adapter-specific traces.

## Decision

1. `breakglass.receipt.evidence.bootstrap_receipt_joins[]` is the canonical optional join surface for **pre-session recovery-path receipts** that materially enabled the emergency session.

2. The first reviewed `kind` vocabulary is intentionally small:
   - `boot.override.receipt`
   - `reset.receipt`

3. These joins are **pre-session only**.
   `breakglass.receipt.evidence.bootstrap_join_posture = pre-session-recovery-path-only` makes that boundary explicit.

4. Post-entry work does **not** use this join surface.
   Repairs performed under breakglass still prove themselves through `repair_outcome.authoritative_receipt_digests` and their own authoritative receipts.

5. Raw adapter state is not a substitute for the typed join.
   Virtual-media attachment, BMC UI breadcrumbs, or similar adapter telemetry may exist as stronger side evidence, but they do not replace the exact `boot.override.receipt` / `reset.receipt` join when those receipts already carried the reviewed authority story.

## Consequences

Good:

- breakglass can explain **how the machine got into recovery** without widening the breakglass method vocabulary,
- virtual-media and recovery-slot boot history stop disappearing into notes,
- support/export surfaces can follow one exact digest path instead of reconstructing bootstrap from dashboards,
- and destructive reset authority remains on `reset.receipt` rather than leaking back into breakglass folklore.

Costs:

- nearby docs and examples need one more evidence join,
- and some legacy/operator-local recovery flows will stay visibly adapter-shaped until they emit the typed upstream receipts this ADR expects.

## Follow-on

Still open as implementation detail:

- exact per-adapter provenance/redaction fields for BMC/SOL/console stacks,
- whether later lanes need first-class joins to non-receipt bootstrap artifacts,
- and how prominent trusted UI / support surfaces should render the pre-session recovery path.
