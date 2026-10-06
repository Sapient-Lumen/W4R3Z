# ADR-0008: Deny network during build by default

Status: Accepted

## Context

Network during builds creates supply-chain risk:
- undeclared inputs
- non-determinism
- data exfiltration

DeriveBSD also assumes builders may be compromised.

## Decision

Build sandboxes (jail/microVM builders) default to **no network access**.

- Fetching is a separate phase governed by the Lock.
- Any exception must be explicit in Plan and policy-approved.

## Consequences

- Better reproducibility.
- Easier auditing: network access becomes a reviewable capability.
