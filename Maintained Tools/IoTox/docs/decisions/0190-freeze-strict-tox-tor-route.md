# ADR 0190: Freeze the strict Tox/Tor SOCKS route

Status: accepted construction route, 2026-08-27.

## Context

The architecture reserved `Tox/Tor`, but merely passing a proxy option to c-toxcore would not prove
route containment. Native UDP, local discovery, DNS, compiled bootstrap catalogs, or a silent retry
through `Tox/native` could contradict the route label. The exact pinned provider also determines
whether relay names can be resolved by the proxy and whether TCP-only bootstrap records remain
necessary.

Source inspection of c-toxcore 0.2.23 establishes two constraints. With UDP disabled,
`tox_bootstrap()` does not execute its DHT datagram branch but still installs onion path nodes.
`tox_add_tcp_relay()` is separately required for the TCP carrier. SOCKS5 connection requests encode
the already-resolved relay IPv4/IPv6 address; they do not use the domain-name address type.

## Decision

Construction-enable only `Tox/Tor`; retain `Tox/I2P` and direct-overlay transports as unsupported.
Require one explicit numeric SOCKS5 endpoint, at least one explicit numeric bootstrap record, and at
least one explicit numeric TCP-relay record. Do not inject the compiled native catalogs for this
route.

Set UDP, local discovery, DHT announcements, and hole punching false; set SOCKS5; set the numeric
proxy host and port; and set c-toxcore's experimental native-DNS-disable option true before
`tox_new()`. Retry only the already validated explicit records. Reject proxy/route confusion,
hostnames, zero or missing endpoints, and UDP-required auxiliary route members before durable or
runtime mutation. Never retry through native configuration.

Keep SOCKS authentication and remote DNS absent because the consumed c-toxcore API provides neither
credential fields nor domain-name relay requests. A local trusted Tor SOCKS endpoint is the intended
operator shape. IoTox does not infer that a SOCKS implementation is Tor.

## Consequences

- Selecting `tox/tor` has a complete fail-closed socket/DNS policy rather than being a cosmetic name.
- Endpoint operators must obtain numeric addresses and update configuration when those addresses
  change; this is less convenient but does not make a false remote-DNS claim.
- Bootstrap records remain present for TCP onion construction without re-enabling native UDP.
- The provider can technically reuse the same Tox savedata, but ADR 0198 now selects distinct
  route-scoped defaults and treats an explicit shared path as a linkability decision.
- Proxy compromise can observe and manipulate reachability metadata. SOCKS containment does not
  itself prove Tor circuits, anonymity, censorship resistance, or a safe proxy host.
- `Tox/I2P`, direct Tor/I2P transports, broad public routed reliability, and infrastructure
  stewardship remain separate work.

## Qualification

Owned tests freeze strict proxy syntax, route capability projection, all rejected topology classes,
exact toxcore option values, no native catalog injection, and the reserved-I2P failure. The bounded
numeric-only SOCKS5 forwarder has its own process test for allowlisted byte-exact forwarding,
unlisted-target denial, and domain-address denial.

`tools/run-tox-tor-smoke.py` realizes the source-linked product and pinned bootstrap fixture, reaches
TCP self-connectivity through SOCKS5, proves from Linux socket ownership that IoTox has neither a UDP
socket nor a direct relay TCP socket, kills the proxy, observes offline state, restarts the same
endpoint, and observes recovery. Its receipt says `source-linked-local-construction-not-actual-tor`.
It refuses a dirty source tree and binds the exact source commit, binaries, and route tools.
The accepted receipt measured 8.038-second construction, 77.993-second provider loss detection,
and 4.921-second recovery. This freezes a second boundary: faster route-health or application-
liveness reporting may supplement, but must not overwrite, c-toxcore's connection truth or advance
a session epoch.
At freeze time, Sandwurm packet capture and an actual operator Tor daemon were the next evidence
gates.

The first of those gates passed as `pair.zyy913jf`: two source-linked Sandwurm guests crossed the
generic SOCKS boundary, lost and recovered the proxy, advanced their online epochs, and exchanged
fresh text after recovery. Their TAP captures contain 913 guest-egress IPv4 packets, all TCP to the
proxy and none to the peer or bootstrap target directly. This promotes the strict generic-SOCKS
construction to route-network evidence without promoting the laboratory forwarder to Tor.

ADR 0191 subsequently closes the other bounded gate without changing this product policy. One clean
source-linked IoTox reached a public numeric Tox relay through an exact Tor 0.4.8.11 daemon; Tor
control attached the stream to initial and recovered three-hop circuits, process socket ownership
showed no IoTox UDP/direct route, and a held Tor outage recovered only after exact endpoint restart.
That evidence is one host/relay/Tor/time sample, not anonymity, long-running reliability, or the
unrun two-IoTox-over-Tor application topology.
