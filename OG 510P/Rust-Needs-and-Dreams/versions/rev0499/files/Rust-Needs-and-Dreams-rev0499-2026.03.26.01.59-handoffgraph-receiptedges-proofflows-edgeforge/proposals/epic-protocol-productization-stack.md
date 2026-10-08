# Epic proposal: Protocol Productization Stack

## Thesis
Rust does not most urgently need another transport crate, proxy helper, or RPC framework shootout.
It needs a **portable productization substrate for protocol-facing products**.

The contribution should sit **above** existing serious lanes:
- gRPC over HTTP/2 via `tonic`,
- browser bridge translation via `tonic-web`,
- QUIC via Quinn,
- HTTP/3 via `h3`,
- WebTransport crates for browser-facing QUIC/HTTP/3 lanes,
- transport-agnostic RPC via `tarpc`,
- and public security posture via `rustls` configuration and feature support.

## The worthy contribution
A worthy contribution would make these truths reviewable and importable without forcing one transport or framework:
1. **wire truth** — protocol families, interaction modes, stream/datagram posture, close/shutdown posture;
2. **bridge truth** — grpc-web, browser/native splits, proxy/intermediary assumptions;
3. **security truth** — TLS/ALPN/SNI/mTLS/root-store posture;
4. **service/schema truth** — service methods, health/reflection attachments, payload/interface evolution;
5. **conformance truth** — spec vectors, interop reports, partial/waived acceptance;
6. **support/docs truth** — supported lanes, checked examples, release/support handoffs.

This should look like a **thin artifact family** such as:
- `protocol-surface/v0`
- `transport-profile/v0`
- `interaction-profile/v0`
- `security-profile/v0`
- `interop-check-report/v0`
- `protocol-product-pack/v0`

## Why this is ecosystem-shaping
This contribution would help at least five families at once:
- gRPC services with browser or native clients,
- QUIC / HTTP/3 / WebTransport products,
- transport-agnostic RPC systems,
- service/schema/client stacks that need real protocol support boundaries,
- and support/release/incident tooling that currently has to reverse-engineer protocol posture from builder code and test fixtures.

It would also create a cleaner import boundary for atlas/docs/editor/assistant consumers, which increasingly matter now that official docs remain canonical while machine-assisted consumption is rising.

## What this should not become
- not a universal networking framework;
- not a universal transport abstraction that erases protocol differences;
- not a transport ranking site;
- not a fake “protocol maturity” score;
- not a schema that erases the difference between gRPC, QUIC, HTTP/3, WebTransport, WebSocket, and transport-agnostic RPC.

## Strong first proving grounds
1. a `tonic` + `tonic-web` service with explicit native-versus-browser bridge truth;
2. a Quinn + `h3` or WebTransport lane with explicit stream/datagram/browser posture;
3. a transport-agnostic `tarpc`-style service with multiple transport attachments;
4. one conformance/interop pack with vector-backed or cross-language evidence;
5. one checked support/docs consumer import showing supported protocol/bridge/security posture.

## References
- https://docs.rs/tonic/latest/tonic/
- https://docs.rs/crate/tonic/latest
- https://docs.rs/tonic-web/latest/tonic_web/
- https://docs.rs/quinn
- https://docs.rs/crate/quinn/latest
- https://docs.rs/h3
- https://docs.rs/crate/h3/latest
- https://docs.rs/rustls/latest/rustls/manual/_04_features/index.html
- https://docs.rs/rustls/latest/rustls/client/struct.ClientConfig.html
- https://docs.rs/wtransport
- https://docs.rs/web-transport-quinn/latest/web_transport_quinn/
- https://docs.rs/tonic-h3
- https://docs.rs/h3-axum
- https://docs.rs/tarpc/latest/tarpc/transport/index.html
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
