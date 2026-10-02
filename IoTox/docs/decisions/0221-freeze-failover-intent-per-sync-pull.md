# ADR 0221: Freeze failover intent per synchronization pull

Status: accepted and full-Agent qualified, 2026-08-28.

## Context

ADR 0220 made replacement permission explicit but process-wide. That was enough to prove the
fail-closed mechanism, not enough to safely mix ordinary availability-oriented pulls with
privacy-sensitive pulls in one Agent. A retry could also be interpreted under a different daemon
configuration than the request that created the job.

This is still not a signed remote privacy grammar. Route network class is deployment-local and is
not present in the stable-device-signed route-set member record. Pretending otherwise would turn an
operator preference into false protocol evidence.

## Decision

- Capture one `available|fail-closed` value in every `SyncPullSnapshot` when the job is created.
- Consult that frozen job value for carrier-loss accounting and replacement. Never consult the
  current process default for an existing job.
- Reject a same-epoch retry that names a different failover value. It cannot weaken or strengthen a
  retained job by ambiguity.
- Preserve local-control operation 68 as the compatibility entrance; it captures the running
  Agent's configured default. Add local-control v1.38 operation 85 with the exact payload
  `policy-byte || friend-u32 || namespace[1..64]`.
- Extend the owner CLI without changing the old command:

  ```text
  iotox sync-pull FRIEND NAMESPACE [available|fail-closed]
  ```

  Omitting the final value uses operation 68. Naming it uses operation 85.
- Render `failover=...` on each content-free job status line. Keep
  `auxiliary-failover-policy=...` as the daemon default so operators can distinguish configuration
  from the live job invariant.

The full-Agent first-byte-loss test deliberately configures the opposite daemon default in both
directions. An explicit `available` job still reassigns and completes under a fail-closed daemon;
an explicit `fail-closed` job remains fenced with zero reassignment under an available daemon.

## Consequences

- One Agent can safely carry pulls with different loss semantics, and a running pull is immune to
  configuration drift or conflicting retries.
- This closes the local per-job prerequisite only. A signed route-class grammar still requires a
  separately negotiated artifact and an authenticated mapping from signed route members to the
  deployment-local `tox/native|tox/tor|tox/i2p` class.
- No IoTox peer framing or sync-wire-v1 byte changes are made.
