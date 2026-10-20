# Architecture

This document describes the current AnonSSH product architecture. The
[specification ledger](../../specs/spec_ledger.json) is authoritative for claim status
and exit conditions; [bond-protocol.md](bond-protocol.md) owns wire and runtime
semantics; [evidence.md](evidence.md) owns campaign interpretation. Architecture
decisions and their rationale live under [`docs/adr/`](../adr/INDEX.md).

## Product model

AnonSSH is a recovery-oriented SSH product built around a reusable striped byte
transport. A password plus a stable machine ID deterministically reconstructs:

- the SSH client and host keys;
- the primary Tor and I2P destinations;
- per-slot Tor and I2P bond destinations; and
- the bond authentication key.

The password and machine ID are therefore the recovery entry point, not a locator for a
mutable account database. OpenSSH accepts only the derived client key and derived host
key. Route, identity, and host-trust overrides fail closed.

The default server publishes a bonded endpoint and compatible direct Tor and I2P
recovery endpoints. The default client asks its resident broker to race authenticated
mixed, Tor-only, and I2P-only bonds with delayed direct recovery candidates. Each
candidate has an independent deadline. One winning byte stream reaches one OpenSSH
process; losing work is cancelled. Tor slot 1 owns one onion service with separate
direct-SSH and bonded-ingress port mappings, avoiding duplicate publication of the same
key.

SSH is one consumer of the bond rather than its organizing abstraction. Named local TCP
forwarding and public Rust streams use the same transport. General SOCKS, TUN,
system-wide interception, and Unix-socket forwarding are outside the current product
boundary. SSH-compatible remote commands are implemented for the tested rsync, Git,
Borg, scp, SFTP, SSHFS, and generic-command subset. The owner-only ALP1 local transport
core now authorizes named
targets in broker memory and opens independent classed streams to static symbolic peer
services. Mixed packaged overlay evidence is complete; dynamic registration,
homogeneous-overlay evidence, and language clients remain unfinished. Both application
boundaries are specified in
[application-interfaces.md](application-interfaces.md).

## Workspace

The workspace has three Rust crates:

- `anonssh-bond` is the runtime-independent ABP frame, topology, flow-control,
  reassembly, sender, scheduler, capability, and adaptive-control core.
- `anonssh-bond-tokio` adds mutually authenticated lane formation, encrypted records,
  generic reliable-stream I/O, multi-stream sessions, and the public `BondDialer`,
  `BondListener`, `BondSession`, and `BondedStream` API.
- `anonssh-cli` is both the `anonssh` binary and a library of product providers. It owns
  identity derivation, configuration, Tor SOCKS/control, I2P SAM, embedded runtimes,
  managed router pools, the resident broker, server ingress, OpenSSH/Dropbear adapters,
  service lifecycle, diagnostics, bootstrap curation, and embedded/live tests.

SSH banner handling exists only in direct proxy code. Neither bond crate parses SSH or
terminal data.

## Runtime ownership

### Client

One private per-user broker owns the client router pool and a bounded registry of
destination sessions. Concurrent commands for the same exact destination, topology,
resource profile, and bond key reuse one authenticated session but open independent
logical streams. A wrong password cannot borrow an unlocked session. Different
destinations receive different sessions while sharing physical router slots when
policy permits.

An on-demand broker exits after a bounded idle period. `anonssh broker start` and the
installed user service keep it resident. The broker owns its Unix socket and lease,
reclaims stale local control state, and reports structured status rather than relying on
log scraping.

The broker's existing Unix socket is a private control and ProxyCommand transport. It
accepts internal destination and key material and is not a public application API. The
implemented ALP listener is a separate versioned owner-only socket: applications name an
already authorized target and symbolic service, receive one bounded setup result, and
then use one raw independent bond stream. Publishing ALP requires peer service
capability negotiation and exact local service policy; it cannot be implemented by
stabilizing the private broker request enum.

### Server

