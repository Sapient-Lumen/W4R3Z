# Gap: network protocol, transport, and RPC contracts

## What is missing
Rust now has real protocol stacks for gRPC, HTTP/2, QUIC, WebSocket, HTTP/3, WebTransport, TLS, and transport-agnostic RPC, but it still lacks a **shared protocol-surface contract**.

Today there is no standard way to describe, exchange, diff, and review:
- which wire protocols are officially supported,
- which side roles are part of the promise (client, server, peer, proxy, bridge),
- which interaction modes are first-class (unary, request/response, client streaming, server streaming, bidi streaming, ordered streams, unreliable datagrams, upgrade handshakes),
- which transport and negotiation assumptions are required (TCP/QUIC, ALPN, HTTP/1.1 upgrade, HTTP/2 prior knowledge, browser bridges, proxy layers),
- which security posture is part of the contract (TLS versions, mTLS, root stores, cert pinning, SNI, early data, origin/CORS posture),
- which browser/native interoperability lanes exist (`grpc-web`, WebTransport, wasm clients, in-memory transports),
- which protocol examples are illustrative versus actually checked,
- and what evidence exists that the declared protocol support still matches the shipped library or application.

That missing layer matters because Rust no longer just has one RPC or stream crate. `tonic` is already a serious gRPC-over-HTTP/2 stack with health, reflection, examples, and interop tests; `h2` already implements HTTP/2 while explicitly leaving ALPN and upgrade handling to users; Quinn is already a pure-Rust QUIC transport with unidirectional streams, bidirectional streams, and unreliable datagrams; `h3` already implements HTTP/3 generically over a supplied QUIC transport; `tungstenite` already implements RFC 6455 WebSockets; `tonic-web` already translates for browser-facing grpc-web; `wtransport` and WebTransport-on-Quinn crates already make browser-oriented QUIC/HTTP/3 sessions real; `rustls` already exposes modern TLS protocol features and ALPN control; and `tarpc` already proves transport-agnostic RPC is a real Rust lane. The remaining pain is increasingly the **portable support boundary above those pieces**, not the existence of protocol libraries.

Sources:
- https://docs.rs/crate/tonic/latest
- https://docs.rs/tonic/latest/tonic/server/struct.Grpc.html
- https://docs.rs/tonic-web/latest/tonic_web/
- https://docs.rs/h2/
- https://docs.rs/quinn/
- https://docs.rs/h3/
- https://docs.rs/tungstenite/latest
- https://docs.rs/rustls/latest/rustls/manual/_04_features/
- https://docs.rs/rustls/latest/rustls/client/struct.ClientConfig.html
- https://docs.rs/wtransport/
- https://docs.rs/tarpc/latest/tarpc/transport/

## The current seam is awkward
The ecosystem clearly has ingredients:
- `tonic` already gives Rust strong gRPC support, including unary, client-streaming, server-streaming, and bidirectional-streaming handlers, plus health/reflection/interoperability lanes;
- `tonic-web` already exists because browser-facing protocol bridges are part of the real deployment story rather than an edge case;
- `h2` already exposes a real HTTP/2 implementation but is explicit that users must manage ALPN or HTTP/1.1 upgrade details themselves;
- Quinn already exposes transport realities that application teams actually care about: uni/bidi streams, unreliable datagrams, congestion, flow control, and connection-level transport configuration;
- `h3` and WebTransport crates already show that HTTP/3 and browser-oriented QUIC sessions are no longer hypothetical;
- `tungstenite`/`tokio-tungstenite` already give WebSocket support, including handshake and close-handshake behavior that often matters operationally;
- `rustls` already exposes security and negotiation posture through TLS version support, ALPN, SNI, trust roots, and client/server config builders;
- `tarpc` already shows that some Rust RPC systems intentionally separate protocol semantics from transport choice.

But actual support truth still gets split across:
- builder flags and feature flags,
- README examples,
- ad hoc ALPN and certificate configuration,
- hidden proxy or browser-bridge assumptions,
- message-size/compression/stream-limit tuning in code,
- “works with browser/native/mobile” claims that are only half-specified,
- and interop tests that are buried in repositories rather than shipped as review artifacts.

