# State token change review page: origin switch, semantic delta, and hidden-lane risk interface spec

## Purpose

Review any change where a visible state token is being introduced, reused, or reassigned across origins.
The page answers:

> if I commit this token or switch this subject into this origin, will the visible word still mean the same thing, and which hidden lanes stay alive afterward?

## Review triggers

Open this page when any of the following happen:

- applying manual pause to a subject that can also be scheduler-paused
- enabling a scheduler rule that reuses an existing visible token
- introducing a new incident or inherited posture that reuses a familiar word
- changing a label while leaving the matrix unchanged
- changing the matrix while keeping the same label
- importing a state vocabulary from another product/runtime

## Required sections

### 1) Token delta

Show current vs proposed:

- current visible token
- proposed visible token
- current origin
- proposed origin
- whether the visible word stays the same or changes
- whether the effective matrix stays the same or changes

### 2) Semantic delta table

Always render current vs proposed for:

| Signal | Current | Proposed |
| --- | --- | --- |
| Outbound bytes | allowed/blocked/limited | allowed/blocked/limited |
| Inbound bytes | allowed/blocked/limited | allowed/blocked/limited |
| Deletes | allowed/blocked/reviewed | allowed/blocked/reviewed |
| Indexing | allowed/blocked/limited | allowed/blocked/limited |
| Discovery | allowed/blocked/limited | allowed/blocked/limited |

If the token stays the same while any row changes, the review must mark the token as semantically unstable.

### 3) Hidden-lane examples

Show concrete examples, not abstract warnings:

- `Delete a file while token remains Paused`
- `Create new files while token remains Paused`
- `Peer requests outbound bytes while this token is active`
- `Switch from manual to scheduled pause while keeping same visible label`

For each example, show expected result and confidence.

### 4) Safer alternatives

Offer explicit replacements such as:

- `Paused (transfers only)`
- `Paused (outbound serving allowed)`
- `Freeze bytes and deletes`
- `Bandwidth-limited`
- `Indexing only`

### 5) Commit actions

- `Commit token and matrix`
- `Commit with qualified label`
- `Keep current label and matrix`
- `Block until wording is split`

## Receipt obligations

A commit from this page must later preserve:

- visible token before and after
- origin before and after
- semantic delta table
- examples shown
- strongest safe sentence after commit

## Data model

- `state_token_change_review_id`
- `target_ref`
- `current_token`
- `proposed_token`
- `current_origin`
- `proposed_origin`
- `current_matrix`
- `proposed_matrix`
- `semantic_stability_verdict`
- `example_forecasts[]`
- `safer_alternative[]`
- `receipt_ref`

## Failure this page prevents

Without this review, the product silently reuses a familiar label across different origins and lets the operator discover the semantic delta only after a delete, upload, or index advance slips through.

AnonSync should make the label-vs-matrix delta explicit before commit.
