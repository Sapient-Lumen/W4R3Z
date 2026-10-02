# ADR 0113: supervise auxiliary routes in process without duplicating authority

Status: accepted

Date: 2026-08-21

## Decision

The first product route workers are independent in-process `ToxTransport` instances under one
`WorkerSupervisor`. Each transport retains its own toxcore owner thread and savedata, while the
parent Agent remains the sole owner of the stable device signer, authority ledger, coordinator,
synchronization roots, and effects.

Activation is explicit through `--enable-route-workers` and a strict private key-named state root.
Each loaded identity is checked against its signed member key before network activity. The initial
worker profile permits exactly one Tox friend so session evidence cannot be attached to an
implicitly selected peer. Constructed workers drive only the canonical application handshake and
enter `connecting`; route-binding verification is still required for authentication and readiness.

## Consequences

Independent toxcore scheduling and congestion domains now exist inside the product binary without
forking authority state or introducing a child-process secret protocol. The worker surface can be
tested with the existing provider double and later in Sandwurm using genuine savedata.

One process failure can still affect all routes, so this is not process-fault isolation. The exact
single-peer restriction is intentionally narrow and must be replaced by an authenticated remote
route association before multi-peer auxiliary profiles are permitted. No bulk scheduler may consume
these workers while their coordinator state remains `connecting`.
