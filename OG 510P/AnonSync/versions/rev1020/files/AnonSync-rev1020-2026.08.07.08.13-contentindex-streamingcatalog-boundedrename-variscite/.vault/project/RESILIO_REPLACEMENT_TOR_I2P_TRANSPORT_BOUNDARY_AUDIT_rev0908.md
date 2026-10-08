# Resilio-replacement mission and Tor/I2P transport-boundary audit — rev0908

## Executive correction

AnonSync's mission is to replace Resilio Sync with an open C++ product. The
replacement target is the user's workflow and operational capability, not
necessarily interoperability with Resilio's proprietary wire protocol. A useful
acceptance test is simple: a person or organization should be able to remove
Resilio Sync, install AnonSync, configure folders and peers, and obtain dependable
continuous peer-to-peer synchronization. AnonSync additionally requires Tor and
I2P to be first-class transports rather than unsupported tunnels assembled by
hand.

Earlier revisions often described the project itself as an evidence-authorized,
crash-consistent convergence engine. That was an inversion of ends and means.
Exact history, durable receipts, bounded work, explicit capabilities, and
fail-closed recovery are valuable implementation constraints. They are not the
reason the product exists. They should make a Resilio replacement dependable;
they must not consume the roadmap while ordinary synchronization remains absent.
Historical documents remain unchanged as lineage, but their mission statement is
superseded by this revision.

## Product baseline

The current official Resilio Sync product surface advertises the capabilities a
replacement must be judged against: automatic folder synchronization across
devices, direct peer-to-peer transfer of large files, selective-sync placeholders,
changeable read/write permissions, bandwidth controls, desktop/mobile/NAS reach,
and operation without storing user content in a third-party cloud. Resilio's
broader product material emphasizes resilient peer-to-peer movement, routing
around failures, and set-it-and-forget-it operation.

Sources observed for this audit on 2026-07-27:

- <https://www.resilio.com/sync/>
- <https://www.resilio.com/sync/download/>
- <https://www.resilio.com/>
- <https://www.resilio.com/active-everywhere/>

Those pages are marketing and product documentation rather than a protocol
specification, but they are sufficient to reject a dangerously narrow definition
of success. A one-shot authenticated file RPC is useful infrastructure; it is not
a Resilio replacement.

## Acceptance model for an actual replacement

A credible first general-purpose release needs all of the following to work as one
service, not as unrelated assurance demonstrations:

1. **Persistent folder ownership.** Configure one or more local roots and keep
   them synchronized while the service runs and across restarts.
2. **Recursive filesystem semantics.** Files, directories, deletion, rename,
   symlinks or an explicit symlink policy, timestamps, permissions, ownership,
   sparse files, case rules, and platform-invalid names need deterministic
   behavior.
3. **Bidirectional and multi-peer convergence.** Every authorized peer can make
   changes; conflicts are visible and recoverable; offline peers catch up later.
4. **Large-file efficiency.** Content is transferred in authenticated blocks with
   resume, deduplication, bounded memory, and no whole-file restart after an
   interrupted route.
5. **Connectivity.** Known peers, LAN discovery, optional rendezvous/tracker
   discovery, NAT traversal, and relay fallback exist for ordinary IP operation.
   Tor and I2P are native alternatives with route-specific publication and
   dialing.
6. **Selective synchronization.** A device can retain metadata/placeholders and
   fetch chosen content on demand without pretending absent bytes are complete.
7. **Access and key lifecycle.** Folder invitations, read-only/read-write roles,
   peer revocation, identity rotation, and recovery are operationally usable.
8. **Service behavior.** Startup, shutdown, configuration reload, retry/backoff,
   bandwidth limits, health, logs, metrics, and upgrades are predictable.
9. **Cross-platform usability.** At minimum Linux, Windows, and macOS need a
   coherent daemon and management surface; mobile/NAS can follow.
10. **Privacy modes.** Direct, Tor, and I2P routes are selectable per peer or per
    folder, and an anonymity profile does not quietly leak through DNS, LAN
    discovery, direct fallback, remote plaintext proxies, or telemetry.

