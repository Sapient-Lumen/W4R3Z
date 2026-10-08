# Evidence intake contract sheet page: target claim, packet fit, and open gaps interface spec

## Purpose

Once a packet has been exported and received, the operator still needs one page that answers:

> what question is this packet supposed to help decide, how well does it fit that question, and what exact gaps still block the stronger sentence?

## Core decision

AnonSync must expose one first-class **Evidence intake contract sheet** whenever any evidence packet is received for review, support, adjudication, escalation, certification, or precedent work.

## Fixed page order

1. **Intake header**
2. **Target-claim card**
3. **Packet-fit card**
4. **Freshness-and-window card**
5. **Open-gap card**
6. **Supplement-candidate card**
7. **Decision sentence**

### 1) Intake header

Show:

- intake sheet id
- source packet id
- source packet posture
- source case or mandate id
- intake owner
- current intake posture
- current strongest safe intake sentence
- strongest blocked sentence

Supported `intake_posture` values:

- `received-not-opened`
- `opened-not-validated`
- `validated-not-matched`
- `matched-but-insufficient`
- `supplement-request-pending`
- `decision-grade-for-bounded-question`
- `decision-grade-with-reservations`
- `intake-stale-or-invalid`

Hard rule:

The header may not jump directly from `received` to `decision-grade`.
At least one explicit validation and one explicit fit judgment must exist.

### 2) Target-claim card

Required rows:

- target question or decision
- candidate stronger sentence sought
- currently safe weaker sentence
- governing scope
- governing world assumptions
- excluded questions

Supported `target_claim_class` values:

- `diagnosis-support`
- `dispute-support`
- `rollout-health-support`
- `control-trust-support`
- `fulfillment-support`
- `precedent-support`
- `certification-support`
- `external-escalation-support`

Hard rule:

A packet cannot be judged sufficient in the abstract.
It must be sufficient *for a named target question*.

### 3) Packet-fit card

Required rows:

- packet artifact classes received
- expected artifact classes for this question
- world match status
- subject or scope match status
- version window match status
- transform or redaction limits still relevant

Supported `packet_fit_verdict` values:

- `shape-match`
- `partial-shape-match`
- `wrong-artifact-shape`
- `wrong-world`
- `wrong-scope`
- `wrong-version-window`
- `transform-limited`
- `mixed-fit`

Hard rule:

A readable packet that comes from the wrong world must not be described as a fit.

### 4) Freshness-and-window card

Required rows:

- observed event time
- capture start and end window
- intake time
- packet freshness horizon
- rotation or truncation risk
- completeness risk

Supported `window_fitness` values:

- `covers-event-window`
- `window-partial`
- `window-unknown`
- `window-missed`
- `rotation-risk-high`
- `rotation-loss-evident`

Hard rule:

Old but still technically openable logs must publish whether the relevant event window was actually preserved.

### 5) Open-gap card

Required rows:

- named missing facts
- why each missing fact matters
- stronger sentence each gap blocks
- whether gap can be tolerated
- burden of closing each gap

Supported `gap_type` values:

- `missing-context`
- `missing-timestamp`
- `missing-peer-role`
- `missing-subject-identity`
- `missing-share-or-file-name`
- `missing-event-window`
- `missing-raw-artifact`
- `wrong-world-source`
- `over-redacted`
- `validation-failed`

Hard rule:

Every open gap must explicitly name the stronger sentence it blocks.
Otherwise the gap is not yet operationally meaningful.

### 6) Supplement-candidate card

Required rows:

- cheapest useful supplement
- alternative heavier supplement
- burden rung
- intrusion cost
- deadline or expiry
- fallback weaker sentence if no supplement arrives

Supported `supplement_candidate` values:

- `clarifying-note-only`
- `timestamp-and-role-addendum`
- `fresh-log-window`
- `larger-log-window`
- `raw-packet-request`
- `different-world-capture`
- `dump-or-crash-artifact`
- `network-benchmark-artifact`
- `no-supplement-worth-it`

Hard rule:

Supplement requests must be minimal-first.
`Send more logs` is invalid unless it is the named cheapest useful supplement.

### 7) Decision sentence

Form:

> This packet is **[intake posture]** for **[named target question]** because **[fit summary]** and **[window summary]**. The strongest safe sentence is **[current safe sentence]**. The strongest blocked sentence is **[blocked sentence]**, blocked by **[named gaps]**. The next best supplement is **[supplement candidate]** with burden **[burden rung]**.
