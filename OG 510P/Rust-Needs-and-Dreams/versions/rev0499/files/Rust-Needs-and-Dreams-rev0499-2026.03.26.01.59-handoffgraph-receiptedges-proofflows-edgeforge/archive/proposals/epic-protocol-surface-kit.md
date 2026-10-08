# Epic proposal: Protocol Surface Kit

## Thesis
Rust’s networking and RPC ecosystem is mature enough that the missing contribution is no longer “yet another gRPC stack,” “yet another WebSocket helper,” or “yet another QUIC wrapper.”
The higher-leverage missing piece is a **portable protocol-surface contract** that lets teams declare, diff, validate, and ship what their systems actually promise at the wire boundary: supported protocols, interaction modes, transport/security assumptions, browser/native bridge lanes, and checked interoperability evidence.

In other words: Rust needs a boring, attachable `protocol-pack/v0` more than it needs another thin wrapper over one transport.

## Why now
The ecosystem signals line up:
- `tonic` is already a serious gRPC-over-HTTP/2 stack with health, reflection, examples, and interop tests.
- `tonic-web` already exists because browser bridges are part of real deployments.
- `h2` already gives Rust an HTTP/2 implementation while making negotiation/upgrade posture explicit.
- Quinn and `h3` already make QUIC and HTTP/3 real Rust lanes.
- WebTransport crates already show browser-friendly QUIC/HTTP/3 sessions are not hypothetical.
- `tungstenite`/`tokio-tungstenite` already make WebSockets routine.
- `rustls` already gives Rust a serious TLS posture with documented features and explicit ALPN/SNI configuration.
- `tarpc` already proves there is appetite for transport-agnostic RPC boundaries.

That means the missing substrate is not raw capability.
It is the **reviewable boundary above today’s pieces**.

Sources:
- https://docs.rs/crate/tonic/latest
- https://docs.rs/tonic/latest/tonic/server/struct.Grpc.html
- https://docs.rs/tonic-web/latest/tonic_web/
- https://docs.rs/h2/
- https://docs.rs/quinn/
- https://docs.rs/h3/
- https://docs.rs/tungstenite/latest
- https://docs.rs/rustls/latest/rustls/manual/_04_features/
- https://docs.rs/wtransport/
- https://docs.rs/tarpc/latest/tarpc/transport/

## What should be built
A first credible version should ship:
1. `protocol-surface/v0`, `transport-profile/v0`, `interaction-profile/v0`, `security-profile/v0`, optional `bridge-profile/v0`, optional `protocol-example-catalog/v0`, `interop-check-plan/v0`, `interop-check-report/v0`, optional `protocol-diff-report/v0`, and `protocol-pack/v0`
2. adapters for common Rust stacks (`tonic`, `tonic-web`, `h2`, Quinn, `h3`, `tungstenite`, `rustls`, WebTransport crates, `tarpc`)
3. docs/reference generation for declared wire protocols, role posture, streaming modes, ALPN/TLS assumptions, and bridge/proxy lanes
4. validation/reporting support for drift in protocol families, streaming modes, TLS/ALPN posture, browser/native lanes, and interop coverage
5. release/CI examples showing protocol packs attached to services, SDKs, browsers, clients, and internal RPC boundaries

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s pieces legible together rather than replacing them.

## Initial pilots
- one `tonic` service with health/reflection and a `tonic-web` browser lane
- one Quinn-based QUIC service with uni/bidi streams plus datagrams recorded explicitly
- one HTTP/3 or WebTransport pilot proving browser/native transport posture can be captured honestly
- one WebSocket app showing close-handshake, origin/TLS posture, and proxy assumptions in a reviewable pack
- one `tarpc` pilot proving transport-agnostic RPC can attach to the same artifact family without collapsing into fake universal transport details

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve protocol families, role posture, interaction modes, and security assumptions
2. **v0.2 adapters**
   - support `tonic`, `tonic-web`, `h2`, Quinn, `rustls`, and WebSocket lanes
   - support raw attachment of browser/proxy/gateway evidence without flattening it
3. **v0.3 bridge + interop depth**
   - support HTTP/3/WebTransport lanes, cross-language interop attachments, and diff reports
   - integrate with Service Surface, Schema Contract, Identity Surface, Support Envelope, and Client App Surface workflows
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one exact stack

## Success metrics
- Teams can review protocol-surface changes as explicit artifacts instead of reading builder code, TLS config, and integration tests.
- Supported wire protocols and bridge lanes remain documented from one declared source.
- Breaking changes in streaming mode, TLS/ALPN posture, or browser/native support become easier to notice.
- Interop evidence survives beyond one CI setup or maintainer’s memory.
- Rust protocol-heavy systems become easier to hand off across backend, infra, browser, mobile, and SDK teams.

## Archive fit
This proposal fills a real gap between several existing concise-archive kits:
- Service Surface Kit covers application/service routes and checked exchanges,
- Event Surface Kit covers message-driven channels and delivery semantics,
- Schema Contract Kit covers payload/interface schemas,
- Identity Surface Kit covers access requirements,
- Support Envelope Kit covers broader platform/runtime support,
- and Client App Surface Kit covers app/package/platform lifecycle boundaries.

But none of those is the portable contract for the **composed protocol and transport boundary itself**.
Protocol Surface Kit is the missing substrate that keeps gRPC/HTTP2/QUIC/WebSocket/WebTransport/TLS/bridge posture attached to one reviewable interface without absorbing everything into one mega-format.