One persistent ingress owns server publications and classifies authenticated first
lanes, additions, and replacements into bounded independent sessions. Only a declared
provider representative may create unknown-session state; one unknown-session decision
is serialized so competing discovery providers cannot split one session. Known sessions
accept only policy-declared inactive lanes with the expected provider, lane ID, failure
domain, protocol version, and server incarnation.

Each accepted `Interactive` bond stream receives its own Dropbear backend connection.
Failure or backpressure on one SSH stream therefore does not terminate or head-of-line
block sibling SSH streams. Publication lifetime belongs to ingress rather than any one
session, so repairing one client cannot unpublish a destination used by another.

Every accepted ABP v6 product stream carries an encrypted bounded symbolic-service
preface. The reserved `ssh` service requires `Interactive` class and relays to Dropbear;
other statically configured names connect to owner-private Unix sockets under a bounded
per-service concurrency limit. The server validates the configured socket before and
the connected peer UID after every connect. It never accepts a peer-selected host,
port, or filesystem path. Legacy sessions remain SSH-only.

### Resident service

The Linux lifecycle installs two user-systemd units: a non-expiring broker and a
recovery server. They use disjoint endpoint ranges and persistent router roots, an
absolute packaged launcher, frozen validated configuration, `Restart=on-failure`, and a
two-second restart delay. Runtime unlock keeps an owner-only credential only for the
current login. Persistent unattended credentials are explicit and owner supplied. The
installer rejects linked or shared state and service executables writable by another
user; third-party router and SSH children do not inherit identity-secret environment
variables.

The resident warm controller prepares local overlay substrate, not target-specific bond
sessions. A target session cannot exist until the destination descriptor and
password-derived key are known. Warm floors and ceilings come from the resource profile;
recent demand, startup cost, memory pressure, and active global demand determine what
surplus remains running.

## Product topology

The normal mixed plan declares sixteen candidate lanes:

- lanes 1-8 use eight independent Tor slots; and
- lanes 9-16 use eight independent i2pd slots.

Each slot has a stable state root, local router endpoint, deterministic destination, and
failure-domain label. A Tor slot may race one primary and one reserve router during
startup, but only the fully bootstrapped winner survives and the slot remains one
failure domain. A healthy explicitly declared external Tor service or occupied I2P SAM
service can replace an owned router without changing slot policy.

The mixed required baseline is lanes 1, 2, 9, and 10. Tor-only lanes 17-24 and I2P-only
lanes 25-32 form disjoint eight-candidate plans with four required lanes. The disjoint
authenticated namespaces commit both peers to one topology. A mixed formation races the
first Tor and I2P representatives and activates after either authenticates; all other
declared lanes start inactive and join progressively. This converts slow provider
startup into reduced initial capacity rather than a login-wide barrier.

Every slot has an independent supervisor with bounded exponential backoff. Router
startup, publication, lane authentication, repair, and drain are cancellation safe. A
slow I2P attempt does not serialize Tor or another I2P slot. Replacement authenticates a
new generation before retiring the failed generation when possible.

## Adaptation and resources

Candidate count and active count are deliberately different. The built-in profiles cap
active product lanes at 4, 8, or 16; the default performance profile permits sixteen but
does not request sixteen. A separate 16+16 plan exercises the protocol's 32-lane bound
only in explicit high-resource campaigns.

Each session controller retains one bounded exponentially weighted prior per declared
lane. Observations cover delivered goodput, queue delay, startup time, CPU, RSS, health,
and confidence. It can:

- admit provider-balanced batches under sustained queue, sender-window, or application
  pressure;
- immediately replace unhealthy or materially inferior paths;
- retain useful capacity through an activation/observation dwell;
- retire marginal lanes only after repeated quiet evidence; and
- periodically explore one stale or under-observed optional path.

Minimum topology, provider diversity, required anchors, two protected lanes, active
dwell, and endpoint resource ceilings remain hard constraints. Pressure can shorten the
control cadence; quiet scale-down remains deliberately slow. Started but not-yet-active
speculative cohorts are cancelled when pressure disappears.

