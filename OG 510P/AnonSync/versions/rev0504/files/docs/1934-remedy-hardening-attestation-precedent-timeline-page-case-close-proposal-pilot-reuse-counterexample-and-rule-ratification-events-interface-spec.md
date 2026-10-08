# Remedy-hardening-attestation precedent timeline page — case close, proposal, pilot reuse, counterexample, and rule-ratification events

## Purpose

This page is the ordered event view for portability claims after closure.
It exists so later operators can see whether the case moved from case-specific settlement to named-class portability, pilot reuse, ratification, narrowing, sunset, or revocation in the right order.

## Event classes

The timeline must support at least these events:

- source case reached closure-safe state
- portability proposal opened
- target class defined or narrowed
- required invariant added
- similarity match proven
- pilot reuse approved
- pilot reuse executed
- pilot reuse succeeded
- pilot reuse failed
- counterexample opened
- policy ratified
- policy narrowed
- sunset scheduled
- review overdue flagged
- precedent revoked or superseded

## Required columns

- timestamp
- event class
- target class or policy scope
- source evidence reference
- resulting precedent-portability class
- stronger sentence newly allowed or newly blocked

## Hard rules

The timeline must never collapse:

- source-case closure and portability approval into one event by default
- one pilot reuse and policy ratification into one event by default
- narrowing after counterexample into silent metadata change
- sunset or review-overdue into an invisible passive state
