# Completion acceptance proof page: finished, accepted, reopened, and surviving obligations interface spec

## Purpose

This page is the durable proof surface answering:

> what completion claim was accepted, by whom, at what strength, and what still survives even after acceptance?

## Proof ladder

The page must render the highest achieved proof rung.

Supported `acceptance_proof_rung` values:

- `self-report-only`
- `evidence-attached`
- `reviewer-confirmed-effect`
- `requester-accepted-scope`
- `multi-party-accepted`
- `estate-effect-confirmed`
- `accepted-then-reopened`

Hard rule:

The rung may go down later.
Acceptance is not irreversible truth.

## Fixed sections

1. **Accepted claim card**
2. **Acceptance basis card**
3. **Surviving obligation card**
4. **Reopen boundary card**
5. **Decision sentence**

### 1) Accepted claim card

Show:

- source mandate id
- accepted scope
- acceptance class
- acceptance time
- accepter identity / lane
- strongest safe completion sentence

Supported `acceptance_class` values:

- `none`
- `accepted-exact`
- `accepted-partial`
- `accepted-temporary`
- `accepted-with-side-effect-debt`
- `accepted-subject-to-observation`
- `reopened`

### 2) Acceptance basis card

Required rows:

- evidence objects relied on
- live witnesses relied on
- reviewer notes
- requester note if different from reviewer
- disputed items explicitly excluded

Hard rule:

The proof page must preserve not only why the return was accepted, but also what was excluded from the acceptance.

### 3) Surviving obligation card

Required rows:

- observation still owed
- cleanup still owed
- wider rollout or publication still blocked
- handoff still owed
- certificate or mandate downgrade still required

Hard rule:

Any surviving obligation stronger than zero blocks rendering the proof as `fully closed`.

### 4) Reopen boundary card

Required rows:

- reopen triggers
- freshness decay trigger
- superseding evidence trigger
- scope-discovery trigger
- recall / cancellation interaction

Supported `reopen_posture` values:

- `stable-no-open-trigger-known`
- `stable-but-observation-window-open`
- `fragile-reopen-likely`
- `reopened-already`

### 5) Decision sentence

Render one sentence only:

- `Completion for [scope] is accepted at rung [rung] with posture [reopen_posture], but the stronger sentence that [overclaim] remains blocked.`
