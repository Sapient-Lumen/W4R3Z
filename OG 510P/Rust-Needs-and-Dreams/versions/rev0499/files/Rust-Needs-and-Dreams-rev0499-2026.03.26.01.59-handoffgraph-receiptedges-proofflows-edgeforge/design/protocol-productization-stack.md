# Design: Protocol Productization Stack (Protocol Surface + Service Surface + Runtime Settings + Schema Contract + Conformance Traceability + Support Envelope)

## Goal
Turn Rust protocol-facing products into a **portable productization stack** instead of leaving each project to express its protocol story as a tangle of transport crates, TLS builders, browser/proxy bridges, ad hoc interop fixtures, generated clients, and support folklore.

The stack should **not** replace `tonic`, `tonic-web`, Quinn, `h3`, WebSocket/WebTransport crates, `rustls`, `tarpc`, service frameworks, or schema tools.
It should make them compose better and make supported protocol behavior reviewable.

## Why this note is needed now
Rust’s current signals say the missing problem is no longer “can Rust speak real protocols?”
They say the missing problem is **what a Rust protocol product can honestly claim to support**:
- `tonic` already treats gRPC over HTTP/2 as a production-oriented building block and ships examples plus interop resources;
- `tonic-web` makes grpc-web translation a direct Rust lane instead of forcing every team through a separate proxy product;
- Quinn is a serious pure-Rust QUIC substrate;
- `h3` is already a generic-over-QUIC HTTP/3 implementation, while still explicitly experimental and already using Duvet for compliance work;
- `rustls` exposes supported protocol features and negotiable configuration surfaces rather than pretending TLS is invisible plumbing;
- WebTransport crates make browser-facing QUIC/HTTP/3 lanes materially different from native-only transport stories;
- `tonic-h3` and `h3-axum` show active HTTP/3 service-bridge experimentation;
- `tarpc` reminds us that some products want transport-agnostic service truth instead of a single transport winner.

Together, those signals argue that the missing contribution is **not** another transport or RPC framework.
It is the **boring portable boundary above the ingredients**.

## Stack layers

### 1) Protocol Surface: wire, transport, interaction, security, and bridge truth
Protocol Surface owns the **declared wire-facing product boundary**:
- protocol families,
- transport kinds,
- negotiation posture,
- interaction modes,
- security posture,
- browser/proxy/native bridge posture,
- and checked interop evidence.

This layer answers questions like:
- “Do we support gRPC over HTTP/2, grpc-web, HTTP/3, QUIC datagrams, WebSockets, or multiple lanes?”
- “Is browser access native, proxied, translated, or unsupported?”
- “What ALPN/TLS/close-handshake posture is part of the contract?”

Design rule: **wire truth must not remain an incidental side effect of chosen crates and builder code**.

### 2) Service Surface: application-facing RPC/service attachment truth
Protocol products almost always attach to a higher-level service contract.
Service Surface owns:
- route/method families,
- health/reflection or service-discovery attachments,
- request/response and streaming attachment lanes,
- service roles,
- and checked application-level exchange behavior.

This layer answers questions like:
- “Which service surface is actually available over this protocol lane?”
- “Are reflection, health, or admin endpoints part of the supported product?”
- “Which protocol changes are actually service-surface changes versus lower-level transport changes?”

Design rule: **application/service truth and wire truth travel together, but they are not the same contract**.

### 3) Schema Contract: payload and interface evolution truth
Schema Contract owns:
- protobuf/OpenAPI/JSON-schema/Serde-derived payload identity,
- message and method evolution posture,
- compatibility notes,
- and schema-level diffs or attachment references.

This layer answers questions like:
- “What payload/interface family does this protocol product actually serve?”
- “Did the wire lane change, or did the schema change?”
- “Which compatibility promises belong to schemas instead of transports?”

Design rule: **schema compatibility must not be smuggled into transport docs or vice versa**.

### 4) Runtime Settings: activation truth for certs, roots, ports, proxies, origins, and features
Real protocol products change behavior through settings:
- ports and bind posture,
- certificates and trust roots,
- ALPN toggles,
- origin/CORS/bridge enablement,
- feature flags,
- browser/native transport toggles,
- proxy/intermediary requirements,
- and local/dev/prod differences.

This layer answers questions like:
- “Why does this only work behind this proxy or origin?”
- “Which cert/root/ALPN settings are actually part of support truth?”
- “What env/config changes alter protocol behavior materially?”

Design rule: **activation posture is product truth, not only deployment trivia**.

