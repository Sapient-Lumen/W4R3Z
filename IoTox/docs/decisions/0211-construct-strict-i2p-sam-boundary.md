# ADR 0211: Construct the strict I2P SAM boundary

Status: accepted construction prerequisite, 2026-08-28.

## Context

`Tox/I2P` is deliberately reserved and fail-closed. c-toxcore names bootstrap and TCP relay records
as IP endpoints, while an I2P service is named by a Destination. Reusing a generic SOCKS outproxy
would permit clearnet routing and would not prove that an exact Tox record reached an I2P service.
Human-readable `.i2p` names also depend on a local address book and are not globally unique.

I2P's SAM v3 API provides reliable ordered STREAM connections through one long-lived session. The
SAM bridge is normally local, unauthenticated, and unencrypted; it must not become a remotely
reachable ambient authority. I2P session health is still an auxiliary observation, not c-toxcore
carrier or IoTox session truth.

## Decision

Add the laboratory-only `tools/run-i2p-sam-socks.py` adapter. It:

- listens as a bounded SOCKS5 CONNECT server for c-toxcore but accepts only numeric IPv4/IPv6
  targets present in an explicit complete-record map;
- maps each admitted record only to one canonical lowercase traditional 52-character `.b32.i2p`
  destination, accepting no DNS name, address-book name, full Destination, extended blinded name,
  wildcard, BIND, or UDP route;
- connects only to an explicit numeric loopback SAM endpoint and negotiates exact SAM 3.1;
- creates one long-lived transient Ed25519 STREAM session with ECIES-X25519 leaseset encryption and
  explicit inbound/outbound tunnel quantity two;
- selects i2pd's interactive streaming profile while making no latency guarantee;
- uses one fresh SAM socket per admitted stream, with `SILENT=false` and a required explicit
  `STREAM STATUS RESULT=OK` before returning SOCKS success;
- keeps one random session ID stable for the process lifetime, withdraws admission on control loss,
  and recreates a new transient session at a higher local generation without relabeling existing
  carrier or application state;
- records only content-free state/counter events, per-attempt SAM setup time, and a domain-separated
  destination commitment, never the SAM-returned private Destination or mapped b32 name; denial
  decisions are durably
  ordered into that audit before their corresponding SOCKS failure reply; and
- has no product daemon integration, server-side I2P service, router download, outproxy, native
  fallback, anonymity claim, or `tox/i2p` enablement.

## Qualification

The independent process double verifies the exact HELLO, SESSION CREATE, and STREAM CONNECT bytes.
Ten byte-identical streams pass, including eight simultaneous streams under one session. It also
sends an otherwise unexpected SAM 3.2 PING and freezes the adapter's defensive PONG response; that
exchange is not a required or claimed part of the negotiated SAM 3.1 protocol.
Unmapped numeric and domain targets fail. Forced control-socket loss produces one admission-closed
interval; recovery creates generation two under the same process-local session ID and subsequent
bytes pass. The audit contains ten admissions, three denials, two ready generations, one loss, and
no raw I2P destination.

## Consequences

- Endpoint naming, no-DNS/no-outproxy policy, SAM framing, bounded concurrency, and local
  loss/recovery now have an executable construction boundary.
- The transient SAM Destination is route plumbing, not the stable IoTox device principal or the
  route-specific Tox savedata identity. Reconnection may rotate it; the remote Tox identity still
  links traffic within that route by design.
- Product `tox/i2p` remains unsupported. Enabling it requires a real router and I2P-hosted Tox TCP
  service, source/process attribution, two-guest packet containment, reconnect, private route
  membership, and exact application-payload evidence equivalent to the accepted Tor gates.

See `docs/i2p-route-construction.md`.
