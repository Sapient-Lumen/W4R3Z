# Runtime stop lineage receipt page: stop scope, proof rung, and re-entry posture

This page exists so later operators do not have to guess whether `closed`, `quit`, `exit`, `stop service`, or `disabled startup` were ever actually achieved.
It is the durable receipt for runtime stop and later restart claims.

## Operator question

> What stop was requested, what proof did we actually reach, what residual or restart posture remained, and what stronger sentence was blocked at the time?

## When this page must appear

Render after every serious stop-adjacent event, including:

- quit / exit / stop confirmations
- service stop reviews
- startup disable / enable changes
- restart provenance events that reopen a prior stop story

## Required receipt fields

### Identity and scope

- receipt id
- subject / runtime id
- host platform
- runtime class
- projection class at time of receipt
- requested stop scope
- resulting stop scope

### Proof reached

- strongest-safe proof rung reached
- joined evidence sources used
- freshness window
- strongest blocked sentence

### Residuals and re-entry posture

- residual work classes still present or unknown
- service-manager state
- startup / boot re-entry state
- whether future automatic return was still armed

### Restart lineage

- previous stop receipt id if this receipt reopens an older stop story
- re-entry trigger if applicable
- continuity class if restart occurred
- chronology-risk verdict if restart followed offline edits or re-indexing

## Receipt headline examples

- `Projection closed only · runtime still eligible to continue · startup unchanged`
- `Runtime exit acknowledged · stable stop not yet proven · service supervisor still armed`
- `Service stopped · future boot re-entry disabled · no-further-publication not yet proven`
- `Runtime returned via startup policy · reopen review required · chronology risk present`

## Detail sections

1. **What was asked**
2. **What was actually proven**
3. **What could still continue or return**
4. **Why a stronger sentence was blocked**
5. **What later event reopened the story**

## What this receipt must preserve

It must preserve enough truth that a later operator can answer all of the following without re-reading support lore:

- was the action only about the visible surface or the runtime itself?
- did service or boot policy remain armed?
- what exact proof rung was reached?
- did a later restart come from human action, supervisor action, or boot policy?
- what chronology-risk sentence was still blocked?

## What this page must never imply

It must never imply that these are the same:

- existence of a stop receipt and proof of stable stop
- disabled projection and disabled runtime
- absent runtime now and impossible future re-entry
- restart receipt and harmless continuity

## CLI projection expectation

A headless projection such as `anonsync receipts show <id>` must print the same scope, proof, residual, and restart fields in stable order.
