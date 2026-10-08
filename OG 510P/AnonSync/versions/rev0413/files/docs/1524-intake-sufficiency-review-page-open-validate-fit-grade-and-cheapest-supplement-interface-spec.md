# Intake sufficiency review page: open, validate, fit-grade, and cheapest supplement interface spec

## Purpose

Once a packet exists, the operator needs one review page that decides:

> can we actually act on this packet now, what exactly is still missing, and what smallest follow-up would most increase confidence or claim ceiling?

## Review outcomes

The page must route every intake to one explicit outcome:

- `return-unopened-or-corrupt`
- `structurally-valid-but-wrong-question`
- `structurally-valid-but-wrong-world`
- `question-matched-but-insufficient`
- `bounded-decision-grade`
- `decision-grade-with-reservations`
- `supplement-required-before-action`
- `supplement-not-worth-burden`

Hard rule:

`useful` is not an allowed outcome.
The page must say whether the packet is sufficient for action, sufficient only for bounded reasoning, or insufficient.

## Review layout

1. **Packet-open review**
2. **Structural-validation review**
3. **Question-fit review**
4. **Window-fitness review**
5. **Sufficiency-grade review**
6. **Supplement-decision review**
7. **Claim-ceiling review**

### 1) Packet-open review

Answer:

- did the packet open
- did it open fully or partially
- were any files unreadable
- did integrity or corruption warnings appear

Hard rule:

A packet that never opened cannot proceed to fit grading.

### 2) Structural-validation review

Answer:

- does the packet contain the promised artifact classes
- are filenames, metadata, or timestamps coherent
- does the redaction class match the declared packet form
- do attached artifacts belong to the same source world or mixed worlds

Hard rule:

Undeclared mixed-world packets must receive an explicit validation penalty.

### 3) Question-fit review

Compare:

- live target question
- supplied packet classes
- supplied subject identifiers
- live doctrine or case route
- expected artifact family for that question

Hard rule:

A packet gathered for generic support cannot silently become decision-grade for a narrower later claim without re-fit review.

### 4) Window-fitness review

Publish:

- event-to-capture lag
- repro-to-capture lag
- log rotation or truncation exposure
- stale-version exposure
- whether the relevant period is directly covered, inferred, or missing

Hard rule:

Inferred window fitness must remain weaker than directly covered window fitness.

### 5) Sufficiency-grade review

Supported `sufficiency_grade` values:

- `none`
- `context-only`
- `diagnostically-suggestive`
- `bounded-decision-grade`
- `decision-grade-with-reservations`
- `decision-grade`

Hard rule:

High effort cannot force a high grade.
A heavy packet may still grade `context-only` if it missed the decisive window or scope.

### 6) Supplement-decision review

The page must rank supplements by:

- discriminator value
- burden
- time sensitivity
- privacy or exposure cost
- probability of actually changing the verdict

Supported `supplement_decision` values:

- `ask-now-minimal`
- `ask-now-heavier`
- `defer-until-route-stabilizes`
- `do-not-ask-cost-exceeds-value`
- `cannot-ask-channel-unavailable`

Hard rule:

The first supplement request must be the cheapest one that could materially raise the sufficiency grade.

### 7) Claim-ceiling review

The page must end by publishing three sentences:

- **safe sentence now**
- **stronger sentence available if supplement lands**
- **strongest sentence forever blocked if no supplement ever lands**

Hard rule:

No review may end without a permanent fallback sentence.
Packets sometimes age out before supplements arrive.
