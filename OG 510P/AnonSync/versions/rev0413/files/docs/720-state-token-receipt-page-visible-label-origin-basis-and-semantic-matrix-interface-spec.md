# State token receipt page: visible label, origin basis, and semantic matrix interface spec

## Purpose

Preserve the state-word truth that was actually in force when a label was applied, reused, or reviewed.

The receipt answers:

> what visible token did the product show, what origin gave it meaning, what matrix was actually active, and what stronger sentence was intentionally avoided?

## Receipt fields

Every state-token receipt must preserve at least:

1. target scope
2. visible token shown
3. origin kind
4. full signal matrix snapshot
5. exceptions still alive under the token
6. evidence strength
7. semantic-stability verdict
8. strongest safe sentence used in UI
9. stronger forbidden sentence
10. review origin (`manual action`, `scheduler`, `policy import`, `incident overlay`, `wording repair`)
11. timestamp and actor

## Example safe sentences

- `At commit time Paused meant transfer work was blocked, but deletes and indexing were still allowed.`
- `At commit time the same Paused label had a scheduled-origin exception that still allowed outbound serving.`
- `At commit time the product qualified the label because the token was semantically unstable across origins.`

## Required comparisons

A receipt must let the operator compare later against:

- current token now
- token at receipt time
- current matrix now
- matrix at receipt time
- whether wording became more or less honest since then

## Data model

- `state_token_receipt_id`
- `target_ref`
- `visible_token`
- `origin_kind`
- `matrix_snapshot`
- `exceptions[]`
- `evidence_strength`
- `semantic_stability_verdict`
- `safe_sentence`
- `forbidden_sentence`
- `review_origin`
- `actor_ref`
- `recorded_at`

## Failure this page prevents

Without this receipt, operators later only remember that something was `Paused`, and lose the more honest record that the active origin still allowed deletes, indexing, or some outbound lane.

AnonSync should keep named-state truth durable enough to survive later folklore.
