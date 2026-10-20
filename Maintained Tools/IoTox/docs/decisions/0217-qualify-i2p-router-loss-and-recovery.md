# ADR 0217: Qualify I2P router loss and recovery

Status: accepted construction evidence, 2026-08-28.

## Context

ADR 0216 proved the first two-guest actual-I2P baseline and strict TAP containment, but it left the
most important availability boundary untested. A reachable bridge SOCKS listener does not mean its
SAM session or router is usable, and an I2P session becoming ready does not mean c-toxcore has
re-established an authenticated peer session. The next gate had to separate those layers and prove
fresh application traffic after an exact router replacement without native fallback.

Fresh i2pd datadirs also made reseed availability part of the construction. The pinned i2pd source
already contains the matching family and reseed certificates, but the baseline did not explicitly
select or receipt that bundle and used an overly narrow startup limit.

## Decision

- Add the Sandwurm `i2p-router-restart` scenario to the existing two-guest
  `tox-i2p-construction` topology. The topology, route policy, public numeric node set, source-linked
  guests, and route-scoped savedata remain identical to the accepted baseline.
- Select the 21-file `contrib/certificates` bundle from the exact pinned i2pd 2.60.0 source, require
  signed SU3 reseed verification, and commit the domain-separated certificate-tree digest and file
  count to the topology receipt. Bound clean-router and child SAM startup at 840 seconds under one
  900-second supervisor wait.
- Require both guests to reach a transcript-confirmed application session before fault injection.
  Kill only the client i2pd process while keeping the bridge adapter listener reachable. Require the
  SAM listener to disappear and the adapter to record generation-one loss.
- Do not recover on the adapter observation alone. Require both guests to report c-toxcore's
  authoritative offline state. Then start a new router process with the exact same private datadir,
  require a distinct PID, and require the adapter's generation-two SAM session.
- Require both guests to advance from authenticated online epoch 1 to epoch 2 and to receive fresh
  post-recovery text from the other guest before either may finish. Listener readiness, SAM
  readiness, c-toxcore connection, session confirmation, and application success remain separate
  facts.
- Keep all three committed fronts admitted before the fault. After recovery, do not require
  c-toxcore to reopen every redundant bootstrap front: it may stop dialing once connectivity is
  restored. Require at least two generation-two admissions to committed fronts and join them to the
  bilateral guest receipts. Permit only `denied-stream`, `denied-sam-unavailable`, and
  `denied-stale-generation` fault retries, with a hard maximum of 384.
- Retain the same content-free compact evidence class as ADR 0216. Router datadirs, Destination
  keys, injected identities, guest disks, savedata, and runtime state remain private and omitted.

Accepted compact proof `pair.v_11i2me` runs clean source commit `5428058`, preserves both route
identities, and records the exact adapter lifecycle `ready(1) -> lost(1) -> ready(2)`. The old client
router PID 1658175 is replaced by PID 1687953 over the same datadir after a 68.991-second fault hold.
Both guests observe offline, advance online epoch 1 to 2, and receive the other's fresh text. The
adapter records six admissions over all three fronts in each generation and eight bounded
`denied-sam-unavailable` attempts while the router is absent.

Both TAP captures remain TCP-only to `10.0.0.1:39053`: 1,307 client and 1,440 device egress IPv4
packets, with zero UDP, direct bootstrap, direct peer, or alternate IPv4 destination traffic. The
raw and compact strict verifiers both pass.

## Consequences

- Listener-positive/SAM-negative loss, exact client-router process replacement, authoritative
  transport interruption, higher-epoch application recovery, and no-fallback containment are now
  closed for the laboratory-only I2P construction on the founding host.
- I2P route health must not be inferred from a listening SOCKS socket or a ready SAM session. The
  product's application/session truth remains c-toxcore plus transcript confirmation.
- Redundant bootstrap-front population is a construction prerequisite, not a post-connect liveness
  invariant. The verifier requires complete initial population and bilateral application recovery
  instead of forcing unnecessary reconnects to every front.
- Production `tox/i2p` remains reserved. At this decision, server/front replacement,
  router-owned external-socket attribution, a private member-bound Ratox or sync payload, repeated
  time/record windows, independent router administration, anonymity, and production availability
  remained open. ADR 0218 later closes the first two bounded construction items.

See `docs/evidence/2026-08-28-sandwurm-i2p-router-recovery.md` and
`docs/i2p-route-construction.md`.
