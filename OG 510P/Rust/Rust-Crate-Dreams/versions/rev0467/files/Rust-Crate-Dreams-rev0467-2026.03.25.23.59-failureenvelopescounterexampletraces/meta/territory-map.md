## Added 2026-03-22 — in-place initialization is its own support-contract sub-territory

Keep a distinct sub-territory for:
- **placement truth** — where bytes are first written and where the final allocation lives,
- **constructor-lane truth** — by-value Rust, pinned-init, out-pointer, `moveit`, Crubit `Ctor`, or future-language lane,
- **address-commit truth** — when movement becomes forbidden,
- **failure-cleanup truth** — what can fail and who owns rollback,
- **transition drift** — what changed release-to-release.

This belongs primarily in **P-0447**, not as a side note inside projection semantics, unsafe fields, or generic FFI.

## Added 2026-03-22 — lint-policy evidence is its own review-contract sub-territory

Keep a distinct sub-territory for:
- **policy-authority truth** — where effective levels came from,
- **checked-scope truth** — what was really checked,
- **diagnostic-channel truth** — which producer/channel emitted each finding,
- **waiver truth** — which exceptions are explicit and owned,
- **lint-policy drift** — what changed across revisions.

This belongs primarily in **P-0459**, not as a side note inside workspace cleanup, unsafe auditing, or generic CI policy.

## Added 2026-03-22 — unsafe-field invariants are their own contract sub-territory

Keep a distinct sub-territory for:
- **field authority truth** — where the invariant claim came from,
- **mutation-lane truth** — which paths can mutate the field,
- **trusted-constructor truth** — which paths may establish the invariant,
- **witness-scope truth** — what evidence touched that contract,
- **field-contract drift** — what changed across revisions.

This belongs in **P-0460**, not as a side note inside generic unsafe auditing, generic docs, or generic Miri/verification work.

## Added 2026-03-22 — documentation-example support as a distinct territory

Within the docs/tooling cluster, keep a distinct sub-territory for:
- **manifest truth** (what rustdoc extracted),
- **rewrite lineage** (what changed after extraction),
- **execution-mode truth** (standalone, merged, wrapper, compile-only, ignored, render-only),
- **support class** (host-run, target-run, docs.rs-render, manual-review),
- **docs-example drift** across toolchains and policy changes.

This sub-territory belongs under **P-0455**, with **P-0481** for runner profiles, **P-0472** for docs.rs parity, and **P-0476** for coverage/debt review.

## Added 2026-03-22 — sanitizer workflow evidence is its own support-contract sub-territory

Keep a distinct sub-territory for:
- **instrumentation-scope truth** — what code and libraries were really on the sanitizer lane,
- **runtime-linkage truth** — whether Rust’s default runtime or an explicit external route carried the run,
- **symbolization-route truth** — whether reports are portable handoff artifacts or only local raw traces,
- **suppression-policy truth** — whether suppressions are owned operational debt or silent evidence laundering.

This belongs in **P-0434**, not as a side note inside target support, debugger support, or verification campaigns.


## Added 2026-03-22 — dependency lifecycle is its own support-contract territory

Keep a distinct sub-territory for:
- **criticality lane truth** — where third-party crates may live,
- **abstraction seam truth** — what makes replacement plausible,
- **transition posture** — pin / contain / fork / vendor / internalize / replace,
- **lifecycle drift** — what widened or tightened exposure release-to-release.

This belongs in **P-0535**, not as a side note inside trust scoring, MSRV policy, or off-ramp recipes.


## Added 2026-03-22 — support-evidence topology as a first-class territory

Within the support-contract cluster, keep a distinct sub-territory for:
- **artifact-route truth** (stable interface vs `target/` convention vs Cargo-internal layout),
- **host-target topology truth** (host build helpers vs target artifacts vs runner/device/docs service),
- **official-support drift** (docs.rs defaults and target-tier movement).

This sub-territory belongs under **P-0484**, not as a separate cargo helper niche.

## 2026-03-22 — cross-language interop now deserves a clearer shared core

The latest scan suggests the archive should treat interop as a **stack**, not one bucket:

- **P-0121** for shared boundary-contract truth,
- language-specific shipkits for packaging/delivery,
- plugin/component lanes for lifecycle and sandboxing,
- runtime-attachment lanes for VM/interpreter-specific obligations.