One endpoint-wide resource governor is authoritative for physical-slot admission across
sessions. A shared router is charged once. Live CPU/RSS cost uses conservative endpoint
observations while useful goodput and pressure aggregate across dependent sessions.
Required baseline registration is atomic; optional reservations roll back if encrypted
topology publication fails. A router can stop only after its final logical claimant
releases it.

Peers exchange authenticated cumulative capability snapshots under ABP v4 and later.
Provider availability, candidate/ready counts, lane/session ceilings, CPU/RSS policy,
startup estimates, queue delay, and delivered goodput define the useful bilateral
intersection before optional supervisors launch. Capabilities cannot authorize an
endpoint, weaken topology policy, or exceed either endpoint's local limit.

## Data plane

Applications open `Control`, `Realtime`, `Interactive`, or `Bulk` logical streams.
Streams have independent lifecycle and receive credit. A flow-controlled writer waits
on lossless actor progress notifications rather than timer polling; a paused reader
withholds its own receive credit without preventing the coordinator from draining lane
events or progressing sibling streams.

The scheduler predicts delivery from smoothed lane rate, RTT, queued bytes, health, and
failure domain. Bulk is assigned by earliest predicted delivery, not round robin. New
bulk chunk size adapts between 16 and 64 KiB from lane bandwidth-delay product and queue
delay. Selective-acknowledgement gaps and retransmission reduce a session pressure cap;
clean cumulative delivery restores it gradually. Retained chunks are immutable and are
never re-chunked during recovery.

Every eligible bulk lane receives a bounded probe budget at activation, restoration,
and a fixed reprobe interval. Between probes, useful traffic follows predicted delivery
time. This lets a later-improving path re-enter without forcing equal provider shares or
reducing the bond to its weakest lane.

Two healthy low-RTT lanes form the protected pool. When both providers are available,
one protected lane comes from each; homogeneous bonds use two independent lanes.
Control, explicit `Realtime`, and `Interactive` chunks up to 2 KiB avoid bulk backlog.
Eligible data races a primary plus one best-effort shadow copy; both copies share one
offset, payload allocation, and sender charge. First authenticated arrival wins and the
duplicate is eliminated. Bulk is not replicated. With fewer than three active lanes,
availability wins and bulk may use protected capacity.

This is physical path racing, not terminal prediction. External OpenSSH makes terminal
semantics opaque to the bond. ADR 0003 rejects blind local echo and defines consistent
delivery, contention isolation, warm reuse, and tail control as the transport goals.

## Hot path

Application payload uses shared immutable slices through sender retention, lane queues,
and retransmission. A writer builds and encrypts one final record buffer in place using a
retained self-zeroizing AEAD context. A reader decrypts in place and decodes owned
slices. In-order data bypasses the reorder tree; only genuinely out-of-order data creates
bounded map state.

The runtime reuses dispatch, acknowledgement-range, released-chunk, and delayed-control
scratch. Delayed acknowledgements and receive-window updates batch by byte threshold
with a bounded timer fallback; the timer is armed only when work exists. Scheduler lane
and chunk selection use bounded scalar scans and no per-decision heap scratch. One
plaintext-to-ciphertext materialization remains intentional because plaintext must stay
available for cross-lane retransmission.

## Failure and recovery

Each lane carries encrypted Ping/Pong liveness records. A probe deadline starts only
after its writer confirms transmission, so queueing behind an in-progress record cannot
declare a healthy lane dead. RTT samples update scheduling. Retained payload uses four
smoothed RTTs with a two-second floor and thirty-second product ceiling instead of one
fixed retransmission delay.

Lane failure immediately makes retained chunks eligible elsewhere without changing
stream offsets. The session replays cumulative authenticated stream-open, receive-credit,
half-close, topology, and session-close state over a surviving or replacement lane.
Exact duplicates are idempotent; conflicting replay fails closed. A temporary zero-lane
session retains bounded protocol state and applies backpressure while supervisors repair
it. Thirty seconds with no active product lane is terminal so a later request can form a
clean session.

