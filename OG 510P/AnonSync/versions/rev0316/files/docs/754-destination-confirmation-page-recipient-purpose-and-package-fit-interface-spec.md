# Destination confirmation page — recipient, purpose, and package-fit interface spec

## Purpose

Confirm the exact destination semantics of the outbound handoff.
This page should answer:

- who or what class of recipient this package is going to
- why that destination is the right audience for this question
- what that audience will see
- whether the package shape matches the destination
- what follow-up the operator should or should not expect

This page exists so a lane choice becomes a real destination contract rather than a vague transport gesture.

## Inputs

- escalation review outcome
- chosen lane
- incident question summary
- evidence manifest or summary package
- privacy/redaction findings
- destination metadata if known (`forum-thread`, `support-request`, `billing-form`, `peer-recipient`, `local-save`, `other`)
- response expectation ceiling

## Primary questions this page must answer

1. What exact recipient class is this going to?
2. What is the purpose of this package at that destination?
3. Is the package appropriately shaped for that audience?
4. What visibility/privacy posture follows?
5. What future reply or redirect should the operator realistically expect?

## Layout

### A. Destination strip

Fields:

- chosen lane
- destination class
- audience visibility
- package shape
- expectation posture

### B. Recipient and purpose card

Show:

- recipient class
- why this audience is relevant
- what the package is meant to accomplish there (`ask`, `submit evidence`, `request billing help`, `share with peer`, `save for later`)
- what the destination is *not* being asked to do

### C. Package-fit card

Show:

- current package type (`summary`, `summary + manifest`, `sanitized artifact set`, `full private package`, `local-only bundle`)
- reasons this package fits or mismatches the destination
- members or details that should be removed, split, or retained
- strongest safe sentence about what the recipient will receive

### D. Visibility and privacy card

Examples:

- visible to public/community readers
- visible to private vendor recipient
- visible to billing/licensing desk only
- visible to peer recipient
- retained only on local machine

Also show:

- sensitive members still present
- whether summary-only is safer
- whether a successor private package may still be needed

### E. Follow-up expectation card

Show:

- response expectation (`none-promised`, `best-effort`, `priority-likely`, `peer-dependent`, `local-only`)
- what silence would mean
- what redirect or re-export trigger would reopen lane review

## Required interactions

- `Confirm destination`
- `Back to escalation review`
- `Narrow to summary`
- `Split package`
- `Keep local only`
- `Issue escalation lane receipt`

## Guardrails

- Never allow `recipient unknown` to masquerade as a confident destination.
- Never hide public/community visibility behind a generic `share` verb.
- Never imply that destination confirmation proves package sufficiency.
- Never let a sensitive package move to a broader audience without an explicit warning.
- Never promise a reply where the lane only supports best-effort or undefined response.

## Output

A reviewed destination-confirmation object that preserves recipient class, package purpose, audience visibility, package fit, and follow-up expectation before export.
