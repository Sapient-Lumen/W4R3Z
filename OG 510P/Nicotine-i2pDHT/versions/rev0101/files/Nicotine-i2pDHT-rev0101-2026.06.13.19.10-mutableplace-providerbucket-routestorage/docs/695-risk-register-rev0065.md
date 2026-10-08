# Risk register — rev0065

## Still risky

- Remote witness semantics are toy-local, not a production witness protocol.
- Family/path labels are lab hints, not real independence proof.
- Repair outbox staging does not define a live publication protocol.
- Conflict cooldown is local pressure, not a distributed fairness system.

## Improved

- Remote witness replay across rounds is now tested.
- Conflict evidence that drops contradiction memory is quarantined.
- Repair staging has exact-boundary marker discipline.
- Repeated duplicate conflict cannot silently become unbounded repair spam.
