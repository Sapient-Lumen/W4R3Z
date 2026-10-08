# ADR 0043 — Wire churn before live SAM

## Decision

The cube will keep building deterministic wire/churn transcript fixtures before live I2P/SAM transport.

## Rationale

Live I2P will add noise. The disagreement algebra should be testable offline: false providers, drops, invalid wire, refusals, delay, and path-family capture.

## Consequence

The current wire envelope is a transcript fixture, not a final RPC protocol.
