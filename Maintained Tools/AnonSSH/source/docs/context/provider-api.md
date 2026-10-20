# Bond Provider API

`anonssh-bond-tokio` exposes the bonded byte transport without requiring an application
to assemble `AuthenticatedLane` or `RuntimeLane` values. `BondDialer` and
`BondListener` own provider lookup, deadlines, mutually authenticated lane joins,
same-session and same-version validation, runtime construction, dynamic addition and
replacement, progress, and cancellation cleanup. They return ordinary `BondSession`
values; applications open independent `Control`, `Realtime`, `Interactive`, or `Bulk`
`BondedStream` values on those sessions.

This document owns the reusable provider boundary. Product router supervision and
resource ownership are described in [architecture.md](architecture.md); ABP wire and
runtime behavior is described in [bond-protocol.md](bond-protocol.md).

This API is for Rust software that wants to own providers or sessions. Applications
that only want product-managed bonded byte streams should not reimplement this layer;
the implemented ALP1 local protocol exposes that service through the resident broker as documented
in [application-interfaces.md](application-interfaces.md).

## Provider Boundary

Providers are deliberately small object-safe traits:

- `LaneDialProvider` connects one explicit endpoint and returns reliable asynchronous
  byte I/O. Its atomic initial-payload operation defaults to connecting, then writing
  and flushing the supplied bytes before returning.
- `LaneListenProvider` binds one explicit endpoint and returns a `LaneAcceptor`.
- `LaneAcceptor` reports the concrete bound endpoint and accepts one reliable stream at
  a time.

Provider type does not confer authorization. A `ProviderPolicy` is an exact allowlist
of `ProviderLane` values and allowed topology actions, plus hard lane and operation
parallelism limits. A remote topology descriptor must match lane ID, failure domain,
provider, and endpoint before any connection is attempted. Unknown providers,
endpoints, actions, descriptor multiplicity, and configuration changes fail closed.

`LoopbackTcpProvider` accepts numeric loopback socket addresses and rejects DNS names,
wildcard addresses, non-loopback addresses, and port zero on dial. On bind,
`tcp://127.0.0.1:0` or its IPv6 equivalent may resolve only to a nonzero port on the same
loopback address. This gives tests and local adapters race-free sockets without turning
the library into an arbitrary TCP proxy.

The `anonssh` library supplies real provider adapters over the same traits:

- `TorSocksDialProvider` connects an exact `tor://` endpoint through one loopback SOCKS
  listener, while `TorOnionListenProvider` publishes only preconfigured onion/key/port
  bindings through authenticated loopback Tor control.
- `I2pSamDialProvider` owns one recoverable SAM session and connects exact `i2p://`
  endpoints. It overrides atomic initial-payload delivery so SAM receives the bytes in
  `STREAM CONNECT` before reporting success and making the peer stream acceptable.
  `I2pSamListenProvider` publishes only preconfigured destination/session/private-key
  bindings.

Private material is redacted from `Debug`, is never put in topology descriptors, and
listener provider lookup is an exact map. Router executable discovery, process
supervision, persistent state, warming, and machine-wide resource policy deliberately
remain application concerns; they are not properties of a byte-lane provider.

## Formation

The listener binds every authorized candidate before the dialer policy is built. The
application reads `bound_lanes()`, distributes only those concrete descriptors through
its authenticated control plane, and creates the dialer's exact policy from them. The
dialer chooses a fresh nonzero session epoch and opens the selected lanes with bounded
parallelism. `BondDialer` prepares each authenticated client hello first and gives it to
the provider as the connection's initial payload; it never writes a duplicate hello
after the provider returns. This is equivalent to an immediate write for TCP and Tor,
but prevents the SAM connect/accept ordering deadlock for I2P. The listener authenticates
each selected lane without trusting a plaintext session hint, then requires one epoch,
one protocol version, unique lane IDs, and the configured failure domains through
`LaneJoinRegistry`. Only the complete valid set selected for that formation call enters
`BondSession::spawn`; an application may deliberately activate from one policy-authorized
lane and add other candidates later through dynamic topology. One `BondListener` also
owns one random nonzero ABP v5-or-later server
incarnation for its entire lifetime. Initial, added, and replacement lanes therefore
identify the same listener process; callers that supervise a remote product can compare
that authenticated value and reject attempts to splice a restarted listener into
volatile session state.

Listener admission and dynamic lane acceptance share one admission lock. Repeated
sessions are supported serially; two callers cannot consume different lanes of the same
formation. A deployment needing concurrent admission should put an authenticated
single-lane demultiplexer in front of per-session listeners rather than relaxing this
invariant.

## Dynamic Topology

`BondListener::advertise_and_accept_lane` emits one encrypted monotonic descriptor and
accepts its authenticated stream. `BondDialer::apply_next_topology` receives that
descriptor, applies local exact policy, and dials it. Additions are declared only after
authentication succeeds. Replacements establish and authenticate the new provider
stream before failing the old runtime generation, minimizing interruption while still
letting the runtime reject a changed failure domain or protocol version. Drains carry no
endpoint connection and simply retire the authorized lane.

Only one topology mutator should operate on a given session at a time. Generation
ordering and replay rejection remain enforced by the encrypted runtime control plane.

## Progress And Cancellation

`subscribe_progress()` returns a bounded broadcast receiver for live UI or telemetry.
`progress_snapshot()` retains the latest 128 ordered events, including bind, bound,
dial, accept, authentication, active, add, replace, drain, rejection, cancellation,
session activation, and shutdown phases. Events contain only lane ID, provider, and the
explicit configured endpoint; providers must avoid putting credentials in endpoint
strings.

Every spawned operation belongs to the calling future. Dropping formation aborts its
task set, drops provider futures and open streams, releases semaphore permits, and emits
cancellation progress. No detached provider task or listener is created. Network and
handshake deadlines are independent, nonzero, and caller configured.

## Executable Contract

[`provider_api.rs`](../../anonssh-bond-tokio/tests/provider_api.rs) is an external-crate
API test. It binds three ephemeral sockets, forms a two-lane session, exchanges exact
interactive and bulk payloads, adds and replaces the third lane, checks structured
progress, and closes cleanly. Separate cases prove exact policy rejection, the
loopback-only boundary, custom-provider compilation, cancellation drop behavior, and a
measured two-operation maximum. `make test-bond` runs this contract.

[`provider_transport_api.rs`](../../anonssh-cli/tests/provider_transport_api.rs) is the
anonymous-provider black-box contract. Fake protocol peers verify SOCKS host and port,
Tor cookie authentication and keyed onion publication, SAM destination generation and
session creation, exact endpoint denial, and inbound/outbound bytes for both providers.
The fake SAM peer withholds connection success until it receives the supplied initial
payload, proving that the I2P adapter does not wait for a status that itself depends on
the ABP hello. A paired fake-SAM router then bridges the public I2P dial and listen
providers into `BondDialer` and `BondListener`, forms a mutually authenticated encrypted
session, exchanges an exact bidirectional `BondedStream` payload, and shuts every layer
down. The product binary imports these same transport modules from the library target
rather than compiling a private fork.