Current broad rerank: **P-0484**, **P-0121**, **P-0036**, **P-0535**, and **P-0532** now form the archive’s clearest top support-contract front line.

When broad scans touch interop, consult `meta/cross-language-interop-frontier-2026-03-22.md` before minting another shipkit-shaped proposal.

## 2026-03-22 — broad scans should keep the frontier balanced across application areas

The latest official signals make it too easy to over-focus on one fashionable lane.
Future territory scans should keep at least one serious frontier visible in each of these families:

- toolchain / target / support posture
- MSRV / stability / dependency lifecycle
- debugging / build friction / diagnosis
- async / runtime / service operations
- cross-language interop
- safety / assurance / verification
- public API / release readiness / trust

Current broad rerank: **P-0484**, **P-0036**, **P-0121**, **P-0535**, and **P-0532** now form the archive’s clearest top support-contract front line.


## 2026-03-21 — add task supervision / restart as a distinct contract lane

The archive already had adjacent lanes for lifecycle/shutdown truth, async replay/debugging, runtime assurance, and actor/plugin/runtime substrate. The next ordinary lie was still too cheap: a crate could say “supports background workers / graceful shutdown / auto restart” and leave downstream teams without one compact answer for **what restarts together, which exits count as restart triggers, what state resets, what timeout means, and what bundle explains the incident**.

The sharper move is therefore to deepen **P-0095 Task Supervision & Restart Kit** with first-class review objects for:

- `supervision-topology.receipt`
- `restart-policy.receipt`
- `health-source.receipt`
- `state-reset.receipt`
- `shutdown-escalation.receipt`
- `supervision-failure-bundle.manifest`

Do not let future passes flatten this lane into another actor framework, another retry helper, or another graceful-shutdown cookbook.

# Territory map

This is the “wide net” map. Not everything here is proposal-ready.
If an idea has weak evidence, keep it here until sources are found.

## Cargo / enterprise
- Compatibility gates / semver regression + evidence bundles (see P-0089)
- Shared evidence-bundle substrate / portable review-pack grammar with container-basis, entry-lineage, attestation-lane, publication-route, and share-safety receipts (P-0256)
- Offline mirrors + airgap bundles (see P-0001, P-0018)
- Policy-as-code for deps, provenance, audits (see P-0007, P-0016, P-0017)

## Supply chain / trust
- Provenance / attestations (P-0015)
- Trust-cost scoring + confusable detection (P-0017)
- Sustainable maintenance signals (P-0011)
- TUF-aware mirroring + verification workflows (see P-0026)

## Async / correctness
- Structured concurrency (P-0008)
- Deterministic testing + record/replay (P-0009)
- “Default cancellation story” docs + patterns
- Async runtime assurance / qualification profiles (new: runtime family, shutdown truth, allocation posture, evidence basis)

## Reflection / metaprogramming
- Comptime reflection bridge artifacts: schema-source, coverage-scope, execution-posture, and loss-accounting receipts above runtime registries, static shape exports, and format projections (P-0439)
- Keep bridge artifacts distinct from final language reflection standardization, runtime value mutation frameworks, and serialization-format-only schemas

## Compliance / legal
- Deterministic third-party license bundles (P-0014)
- License-change gating (candidate: integrate into P-0014)

## Plugins / extensibility
- Wasm Component Model plugin kit (P-0002)

## WASI / Component Model interop
- Conformance suites + golden fixtures across runtimes (candidate: WASI conformance kit)

## Desktop shipping
- Packaging/signing/updates kits (P-0012)

## Data integration
- Connector authoring runtime kit (P-0013)


## Privacy / metrics
- Privacy-respecting metrics kit (P-0022)

- Privacy gateways (OHTTP/BHTTP) deploy + interop bundles (see P-0194, P-0196)
## Local-first / sync
- Opinionated local-first sync building blocks (CRDT adapter + transport + E2EE + fixtures)

## Data contracts / schema evolution
- Data contract + schema compatibility kit (P-0024)
- OpenAPI 3.1 / JSON Schema toolchain contract with explicit dialect, ref-policy, projection, compatibility-profile, and semantic-diff receipts (see P-0224)

