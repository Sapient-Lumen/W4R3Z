# Remedy-hardening-attestation durable-closure timeline page — close, latent survivor, reappear, reopen, renarrow, and redurable events

## Purpose

This page makes durable closure legible over time.
It exists so the archive can show not only when closure was declared, but also what later rediscovery did to that claim.

## Timeline events the page must support

The page must support at least:

- closure verdict issued
- durable-closure claim issued
- rediscovery surface enumerated
- latent survivor explicitly tolerated
- late survivor rediscovered
- hidden archive opened
- disconnected folder reconnected
- placeholder refetch initiated
- forwarded artifact reported
- closure verdict reopened
- sentence narrowed after rediscovery
- re-cleanup attempted
- durable closure re-established

## Event requirements

Each event row must preserve:

- timestamp or bounded time window
- actor / audience slice / surface
- event class
- affected survivor class
- whether the event strengthened, narrowed, contradicted, or reopened the durable-closure claim
- whether the strongest honest sentence changed

## Durable-closure rule

The timeline must not allow `durable closure established` unless it also records:

- the base closure verdict it relies on
- the rediscovery surfaces considered
- the invalidators that would reopen the claim
- the latest event that would still keep the durable sentence honest
- the stronger sentence still blocked anyway

## Visual emphasis

The page should visually distinguish:

- base closure events
- latent-survivor inventory events
- rediscovery events
- reopen / renarrow events
- re-cleanup events
- re-established durable-closure events
