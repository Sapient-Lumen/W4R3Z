# Coordinated capture run page — steps, participants, dwell, and success window interface spec

## Purpose

Model one reviewed attempt to catch the target symptom inside a usable evidence window.
This page should answer:

- which participants are expected to be ready
- what steps define the run
- what minimum dwell or capture window is required
- what counts as success, partial success, no reproduction, or capture failure
- which evidence window the run actually produced

This page exists so `reproduce issue and let logs run` becomes a typed run object instead of support folklore.

## Inputs

- incident identifier
- current incident brief
- current symptom bookmark if any
- witness set and required participants
- active capture windows by participant
- requested artifact families
- reproduction steps or trigger condition
- current send/export posture

## Primary questions this page must answer

1. Who must be ready before the run starts?
2. What exact actions or conditions define this run?
3. How long must capture stay active for the run to be usable?
4. Did we actually catch the target symptom?
5. What evidence window did the run produce for later review or export?

## Layout

### A. Run strip

Fields:

- run label
- incident headline
- target symptom
- success window target
- run state (`draft`, `staged`, `running`, `caught`, `no-repro`, `capture-failed`, `partial`, `expired`)

### B. Participant readiness matrix

Columns:

- participant
- role
- required or optional
- capture active
- restart satisfied
- ready now
- blocking issue if not ready

### C. Step choreography card

Show in order:

- preconditions
- actions to perform
- participant coordination notes
- what observation should count as the target symptom
- what alternative observation still counts as useful partial capture

### D. Success window card

Show:

- dwell floor
- current elapsed time
- whether the run is `too-short`, `usable-if-symptom-caught`, `usable`, or `stale`
- evidence window actually produced (`pre-event`, `during-event`, `post-event`, `missed-event`, `mixed`)

### E. Abort and partial-failure card

Possible outcomes:

- symptom not reproduced
- participant not ready in time
- restart pending or forgotten
- capture stopped too early
- symptom occurred outside the captured window
- wrong subject or participant involved

## Required interactions

- `Stage coordinated run`
- `Mark participant ready`
- `Start run`
- `Mark target symptom observed`
- `Mark useful partial symptom`
- `Mark no reproduction`
- `Stop run`
- `Open witness completeness review`
- `Issue capture brief receipt`

## Guardrails

- Never treat elapsed time alone as success if the target symptom was never observed.
- Never merge fresh and stale participant windows without saying so explicitly.
- Never start a coordinated run if a required participant still lacks the requested capture family.
- Never treat `packet sent` as proof that the run caught the right event.
- Never let a later export hide whether the run ended in success, partial, or no reproduction.

## Output

One reviewed capture-run object that preserves readiness, step order, dwell sufficiency, symptom outcome, and the usable evidence window actually produced.
