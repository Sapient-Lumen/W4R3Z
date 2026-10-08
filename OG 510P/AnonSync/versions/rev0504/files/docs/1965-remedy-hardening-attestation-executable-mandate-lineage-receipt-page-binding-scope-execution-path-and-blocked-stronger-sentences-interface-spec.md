# Remedy-hardening-attestation executable-mandate lineage receipt page — binding scope, execution path, and blocked stronger sentences

## Purpose

This page is the durable one-receipt summary for mandate executability after verdict legitimacy review.
It lets a later operator read one artifact and know exactly whether the legitimate verdict remained advisory, became binding, entered a specific execution route, stalled into fallback, or completed only for a named slice while stronger execution-complete language stayed blocked.

## Receipt fields

- receipt identifier
- executable-mandate identifier
- source verdict-legitimacy receipt identifier
- governing verdict sentence
- mandate issuer summary
- binding-scope summary
- obligated actor summary
- action and deadline summary
- primary actuator summary
- fallback summary
- current executable-mandate class
- highest honest execution sentence
- blocked stronger sentence
- evidence references
- issued-at timestamp

## Primary sentence block

The receipt must begin with exactly two lines:

- **Highest honest executable-mandate sentence**
- **Blocked stronger sentence**

## Required sections

1. **Why this verdict is or is not binding here**
2. **Who is obligated to act and by when**
3. **Which execution route, manual steps, and prerequisites govern**
4. **Whether fallback, partial execution, or world-scope limits still matter**
5. **Why the next stronger execution sentence is blocked**

## Hard rules

The receipt must never let:

- `legitimate verdict exists` impersonate `real mandate exists`
- `permission changed somewhere` impersonate `the bound actors executed`
- `automatic linked-device behavior` impersonate `all required topologies are handled`
- `one restarted or reconnected world` impersonate `all relevant worlds executed`
- `one slice completed` impersonate `broader execution complete`
