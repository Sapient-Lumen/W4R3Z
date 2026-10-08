# Design: Protocol Productization pilot program

## Goal
Turn the newly explicit **Protocol Productization Stack** into a ranked rollout instead of a vague “Rust networking needs better tooling” idea.

The archive already has a strong **Protocol Surface Kit**.
This pilot program is about proving the **higher-level product boundary** above it:
- protocol family truth,
- bridge/security/settings truth,
- service/schema attachment truth,
- conformance evidence,
- and support/docs truth.

## Why this pilot is worth doing now
Rust protocol work is already too real and too heterogeneous for README-level support claims:
- `tonic` plus `tonic-web` makes native gRPC and browser grpc-web support a live product lane;
- Quinn + `h3` + WebTransport crates make QUIC/HTTP/3/browser transport stories real but still fragmented;
- `rustls` makes security/ALPN/SNI configuration a public API surface;
- transport-agnostic RPC crates like `tarpc` prove some products want one service contract and multiple transport choices;
- and the `h3` project’s explicit experimental posture plus Duvet-based compliance work is exactly the kind of “serious but not flattened” signal the archive should treat carefully.

That is a good moment for a productization pilot:
late enough that the ingredients are real, early enough that the archive can still help shape the boundary.

## Ranked pilots

### 1) gRPC over HTTP/2 + grpc-web lane
**Why first:** it proves native + browser bridge truth on a serious Rust lane people already ship.

**Concrete scope**
- `grpc-h2` service posture,
- grpc-web bridge posture,
- unary/streaming mode declarations,
- TLS/ALPN/origin/CORS assumptions,
- reflection/health attachment posture,
- service/schema attachments,
- checked native + browser/client interop evidence.

**Graduation bar**
- a reviewer can tell what part of the product is native gRPC, what part is grpc-web translation, what streaming modes are official, and what security/bridge assumptions were actually checked.

### 2) QUIC / HTTP/3 / WebTransport lane
**Why second:** this is where modern transport heterogeneity becomes impossible to hide.

**Concrete scope**
- QUIC stream/datagram posture,
- HTTP/3 versus raw-QUIC versus WebTransport distinctions,
- browser/native lane differences,
- ALPN and certificate posture,
- experimental or partial support flags,
- checked interop or acceptance evidence.

**Graduation bar**
- the pack can explain which transport family was actually supported, which browser/native cases were exercised, and which claims remain experimental.

### 3) Transport-agnostic RPC lane
**Why third:** it prevents the stack from silently becoming “whatever tonic/quinn do.”

**Concrete scope**
- one service surface attached to multiple transport profiles,
- in-memory vs networked transport distinction,
- protocol-agnostic client/server posture,
- runtime-setting differences per lane,
- checked evidence for at least two materially different transports.

**Graduation bar**
- a reviewer can tell what service truth stays stable across transports and what changes with each transport lane.

### 4) Cross-language / conformance lane
**Why fourth:** this is where protocol products stop being local demos and start becoming serious interoperability claims.

**Concrete scope**
- vector/spec references,
- cross-language clients or servers,
- version/bridge/proxy permutations,
- partial or waived cases,
- acceptance and drift reports,
- explicit capability declarations.

**Graduation bar**
- the pack can explain what was checked against spec vectors or other implementations, what failed, and what remained out of scope.

### 5) Support / docs / consumer lane
**Why fifth:** this is where the stack proves it matters beyond interop fixtures.

**Concrete scope**
- supported protocol/bridge/runtime floors,
- checked docs/examples,
- release/deploy/support imports,
- incident/archeology handoff examples,
- atlas/editor/assistant summaries importing the same artifacts.

**Graduation bar**
- support or release consumers can answer what protocol story is actually supported and what evidence shipped with it.

## What to defer
- a giant universal networking platform;
- a one-number readiness score for protocols;
- replacing transport crates or TLS libraries;
- pretending every protocol family must share one schema and one runtime model;
- vague “supports HTTP/3/QUIC/WebTransport” claims that skip bridge, settings, conformance, and support truth.

## Immediate archive consequences
- Treat **Protocol Surface** as the anchor of wire/bridge/security/interaction truth rather than as a standalone networking kit.
- Treat **Service Surface + Schema Contract** as attachment lanes instead of places to smuggle in transport facts.
- Treat **Runtime Settings** as the activation lane for certs/roots/ports/proxies/origins/feature toggles that materially change protocol behavior.
- Treat **Conformance Traceability + Support Envelope + DocProof** as downstream proof lanes rather than optional polish.
- Add a specific amnesia resistor so later revisions cannot collapse wire truth, bridge/security posture, service/schema attachments, conformance evidence, and support conclusions into one fake protocol-readiness story.

## Read this together with
- `design/protocol-productization-stack.md`
- `design/protocol-surface-kit.md`
- `design/service-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/schema-contract-kit.md`
- `design/conformance-traceability-stack.md`
- `design/support-envelope-kit.md`
- `design/docproof-kit.md`
