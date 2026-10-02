# ADR 0206: Qualify Ratox across actual-Tor process loss

Status: accepted, implemented, and bounded-live-qualified, 2026-08-27.

## Context

ADR 0197 freezes Ratox total-loss behavior under native and generic-SOCKS laboratory routes:
heartbeat loss warns first, authoritative carrier loss detaches without killing the remote PTY, and
an explicit higher-epoch resume preserves session identity and byte positions. ADR 0205 separately
proves that an independently supervised Tor process can disappear and return without restarting its
IoTox route worker. Neither result establishes the latency-sensitive terminal lifecycle when the
primary IoTox transport itself runs through actual Tor.

The distinction matters. A local SOCKS forwarder has no Tor bootstrap, circuit, control, or process
identity. A sync auxiliary can reassign an immutable object to a native member, while one Ratox
attachment must never silently migrate or fabricate session progress from route-health evidence.

## Decision

Add the distinct opt-in Sandwurm scenario `ratox-route-actual-tor-loss`. It runs both primary IoTox
agents as strict `Tox/Tor` clients through separate host Tor processes, source-only SOCKS policies,
authenticated control sockets, and the one operator-supplied public numeric Tox record. The private
fixture remains available only for deterministic identity handoff and must receive no guest packet.

After the controller opens the bounded echo PTY and completes its first heartbeat/byte exchange, the
host must:

1. capture the client Tor process, authenticated STREAM/CIRC, source, target, and control identity;
2. send `SIGKILL` only to that client Tor process group;
3. release the already-running Ratox probe and observe heartbeat timeout while c-toxcore still
   reports TCP;
4. wait for authoritative offline and verify the host retains exactly one detached live PTY;
5. restart the identical Tor binary, configuration, and private data directory; and
6. allow only explicit Ratox resume after a higher authenticated online epoch.

Acceptance requires the same session commitment and host incarnation, generation 1 to 2, input and
output sequence 1 to 2, post-resume PTY echo, zero IoTox daemon restarts, distinct pre-loss/recovered
Tor process and control identities, a continuous device Tor process, and independently reparsed
three-hop application-circuit evidence for all three phases. Each TAP must contain guest egress only
to its exact local Tor listener: zero UDP, direct bootstrap, direct relay, or peer packets.

The measured heartbeat, authoritative-offline, Tor-bootstrap, route-ready, resume-open, terminal,
and render times are retained as observations. None is a protocol deadline or public-network SLA.

## Consequences

- Actual-Tor terminal recovery reuses the frozen Ratox state machine; no Tor-specific session
  mutation, automatic migration, or route-health authority is added.
- The remote PTY belongs to the device-side session incarnation rather than the client Tor process.
- A successful gate supports an Eternal/Mosh-style explicit reattachment direction, but does not
  claim roaming between route identities or transparent multi-path terminal striping.
- The result remains one host, one public Tox record, one Tor build, one loss, and one bounded
  session. Long soak, relay/exit/time diversity, asymmetric faults, and adversarial local proxies
  remain separate M8 work.

## Qualification

Accepted compact proof `.sandwurm/exports/pairs/pair.2waqdpgk` runs clean commit
`08baaba59f4f51c8b900c7a4041a4a02a0934e9b`. The host killed client Tor PID 2,060,846 after initial
PTY progress; heartbeat warning arrived after 2.204 seconds while carrier truth remained TCP and
authoritative offline arrived after 27.379 seconds. The device retained one detached live PTY.

The identical Tor binary bootstrapped after 2.418 seconds as PID 2,243,633 with a distinct control
inode. Explicit resume preserved the exact session and host incarnation, advanced generation and
input/output sequences from 1 to 2 under a higher authenticated epoch, and completed a second PTY
exchange. Both IoTox daemon restart counts were zero. All 1,010 client and 1,066 device guest IPv4
egress packets were TCP to the exact role-local Tor listener; UDP and direct bootstrap/relay/peer
counts were zero. Three authenticated Tor phases each reached bootstrap 100 and joined the exact
guest source to a three-hop application circuit.

The 1,728,512-byte compact proof and its 2,569,691,136-byte private source independently pass the
strict verifier. See `docs/evidence/2026-08-27-sandwurm-actual-tor-ratox-loss.md`. This accepts only
the bounded claim in this ADR; diversity, duration, adversarial-proxy behavior, automatic resume,
and production support remain open.
