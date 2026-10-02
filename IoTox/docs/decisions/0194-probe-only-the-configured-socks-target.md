# ADR 0194: Probe only the configured SOCKS target

Status: accepted construction surface, 2026-08-27.

## Context

ADR 0192 can identify a dead local SOCKS listener within a small bound, but a successful TCP connect
to that listener says nothing about method negotiation, route policy, circuits, or the target. The
operator-Tor gate can authenticate Tor's control plane, but making Tor control credentials part of
the ordinary IoTox daemon would create a new secret/configuration boundary and would not generalize
to every strict SOCKS route.

An upstream probe must not become a user-supplied port scanner, disclose route endpoints in evidence,
or silently enter the 250 ms persistent watch.

## Decision

Add local-control v1.37 operation 84 and the explicit one-shot owner command:

```text
iotox [--timeout-ms N] route-target-health
```

The Agent selects only index zero of the numeric TCP-relay list already required and validated for
its immutable `Tox/Tor` route. The request cannot contain a host, port, DNS name, relay index, or
friend. `Tox/native`, an absent relay, a hostname, or an absent SOCKS endpoint fails before any probe.

The probe opens one nonblocking connection to the configured SOCKS endpoint under one absolute
1..5000 ms deadline, negotiates SOCKS5 no-auth, sends one numeric IPv4/IPv6 CONNECT for the selected
relay, consumes the complete bounded reply, sends no application bytes, and closes. The report is
content-free:

```text
network=Tox/Tor
carrier-connection=tcp|offline|udp
target-source=configured-tcp-relay-0
probe-stage=proxy-connect|method-negotiation|target-connect|complete
target-health=reachable|refused|denied|timed-out|unreachable|failed
target-rtt-us=DECIMAL
socks-reply-code=none|0..255
semantics=auxiliary-only-explicit-numeric-relay-no-carrier-or-session-epoch-mutation
```

The CLI strictly parses and canonically rerenders the response. SOCKS reply 0 is reachable; 2/7/8
are denied, 3/4 unreachable, 5 refused, and 6 timed out. The probe stage distinguishes failure to
reach the local proxy from a response about the configured target.

`route-health-watch` does not invoke this operation. Repeated upstream sampling must be an explicit
operator/science choice, not the default 250 ms liveness cadence.

## Consequences

- A reachable local SOCKS boundary and a successful configured-target CONNECT are now separate facts.
- The selected target is already part of the frozen route configuration; the command cannot expand
  egress authority or choose an arbitrary destination.
- The exact carrier label is copied, not inferred. Target success or failure cannot relabel toxcore,
  advance an online epoch, or detach/resume a Ratox session.
- A successful CONNECT proves only that this proxy admitted and established this target TCP stream at
  this instant. It does not prove a particular Tor circuit, anonymity, relay protocol correctness,
  future availability, application liveness, or a Tox session.
- Selecting only the first relay is deterministic and content-free. Multi-target sampling, cadence,
  rotation, and fleet policy remain future work.

## Qualification

The whole-binary process gate starts the strict numeric allowlisted SOCKS fixture, one configured TCP
target, mock-backed `iotox run`, and the installed control CLI. It first waits for authoritative TCP,
then proves:

1. complete CONNECT, `reachable`, and SOCKS reply 0;
2. carrier still TCP while the proxy returns reply 5 for the stopped configured target; and
3. carrier still TCP while local proxy connection is refused with no SOCKS reply.

The independent proxy audit contains exactly one admitted and one failed-connect record, both for the
sole allowlisted target, and no denied or domain-name target. Parser tests reject endpoint-bearing,
noncanonical, and stage/result-incoherent reports. This is local strict-SOCKS construction evidence;
an operator-Tor run must separately bind the target result to authenticated circuit and process/socket
evidence.

ADR 0195 subsequently closes that bounded public binding: authenticated Tor control correlates the
new Agent SOCKS source from `NEW` through the same stream ID's `SUCCEEDED` event, configured relay
zero, and a built three-hop `GENERAL` or `CONFLUX_LINKED` application circuit. This strengthens the
operator evidence without putting Tor credentials or circuit interpretation into this ordinary
command.