### 5) Conformance Traceability: spec, vector, interop, and acceptance truth
Protocol claims need checked evidence.
Conformance Traceability owns:
- spec references,
- executable vectors,
- interop plans and reports,
- cross-version or cross-language acceptance,
- explicit partial/unsupported cases,
- and traceability between text, vectors, and observed outcomes.

This layer answers questions like:
- “What part of the protocol family was actually exercised?”
- “Was this checked against a spec vector, another implementation, or only local smoke tests?”
- “What is still experimental or only partially validated?”

Design rule: **interop screenshots and README claims are not conformance evidence**.

### 6) Support Envelope + DocProof: public promise and checked-doc truth
Support Envelope and DocProof together own:
- supported protocol families and runtime floors,
- browser/native/proxy support posture,
- docs/examples/tutorial truth,
- supported interoperability expectations,
- and public support promises.

This layer answers questions like:
- “Which lanes are actually supported versus merely experimental?”
- “Did the docs describe the same protocol/bridge/security story that shipped?”
- “What can support and release teams safely promise?”

Design rule: **one passing interop demo or example repo is not the support contract**.

### 7) Downstream consumers
The stack becomes ecosystem-shaping when real consumers can import it honestly:
- **release/deploy** consumers can attach shipped protocol/support truth;
- **support/incident** consumers can answer whether a failure belongs to the wire lane, schema lane, proxy/bridge lane, settings lane, or support boundary;
- **atlas/learning** consumers can compare serious Rust protocol lanes without pretending one transport has already won;
- **editor/assistant/docs** consumers can summarize protocol products without guessing from builder code and sample configs.

Design rule: **consumers import selected protocol-productization facts; they do not redefine the stack**.

## What an epic contribution should look like in practice
A worthy contribution here is not “the one true Rust network stack.”
It is a portable boring stack with clear boundaries:

1. **wire and bridge truth first**
   - prove stable product identity, protocol families, negotiation posture, interaction modes, and browser/proxy bridge declarations on one real product;
2. **service/schema attachments second**
   - make service methods, reflection/health posture, and payload/interface attachments reviewable without collapsing them into transport metadata;
3. **settings and activation truth third**
   - prove cert/root/ALPN/origin/proxy/feature posture can be captured honestly;
4. **interop and conformance evidence fourth**
   - prove cross-language, cross-version, and vector-backed checks can be attached as durable evidence;
5. **support/docs and release/incident consumers fifth**
   - prove protocol floors, checked docs, and shipped/support lanes can be imported without re-deriving them.

An eventual aggregate artifact may exist, but it should be a **thin pack of linked artifacts**, not a mega-schema that erases wire truth, service truth, schema truth, settings truth, conformance truth, and support truth.

## Ranked first execution lanes
1. **gRPC over HTTP/2 + grpc-web lane**
   - best first exporter because it proves native + browser bridge truth, streaming modes, TLS posture, and service attachments without immediately requiring every modern transport family.
2. **QUIC / HTTP/3 / WebTransport lane**
   - proves stream/datagram/browser/ALPN/transport heterogeneity is part of the product contract.
3. **transport-agnostic RPC lane**
   - proves one service surface may attach to multiple transport stories without flattening them.
4. **cross-language / conformance lane**
   - proves vectors, acceptance, and interop should travel as evidence instead of living only in CI logs.
5. **support/docs consumer lane**
   - proves protocol floors, bridge posture, and checked docs are importable by support and release consumers.

## Non-goals
- one universal RPC framework;
- one universal transport abstraction that erases protocol differences;
- one fake “network maturity” score;
- flattening wire truth, service truth, schema truth, settings truth, interop truth, and support truth into one readiness blob;
- pretending gRPC, QUIC, HTTP/3, WebTransport, WebSocket, and transport-agnostic RPC are the same lane.

## Archive implications
- The archive should now treat **Protocol Surface + Service Surface + Runtime Settings + Schema Contract + Conformance Traceability + Support Envelope** as a coupled **Protocol Productization Stack** in frontier discussions.
- Future revisions should prefer **wire/bridge truth, service/schema attachments, activation truth, conformance evidence, and support/docs truth** over new transport bake-offs, proxy wrappers, or generic “Rust networking” scorecards.
- When Service, Web, Client, Identity, or Conformance work touches protocols, it should import protocol-productization artifacts rather than re-explain transport/security/bridge posture from scratch.

## Read this together with
- `design/protocol-surface-kit.md`
- `design/service-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/schema-contract-kit.md`
- `design/conformance-traceability-stack.md`
- `design/support-envelope-kit.md`
- `design/docproof-kit.md`
