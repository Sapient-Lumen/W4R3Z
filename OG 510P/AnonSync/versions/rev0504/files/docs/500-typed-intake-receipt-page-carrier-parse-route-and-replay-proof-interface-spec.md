# Typed intake receipt page: carrier, parse, route, and replay proof interface spec

## Purpose

After imported material has been typed and routed, the product still needs one durable proof object that answers:

> what exactly did we receive, what did we believe it was, which reviewed route did we follow, and what did we intentionally *not* prove?

This page turns that proof into an ordinary shareable surface.

## Core decision

Every typed intake event must emit one first-class **Typed intake receipt**.
That receipt is distinct from deeper join/claim/custody receipts.

It preserves the intake truth:

- carrier
- parse result
- family verdict
- route chosen
- onward reviewed page
- secrecy boundary
- replay / re-open behavior

## Primary page layout

The page always renders the same top-level regions in the same order:

1. intake summary strip
2. parse and family card
3. route and onward-review card
4. secrecy and replay card
5. related deeper receipts
6. export / share card

### 1) Intake summary strip

Show:

- intake time
- intake carrier
- family verdict
- final route taken or stop result
- one-line summary

Examples:

- `Pasted text typed as encrypted-custody artifact · routed to Encrypted custody setup`
- `Browser-open wrapper typed as subject-claim artifact · routed to Claim lane`
- `Scanned code typed as ambiguous artifact · stopped before commitment`

### 2) Parse and family card

Show:

- parse confidence
- competing families considered
- strongest evidence for the chosen family
- strongest unresolved ambiguity
- whether raw secret material is suppressed

The operator should be able to answer: **what did the product think it saw?**

### 3) Route and onward-review card

Show:

- route chosen
- onward page opened
- whether live commitment happened later or not
- links to the resulting deeper receipts when they exist

The operator should be able to answer: **where did this intake event lead?**

### 4) Secrecy and replay card

Show:

- whether the receipt contains redacted or hashed identifiers only
- whether the original artifact can be safely re-opened or must be re-issued
- whether replay would preserve the same route semantics
- what was intentionally excluded from the receipt

Rules:

- the receipt must not become a disguised bearer artifact
- support/share export must preserve route truth without exporting live secrets
- replay-safety must be explicit rather than implied

### 5) Related deeper receipts

Show links to resulting deeper receipts such as:

- identity-join receipt
- claim-lane receipt
- encrypted-custody commitment receipt
- stop-without-commitment note

This keeps intake truth adjacent to later commitment truth.

### 6) Export / share card

Allowed exports:

- `Support-safe summary`
- `Operator handoff summary`
- `Local full receipt`
- `Clear exported copy`

Each export must state:

- audience
- redaction level
- whether it is safe to circulate outside the current trust boundary

## Acceptance criteria

This spec is satisfied when:

- typed intake leaves a durable receipt even without commitment
- the receipt preserves route truth without preserving live bearer secrets
- later commitment receipts can be reached from intake receipts
- support and handoff exports do not require screenshots or memory to reconstruct the intake event
