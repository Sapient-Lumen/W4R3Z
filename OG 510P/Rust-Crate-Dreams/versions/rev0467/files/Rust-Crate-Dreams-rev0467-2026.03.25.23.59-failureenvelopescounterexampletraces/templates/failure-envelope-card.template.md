# Failure-envelope card template

## Lane
`P-____`

## Receiver
- who reads the failure envelope
- who challenges it
- who repairs or replays it later

## Failing scenario family
- scenario 1
- scenario 2

## Decisive counterexample family
- witness 1
- witness 2

## Smaller surviving claim
- degraded claim 1
- degraded claim 2

## Withdrawn guarantees
- withdrawn guarantee 1
- withdrawn guarantee 2

## Repair / replay hint
- smallest honest replay slice
- full reset trigger

## Refutation / supersession rule
- challenged
- downgraded
- refuted
- cleared
- superseded

## Artifact family
- `failure-envelope.json`
- `counterexample-trace.json`
- `disproof-summary.md`
- `degraded-claim.json`
- `withdrawn-guarantee.md`
- `repair-hint.json`
- `refutation-bridge.json`

## First honest `0.1`
- one bounded failing-scenario family
- one decisive counterexample family
- one degraded-claim vocabulary
- one withdrawn-guarantee note
- one repair hint

## Refusal boundary
State what the crate will not infer from one counterexample.