## Reliability testing
- Chaos/fault-injection lab with reproducible artifacts (P-0025)

## Verification / formal methods
- Cross-tool verification campaign contract for Kani / Creusot / Prusti / Miri / Flux / Verus with explicit obligation inventory, trust ledger, policy gates, and comparability reports (see P-0485)

## Safety-critical / assurance
- Assurance-case workbench: claim/evidence graphs + GSN/SACM export + change-impact review packs (see P-0503)
- Keep this distinct from raw evidence producers like contracts, lints, coverage, and unsafe-audit receipts
- Keep this distinct from full certification/lifecycle platforms

## Networking / realtime web
- WebTransport “shipkit” + interop capture bundles (P-0170)

## Hardware crypto / HSMs
- PKCS#11 keystore + HSM operational workbench with redacted evidence bundles (P-0171)

## Messaging / brokers
- NATS/JetStream ops + replayable incident bundles (P-0172)

Last updated: 2026-03-22

## Robotics / autonomy
- ROS 2 ergonomics layers for rclrs (high-level patterns, launch/config, TF-like transforms)
- Deterministic simulation + replay harnesses for robot stacks

## Embedded fleet operations
- Secure OTA update artifact formats + state machines + conformance fixtures

## HPC / distributed computing
- Typed MPI ergonomics (see P-0021)
- GPU portability layers and array standards (see P-0003)

## GUI / UX
- Text input/IME/composition as reusable engine (see P-0027)

## Data / analytics
- Open table formats interoperability (Iceberg/Delta/Hudi) (see P-0028)

## Creative / media
- Real-time DSP graph primitives (see P-0029)


## Build-time sandboxing
- Sandbox build scripts and proc macros (P-0030, P-0033)
- Wasm-based proc macro sandbox runners (track upstream proposals; tooling bridge)

## Sandboxing primitives
- Cross-platform process sandbox crate (P-0031)
- Standard “policy profiles” + conformance tests for sandboxes

## Linkers / cross-link lanes
- Linker lane support contracts and doctor bundles: system default vs self-contained lld vs Zig vs Windows SDK vs containerized lanes
- Lane-switch diffs that separate perf-only shifts from support-surface changes
- Host/target config-scope contracts: which flags/config hit build scripts, proc macros, rustdoc, and target artifacts, with mixed-build drift bundles
- Same-triple lane-change witnesses: explicit `--target <host-triple>` or docs-builder command shapes that materially change scope even when triples look equal

## Build & dependency ergonomics
- Native dependency contracts with explicit system/vendored/override mode locks and policy receipts (see P-0058)
- Dependency update policies (holds / forbid versions / pubtime age gating) (P-0034)
- Build performance insights from persisted build metadata (P-0035)
- Rebuild explanation bundles that freeze Cargo sessions/live capture into one support artifact (P-0469)
- Resolver why-bundles with MSRV-aware version-choice receipts, lane-partition + platform-coverage reports, unification-scope reports, feature-intent reports, dependency-origin reports, feature-origin reports, dependency-identity reports, selection-scope locks, and explicit exact/manual-review boundaries (P-0468)
- MSRV inference and mixed-workspace workflows (P-0036)
- Lock-contention witnesses: who blocked whom, on which target/build/package-cache root, with what mitigation and wrapper/cache-mode context (P-0490)

## App plumbing
- Secrets provider chains and typed redaction across environments (P-0037)


## Determinism & rollback gamedev
- Shared determinism harnesses (state hashing, snapshot/restore, desync repro artifacts)

## Kubernetes operator engineering
- Black-box integration test harnesses for controllers/services (Kind/k3d fixtures, artifact capture)

## Safe content rendering
- Turnkey safe Markdown pipelines (parser + sanitizer + highlight allow-lists + XSS corpus)

## Devtools / debugging

- Error surface contracts: stable codes, audience modes, remediation receipts, and safe-export posture above today's error/report crates (P-0533)
- (P-0124) Schema compatibility workbench (`cargo schema`) with portable diff reports.
- (P-0123) Energy/Carbon observability for benchmarks and CI diffs.
- Debugger UX: LLDB/GDB pretty printers + cargo doctor + conformance goldens (P-0083)
- Debugger visualizer compatibility receipts: embedded NatVis/GDB asset matrices and drift bundles (P-0491)
- Memory observability kit: capture/diff bundles, allocator + optional eBPF (P-0084)

