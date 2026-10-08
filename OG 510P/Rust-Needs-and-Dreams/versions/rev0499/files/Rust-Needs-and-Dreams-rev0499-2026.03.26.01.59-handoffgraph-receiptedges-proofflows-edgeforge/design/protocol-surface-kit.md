# Design: Protocol Surface Kit (`cargo protocolcheck`, `protocol-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing a Rust library or application’s supported **protocol surface**: wire protocols, transport and negotiation posture, interaction modes, security assumptions, browser/native bridge lanes, and evidence that the declared protocol support still matches reality.

This should **not** replace `tonic`, `h2`, Quinn, `h3`, `tungstenite`, `rustls`, WebTransport crates, `tarpc`, or future protocol stacks.
It should make them compose better and make support claims reviewable.

## References (signals)
- `tonic` is explicitly a gRPC over HTTP/2 implementation focused on interoperability and flexibility, and its project layout already includes health, reflection, examples, and interop tests.
  https://docs.rs/crate/tonic/latest
- `tonic::server::Grpc` explicitly supports unary, client-streaming, server-streaming, and bidirectional-streaming handlers.
  https://docs.rs/tonic/latest/tonic/server/struct.Grpc.html
- `tonic-web` explicitly provides grpc-web protocol translation for tonic services and can serve grpc-web clients without an external proxy.
  https://docs.rs/tonic-web/latest/tonic_web/
- `h2` explicitly implements HTTP/2 while leaving ALPN and HTTP/1.1 upgrades to the embedding application.
  https://docs.rs/h2/
- Quinn is explicitly a pure-Rust QUIC implementation; its docs expose uni/bidi streams, unreliable datagrams, and configurable transport behavior.
  https://docs.rs/quinn/
  https://docs.rs/quinn/latest/quinn/struct.Connection.html
  https://docs.rs/quinn/latest/quinn/struct.TransportConfig.html
- `h3` explicitly provides an HTTP/3 implementation generic over a provided QUIC transport.
  https://docs.rs/h3/
- `tungstenite` explicitly implements RFC 6455 WebSockets.
  https://docs.rs/tungstenite/latest
- `rustls` explicitly documents supported protocol features and exposes ALPN/SNI/TLS configuration via client/server config builders.
  https://docs.rs/rustls/latest/rustls/manual/_04_features/
  https://docs.rs/rustls/latest/rustls/client/struct.ClientConfig.html
  https://docs.rs/rustls/latest/rustls/server/struct.ClientHello.html
- `wtransport` and adjacent crates explicitly position WebTransport as a modern QUIC/HTTP/3-based alternative to HTTP and WebSockets, including browser-oriented secure session setup.
  https://docs.rs/wtransport/
- `tarpc` explicitly presents itself as transport- and protocol-agnostic.
  https://docs.rs/tarpc/latest/tarpc/transport/

## Problem statement
Rust protocol support is increasingly real and varied, but the support boundary is still awkward to review.

Today, a team that wants to understand “what protocols do we actually support?” usually has to reconstruct that answer from:
- selected crates and features,
- codegen choices,
- ALPN/TLS builder configuration,
- proxy/bridge notes,
- browser/native caveats,
- message size and compression tuning,
- integration tests,
- and partial examples.

That creates recurring failure modes:
- teams conflate application-level routes or schemas with lower-level transport guarantees;
- browser compatibility depends on `grpc-web`, WebTransport, or WebSocket translation, but that bridge posture is not recorded as first-class support data;
- QUIC/WebTransport/WebSocket support gets announced without being clear about datagrams, bidi streams, compression, close-handshake behavior, or fallback lanes;
- security-relevant choices like ALPN values, TLS version posture, trust-root sources, or mTLS requirements are implicit in code rather than explicit in shipped artifacts;
- and protocol interop is “known” because a repo had tests, not because the released artifact still carries checked evidence.

## Design principles
1. **Protocol truth should be reviewable.**
   Wire-protocol support should survive outside source trees and CI logs.
2. **Do not erase protocol differences.**
   gRPC over HTTP/2, raw HTTP/2, WebSocket, QUIC, HTTP/3, WebTransport, and transport-agnostic RPC are not one thing.
3. **Separate application surface from wire surface.**
   Service routes, event channels, and schema catalogs should attach to protocol artifacts, not be replaced by them.
4. **Make bridge lanes first-class.**
   Browser/native/proxy translation is often the real product boundary.
5. **Keep security posture explicit.**
   ALPN, TLS version posture, roots, mTLS, and SNI assumptions belong in review artifacts.
6. **Ship checked evidence, not only declarations.**
   Protocol packs should record what interop and handshake behavior was actually exercised.

## Core artifact set
### 1. `protocol-surface/v0`
Top-level declaration of:
- package/system identity,
- supported protocol families (`grpc-h2`, `grpc-web`, `raw-h2`, `quic`, `h3`, `websocket`, `webtransport`, `custom-rpc`, `in-process-rpc`),
- supported roles (client, server, proxy, peer, bridge),
- references to attached application-level kits (service, event, schema, identity),
- explicit non-goals and unsupported lanes.

### 2. `transport-profile/v0`
Declares transport and negotiation posture:
- TCP/Unix socket/QUIC/in-memory/custom transport kinds,
- HTTP/1.1 upgrade requirements,
- ALPN values,
- proxy requirements or assumed intermediaries,
- stream-count or message-size envelopes when declared,
- datagram/flow-control/concurrency assumptions,
- load-balancer or browser constraints when relevant.

