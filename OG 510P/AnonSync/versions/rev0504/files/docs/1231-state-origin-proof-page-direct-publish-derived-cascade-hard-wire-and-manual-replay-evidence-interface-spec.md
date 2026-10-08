# State-origin proof page — direct publish, derived cascade, hard-wire, and manual replay evidence

## Purpose

Give the operator one explicit proof surface for the sentence `this is where the current state came from`.
The page must distinguish between proof of a **result** and proof of an **origin**.

## Operator question

> What evidence supports the claim that this state came from a direct publish, a derived cascade, a hard-wired seat rule, a manual replay, or only a detection-induction act?

## Fixed page order

1. **Claim under test**
2. **Evidence families**
3. **Proof ladder**
4. **Proof gaps and weaker surviving sentences**

## 1) Claim under test

The page must render exactly one claim under test, such as:

- `direct remote publish caused current bytes`
- `automatic source-heal caused current bytes`
- `parent-source cascade caused current posture`
- `encrypted hard-wire caused current delete-follow behavior`
- `manual archive replay caused current bytes`
- `touch / mtime induction caused current notice without proving new content`

## 2) Evidence families

For the claim under test, show evidence families separately:

- **seat-posture evidence**
- **role / derivation evidence**
- **manual-act evidence**
- **timeline evidence**
- **content / name consequence evidence**
- **current runtime-witness evidence**

No family may be silently omitted when relevant.

## 3) Proof ladder

Render one proof ladder with classes:

- **documented by standing posture only**
- **posture plus matching consequence**
- **manual act plus matching consequence**
- **derived-source linkage plus matching consequence**
- **runtime witness with no strong contradiction**
- **origin proven strongly enough for durable receipt**

The operator must be able to answer: **how strong is the origin proof, not just the visible result?**

## 4) Proof gaps and weaker surviving sentences

Show:

- what still prevents a stronger sentence
- which weaker sentence still survives
- what later event should reopen the proof

Examples of weaker surviving sentences:

- `result matches source-heal posture`
- `notice refreshed after touch`
- `manual replay occurred, but shared convergence is not yet proven`
- `derived-source cascade is the strongest current explanation`

## What this page must never imply

It must never imply that these are the same:

- result parity and origin proof
- posture existence and action occurrence
- manual replay and successful topology-wide republish
- mtime induction and authored content
- hard-wired seat behavior and named human action

## Public objects

### `state_origin_claim`

Fields:

- `state_origin_claim_id`
- `target_ref`
- `claim_class`
- `current_result_class`
- `proof_grade`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `updated_at`

### `state_origin_evidence_bundle`

Fields:

- `state_origin_evidence_bundle_id`
- `claim_ref`
- `seat_posture_evidence[]`
- `derivation_evidence[]`
- `manual_act_evidence[]`
- `timeline_evidence[]`
- `runtime_witness_evidence[]`
- `contradictions[]`
- `generated_at`

## CLI shape

```text
anonsync provenance show <subject>
anonsync provenance explain <subject> --claim auto-heal
anonsync provenance receipt <receipt>
```