The result is not that Rust lacks protocol code.
The result is that there is still no portable way to say:
- “these wire protocols and interaction modes are officially supported,”
- “these transport and security assumptions are part of the promise,”
- “these browser/native/proxy bridge lanes are first-class versus best-effort,”
- or “these interoperability, downgrade, handshake, and streaming cases were actually run.”

That is exactly the archive pattern worth elevating: strong point libraries, weak shared review layer.

Sources:
- https://docs.rs/crate/tonic/latest
- https://docs.rs/tonic/latest/tonic/server/struct.Grpc.html
- https://docs.rs/tonic-web/latest/tonic_web/
- https://docs.rs/h2/
- https://docs.rs/quinn/
- https://docs.rs/quinn/latest/quinn/struct.Connection.html
- https://docs.rs/quinn/latest/quinn/struct.TransportConfig.html
- https://docs.rs/h3/
- https://docs.rs/tungstenite/latest
- https://docs.rs/rustls/latest/rustls/manual/_04_features/
- https://docs.rs/wtransport/
- https://docs.rs/tarpc/latest/tarpc/transport/

## Why this matters
This gap is bigger than “better networking docs.”
It affects:
1. **product honesty** — “supports gRPC/QUIC/WebSockets” can hide major differences in stream modes, browser support, proxies, TLS posture, or downgrade behavior;
2. **compatibility review** — changing ALPN values, compression defaults, interaction modes, datagram support, or browser bridges can be a real breaking change even when application routes or payload schemas do not change;
3. **security clarity** — TLS versions, trust-root sources, mTLS requirements, certificate assumptions, and origin/CORS posture are support claims, not invisible implementation details;
4. **interop confidence** — teams often need explicit evidence that Rust stacks still behave correctly against browsers, other language clients, gateways, load balancers, and prior versions;
5. **cross-kit composition** — Service Surface Kit, Event Surface Kit, Schema Contract Kit, Identity Surface Kit, Client App Surface Kit, and Support Envelope Kit all need a lower-level protocol boundary without owning it;
6. **future maintenance** — protocol stacks are full of versioning, feature, browser, TLS, and transport subtleties that get lost quickly when maintainers rotate.

There is also an honesty constraint: a protocol-surface kit should not pretend every Rust app needs to expose raw protocol detail to every reviewer. Some teams only need a small gRPC client; some need QUIC plus WebTransport; some need WebSockets; some need transport-agnostic RPC inside one process boundary. A good contribution should therefore make supported scope and non-goals explicit instead of selling “networking support” as one magical universal capability.

Sources:
- https://docs.rs/crate/tonic/latest
- https://docs.rs/h2/
- https://docs.rs/quinn/
- https://docs.rs/rustls/latest/rustls/manual/_04_features/
- https://docs.rs/wtransport/
- https://docs.rs/tarpc/latest/tarpc/transport/

## What “good” looks like
A worthy contribution here is **not** another RPC framework, another QUIC stack, another TLS library, another proxy, or another browser-bridge wrapper.

It is a shared protocol-surface boundary:
- one `protocol-surface/v0` describing library/app identity, supported protocol families, and role posture,
- one `transport-profile/v0` describing transport kinds, negotiation paths, upgrade requirements, ALPN values, proxy/bridge assumptions, and relevant size/flow limits,
- one `interaction-profile/v0` describing supported interaction modes such as unary, request/response, client streaming, server streaming, bidi streaming, byte streams, and unreliable datagrams,
- one `security-profile/v0` describing TLS versions, mTLS posture, trust-root sources, certificate assumptions, SNI/ALPN details, and origin/CORS notes when relevant,
- one optional `bridge-profile/v0` describing `grpc-web`, WebTransport, wasm/browser, proxy, or in-memory transport lanes,
- one `interop-check-plan/v0` describing which handshakes, cross-language clients, browser/native lanes, downgrade cases, compression settings, proxies, and streaming patterns were exercised,
- one `interop-check-report/v0` recording checked protocols/transports/platforms, failures, drift findings, and raw attachment pointers,
- one optional `protocol-diff-report/v0` for additive/breaking support changes,
- and one `protocol-pack/v0` bundle for CI, release review, SDK/app handoff, and later archaeology.

That would let Rust teams treat wire-protocol support as a reviewable product surface instead of a pile of config builders, feature flags, proxy notes, integration tests, and tribal memory about what “supports gRPC/QUIC/WebSockets” really meant.
