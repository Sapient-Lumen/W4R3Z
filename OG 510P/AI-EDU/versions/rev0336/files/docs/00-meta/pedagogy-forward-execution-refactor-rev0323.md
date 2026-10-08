# rev0323 pedagogy-forward execution refactor

## Refactor target

The micro-pilot path had become command-routed through packet preparation, readiness scoring, dry-run
rehearsal, and next-action selection. The missing step was a durable owner-review boundary for a real
non-synthetic packet.

## Change

Rev0323 adds one utility command instead of another doctrine surface:

```bash
make micro-pilot-owner-review
```

It records a scratch-only owner-review stop after a human local owner reviews the completed aggregate
packet. It refuses synthetic packets and packet/readout decision mismatches.

## Why this is pedagogical

The teacher/tutor micro-pilot is supposed to test whether AI can improve human instructional moves
without leaking answers, increasing inequity, or creating false learning claims. A local owner-review
stop keeps the teacher/tutor owner in charge of the next decision and prevents the archive from
promoting packet mechanics into learning evidence.

## Hot-path rule

The next useful work is still human execution:

1. send or block the `FT-0181` owner request;
2. run the equality-one-step teacher/tutor micro-cycle locally;
3. score the completed aggregate packet;
4. record the owner-review stop only after human review.

Anything else should reduce friction on those steps or be deferred.
