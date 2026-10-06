# Runtime dreambank 020 — model-oracled scheduler and provider kernel

Revision: rev0028

BrowserRT's ambition is now large enough that the testing strategy must be ambitious too. The dream is not merely a fast runtime; it is a runtime whose primitives are surrounded by models, histories, traces, and replayable counterexamples.

## Dream

A future BrowserRT provider could be born with the following shape:

```txt
provider contract
  -> implementation
  -> fake provider
  -> reference model
  -> deterministic command generator
  -> invariant suite
  -> trace schema
  -> replay artifact
  -> non-claims
```

The important idea: implementation and proof scaffolding grow together.

## Scheduler dream

A future scheduler stack could split into phases:

```txt
intent
  -> classify priority
  -> admit or reject
  -> pick candidate lanes
  -> score candidates
  -> reserve capacity
  -> bind work
  -> dispatch
  -> complete / cancel / retry
  -> reconcile accounting
```

Each phase can have model coverage before provider/browser coverage.

## Rev0025 rung

`scheduler:cross-lane-model-walk-proof` compares the fake-provider `CrossLaneScheduler` to an independent reference model across deterministic seeded operation walks. It is cheap enough for release and deep enough to catch many refactor mistakes.

## Future rungs

1. Cross-lane interleaving simulator for submit/dispatch/complete histories.
2. Provider-integrated storage-lane scheduling against fake persisted-spill providers.
3. Retention/compaction policy model for persisted spill queues.
4. Deadline/yield/cancellation model before any browser Worker scheduling proof.
5. Browser Worker scheduler smoke proof, explicit tier only.
6. Mesh-local placement model across visible tab, hidden tab, storage leader, and maintenance agent.
7. Formal mini-specs for the hardest queue and scheduler invariants.

## Guardrail

Do not confuse model-walk confidence with production correctness. The model proof is a stair; it is not the summit.
