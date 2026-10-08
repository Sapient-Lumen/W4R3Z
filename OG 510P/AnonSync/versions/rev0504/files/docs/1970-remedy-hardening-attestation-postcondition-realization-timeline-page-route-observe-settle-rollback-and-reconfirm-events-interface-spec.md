# Remedy-hardening-attestation postcondition-realization timeline page — route, observe, settle, rollback, and reconfirm events

## Purpose

This page is the ordered event view for realization questions after executable mandate review is established.
It exists so later operators can see whether the case moved from a routed mandate into an actually realized target state, or whether placeholders, contradictory observations, rollback hazards, or open settlement windows kept the stronger sentence blocked.

## Event classes

The timeline must support at least these events:

- executable mandate imported as realization candidate
- target postcondition defined
- first route execution witnessed
- first outcome observation recorded
- route-local-only observation recorded
- beneficiary-usable observation recorded
- named-slice realization confirmed
- placeholder-only observation flagged
- contrary observation recorded
- rollback hazard raised
- settlement window opened
- rollback or displacement occurred
- re-execution or restore ordered
- settlement window cleared
- governed-slice realization confirmed
- broader stronger sentence blocked
- postcondition superseded or withdrawn

## Required columns

- timestamp
- event class
- source evidence or observation reference
- resulting postcondition-realization class
- stronger realization sentence newly allowed or newly blocked

## Hard rules

The timeline must never collapse:

- route execution and first outcome observation into one event by default
- first observation and named-slice realization into one event by default
- named-slice realization and governed-slice realization into one event by default
- contrary observation and rollback into one event by default
- settlement-window opening and settlement completion into one event by default
