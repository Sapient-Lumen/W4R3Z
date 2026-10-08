# Owner-route block audit rev0281

## Question

What should the cube do when the packet is ready but no real accountable owner
route is available?

## Finding

Before rev0281, the answer was partly executable and partly freeform: the
send-now brief said to record the block locally, but the router could only see
packet, send-log, contact-status, intake, seed, review, decision, ticket, and
live-window card artifacts. A route block captured only in narrative could be
missed, allowing a later operator to record a send log without a human send or to
write more doctrine to avoid the field block.

## Repair

Rev0281 adds `route-block.json` as a scratch-local, no-send, non-evidence record.
It must source a valid prepared packet manifest. It records only class-level route
failure, no recipient names, no addresses, no owner answers, no learner facts, no
protected facts, and no raw material. The router now treats a valid latest route
block as a stop state: keep `FT-0181` live, do not record send log, do not open a
contact clock, do not intake data, do not upgrade claims, and do not close.

## Boundary

A route block is not owner evidence. It does not prove the service works or fails.
It only proves that this local field session should not pretend a send happened.
If a real accountable owner route later appears, use a routed scratch path and a
real human send/adaptation before recording a send log.

## Next audit target

The next audit should follow the next real artifact: a send log after actual
human send, a route block after real no-route determination, or a returned owner
CSV after an active source clock. Do not audit the rest of the cube merely
because it exists.
