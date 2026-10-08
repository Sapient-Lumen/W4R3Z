# Gap: protocol products, transport bridges, and interop/support contracts

## What is missing
Rust now has serious protocol ingredients, but it still lacks a **portable productization layer for protocol-facing products**.

Today there is no shared way to publish, exchange, and diff:
- which wire protocols a product actually supports;
- which transport and negotiation posture is official (HTTP/2, QUIC, HTTP/3, WebSocket, grpc-web bridges, ALPN, TLS, mTLS, proxies, browser bridges);
- which interaction modes are really promised (unary, client/server/bidi streaming, byte streams, datagrams, graceful close, compression/framing limits);
- which application/service/schema attachments are part of the public protocol story;
- which interop, conformance, and cross-language cases were actually checked;
- and which support/docs claims tell operators and users what is truly supported.

That missing layer matters because the Rust protocol problem is no longer “can Rust speak HTTP/2 or QUIC?”
The problem is “how does a Rust protocol product become a reviewable product instead of a pile of transport crates, TLS settings, bridge adapters, interop tests, and README folklore?”

## The current seam is awkward
Rust already has strong protocol ingredients, but they stop short of a shared product boundary:
- `tonic` is a gRPC-over-HTTP/2 implementation focused on interoperability and flexibility, with examples and interop resources that already act like real product-facing evidence lanes;
- `tonic-web` directly translates grpc-web without an external proxy, which means browser-bridge posture is already a first-class product boundary;
- Quinn is a pure-Rust, userspace QUIC implementation rather than a toy experiment;
- `h3` is generic over QUIC transports, still explicitly experimental, and already uses Duvet for standards-compliance reporting;
- `rustls` documents supported protocol features and exposes ALPN/SNI/TLS builder configuration as real public surfaces;
- `wtransport` and `web-transport-quinn` treat WebTransport as a browser-facing QUIC/HTTP/3 lane rather than only another internal transport;
- `tonic-h3` and `h3-axum` show HTTP/3/gRPC-over-HTTP/3 and HTTP/3 service bridges are active, but clearly still heterogeneous;
- `tarpc` remains transport- and protocol-agnostic, which is a useful reminder that many Rust products want one service contract and multiple transport lanes.

So the ecosystem is not missing one more transport crate, proxy, TLS helper, or RPC framework.
It is missing the **boring contract/evidence layer that keeps wire truth, bridge truth, security truth, schema/service truth, conformance truth, and support truth distinct while still letting them compose**.

## Why this matters
This gap matters because it cuts across several real Rust families at once:
1. **gRPC products** — native HTTP/2, grpc-web bridge posture, reflection/health attachments, TLS posture, streaming-mode truth, and interop evidence all shape what is actually supported;
2. **QUIC / HTTP/3 / WebTransport products** — streams, datagrams, browser/native splits, ALPN, and transport choice become part of the public contract;
3. **transport-agnostic RPC products** — teams want to preserve one service contract while varying the underlying transport story;
4. **service + schema + client products** — application routes, message schemas, and browser/native clients attach to protocol truth but do not replace it;
5. **support / incident / archaeology consumers** — teams often cannot later answer which protocol families were promised, which bridges or intermediaries were required, what TLS/ALPN posture was shipped, and what interop evidence actually existed.

A worthy contribution here is therefore not “a better protocol crate.”
It is a shared way to make **Rust protocol products legible as products**.

## What “good” looks like
A worthy contribution here is **not** another giant abstraction crate.
It is a thin stack above the existing pieces:
- **Protocol Surface Kit** for declared wire families, transport posture, interaction modes, security posture, and browser/native bridge truth,
- **Service Surface Kit** for application-facing service attachment, method/route families, health/reflection posture, and request/response attachments,
- **Runtime Settings Kit** for cert/root/proxy/ALPN/port/origin/feature activation truth,
- **Schema Contract Kit** for payload/interface evolution truth,
- **Conformance Traceability Stack** for spec/vector/interop evidence,
- **Support Envelope + DocProof** for public support/docs truth,
- and one thin aggregate artifact such as `protocol-product-pack/v0` that references those lower-layer artifacts instead of erasing them.

That would let release tooling, deploy/review pipelines, docs, support, ecosystem-atlas work, and future editor/assistant consumers talk about the **same protocol product** without scraping transport builder code and ad hoc interop fixtures.

## Sources
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
- https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
