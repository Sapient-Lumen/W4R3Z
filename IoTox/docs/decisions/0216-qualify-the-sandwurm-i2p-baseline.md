# ADR 0216: Qualify the Sandwurm actual-I2P baseline

Status: accepted construction evidence, 2026-08-28.

## Context

ADRs 0211–0215 established the strict SOCKS-to-SAM boundary, a persistent I2P service Destination,
two live i2pd routers, the 120-second c-toxcore TCP establishment budget, address-preserving node
fronts, and a complete same-host real-peer lifecycle. That work did not prove that separately booted
IoTox guests confined all network traffic to the I2P adapter or that the evidence could survive
secret-free export and independent verification.

The next useful gate had to reuse the ordinary Sandwurm pair lifecycle rather than invent an I2P-only
application test. It also had to bind the exact router implementation and source, keep all service
Destination keys private, and retain packet evidence from both guest TAPs.

## Decision

- Pin i2pd 2.60.0 and its exact source as separate Nix flake outputs. Hash the executable and the
  canonical source tree into the topology receipt.
- Supervise exactly two routers, three persistent address-preserving service fronts, three bounded
  exact-target clearnet egress shims, and one bridge-facing strict SOCKS-to-SAM adapter as a single
  fail-fast topology.
- Require exactly three distinct operator-supplied public numeric Tox records. Neither discovery nor
  compiled catalogs may populate this gate.
- Boot two source-linked Sandwurm/KVM guests with independent route-scoped savedata copies. Give each
  guest only `10.0.0.1:39053` and the same committed three-record set; disable guest DNS, UDP,
  private-L2 probing, native discovery, and fallback.
- Retain both TAP captures, exact launch/receipt chains, the content-free final topology record, and
  four append-only audits in the compact evidence form. Omit router state, Destination keys, guest
  disks, injected identities, runtime state, and bootstrap secret material.
- Accept bounded initial `denied-stream` outcomes as I2P tunnel-convergence retries only when every
  record names one of the three committed Destinations, no other denial class exists, all three
  Destinations later admit, six through twenty-four admissions complete, and at most six transient
  refusals occur. A transient I2P refusal is not a containment leak or a successful carrier.

Accepted compact proof `pair.k_vopzf5` runs clean source commit `0af4759`, reaches TCP friendship,
canonical session confirmation, and bidirectional text in both guests, and passes the raw and compact
strict verifier. Both TAPs show TCP only to the configured bridge adapter: 1,054 client and 1,164
device egress IPv4 packets, with zero UDP, direct bootstrap, direct peer, or other IPv4 destinations.
The adapter records seven admissions, two bounded initial `denied-stream` outcomes, and one session
ready event. Every Destination later admits; all three persistent forwards remain ready without
loss.

## Consequences

- The first two-guest actual-I2P containment and baseline application gate is closed on the founding
  host. It is stronger than the same-process real-peer result because two independent guest kernels,
  VMM chains, TAP captures, and source-linked receipts agree.
- Production `tox/i2p` remains reserved. The accepted spelling remains
  `tox/i2p-construction`, baseline-only in the Sandwurm runner.
- Listener-positive/SAM-negative loss, router/front replacement, bounded carrier recovery, private
  route-member proof, and an exact authority-bound Ratox or sync payload remain separate gates.
- The result proves neither anonymity, independent router administration, availability, latency,
  timing-correlation resistance, physical-host diversity, nor production suitability.

See `docs/evidence/2026-08-28-sandwurm-actual-i2p-baseline.md` and
`docs/i2p-route-construction.md`.