The current repository satisfies only a narrow subset. The gap should be visible
in every roadmap and release gate.

## What rev0908 implements

### A route is now separate from TLS and peer identity

Before rev0908, the shipping TLS client created and connected a numeric TCP socket
itself. This made direct IP an architectural assumption rather than one route.
Adding `.onion` or `.i2p` strings to that endpoint structure would either invoke
process DNS, fail numeric parsing, or force route protocol details into the TLS
owner.

Rev0908 introduces `SyncReplicaStreamConnector`. It owns only establishment of
one reliable nonblocking byte stream. The existing TLS 1.3 mutual-authentication,
expected actor/SPKI policy, file request, receipt, and durable application remain
unchanged above it. This separation is important for product evolution:

- a peer identity is not an IP address, onion name, or I2P destination;
- the same peer can eventually advertise several routes;
- route selection can become scheduler policy without weakening TLS identity;
- connection telemetry can be route-specific without exposing application
  secrets; and
- future relay, QUIC, or pluggable transports need not fork the file protocol.

The original numeric endpoint overload remains as a compatibility wrapper over a
one-shot direct connector, preventing an immediate split between old tests and the
new product path.

### Direct TCP

Direct routing accepts only numeric IPv4 or unscoped IPv6 endpoints. It retains
the existing no-process-DNS policy, nonblocking socket, close-on-exec proof, one
absolute connect deadline, and typed failure result.

This is not yet ordinary consumer connectivity. There is no peer discovery, NAT
mapping, hole punching, relay, IPv6 scope support, DNS-based configured peers, or
Happy Eyeballs policy. Numeric-only direct dialing is acceptable as a secure
primitive, not as the final Resilio-compatible user experience.

### Tor outbound

Tor outbound routing performs SOCKS5 username/password negotiation with a local
numeric proxy and sends the remote service as a domain-name request. The process
resolver never observes the `.onion` name. The connector requires:

- one canonical lowercase v3 onion service;
- the 56-character service label, `.onion` suffix, v3 version byte, and checksum;
- a nonzero virtual service port;
- a loopback SOCKS endpoint; and
- a bounded visible isolation token.

The SOCKS username is the current Tor format-zero extension
`<torS0X>0`, and the password is the command isolation token. A random 32-byte
hex token is created when the operator does not provide one. This separates
AnonSync command circuits without relying on legacy SOCKS-auth interpretation.

Official source:

- <https://spec.torproject.org/socks-extensions.html>

The v3 checksum validation is not cosmetic. A base32-looking 56-character string
can still be a typo or fabricated identity. Sending it first and trusting a SOCKS
failure would spend routing authority, produce misleading diagnostics, and make
configuration errors look like peer outages.

### Tor inbound

`serve-one` and `serve-batch` accept a Tor publication profile. The C++ receiver:

- validates the checksum-bearing v3 onion identity and virtual port;
- requires its actual TLS listener to be loopback; and
- reports the selected publication mode without printing route secrets.

The Tor daemon remains the explicit onion-service publication owner. Rev0908 does
not connect to Tor's ControlPort, create an ephemeral onion service, inspect the
published service key, or prove that the configured onion actually maps to the
listener. This is a safe and useful intermediate boundary, not complete native
onion-service lifecycle ownership.

### I2P outbound through SAM 3.1

I2P is implemented through SAM 3.1, the documented interface intended for
non-Java applications. One command-local connector lazily creates and retains a
STREAM session on its control socket. Every delivery uses a fresh data socket,
performs its own HELLO, and issues `STREAM CONNECT` for the configured remote
I2P destination.

The route carries explicit inbound/outbound tunnel quantities and requests
ECIES-X25519 lease-set encryption. A transient session requests Ed25519
`SIGNATURE_TYPE=7`. A persisted destination does not: the SAM specification
allows that option only when the bridge generates a transient destination, and a
saved private destination already embeds its signature type.

The minimum/default I2P stage timeout is 180 seconds. SAM documentation notes
that stream connection alone may consume approximately a minute and tunnel
construction can also be slow. The earlier ordinary-TCP-scale timeout would have
made healthy I2P look unavailable. Batch admission also refuses to begin a new
I2P session when less than one complete I2P stage budget remains.

