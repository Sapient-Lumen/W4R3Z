# ADR 0111: checkpoint route generation before networking

- Status: accepted and implemented policy-loading boundary
- Date: 2026-08-21
- Scope: route-set persistence, rollback/fork refusal, startup ordering, and operator visibility
- Depends on: ADR 0011, ADR 0030, ADR 0108, and ADR 0110

## Context

A valid stable-device signature proves who authored a route set, but does not prove it is current.
Restoring an older signed artifact could reactivate revoked routes or old budgets. Accepting two
different artifacts at the same generation would also leave workers with irreconcilable policy.
The coordinator additionally needs an operator surface before real worker supervision is safe to
debug.

## Decision

An explicitly configured route artifact is loaded through one private-file store before toxcore is
started. The artifact and generation state must each be an owner-owned, single-link, mode-0600
regular file read with `O_NOFOLLOW` and exact size bounds. Their immediate parents must be
owner-owned mode-0700 directories so another account cannot replace both directory entries. A
persistent private advisory lock serializes local processes.

The generation state binds the stable device principal, highest accepted generation, and a
domain-separated digest of the complete signed artifact. It is itself signed by the stable device.
A newer generation is atomically checkpointed and reread before the route set is returned. An older
generation, same-generation different digest, malformed state, foreign signer, weak permission,
hard link, symlink, or commit failure fails closed before networking.

Local control minor 24 allocates operation 66, `route-inventory-show`. `iotox routes` returns its
coherent content-free snapshot. `iotox routes-watch` polls that same operation and emits only changed
complete snapshots; it does not create an independent event truth. Failures use a closed enum, not
worker-supplied text.

When `--route-set` is absent, no route artifact or generation state is opened or created. The
existing single-route agent path remains active and the read surface reports
`mode=single`/`route-set-configured=0`.

## Consequences

- Ordinary local rollback and same-generation fork replacement are detected. Restoring the signed
  artifact and its signed generation checkpoint together still requires a future external monotonic
  witness to detect.
- `--route-generation-state` cannot be supplied without `--route-set`; otherwise the state path is
  derived beside the artifact.
- Expiring membership requires `--trust-wall-clock` and the existing persisted command-clock
  rollback check to pass; absent trusted time fails coordinator creation.
- The inventory is now a real pre-network product configuration and operator surface, but its
  members remain `configured`. Route worker creation, process fencing, and transcript-derived
  authentication are the next Gate 2 slice.
