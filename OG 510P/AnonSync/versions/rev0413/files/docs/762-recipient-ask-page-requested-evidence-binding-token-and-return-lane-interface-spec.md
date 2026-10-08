# Recipient ask page — requested evidence, binding token, and return lane interface spec

## Purpose

Give the operator one durable page that answers:

- who asked for more information or artifacts
- what exact material the recipient is asking for
- what existing case, ticket, thread, or companion object the answer must bind to
- what lane the answer is expected to use
- whether the ask is currently satisfiable from the present machine and surface

This page exists so `reply to the ticket`, `include the ticket number`, `mention the forum link`, and `ask for a bigger upload link` become typed product truth instead of memory work.

## Inputs

- incident identifier
- escalation lane and companion-case state if any
- imported reply or recipient message that created the ask
- requested artifact families and explanatory fields
- known binding token candidates (`ticket-id`, `thread-url`, `portal-request-id`, `none`)
- lane constraints (`reply-chain`, `portal-upload`, `new-private-packet`, `public-follow-up`, `local-only-hold`)
- size, format, and privacy constraints
- current evidence manifest candidates

## Primary questions this page must answer

1. Who is asking, in what audience lane, and with what authority ceiling?
2. What exact artifacts or explanations were requested?
3. What binding token or reply chain must carry the answer back?
4. What return lane is expected or allowed?
5. Is the ask currently satisfiable, partially satisfiable, blocked, or ambiguous?

## Layout

### A. Ask strip

Fields:

- incident headline
- ask state (`new`, `in-review`, `satisfiable`, `partial`, `blocked`, `fulfilled`, `superseded`)
- requester / lane
- urgency posture
- binding confidence

### B. Request clauses card

Show one row per requested clause:

- artifact or explanation requested
- target participant or scope
- privacy class
- optional vs required
- current candidate coverage

### C. Binding card

Show:

- binding token type (`ticket-id`, `forum-thread`, `portal-request`, `companion-id`, `none-yet`)
- concrete token value or `missing`
- whether the binding is system-derived, imported, or operator-entered
- contradiction warnings

### D. Return lane card

Show:

- expected return lane
- allowed alternate lanes
- reply-chain requirement
- size or attachment constraints known so far
- whether preliminary lane work is needed first

### E. Satisfaction card

Show:

- strongest supported satisfaction verdict now
- clauses already coverable from current evidence
- clauses requiring new capture or new participant returns
- clauses blocked by privacy, format, or lane limits

## Required interactions

- `Normalize ask from imported reply`
- `Mark clause required or optional`
- `Open ask fulfillment review`
- `Open return lane review`
- `Bind to ticket / thread / companion`
- `Issue ask receipt`
- `Mark as superseded`

## Guardrails

- Never flatten a recipient ask into a generic `needs more info` label.
- Never show `ready to reply` without naming the binding token and return lane.
- Never treat `send something` as satisfying the ask unless clause coverage is explicit.
- Never hide extra-disclosure risk once the ask is narrower than the candidate packet.
- Never let a missing or ambiguous binding token disappear behind a green send button.

## Output

A reviewed recipient-ask object that preserves requester lane, requested clauses, binding token, return-lane expectation, and current satisfaction posture.