Official source:

- <https://geti2p.net/en/docs/api/samv3>

### I2P inbound through native STREAM FORWARD

The receiver can now own an inbound I2P service for its bounded lifetime. It
creates and retains:

1. a SAM control socket carrying the persistent STREAM session; and
2. a SAM forwarding socket carrying `STREAM FORWARD` to the receiver's loopback
   TLS listener.

`SILENT=true` is mandatory. Without it, SAM prefixes each forwarded TCP child
with the remote I2P destination line. The TLS server would parse those ASCII bytes
as a TLS record and fail before peer authentication. The bridge and local target
must both be loopback.

The I2P destination is persistent rather than transient for inbound use. The
private destination file enters through a new reusable secret-file boundary:

- absolute path;
- no final symlink;
- bounded exact read;
- regular file;
- effective-user ownership;
- exactly one link;
- exact POSIX mode `0600`; and
- stable identity/access policy across the read.

The Windows implementation fails closed because an equivalent owner-only DACL
proof is not yet implemented. This limitation matches the current Linux-only
exact socket connector rather than silently weakening secret admission.

### Retained-session health

SAM sessions exist only while their control socket remains live. Reusing a dead
control descriptor would make every later batch connection fail in confusing
ways. Before reuse, the connector checks the retained socket without consuming
bytes. EOF, terminal socket error, or unexpected queued protocol bytes mark the
session stale. The connector discards it and returns the current attempt as a
route failure. A later bounded session may create a new session; the connector
does not secretly retry inside the ambiguous attempt, sleep, or extend a deadline.

The distinction matters. Recovery is caller-authorized on a new session boundary,
not an invisible loop beneath the product supervisor.

## Severe findings corrected in this revision

### 1. Product mission was misdeclared

The README and release gate called AnonSync an evidence-authorized convergence
engine and explicitly said its mission was not ordinary file copying. That was
wrong. The README now states the replacement mission directly. The release gate
must do the same. Historical evidence remains available, but future work should be
measured against product capability.

### 2. Numeric direct TCP was embedded in the TLS client

This was the principal route blocker. It made Tor/I2P an afterthought and would
have encouraged hostname resolution or duplicated TLS implementations. The typed
stream connector removes that coupling.

### 3. Tor address syntax was accepted without cryptographic checksum proof

Canonical length/base32 alone is insufficient for v3 onion identity. Full version
and checksum validation now happens before network work.

### 4. Plaintext proxy protocols could have been sent to remote endpoints

SOCKS5 username/password and SAM commands expose destinations and session
material on the local-proxy hop. Both proxy endpoints are now loopback-only until
AnonSync owns an authenticated encrypted remote-proxy channel.

### 5. Persisted SAM destinations received an invalid option

The first implementation added `SIGNATURE_TYPE=7` to every `SESSION CREATE`.
Official SAM documentation makes it transient-only. Persisted identities now omit
it, and a regression test checks the exact command.

### 6. Stale SAM control state poisoned later work

A retained control socket was initially trusted solely because the descriptor
object existed. It is now liveness-checked and invalidated fail-closed.

### 7. Ordinary TCP deadlines were applied to I2P

Ten seconds is not a viable tunnel/session default. I2P now has a 180-second
minimum and command-budget admission.

### 8. Inbound SAM could corrupt the TLS stream

`STREAM FORWARD` defaults to `SILENT=false`, which injects peer text ahead of
application data. Native inbound forwarding forces `SILENT=true` and the process
test verifies the exact command.

### 9. A long-term I2P identity could be read from weak storage

The initial implementation used the ordinary bounded reader. Rev0908 adds and
uses a private-file reader with owner, link, and mode proof.

### 10. Sender JSON contained a duplicate key

`send-one` emitted `transport` twice. Duplicate JSON keys have parser-dependent
meaning and can mislead operators or automation. The duplicate is removed.

## Test architecture

### Connector-level C++ tests

`anonsync_sync_replica_stream_connector_test` uses local modeled peers and checks:

- direct connection and numeric policy;
- loopback recognition across IPv4 `127/8` and IPv6 `::1`;
- rejection of remote SOCKS/SAM endpoints;
- valid and invalid Tor v3 checksums;
- exact SOCKS5 method, username/password, address, and reply handling;
- SAM HELLO version pinning;
- transient and persisted SESSION CREATE command construction;
- outbound STREAM CONNECT;
- retained-session reuse and stale-session recovery;
- inbound STREAM FORWARD with `SILENT=true`;
- route-token validation;
- typed SAM result mapping; and
- expired setup with no hidden retry.

### Shipped-executable process tests

`test_anonsync_replica_anonymous_routes.py` does not stop at a connector mock. It
bootstraps real sender and receiver deployments, TLS certificates, membership,
clock state, payloads, and outbox operations, then runs the shipped CLI through:

- a fake Tor SOCKS5 bridge that verifies the v3 target and format-zero isolation
  credentials and relays the real TLS stream;
- a fake outbound SAM bridge that verifies HELLO, SESSION CREATE, and STREAM
  CONNECT and relays the real TLS stream;
- a validated Tor receiver profile over a loopback TLS target; and
- a fake inbound SAM bridge that verifies the persisted identity and exact
  `STREAM FORWARD ... SILENT=true` command, then models an I2P peer connecting to
  the real TLS listener.

Each successful lane checks exact destination file bytes, authenticated peer
identity, application receipts, and safe route telemetry. Parser/admission tests
also prove rejection of nonloopback proxies, missing persistent inbound identity,
short I2P deadlines, and contradictory batch budgets.

This remains a modeled-proxy proof. A subsequent integration lane should run
against real current Tor and at least one Java I2P and i2pd implementation in an
isolated test environment. That would test protocol interpretation, tunnel
construction, address publication, and shutdown behavior that a fake bridge
cannot prove.

## What remains missing, prioritized against the real mission

### P0: required before anyone can replace Resilio for normal folder sync

1. **Long-running service.** The bounded `send-*` and `serve-*` commands are
   building blocks, not `anonsyncd`. There is no persistent configuration owner,
   graceful shutdown, reload, retry/backoff, or restart-resume service loop.
2. **Recursive scanner plus watcher.** There is no continuous filesystem
   observation. Watcher events should be hints; periodic full scans must repair
   missed events and establish a deterministic catalog.
3. **Folder/catalog reconciliation.** Peers cannot exchange a scalable catalog,
   determine all missing/newer entries, or repeatedly converge a folder.
4. **Complete filesystem operations.** Directory creation, tombstones, deletion,
   rename, symlink policy, metadata, case collisions, Unicode normalization,
   reserved names, and permission semantics are not product-complete.
5. **Block protocol and resume.** Current payload delivery is effectively one
   bounded file operation. A Resilio replacement needs fixed or content-defined
   authenticated blocks, availability maps, partial durable files, resume, and
   final whole-file verification.
6. **Multiple peers and routes.** There is no peer directory, route set,
   connection scheduler, fairness, per-peer backoff, health score, or concurrent
   transfer policy.
7. **Ordinary Internet connectivity.** There is no LAN discovery, rendezvous,
   NAT traversal, port mapping, hole punching, or relay fallback.

### P1: required for practical replacement breadth

- selective-sync metadata and placeholders;
- read-only/read-write folder roles and invitation UX;
- bandwidth and schedule controls;
- version history/trash/recovery policy;
- conflict presentation and operator resolution;
- permissions, ownership, xattrs/ACLs, sparse files, and platform mappings;
- service installation, configuration file format, status, logs, metrics, and
  upgrades;
- remote peer enrollment and key rotation; and
- efficient catalog indexes and retention/garbage collection.

### P2: parity and ecosystem

- desktop UI and filesystem-shell integration;
- mobile clients and camera backup;
- NAS packaging;
- relay/rendezvous deployment tooling;
- fleet administration and API;
- remote selective fetch; and
- polished migration from existing Resilio folder layouts.

## Tor/I2P-specific gaps

### Tor

- No ControlPort ownership or authenticated ephemeral onion-service creation.
- No proof that the configured onion identity maps to the active loopback
  listener.