## GPU / compute
- GPU compute interop kit: CUDA/ROCm/wgpu compute with kernel packaging + conformance (P-0085)

## Networking

- (P-0122) QUIC + HTTP/3 interop & capture bundles (qlog/pcap) for CI and maintainers.
- Deterministic rollback + replay bundles (see P-0090)


## Added lanes (2026-03-05)
- **GUI / UX testing**: snapshot/event harnesses, accessibility regression.
- **Privacy engineering**: differential privacy pipelines, policy/budget tooling.
- **Hermetic builds**: capsules, offline/locked, reproducibility transfer artifacts.

## Crypto / PQC / protocol agility
- Hybrid PQC transport integration (TLS/QUIC/SSH) with interop vectors and policy tooling (P-0098)

## Data evolution & archive safety
- Schema evolution workbench (versioned wire types + verified migrations + reports/corpora) (P-0099)
- Zero-copy archive safety envelope (validation + compatibility evidence + corpus replay) (P-0100)

## Crash pipelines / postmortems
- Crash bundle + symbolication workbench (P-0101) — capture-basis, module-identity, symbol-route, analysis-coverage, replayability, and share-safety receipts above today's dump writers, stackwalkers, and symbol fetchers
- Async incident replay contracts and deterministic replay artifacts for bugs (see P-0073)

## Wasm / components
- Component warmstart / pre-initialization + verification (P-0103)
- WASI conformance suites (see earlier WASI kit proposals)


## Security & identity (additional lanes)
- Passkeys / WebAuthn integration kits (storage + framework adapters + diagnostics)
- Hardware-backed key stores (TPM2 flows, attestation, sealing)

## Data layer reliability (additional lanes)
- Schema drift detection + migration replay conformance (sqlx/diesel/sea-orm)

## Artifact distribution (OCI / registries)
- Cargo-native OCI artifact publishing + referrer graph management (P-0131)

## Formal methods → tests
- Spec-to-test connectors (TLA+/Apalache/embedded model checking) with replayable corpora + minimized counterexamples (P-0132)

## Chaos / resilience practice
- Scenario libraries + portable failure bundles + adapters for in-process failpoints and simulated networks (P-0133)
## Identity / zero‑trust
- Workload identity ergonomics (SPIFFE/SPIRE golden path, rotation, policy, debug bundles)
- OAuth/OIDC interoperability + hardened profile suites (PAR, DPoP, evidence bundles)
- SCIM provisioning conformance harness + replayable incident bundles
- SD-JWT / SD-JWT VC conformance vectors + privacy-negative tests

## Localization / product i18n
- End‑to‑end l10n pipelines (extract/validate/compile/pseudo‑l10n, ICU4X+Fluent integration)


## IoT / smart home
- Matter device/controller interop harness + evidence bundles (P-0137)
- “pre-cert” regression profiles that can run in CI (commissioning, interactions)

## Email / messaging
- Email auth verification lab: DKIM/SPF/DMARC/ARC/BIMI with replayable DNS evidence (P-0138)
- Deliverability incident bundles that can be shared safely (redaction-first)

## Data / SQL engines
- SQL dialect conformance + differential testing corpora + `sqlfail.zip` (P-0139)
- Triangulation harnesses (3 engines) to isolate semantic regressions quickly
## Performance traces / profiling UX
- Perfetto-first “trace bundles” + cargo workflows: capture → open → diff → share (`perfettobundle.zip`) (P-0140)
- Cross-tool conversions (traceconv) and CI diff-friendly summary reports

## GPU / graphics conformance
- WebGPU CTS runner + triage + minimization bundles (`ctsfail.zip`) and interop comparisons (P-0141)

## Modern crypto envelopes
- HPKE-based envelope formats with profiles, vectors, and bug bundles (`hpkebundle.zip`) (P-0142)


## Robotics workflows
- ROS 2 “workcell” scaffolding + bag replay fixtures + conformance bundles (`rosbundle.zip`) (P-0143)

## Geospatial data distribution and analytics interop
- PMTiles / COG / GeoParquet pipelines with validators + reproducible evidence bundles (`geobundle.zip`) (P-0144)