Process loss is a different boundary. Owned Tor, i2pd, and Dropbear children use ordinary
cleanup plus Linux parent-death signaling. ABP v5 and later authenticate one server-process
incarnation across every lane, preventing a restarted server from being spliced into old
volatile state. Existing SSH streams terminate when their broker or server dies; a new
process reclaims endpoints and stale local control state, reuses persistent router roots,
republishes deterministic destinations, and serves new connections. Monotonic deadlines
ignore wall-clock corrections; suspend may expire a transmitted unanswered probe but
cannot expire a probe that never left its queue.

## Persistent state

Router state survives commands and product restarts because Tor bootstrap and especially
I2P profiles improve with retained operation. It is never deleted automatically. State
quota is a health and new-admission boundary: established sessions can continue, but new
destination allocation fails closed while over quota.

The private runtime cache contains content-addressed embedded program payloads and
ephemeral SSH client/server runtime files. Derived server authorization and host-key
material lives under the private XDG state hierarchy so Dropbear never has to trust a
possibly shared cache parent; it is still removed when the server stops. A no-symlink
walk may remove only old non-current payload roots,
first by retention and then oldest-first to satisfy quota. Current payloads and router
roots are ineligible. Derived SSH and trust files are removed after their operation.
Router stdout/stderr is drained into a bounded redacted in-memory tail rather than
unbounded log files.

The portable x86-64 release carries Tor, i2pd, OpenSSH, and Dropbear as six static child
program payloads. The Nix-integrated Monsternix product compiles the same Rust code with
those payloads absent and wraps it with exact caller-selected Nix store paths instead;
its runtime cache therefore never extracts child programs. The former is independently
copyable, while the latter is smaller and deliberately depends on its system closure.
Both retain the embedded public I2P bootstrap corpus and identical protocol behavior.

## I2P bootstrap

Fresh owned i2pd instances receive verified public RouterInfo hints before startup. The
repository observer records a stable public router identity only when at least two
mature local routers have both current RouterInfo and positive peer-profile evidence.
At most one observation day is added per UTC day; absent identities remain in the
ledger. Profiles, private keys, destinations, source-local scores, configuration, and
address books are never shipped.

Longevity and current usefulness are separate. Three observation days spanning seven
days qualify an identity; the newest currently corroborated signed RouterInfo provides
its time-sensitive addresses. There is no corpus-size ceiling. Runtime validation rejects
unexpected paths, symlinks, malformed records, duplicate identities, excessive sizes,
and digest mismatches before no-overwrite import. i2pd remains responsible for signature,
network, address, and age validation. Ordinary certificate-verified reseeding remains
enabled, so embedded RouterInfos are disposable bootstrap hints rather than trust roots.

The promoted v3 corpus contains 636 identities satisfying this policy and passed a
reseed-disabled fresh-state product login on 2026-10-19. The dated observation snapshot,
selection result, and continuing collection procedure are in
[evidence.md](evidence.md#longitudinal-i2p-evidence); the implemented contracts and exit
conditions remain in the specification ledger.

## Security boundaries

Every lane performs mutual bond-key authentication and an ephemeral ML-KEM-768 exchange.
The transcript and lane nonces feed HKDF-SHA-256; each direction uses independent
ChaCha20-Poly1305 keys and monotonic record counters. There is no plaintext or downgrade
mode. Provider endpoints and topology actions require exact local authorization.

Custom protocol means AnonSSH owns multipath semantics, not cryptographic primitives.
The RustCrypto ML-KEM-768 implementation follows FIPS 203. The product does not claim
transparent survival of an existing SSH stream across process replacement, predictive
terminal echo, arbitrary network exit, Unix-socket forwarding, dynamic ALP service
registration, or an AArch64 release. SSH remote-shell compatibility is limited to the
tested subset; compatibility with another SSH-based tool is not implied until its stock
client passes an end-to-end campaign.
Static-service ALP is implemented and mixed-overlay proven; homogeneous overlays and
language clients retain separate explicit proof boundaries.
