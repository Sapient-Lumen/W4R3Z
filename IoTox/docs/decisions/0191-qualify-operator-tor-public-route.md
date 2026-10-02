# ADR 0191: Qualify the operator Tor public route without claiming anonymity

Status: accepted bounded operator-route gate, 2026-08-27.

## Context

ADR 0190 freezes a strict `Tox/Tor` SOCKS construction, and the Sandwurm gate proves two-peer
application traffic and packet containment through a generic SOCKS forwarder. Neither proves that
the proxy is Tor, that a public Tox relay is reachable through a Tor circuit, or that Tor
loss/restart remains fail closed.

The provider presents an unusual but intentional interface boundary: c-toxcore sends already
numeric IPv4/IPv6 SOCKS destinations, while IoTox prohibits relay hostnames and native DNS. Tor's
`SafeSocks 1` rejects numeric destinations because Tor cannot determine how they were obtained. It
therefore cannot be used with this provider contract even though no application DNS lookup occurs.

## Decision

Add a separate opt-in public-network gate, `tools/run-tox-operator-tor-smoke.py`. It accepts one or
more explicit current public numeric Tox TCP relay records and never downloads, resolves, compiles,
or substitutes a node catalog. It refuses a dirty source tree and binds the source-linked IoTox
binary plus exact Tor path, version, digest, invocation, and normalized configuration.

Run Tor as a loopback-only client with cookie-authenticated Unix control, IPv4 external circuits,
private ephemeral state, and loopback SOCKS policy. Set `SafeSocks 0` explicitly because the
operator—not application DNS—supplies numeric relay records. Keep IoTox native DNS disabled and
require numeric records at its boundary.

Qualification requires all of these facts at initial connection and after one Tor restart:

- c-toxcore reports `Tox/Tor` over TCP;
- the exact IoTox PID owns only loopback TCP connections to the Tor SOCKS endpoint and owns no UDP
  socket;
- Tor control reports bootstrap progress 100 and the allowed relay stream as `SUCCEEDED` on a
  built application circuit with at least three hops. ADR 0195 freezes the exact accepted purposes
  as `GENERAL` or `CONFLUX_LINKED` and adds source/stream lifecycle correlation;
- the exact Tor PID owns at least one public TCP connection;
- Tor death produces c-toxcore `offline`, a held outage contains repeated no-bypass socket checks,
  and no native fallback appears before same-endpoint recovery.

Retain a canonical content-minimized receipt. Hash Tor circuit paths and public socket endpoint sets
rather than publishing guard/exit identities. Independently verify the receipt schema, exact policy,
route observations, durations, source/tool hashes, and nonclaims with
`tools/verify-tox-operator-tor-smoke.py`.

## Consequences

- `Tox/Tor` now has bounded evidence for a real operator Tor daemon and public numeric Tox relay,
  independently of the generic SOCKS fixture.
- `SafeSocks 0` is not permission for application DNS. Numeric-only IoTox configuration and disabled
  native DNS remain mandatory; changing either side requires a new decision and leak gate.
- Public relay liveness is volatile. Operators must choose current records; failures do not trigger
  a hidden catalog or native route.
- c-toxcore's roughly 78-second loss report remains authoritative carrier truth. A future faster
  route-health/application-liveness signal must remain separate.
- One application stream on one three-hop circuit is not an anonymity proof. Circuit construction,
  Tor software identity, public reachability, and anonymity are distinct claims.
- The actual-Tor gate and generic-SOCKS two-peer gate are complementary, not transitive evidence for
  an unrun two-IoTox-over-Tor application topology.

## Accepted evidence

Clean source commit `715e1c823b4dabaf7b7a7a9b967a6a8c4b1420a0` passed with Tor 0.4.8.11 and
one current public relay. Initial TCP took 9.120 seconds. ADR 0192's auxiliary signal observed local
refusal after 35 ms while c-toxcore still reported TCP; authoritative offline arrived after 74.602
seconds. The route stayed absent for 30.290 seconds and 30 socket checks, and recovery took 3.913
seconds. ADR 0195 additionally binds initial/recovered configured-target successes to new Agent
sources and distinct three-hop `CONFLUX_LINKED` circuits. IoTox owned no UDP or direct-relay socket
in any sampled phase. The canonical receipt is
`artifacts/rev0045/tox-operator-tor-smoke.json`; detailed claim boundaries are in
`docs/evidence/2026-08-27-operator-tor-public-route.md`.