## Threshold cryptography operations
- FROST threshold signing service kit with transcripts, policies, and replayable vectors (`frostbundle.zip`) (P-0145)

## Secure messaging / E2EE subsystems
- MLS deployment layer (storage + envelope migration + delivery semantics + replay bundles) (P-0146)

## PKI / TLS automation
- Autotls (ACME + rustls) with doctor workflows + evidence bundles (P-0147)

## CBOR credentials / COSE tokens
- COSE/CWT/SD-CWT profiles + conformance corpora + evidence bundles (P-0148)

## ZK / verifiable compute
- zkVM workbench: cargo workflows + proof attempt bundles (`zkbundle.zip`) + cross-backend portability tests

## Bluetooth / device interop
- BLE interop + GATT conformance harnesses, evidence bundles (`blebundle.zip`), and scenario minimization

## SIMD / kernel verification
- shared SIMD kernel catalog + correctness harness + standardized performance reports

## Realtime / WebRTC
- SFU/media router core + interop harness + portable bug bundles (P-0152)

## Secrets / GitOps
- SOPS/age compatible library + CI evidence bundles + policy gates (P-0153)

## Wasm / portability
- Wasmtime deployment evidence capsules + Pulley-aware portability checks (P-0154)

## Routing security (RPKI / RTR / ROV)
- Incident replay + decision diffs + portable evidence bundles (`rpkibundle.zip`) (P-0155)

## Time synchronization
- NTP/NTS + PTP/gPTP discipline workflows + reproducible drift bundles (`timesyncbundle.zip`) (P-0156)

## Privacy-preserving compute
- FHE application workbench: profiles + conformance + shareable evidence bundles (`fhebundle.zip`) (P-0157)


## New lanes (2026-03-05)
- SMR conformance & failure bundles (`smrbundle.zip`)
- Embedded HIL evidence bundles (`hilbundle.zip`)
- Codemod-driven ecosystem migrations (`codemod-report.json`)

## XR / OpenXR
- XR runtime selection + diagnostics (`XR_RUNTIME_JSON` etc.) and portable bug bundles (see P-0161)

## DNS / transport policy
- DoT/DoH/DoQ/DoH3 policy + matrix testing + evidence bundles (see P-0162)

## Dataflow ergonomics
- “Ops layer” on timely/differential: deterministic replay bundles + conformance packs (see P-0163)

## Industrial + Automotive
- OPC UA deployment + conformance harnesses
- CAN/ISO-TP/UDS diagnostics incident bundles

## Data privacy in observability
- Redaction policy-as-code + evidence bundles + CI gates


### Lanes (recent additions)
- IoT interop/conformance (MQTT)
- Mobile shipping kits (Android)
- Database extension ship/release engineering (Postgres/pgrx)

## New lanes (2026-03-05)

- Email APIs: JMAP client/server workbench (P-0173)
- MASQUE / CONNECT-UDP proxy shipkit (P-0174)
- Cargo/registry: trusted publishing tooling (P-0175) — provider-scope matrices, claim-basis receipts, trigger-policy reports, and publish-mode rehearsal bundles


## Fediverse / Social protocols
- ActivityPub federation ops substrates, interop corpora, incident bundles.


## Kernel / USB / Device fuzzing
- External USB fuzzing harnesses, virtual device models, portable crash bundles.


## TUI Testing
- Deterministic render snapshots, interaction replay, CI diffs for Ratatui/terminal apps.

## Media provenance / authenticity
- C2PA content credentials ShipKit (P-0179)

## Web security interop
- HTTP Message Signatures profiles + fixtures (P-0180)
- DPoP / OAuth sender-constrained flows (see earlier proposals)

## ISA / emulation conformance
- RISC-V emulator/ISS conformance runner + bundle artifacts (P-0181)

## Messaging / federation
- Matrix Sliding Sync interop harness + evidence bundles (P-0185)

## PKI / transparency
- CT v2 monitor + bundle-first SCT/proof verification (P-0186)

## Bioinformatics / scientific data
- Bioformats conformance profiles + reproducible pipeline evidence (P-0187)

