# Discriminator acquisition contract sheet page: open gaps, question value, and burden interface spec

## Purpose

After the archive learned how to name candidate doctrines and the next best distinguishing question, it still needed one ordinary operator page for the next question:

> which fact should we actually try to obtain now, why is it worth the trouble, how expensive is it, and what do we do if that evidence channel is unavailable?

## Core decision

AnonSync must expose one first-class **Discriminator acquisition contract sheet** whenever a fresh case still has open routing ambiguity or blocked stronger sentences because a missing fact matters.

## Fixed page order

1. **Acquisition header**
2. **Open-gaps card**
3. **Candidate-asks card**
4. **Burden and intrusion card**
5. **Fallback-path card**
6. **Current ask decision card**
7. **Decision sentence**

### 1) Acquisition header

Show:

- acquisition sheet id
- source case id
- source applicability sheet id
- current operator owner
- evidence posture
- current strongest safe sentence
- strongest blocked sentence

Supported `evidence_posture` values:

- `cheap-facts-available`
- `medium-burden-capture-justified`
- `heavy-capture-not-yet-justified`
- `heavy-capture-justified`
- `capture-channel-unavailable`
- `enough-to-route-with-weaker-claim`

Hard rule:

The page may not request evidence without naming the burden posture first.

### 2) Open-gaps card

Required rows:

- unresolved fact gap
- why the gap matters
- doctrine routes or interventions affected
- stronger sentence blocked by this gap
- expiry if the gap becomes irrelevant later

Hard rule:

Every open gap must map to a concrete blocked decision or blocked stronger sentence.
A curiosity gap is not enough.

### 3) Candidate-asks card

For each evidence ask, show:

- ask id
- question or capture request
- answer channel
- expected discriminator value
- freshness requirement
- who can satisfy it
- route impact if answered either way

Supported `expected_discriminator_value` values:

- `route-collapsing`
- `major-narrowing`
- `moderate-narrowing`
- `confirmation-only`
- `weak-context-only`

Supported `answer_channel` values:

- `ui-observation`
- `operator-question`
- `device-setting-check`
- `peer-comparison`
- `history-or-queue-inspection`
- `warning-detail-read`
- `log-capture`
- `profiler-or-crash-artifact`
- `external-human-approval`

Hard rule:

The sheet must support multiple candidate asks at once.
The operator should not have to compare question value mentally.

### 4) Burden and intrusion card

Required rows for each ask:

- burden rung
- restart requirement
- reproduction requirement
- downtime or pause risk
- privacy or disclosure cost
- multi-peer dependency
- estimated failure modes

Supported `burden_rung` values:

- `trivial-read`
- `single-check`
- `guided-inspection`
- `multi-peer-check`
- `restart-and-reproduce`
- `artifact-heavy`

Hard rule:

Decision value and burden must stay separate.
A high-value ask may still be deferred if the burden is not justified yet.

### 5) Fallback-path card

Required rows:

- preferred ask if available
- first fallback ask
- lowest-burden fallback ask
- ask to avoid unless posture worsens
- claim ceiling if all remaining asks are declined or unavailable

Hard rule:

A sheet with a preferred ask must also publish a fallback.
`Ask for logs` is not enough.

### 6) Current ask decision card

Supported `current_ask_decision` values:

- `ask-now`
- `observe-before-asking`
- `collect-cheaper-fact-first`
- `defer-heavy-capture`
- `skip-unavailable-channel`
- `escalate-because-capture-blocked`
- `route-with-weaker-claim`

Required rows:

- current ask decision
- chosen ask id
- why it beat alternatives
- what action is allowed while waiting
- what action is blocked while unanswered
- rereview trigger

Hard rule:

The chosen ask must publish both what it enables and what remains blocked.

### 7) Decision sentence

Render one sentence only:

- `Given current ambiguity, the next evidence move is [current_ask_decision] via [chosen ask], because its discriminator value is [value] at burden rung [rung]; the stronger blocked sentence remains [sentence].`

## Required interactions

- **Add open gap**
- **Attach candidate ask**
- **Raise or lower burden rung**
- **Promote fallback ask**
- **Shift current ask decision**

## Failure state

If no feasible ask exists, show:

- `No feasible evidence move is currently available. Route with the weaker claim or escalate with explicit capture unavailability.`
