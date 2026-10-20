# ADR 0007: Authorization is independent of Tox friendship

**Status:** accepted for rev0002

## Context

Tox authenticates a transport peer by key. It does not express IoT device ownership, roles, action capabilities, delegation, ownership epochs, or revocation policy.

A recall-root-derived controller also should not need to use the high-value root directly for every daily operation.

## Decision

Every device maintains an application-level authorization ledger independent of its Tox friend list.

The ledger will represent owner roots, delegated controller keys, roles, capability grants, expiry, ownership epochs, and revocations. IoTox protocol messages that affect device state will be authorized against this ledger even when they arrive over an authenticated Tox session.

## Consequences

- A Tox friend is not automatically an owner or operator.
- Transport identities can rotate without silently changing authorization.
- The recall root can authorize delegated daily-use keys.
- Compromised controllers can be revoked without changing every transport relationship.
- Ledger persistence, signatures, rollback resistance, and transition formats remain critical implementation work.