- Identity & IAM: VC v2.0 interop workbenches, credential profiles, bundle-first debugging
- IaC & Infra Plugins: Terraform provider SDKs in Rust (protocol bindings + acceptance harness)
- API Composition: GraphQL federation subgraph compliance & conformance harnesses



## Dependency source / vendoring
- Vendored-source parity, source identity, replacement-chain, and coverage bundles (P-0496)

## Hardware support / CPU contracts
- CPU baseline promises, runtime-dispatch manifests, and illegal-instruction risk bundles (P-0497)

## Foreign package ecosystems
- Python wheel and ABI contracts (see P-0466, P-0482, P-0487)
- Apple XCFramework / SwiftPM release contracts (see P-0467, P-0482, P-0487)
- Node/npm native-addon package and prebuild contracts (see P-0498)
- NuGet RID-aware native interop ship contracts (see P-0499)
- JVM/JAR/JNI release contracts (see P-0500)
- RubyGems native-extension ship contracts (see P-0501)


## Cargo tool-only workflow parity
- Tool-build receipts, comparison-baseline locks, and override-command provenance bundles for rust-analyzer / wrapper / preflight workflows (P-0494)

- Tool-build receipts, comparison-baseline locks, override-command provenance bundles, **selection-coverage reports**, and **workspace-invocation receipts** for rust-analyzer / wrapper / preflight workflows (P-0494)

- Service readiness & drain contracts: activation gates, readiness surfaces, health channels, shutdown triggers, drain policy, and in-flight-fate reports above Tower/Hyper/Axum/Tonic/Tokio substrate (see P-0534)

- Async dyn transition / migration receipts above `async-trait`, `trait-variant`, `dynosaur`, `dynify`, and future native support (P-0458).

- Assurance-case productization: claim-library basis + import policy + assumption ledger + review gate + export projection (see P-0503 refinement, 2026-03-21)

## Sustainable maintenance / stewardship routing
- Health/support windows plus work-routing contracts, response-channel posture, and continuity backstops (P-0011)

## Added 2026-03-22 — unsafe contract auditing sits between docs, witnesses, and larger verification campaigns

`P-0120 Unsafe Contract Auditor Kit` now occupies a sharper territory cell:

- below full verification campaigns,
- above raw witnesses like Miri and Loom,
- adjacent to FFI boundary contracts,
- and distinct from sanitizer/debugger operational evidence.

Its job is to keep unsafe obligation authority and witness limits legible.

## 2026-03-22 — delegated build-time support frontier

The archive should now treat build-time delegation as a distinct frontier above today’s buildscript/native/packaging substrate.
The core territory is not “all build scripts”; it is the review layer for:

- named build-unit topology,
- per-unit output lanes,
- override authority,
- artifact-bridge posture,
- and drift across releases/toolchains.

Anchor proposal: **P-0508 Cargo Build Script Delegation Kit**.
Adjacent but distinct lanes: **P-0046 buildscript-ux-kit**, **P-0059 buildscript-testkit**, **P-0484 toolchain/target support**, and native dependency policy lanes.


## 2026-03-22 — compile-time sandbox policy frontier

The archive should now treat compile-time sandbox policy as a distinct territory cell above today’s Cargo/build-script/proc-macro substrate.
The core territory is not “all sandboxing”; it is the review layer for:

- policy authority,
- actor capability scope,
- enforcement mode,
- exception ownership,
- and drift across revisions/backends.

Anchor proposal: **P-0107 Cargo Sandbox & Capability Policy Kit**.
Adjacent but distinct lanes: **P-0508 delegated build-time support**, **P-0040 proc-macro sandbox readiness**, **P-0519 runtime crate authority**, and lower-level sandbox/runtime substrate proposals.


## 2026-03-22 — rebuild-causality support frontier

The archive should now treat rebuild-causality support as a distinct territory cell above Cargo’s current build-analysis substrate.
The core territory is not “all performance analysis”; it is the review layer for:

- session import/freeze,
- baseline authority,
- exactness class,
- reverse-impact honesty,
- and small portable support bundles.

Anchor proposal: **P-0469 Cargo Rebuild Explanation Kit**.
Adjacent but distinct lanes: **P-0035** historical build insights, **P-0490** contention witnesses, **P-0494** tool-surface parity, and **P-0468** resolver explanation.