- No onion key generation/import/rotation command.
- No pluggable-transport or bridge configuration surface.
- No route-specific retry and circuit-health policy.
- No anonymity profile that automatically disables LAN discovery, direct
  fallback, and destination-bearing telemetry.

### I2P

- No private-destination generation, export, import, rotation, or public-address
  display command.
- No naming-system resolution policy distinct from raw b32/base64 destinations.
- No real-router compatibility matrix across Java I2P and i2pd.
- No tunnel warm-up/readiness lifecycle beyond one bounded setup attempt.
- No destination-port policy or multiplexed folder services.
- No encrypted/authenticated remote SAM bridge support.

### Metadata reality

Tor and I2P route content through anonymity networks; they do not automatically
hide all metadata. TLS certificates, stable application peer IDs, folder
identifiers, message sizes, timing, transfer volume, local filesystem behavior,
and endpoint configuration can still identify or correlate users. AnonSync needs
separate documented threat profiles:

- **private transport:** content protected in transit;
- **hidden endpoint:** no direct peer IP disclosure;
- **route-isolated:** no direct/LAN fallback and per-peer or per-folder circuit
  isolation;
- **metadata-minimized:** padded/chunk-scheduled traffic and minimized stable
  identifiers; and
- **high-latency anonymous:** delays, cover traffic, or batching where traffic
  analysis matters.

Only the first two are partially approached here. Claims should remain narrow.

## Recommended architecture from here

The next product code should be organized around explicit runtime owners rather
than extending `anonsync_replica.cpp` indefinitely:

- `FolderConfigurationStore`: folders, peers, route sets, roles, limits.
- `FolderScanner`: recursive deterministic snapshots and watcher reconciliation.
- `ChangeJournal`: durable local filesystem intents and tombstones.
- `PeerDirectory`: stable peer identity separated from route advertisements.
- `CatalogProtocol`: version/index exchange and missing-work derivation.
- `BlockStore` and `BlockTransferProtocol`: hashes, partials, resume, dedupe.
- `TransferPlanner`: fairness, dependency readiness, per-peer concurrency,
  bandwidth, and route selection.
- `RouteDialer`: the rev0908 direct/Tor/I2P connector family.
- `InboundPublisher`: direct listener, Tor service owner, I2P service owner.
- `ApplyEngine`: atomic file/metadata/delete/rename effects and conflict policy.
- `FolderSupervisor`: service lifecycle, shutdown, backoff, checkpoint, status.

The existing SQLite and exact-evidence components can back these owners. The key
change is sequencing: product behavior defines the vertical slice, and assurance
proves that slice. Assurance should no longer create a parallel roadmap.

## Highest-value next C++ slice

Implement a minimal persistent `anonsyncd` service for one configured folder and
one or more peers:

1. load one versioned configuration containing folder root, local identity, peer
   identities, and ordered route sets;
2. perform a recursive initial scan;
3. subscribe to filesystem watcher hints while scheduling periodic full scans;
4. durably journal create/modify/delete operations;
5. run the existing bounded sender/receiver sessions under explicit retry,
   backoff, and shutdown policy;
6. persist peer route health without treating it as identity;
7. resume after process crash; and
8. expose a compact status command showing scan state, pending files, peers,
   selected routes, last success/failure, and retry deadlines.

That slice will still transfer whole files, but it will finally behave like a
small synchronization product. The following slice should replace whole-file
payloads with a block protocol and durable partial resume. These two slices are
more important to the replacement mission than another broad standalone
assurance family.

## Conclusion

Rev0908 corrects the project's stated purpose and removes the most immediate
architectural barrier to Tor and I2P. The real C++ file protocol now traverses
direct TCP, Tor SOCKS5, and I2P SAM without weakening application TLS identity.
Inbound I2P service forwarding is native, inbound Tor configuration is validated,
and several protocol/security defects were found and corrected during the
refactor.

This is meaningful progress, but route support is only one subsystem. AnonSync is
not yet a Resilio replacement. The repository should now optimize for continuous
folder synchronization, service operation, blockwise resume, discovery, and
multi-peer usability, with its unusually strong correctness work serving those
features rather than defining a different mission.
