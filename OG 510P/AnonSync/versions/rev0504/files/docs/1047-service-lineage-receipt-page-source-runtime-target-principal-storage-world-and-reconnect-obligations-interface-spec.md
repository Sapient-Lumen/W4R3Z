# Service lineage receipt page — source runtime, target principal, storage world, and reconnect obligations

## Purpose

Preserve the durable truth about a service cutover so later operators do not have to reconstruct it from memory or troubleshooting history.

This page exists to answer:

- `what runtime was cut over into what service seat?`
- `which principal and storage world won?`
- `was continuity preserved, partially preserved, or intentionally branched?`
- `what observation and exposure changes survived the cutover?`
- `what reconnect or re-share obligations remain open?`

## Receipt fields

Must show:

- receipt id
- source runtime class and principal
- target runtime class and principal
- reviewed intent
- final continuity verdict
- source storage root
- target storage root
- roster carry-forward verdict
- observation-grade delta
- control-audience verdict
- reconnect obligations
- stronger rejected sentence
- created-at time

## Narrative summary

The receipt must generate one ordinary-language summary such as:

- `Interactive current-user seat was promoted into current-user service with reviewed roster carry-forward and no reconnect obligations.`
- `Interactive current-user seat was replaced by a Local System service that opened a different storage world; old subjects require reviewed reconnect.`
- `Operator intentionally created a clean service branch; no carry-forward was expected.`

## Evidence attachments

Must preserve references to:

- service promotion contract sheet
- principal switch review
- service world preview
- service cutover proof
- any reconnect reviews opened as a result

## Reopen triggers

Must show what later events invalidate the receipt as a current operational guide, including:

- principal changed again
- service storage root changed
- config-mode authority changed
- listener posture changed materially
- reconnect obligations completed or superseded

## Guardrails

- Never let the receipt collapse `different storage world` into a generic success message.
- Never drop reconnect obligations once they were part of the cutover verdict.
- Never let later browser access overwrite the original audience verdict.
- Never lose the blocked stronger sentence that was rejected at cutover time.

## Output

A durable service-lineage receipt that keeps principal, storage world, cutover verdict, and remaining repair obligations attached to one ordinary artifact.
