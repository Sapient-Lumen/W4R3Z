# ADR 0222: Pin synchronization pulls to a constructed route class

Status: accepted owner-local prerequisite, 2026-08-28.

## Context

Per-job failover intent prevents an established private carrier from falling back after loss, but it
does not constrain initial placement. Fixed/adaptive selection could still choose a native worker,
and absence of every auxiliary worker previously meant ordinary primary-carrier fallback.

The current signed route set authenticates member key, role, TCP/UDP connection class, work budget,
restart budget, and expiry. It does not authenticate the deployment-local worker network override
(`tox/native`, `tox/tor`, or laboratory `tox/i2p-construction`). This decision must therefore remain
an owner-local enforcement fact rather than a signed remote claim.

## Decision

- Add frozen per-pull route classes `any`, `tox/native`, `tox/tor`, and
  `tox/i2p-construction`.
- Retain each candidate's actual `WorkerSessionSnapshot.network`, which comes from the exact
  constructed worker context. Filter both initial selection and mandatory replacement by the
  pull's frozen class.
- `any` preserves compatibility, including primary-carrier fallback when no auxiliary route is
  ready. Every named class requires an authenticated auxiliary worker of that exact class. If none
  is ready when a HEAD result arrives, leave the HEAD request live for an explicit retry and send no
  object request through primary.
- Reject same-epoch retries that conflict with either frozen failover or route-class intent.
- Add local-control v1.39 operation 86 with payload
  `route-class-byte || failover-byte || friend-u32 || namespace[1..64]` and extend the CLI to:

  ```text
  iotox sync-pull FRIEND NAMESPACE \
    [available|fail-closed [any|tox/native|tox/tor|tox/i2p-construction]]
  ```

- Render `route-class=...` on each job line. The actual-I2P payload guest now explicitly requests
  `fail-closed tox/i2p-construction`.

The selector test uses simultaneous native, Tor, and I2P-construction candidates and proves exact
class choice. The existing full-Agent first-byte-loss test now uses operation 86 and requires
`route-class=tox/native` while continuing to prove opposite-default per-job failover behavior.

## Consequences

- The accepted actual-I2P payload gate no longer depends on route-key ordering for initial
  placement, and a future loss test cannot reassign that job onto a native or Tor worker.
- This is a real local enforcement boundary, but not signed route-class intent. Closing the latter
  requires a new signed inventory generation or another stable-device-signed artifact that binds
  each member key to a route class without disclosing deployment endpoints.
- No IoTox peer frame or sync-wire-v1 byte changes are made.