### 3. `interaction-profile/v0`
Declares supported interaction modes:
- unary/request-response,
- client streaming,
- server streaming,
- bidirectional streaming,
- byte-stream sessions,
- message-oriented sessions,
- unreliable datagrams,
- close-handshake / graceful shutdown expectations,
- compression and framing notes when part of support truth.

### 4. `security-profile/v0`
Declares security and negotiation posture:
- TLS version posture,
- root-store or certificate-source assumptions,
- mTLS/client-cert posture,
- certificate pinning or custom verifier usage,
- SNI and ALPN behavior,
- early-data posture when relevant,
- origin/CORS/browser notes where required by protocol bridges.

### 5. `bridge-profile/v0` (optional)
Captures translation or cross-environment lanes:
- `grpc-web` translation,
- wasm/browser-specific clients,
- WebTransport browser/native splits,
- in-memory transport lanes,
- fallback/proxy/downgrade stories,
- per-bridge limitations and ownership boundaries.

### 6. `protocol-example-catalog/v0` (optional)
Declares illustrative examples, snippets, wire captures, or client recipes while marking them as checked or illustrative-only.

### 7. `interop-check-plan/v0`
Describes what to run:
- protocol handshake cases,
- cross-language or cross-version clients,
- browser/native bridge checks,
- TLS/ALPN permutations,
- compression/message-size limits,
- proxy/load-balancer/gateway cases,
- unary and streaming patterns,
- graceful-close and failure-path checks.

### 8. `interop-check-report/v0`
Records:
- which protocol lanes were actually checked,
- environment/platform details,
- failures and skipped cases,
- drift between declared and observed posture,
- attachments to raw logs, packet captures, interop suites, or fixture repos.

### 9. `protocol-diff-report/v0` (optional)
Summarizes additive/breaking changes across revisions:
- added/removed protocols,
- changed streaming modes,
- TLS/ALPN posture changes,
- bridge or proxy posture changes,
- altered interop evidence coverage.

### 10. `protocol-pack/v0`
Bundle for CI artifacts, release review, SDK distribution, and long-term archaeology.

## Candidate CLI shape
- `cargo protocolcheck init`
- `cargo protocolcheck detect`
- `cargo protocolcheck examples`
- `cargo protocolcheck plan`
- `cargo protocolcheck run`
- `cargo protocolcheck diff`
- `cargo protocolcheck pack`

## How it would work in practice
### gRPC service with browser access
A team using `tonic` plus `tonic-web` could:
- declare `grpc-h2` server support,
- attach unary/streaming interaction modes,
- attach `grpc-web` bridge posture and browser limits,
- record TLS/ALPN/mTLS configuration assumptions,
- record that reflection/health are supported (or intentionally not),
- and ship interop evidence for native clients plus browser/grpc-web clients.

### QUIC/WebTransport service
A team using Quinn plus `h3`/WebTransport crates could:
- declare uni/bidi stream and datagram posture,
- record ALPN and HTTP/3/WebTransport handshake assumptions,
- separate browser-facing session support from native-only QUIC support,
- and ship reports showing which stream/datagram/browser cases were actually exercised.

### WebSocket application
A team using `tungstenite`/`tokio-tungstenite` could:
- declare WebSocket endpoint support,
- attach compression/close-handshake assumptions if relevant,
- record TLS/origin/proxy posture,
- and ship evidence covering handshake success, backpressure, and graceful-close cases.

### Transport-agnostic RPC or in-process boundaries
A team using `tarpc` could:
- declare transport-agnostic interaction modes,
- attach multiple transport profiles,
- and keep the application RPC surface separate from transport-specific rollout.

## Adapters worth building first
- `tonic`, `tonic-health`, `tonic-reflection`, `tonic-web`
- `h2`
- Quinn
- `h3`
- `tungstenite` / `tokio-tungstenite`
- `rustls`
- `wtransport` / WebTransport-on-Quinn crates
- `tarpc`
- optional attachment readers for packet captures, interop logs, browser tests, and gateway/proxy configs

## Non-goals
This kit should **not**:
- define business routes, event subjects, or schema evolution rules;
- replace transport stacks or TLS libraries;
- hide meaningful protocol differences behind one mega-abstraction;
- own certificate issuance or PKI lifecycle;
- claim to validate every intermediary or internet-path condition automatically.

## Overlap boundaries
- **Service Surface Kit** owns HTTP/service route and request/response behavior at the application boundary.
- **Event Surface Kit** owns channel/event/delivery boundaries for message-driven systems.
- **Schema Contract Kit** owns payload/interface schema compatibility.
- **Identity Surface Kit** owns auth/access requirements that may attach to protocol surfaces.
- **Support Envelope Kit** owns platform/runtime support claims broader than protocols.
- **Client App Surface Kit** may attach browser/mobile capability assumptions without owning protocol transport truth.

Protocol Surface Kit exists because those kits should not have to absorb ALPN, QUIC datagrams, browser bridges, or TLS posture just to stay useful.

## Why this could be high leverage
A good protocol-surface kit would:
- make transport support honest without forcing every team to publish an RFC,
- make breaking changes easier to review,
- help browser/native/server teams coordinate on one declared boundary,
- survive crate swaps (`tonic` to another stack, Quinn to another QUIC provider, different proxy/gateway choices),
- and make protocol interop evidence portable across teams and time.
