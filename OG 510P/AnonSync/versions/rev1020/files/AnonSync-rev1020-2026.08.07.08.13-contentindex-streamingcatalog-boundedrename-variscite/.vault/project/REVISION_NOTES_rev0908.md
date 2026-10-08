# AnonSync rev0908 revision notes

## Mission

AnonSync's mission is to replace Resilio Sync with an open C++ product, including
first-class direct, Tor, and I2P operation. This revision explicitly supersedes
the prior framing that treated an evidence-authorized convergence engine as the
product mission. Crash consistency, exact evidence, explicit capabilities, and
bounded work remain implementation requirements in service of synchronization.
They are not a substitute for continuous folder-sync functionality.

No Resilio proprietary wire compatibility is claimed. The replacement target is
the installed product and user workflow.

## Main implementation

### Typed stream-route boundary

Added:

- `src/sync_replica_stream_connector.hpp`
- `src/sync_replica_stream_connector.cpp`
- `tests/sync_replica_stream_connector_test.cpp`

`SyncReplicaStreamConnector` establishes one reliable byte stream by explicit
route and returns move-only ownership of an exact nonblocking, close-on-exec
socket. The existing mutual-TLS file-delivery client consumes that stream. The
former numeric direct-TCP client API remains as a compatibility wrapper.

Supported outbound routes:

- numeric direct TCP;
- Tor v3 onion service through SOCKS5; and
- I2P destination through SAM 3.1 STREAM.

No remote onion or I2P name is sent to process DNS.

### Tor

- Requires a lowercase checksum-valid v3 `.onion` service and nonzero virtual
  port.
- Validates base32, version byte, and checksum before dialing.
- Uses SOCKS5 username/password method with current Tor format-zero username
  `<torS0X>0`.
- Uses a caller-provided or cryptographically random command isolation token.
- Requires the SOCKS proxy to be numeric loopback until authenticated remote
  proxy transport exists.
- Adds a Tor receiver publication profile that validates the onion identity and
  requires the TLS listener to be loopback; Tor remains the external publication
  owner in this revision.

### I2P

- Uses SAM 3.1 HELLO, SESSION CREATE, and STREAM CONNECT.
- Retains one command-local control session across bounded sender sessions.
- Detects stale retained control sockets and permits recovery only on a later
  caller-authorized session.
- Requests explicit tunnel quantities and ECIES-X25519 lease-set encryption.
- Applies `SIGNATURE_TYPE=7` only to `DESTINATION=TRANSIENT`; persisted private
  destinations carry their own signature type.
- Sets a 180-second minimum/default I2P stage timeout and refuses batch admission
  when less than one full stage budget remains.
- Adds native inbound I2P service publication through one retained SAM session
  and one retained `STREAM FORWARD` socket.
- Forces `SILENT=true` for forwarding so SAM cannot prefix an I2P destination
  line ahead of TLS.
- Requires both SAM bridge and local forward target to be numeric loopback.

### Private I2P destination admission

Added a reusable bounded private-file reader:

`read_sync_bounded_private_regular_file_no_symlink_or_throw`

On POSIX it requires the opened object to remain:

- a regular file;
- owned by the effective user;
- single-link;
- exact mode `0600`; and
- stable in identity and access policy across the read.

The Windows path fails closed until an equivalent owner-only DACL proof exists.
The I2P private destination CLI now uses this boundary.

### CLI and telemetry

`send-one` and `send-batch` accept:

- `--transport direct --address ... --port ...`
- `--transport tor --onion-address ... --onion-port ...`
- `--transport i2p --i2p-destination ...`

`serve-one` and `serve-batch` accept direct, validated Tor publication, or native
I2P SAM forwarding profiles.

JSON reports route kind and safe connection-stage evidence without printing Tor
isolation tokens, SAM session IDs, or private I2P destinations. A pre-existing
duplicate `transport` key in `send-one` output was removed.

### Process proof

Added `tools/test_anonsync_replica_anonymous_routes.py` and registered it with
CTest on Linux. The test drives the shipped executable through modeled Tor
SOCKS5 and I2P SAM bridges while relaying the real TLS 1.3 mutual-authentication
and file-delivery protocol. It proves:

- outbound Tor file delivery;
- outbound I2P file delivery;
- validated inbound Tor publication profile;
- native inbound I2P `STREAM FORWARD` delivery;
- exact payload bytes and authenticated receipts; and
- rejection of remote plaintext proxies, short I2P deadlines, missing persistent
  inbound identity, and contradictory batch budgets.

## Audit/refactor findings corrected

1. The repository's current README stated the wrong mission.
2. Numeric TCP dialing was embedded in the TLS owner.
3. Onion length/base32 validation did not prove the v3 checksum.
4. Plaintext SOCKS/SAM control could be pointed at remote hosts.
5. Persisted SAM destinations received a TRANSIENT-only signature option.
6. A dead retained SAM socket could poison later batch sessions.
7. I2P inherited unrealistic ordinary-TCP deadlines.
8. Inbound SAM's default destination preamble would corrupt TLS.
9. Long-term I2P service identity bytes lacked private-file mode/owner proof.
10. Sender JSON contained a duplicate key.

## Deliberate nonclaims

- AnonSync is not yet a continuous folder daemon or complete Resilio replacement.
- Tor onion-service creation and key lifecycle remain externally configured.
- I2P private-destination generation, naming, rotation, and real-router
  compatibility coverage remain open.
- There is no LAN/rendezvous discovery, NAT traversal, relay, multi-peer route
  scheduler, or automatic direct/Tor/I2P fallback policy.
- There is no recursive watcher/scanner loop, complete directory/delete/rename
  model, selective sync, permissions parity, bandwidth control, or blockwise
  large-file resume.
- Tor and I2P do not by themselves eliminate traffic analysis or application
  metadata.
- The anonymous-route process test uses modeled bridges, not real Tor/I2P
  daemons.

## Next product work

The next C++ vertical slice should be a persistent folder supervisor (`anonsyncd`)
that owns versioned configuration, recursive initial/periodic scans, watcher
hints, durable change journaling, multiple peer route sets, bounded sessions under
explicit retry/backoff/shutdown policy, crash resume, and useful service status.
The following slice should introduce authenticated block transfer and durable
partial-file resume.

See
`RESILIO_REPLACEMENT_TOR_I2P_TRANSPORT_BOUNDARY_AUDIT_rev0908.md` for the full
product-gap, route-security, and architecture audit.
