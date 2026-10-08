# Companion-case receipt page — public post, private packet, and continuation boundary interface spec

## Purpose

Leave one durable record of how the case was split across audiences and what now exists.
This page should answer:

- whether a public summary was posted, drafted, or withheld
- whether a private packet was sent, saved, or withheld
- how the artifacts were linked
- what audience each artifact was shaped for
- what continuation or reopen boundary now applies

This page exists so `forum post plus logs sent` becomes a typed receipt instead of folklore and pasted references.

## Inputs

- companion-case object
- public-summary review outcome
- private-companion-linkage outcome
- delivery states for both artifacts if any
- continuation expectations
- reopen / stale triggers

## Layout

### A. Receipt strip

Fields:

- companion receipt id
- incident headline
- companion state
- public artifact state
- private artifact state
- linkage state

### B. Artifact summary card

Show rows for public summary and private packet with:

- audience class
- purpose
- package/statement shape
- delivery state
- strongest safe sentence

### C. Linkage and withholding card

Show:

- companion reference basis
- what was intentionally withheld from the broader audience
- whether the link is strong, provisional, or missing
- whether the case can be continued coherently later

### D. Continuation card

Show:

- next expected lane and actor
- what a public follow-up may safely say
- what a private follow-up may safely assume
- whether the companion set is complete or still missing one side

### E. Reopen boundary card

Show conditions such as:

- public summary needs stronger redaction
- private packet needs splitting or narrowing
- a new audience joins the case
- the public artifact and private packet drift apart
- a recipient redirects the operator to a different lane
- the case collapses back to private-only or local-only

## Required interactions

- `Copy companion receipt summary`
- `Open companion case`
- `Open public summary review`
- `Open private companion linkage`
- `Reopen audience split`
- `Create successor companion packet`

## Guardrails

- Never merge public and private delivery into one flat `sent` state.
- Never omit the audience class for each artifact.
- Never lose the record of withheld details.
- Never equate linkage proof with diagnostic proof.
- Never let later edits silently rewrite this receipt without chronology.

## Output

A durable companion-case receipt that preserves public/private artifact state, linkage basis, withheld-detail boundary, continuation expectations, and reopen conditions.

