# Ask fulfillment receipt page — request version, return proof, and reopen boundary interface spec

## Purpose

Leave a durable receipt proving what recipient ask was answered, how it was answered, and what still remains open.

## Inputs

- recipient ask object
- ask fulfillment review
- return lane review
- actual returned packet or export reference
- actual binding token used
- send / upload / draft state

## Primary questions this page must answer

1. Which ask version or clause set did this return answer?
2. Which reviewed members actually traveled?
3. What binding token or reply chain tied the return to the case?
4. What clauses remain open, partial, blocked, or superseded?
5. When should the operator reopen this ask rather than trust the receipt as closure?

## Sections

### 1. Ask answered

Show:

- ask identifier and version
- requester / lane
- clause count and required-count
- satisfaction class (`complete`, `partial`, `blocked`, `redirected`, `draft-only`)

### 2. Returned members

Show:

- packet / manifest version
- members actually included
- members intentionally excluded
- extra-disclosure verdict

### 3. Binding proof

Show:

- binding token type and value
- reply-chain or portal proof
- companion-case reference if any

### 4. Residual gaps

Show:

- unsatisfied clauses
- missing follow-up preparation
- stronger forbidden closure sentence

### 5. Reopen boundary

Show clear triggers such as:

- recipient says artifact missing or unreadable
- size/format lane rejects the return
- a new ask version supersedes this one
- current return covered only a partial clause set

## Guardrails

- Never let this receipt read like case closure if it only proves one follow-up return.
- Never omit the ask version.
- Never omit intentionally excluded members once narrowing was part of the review.
- Never treat `draft saved` as `returned`.

## Output

A durable ask-fulfillment receipt preserving ask version, reviewed members, binding proof, residual gaps, and reopen boundary.
