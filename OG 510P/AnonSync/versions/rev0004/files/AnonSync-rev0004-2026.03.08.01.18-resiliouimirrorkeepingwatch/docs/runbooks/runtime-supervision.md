# Runtime Supervision Runbook

## Purpose

Capture the initial expectations for supervising bundled tor and bundled `i2pd` child processes.

## Assumptions

- the user does not manually operate either runtime
- the application generates and owns runtime config
- loopback-only control surfaces are preferred
- failure reporting should be product-friendly, not router-jargon-heavy

## First design checkpoints

1. define where generated runtime config lives
2. define child-process startup ordering
3. define readiness checks for tor and `i2pd`
4. define restart / backoff policy
5. define shutdown and cleanup behavior
6. define log capture and redaction policy
7. define update and version pinning rules

## Current likely shape

- start bundled tor child process
- start bundled `i2pd` child process when policy enables I2P
- verify reachability of required loopback endpoints
- expose only high-level health states to the user

## Non-goal

Do not turn this runbook into a human operator guide for manually managing Tor or I2P.
