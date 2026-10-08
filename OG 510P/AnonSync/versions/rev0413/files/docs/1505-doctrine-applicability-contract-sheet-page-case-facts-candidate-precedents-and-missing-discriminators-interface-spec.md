# Doctrine applicability contract sheet page: case facts, candidate precedents, and missing discriminators interface spec

## Purpose

After the archive learned how to publish doctrine, it still needed one ordinary page for the next operator question:

> this new case resembles several older ones — which doctrine candidates are live, which facts already disqualify some of them, and what fact is still missing before we can safely route it?

## Core decision

AnonSync must expose one first-class **Doctrine applicability contract sheet** whenever a fresh case, warning cluster, or routed escalation is being matched against existing doctrine.

## Fixed page order

1. **Applicability header**
2. **Observed-facts card**
3. **Candidate-precedents card**
4. **Disqualifiers and gaps card**
5. **Next-best-question card**
6. **Temporary routing stance card**
7. **Decision sentence**

### 1) Applicability header

Show:

- applicability sheet id
- source case id
- current operator owner
- intake time
- current ambiguity class
- current strongest safe sentence
- current unsafe overclaim

Supported `ambiguity_class` values:

- `single-clear-route`
- `few-live-lookalikes`
- `many-live-lookalikes`
- `insufficient-facts`
- `evidence-contradiction`
- `route-reversal-pending`

Hard rule:

A new case may not jump directly from symptom text to governing doctrine without first naming the ambiguity posture.

### 2) Observed-facts card

Required rows:

- primary symptom summary
- known environment/world facts
- known peer/connectivity facts
- known time/state facts
- known history or warning facts
- known operator actions already attempted

Hard rule:

The page must separate **observed facts** from **inferred cause**.
Facts are the substrate for routing; doctrine fit cannot be built on blurred speculation.

### 3) Candidate-precedents card

For each candidate doctrine, show:

- doctrine id
- why it was surfaced
- fit class
- strongest safe claim if this candidate wins
- strongest disqualifying fact already present
- additional fact needed to confirm or reject it

Supported `fit_class` values:

- `governing-if-confirmed`
- `strong-lookalike`
- `possible-but-weak`
- `currently-disqualified`
- `historically-related-only`

Hard rule:

The sheet must support more than one candidate precedent at once.
The operator should not have to flip between doctrine receipts to compare fit.

### 4) Disqualifiers and gaps card

Required rows:

- facts that rule out candidates already
- facts that weaken but do not eliminate candidates
- facts still missing
- facts that would collapse the ambiguity fastest
- contradictions between current witnesses

Hard rule:

A missing fact is not the same as an adverse fact.
The page must keep uncertainty separate from disqualification.

### 5) Next-best-question card

Required rows:

- next best distinguishing question
- why this question has the highest decision value
- evidence channel needed to answer it
- who may answer it
- fallback question if unavailable

Hard rule:

The product must publish one ranked next question whenever routing remains ambiguous.
`Read more docs` is not an acceptable substitute.

### 6) Temporary routing stance card

Supported `temporary_routing_stance` values:

- `apply-governing-doctrine-now`
- `treat-as-provisional-lookalike`
- `hold-for-next-fact`
- `route-to-fact-capture`
- `route-to-human-adjudication`
- `route-reversal-under-review`

Required rows:

- temporary routing stance
- what action is allowed under that stance
- what action is blocked under that stance
- what stronger sentence remains blocked
- expiry or rereview boundary

Hard rule:

Temporary stance must bound action.
Ambiguous routing may not silently authorize the same actions as a confirmed governing doctrine.

### 7) Decision sentence

Render one sentence only:

- `Given current facts, this case is [temporary_routing_stance] with [ambiguity_class]; leading candidate doctrine is [candidate] and the next best distinguishing question is [question].`

## Required interactions

- **Add observed fact**
- **Attach candidate precedent**
- **Disqualify candidate**
- **Promote question to primary discriminator**
- **Shift temporary routing stance**

## Failure state

If no candidate doctrine exists yet, show:

- `No doctrine candidate surfaced yet. This case remains unclassified and requires fresh fact-pattern work before any doctrine claim is safe.`
