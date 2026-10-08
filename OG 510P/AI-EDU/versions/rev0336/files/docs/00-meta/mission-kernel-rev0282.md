# Mission kernel rev0282

The heart of the mission remains institutional truth in education: AI systems may
assist learning work, but they must not silently gain authority over learning
claims, grades, records, protected routes, public language, service changes, or
closure before owner evidence and reversible controls justify that authority.

Rev0282 spends the change budget on the next easiest place to fake progress: the
one permitted clarification after a missing or malformed owner return. A first
send already has a `send-log` firebreak. Rev0282 gives the re-ask the same
shape: no `REASK_AWAITING_REPLY` clock may be recorded until a local
`owner-reask-log` says a human actually sent or adapted the bounded clarification
through a class-level owner route.

## Current live kernel

1. Ask the router for exactly one executable command.
2. Prepare the bounded `AIEDU-SR-003` owner packet when scratch is empty.
3. If an accountable owner route exists, send/adapt the generated email and
   blank CSV outside the archive.
4. If no accountable owner route exists, record `owner-route-block` locally and
   stop without creating a send log or contact clock.
5. Record a local send log only after an actual human send/adaptation.
6. Record the bounded first contact clock from the send log, not from the packet.
7. If the first clock lapses or a real returned packet needs one clarification,
   record `owner-reask-log` only after the human sends/adapts the bounded re-ask.
8. Record the bounded re-ask contact clock from the reask log, not directly from
   the prior contact clock, intake bundle, or workbench review.
9. Intake a real returned CSV only through the active source contact clock.
10. Seed, review, decide, ticket, card, and read out only through the routed
    non-evidence chain.
11. If the bounded re-ask expires, record `NO_OWNER_PACKET`; do not widen the ask
    or create new governance surfaces to compensate.

## What changed in rev0282

Rev0282 adds `tools/record_ft0181_owner_reask_log.py`, a Make target,
shared-guard validation, a direct validator, registry/lint coverage, and router
states that require a reask log before any dated clarification clock can exist.
The router no longer jumps from `RE-ASK-ONCE`, `REASK-OWNER`, or a due first
clock straight to `STATUS=reask-awaiting-reply`. It emits `make owner-reask-log`
first, then routes the valid `reask-log.json` to the dated contact-status command.

This is not a new doctrine branch. It is a small executable firebreak that keeps
the one allowed clarification honest while preserving the source boundary: no
recipient details, no owner answers, no raw or protected material, no evidence
upgrade, no public claim, no closure, and no second re-ask loop.

## What counts as progress now

- A real external send/adaptation followed by a local send log.
- A bounded route-block record when the packet cannot be sent because no real
  accountable owner route exists.
- A bounded first contact clock after a real send log.
- A bounded reask log after a real human clarification send/adaptation.
- A bounded reask contact clock sourced only from that reask log.
- A real owner-returned CSV tied to an active contact clock.
- A source-clocked intake, seed, review, first-packet decision, post-decision
  ticket, live-window card, and readout that remain below acceptance.
- A bounded `NO_OWNER_PACKET` record after the permitted clocks expire.
- A small executable refactor that makes one of those steps harder to fake or
  skip.

## What must not happen

Do not convert a route block, fresh version stamp, packet, send-now brief,
field-texture memo, send log, reask log, contact clock, intake bundle, workbench
seed, review, decision board, change ticket, live-window card, readout, or audit
into owner evidence, custody evidence, acceptance, closure, public-summary
support, or a claim that the service improves learning, safety, access,
workload, compliance, scale, or effectiveness.
