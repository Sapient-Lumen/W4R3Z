# ADR 0213: Freeze the I2P Tox-service construction

Status: accepted construction prerequisite, 2026-08-28.

## Context

ADRs 0211 and 0212 qualify exact outgoing SOCKS-to-SAM mapping and actual two-router I2P STREAM
bytes. They do not expose a stable service Destination or connect an incoming I2P stream to a Tox
TCP relay. Reusing a transient server Destination would force every client mapping to change after
restart. Using an i2pd tunnel file directly would leave key custody, exact SAM framing, target
selection, and content-free evidence outside the IoTox repository.

The product name `tox/i2p` must remain reserved until the complete route has Sandwurm containment,
loss/recovery, and application evidence. Experiments nevertheless need an honest network label;
calling an I2P SAM adapter `tox/tor` would make status and evidence false.

## Decision

Add `tools/run-i2p-sam-forward.py` as a laboratory-only owner-side boundary. It:

- requires numeric loopback SAM and target endpoints and negotiates exact SAM 3.1;
- creates one Ed25519 Destination with `DEST GENERATE SIGNATURE_TYPE=7`, stores its canonical public
  and private material in one owner-owned, single-link, mode-0600, bounded, no-follow file, and
  reuses that exact identity after process restart;
- verifies that the decoded private Destination begins with the complete decoded public Destination
  before deriving the traditional b32 address;
- creates a persistent STREAM session with ECIES-X25519 leaseset encryption and two inbound/two
  outbound tunnels plus i2pd's interactive streaming profile;
- issues exactly `STREAM FORWARD ... HOST=<numeric-loopback> PORT=<exact-port> SILENT=true`, so the
  local Tox service receives raw stream bytes rather than a remote-Destination prefix;
- retains both session and forward control sockets, withdraws readiness on either loss, and recreates
  the pair under a fresh session ID and higher local generation;
- creates the audit with no-clobber mode and records only a shared domain-separated b32 commitment,
  lifecycle generation, outcome, and monotonic time; and
- has no router download, address-book name, clearnet outproxy, remote target, UDP path, product
  service management, or anonymity claim.

Add the exact route spelling `tox/i2p-construction`. It reuses the already frozen strict routed-Tox
contract: numeric SOCKS endpoint, nonempty explicit numeric bootstrap and TCP-relay records, no
compiled catalogs, UDP/discovery/announcements/hole punching/native DNS off, and no fallback. It
uses the separate `device.tox-i2p.toxsave` identity. The existing `tox/i2p` and `tox-over-i2p`
spellings remain unsupported.

Extend `tools/run-real-peer-smoke.sh` with explicit network/proxy/bootstrap/relay environment inputs.
Strict routed invocations require fresh identities; the default reusable native cache cannot be
silently copied across route contexts.

## Qualification

The independent process double freezes exact DEST, SESSION, and FORWARD bytes; canonical padded I2P
Base64; destination key creation and restart reuse; `SILENT=true`; raw service bytes; loss and
generation-two recovery; key permissions; audit no-clobber; loopback-only targets; and absence of
raw public/private Destinations from audit records. A live two-i2pd construction then retained one
persistent b32 address across forward-process restart and echoed exact bytes through the strict
client adapter into the forwarded loopback service.

This qualifies the service boundary, not Tox-over-I2P. The next gate must put the pinned Tox TCP
bootstrap/relay behind it and carry source-linked IoTox application behavior through the route.

## Consequences

- Client and server I2P naming/key custody are now explicit, separate, and restart-testable.
- Construction experiments report `Tox/I2P-construction`; they cannot be mistaken for Tor or for the
  still-disabled product route.
- A stable I2P service address is deployment-sensitive owner state. Losing the key changes the route
  endpoint; publishing the private record compromises the service identity.
- SAM listener reachability and forward readiness remain auxiliary. c-toxcore alone owns carrier
  truth, and IoTox application sessions remain above that carrier.

See `docs/i2p-route-construction.md`.
