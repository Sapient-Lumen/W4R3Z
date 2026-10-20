# ADR 0135: recover synchronization publisher guest restart from persisted state

Status: accepted

Date: 2026-08-22

## Decision

A publisher guest restart does not preserve a live synchronization transport handle. When the
publisher disappears, the subscriber applies ADR 0132 to the old authenticated epoch: the old pull
becomes terminal, all admitted receives are closed, private staging and signed active-attempt truth
are cleared, and no accepted HEAD or activation may appear. Reconnection cannot implicitly revive
that job or reuse its FileIds.

The publisher's durable state is different from its transport state. A controlled reboot may retain
the exact Tox savedata, stable device identity, authority ledger, namespace policy, source file,
immutable artifact and manifest objects, and stable-device-signed publication HEAD on its persisted
disk. Startup must load that policy before advertising synchronization, preserve the public Tox and
stable-device identities, and validate the persisted source and both immutable objects against the
saved publication record. It must not generate a replacement revision merely to recover service.

The stable subscriber may issue a new `sync-pull` only after it observes a strictly higher confirmed
online epoch, current exact-head authority, the configured carrier, and one unchanged recovery epoch
for 50 consecutive 100 ms samples. That pull is a new process-local job with new transport handles.
It fetches complete immutable objects, accepts the signed HEAD last, and still requires a separate
exact-token local activation.

This contract treats guest reboot as publisher availability loss plus durable publication recovery,
not as byte-range resume. Partial bytes from the retired epoch are deliberately not trusted or reused.

## Consequences

- A rebooted publisher can serve the exact previously published revision without key injection,
  authority re-bootstrap, namespace reinstallation, object regeneration, or HEAD advancement.
- Subscriber cleanup is identical for link loss and publisher reboot at the epoch boundary, while
  persisted publisher validation is additional reboot-specific evidence.
- Recovery latency includes guest boot, Tox route establishment, authority confirmation, the stable
  epoch window, and a complete explicit retry. Forced TCP may therefore require a longer bounded
  laboratory watchdog than direct UDP.
- A changed publisher boot ID and unchanged client boot ID distinguish guest replacement from daemon
  replacement or a bilateral laboratory reset.
- This does not authorize automatic subscription, partial-range reuse, paused-handle reconstruction,
  abrupt power-cut recovery, filesystem-corruption repair, rollback of a valid older disk image,
  multi-source failover, deterministic-directory activation, or unattended OTA execution.

## Evidence

The `sync-file-guest-restart` Sandwurm cell uses a rate-shaped 8 MiB `range-v1` pull. After positive
provider position, the publisher checkpoints only evidence metadata and requests an operating-system
reboot. The initial Cloud Hypervisor chain records its bounded reboot exit; a successor Sandwurm chain
uses the exact initial prelaunch receipt and writable runtime-root disk without reinjecting identity.
The stable subscriber must observe offline, terminal failure and complete cleanup before that
successor can establish a fresh authorized epoch. Both roles then bind the preserved publication and
explicit retry through convergence and activation.

Direct UDP and forced TCP pass from clean commit
`f26126e17fe22df1f6cd709ea69005ea2552261d`. Their compact digests, boot/epoch observations, and exact
nonclaims are retained in `evidence/2026-08-22-sandwurm-sync-guest-restart.md`. The strict verifier
joins both VMM epochs, the initial bounded reboot launch, role-specific boot IDs, preserved identity,
partial pre-fault position, cleanup, 50-sample recovery, retry, revision identity, and final
activation. Its forged-evidence fixture rejects a missing retry.
