# Frontier salience — 2026-03-25 (243)

## Main judgment

The wide territory scan still does **not** justify a new monolithic frontier lane.

It does justify three sharper conclusions:

1. the archive’s best near-frontier work remains **horizontal** rather than domain-umbrella-shaped;
2. **P-0509 + P-0536** now look even more clearly like the practical front door;
3. any new sector proposal should now clear a stricter worthiness bar before it can compete with the control-plane ring.

## Salience board

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit — task-oriented crate selection, interop-aware starter sets, and reviewable decision receipts**
2. **P-0536 Crate Knowledge Pack Kit — canonical API/docs/example bundles for search, support, and assistant-grade crate understanding**
3. **P-0486 Debuggability Support Contract Kit — support-posture receipts, symbol-sidecar manifests, and debugger-ready release bundles**
4. **P-0538 Concurrency Contract Kit — reentrancy scopes, progress/fairness classes, wait-cancellation reports, and execution-context boundaries**
5. **P-0472 Docs.rs Build Parity & Evidence Kit — docs.rs preflight receipts, sandbox-limit reports, and local-vs-hosted diff bundles**
6. **P-0535 Dependency Lifecycle Transition Kit — criticality lanes, abstraction seams, replacement-readiness, and lifecycle drift bundles**
7. **P-0484 Toolchain & Target Support Contract Kit — rust-toolchain intent, component/target receipts, and support-drift bundles**
8. **P-0537 Compile Iteration Feedback Kit — coverage-scope/claim-ceiling receipts, patch-eligibility and live-update truth, activation/generation/retirement truth, and restart-fallback bundles**
9. **P-0431 Public Dependency Boundary Kit — manifest-intent receipts, effective-boundary verdicts, and migration bundles**
10. **P-0496 Cargo Vendor & Source Parity Kit — source-identity locks, mirror-honesty reports, and offline coverage bundles**
11. **P-0489 Cargo Build-Dir Consumer Transition Kit — consumer inventories, path contracts, and upgrade-safe transition receipts**
12. **P-0011 Crate Health Contract Kit — maintenance windows, succession maps, and support-intent receipts**
13. **P-0058 native-deps-kit — declarative system dependency management across pkg-config/vcpkg/vendoring**
14. **P-0125 Cargo SBOM Precursor Workbench Kit — precursor capture locks, normalized build-graph transforms, and diffable review bundles**
15. **P-0046 buildscript-ux-kit — structured build-script diagnostics, summaries, and policy hooks**
16. **P-0532 Async Runtime Assurance Profile Kit — runtime profiles, service-topology receipts, capability routes, and bridge-debt evidence for async runtime choice under scrutiny**

## Why the board changed a little

### P-0536 moves up

The archive had already made decision packs important.
The broad sector scan makes it clearer that **knowledge portability** is the next universal bottleneck:
- docs/examples/API surfaces are still central to how people evaluate crates;
- online docs remain a preferred canonical reference;
- docs.rs and rustdoc JSON surfaces make more of that substrate machine-consumable;
- assistant-mediated evaluation is increasingly real whether the ecosystem wants it or not.

That makes **P-0536** more than an adjacent docs helper.
It looks increasingly like the **memory plane** of crate evaluation.

### P-0537 moves up

Compile-iteration truth is not only a “tooling nerd” concern.
It matters across:
- service edit/build/restart loops,
- Wasm/plugin development,
- GUI/desktop iteration,
- and target-constrained environments where feedback claims are often fuzzy.

A crate that exports honest coverage/claim-ceiling/activation truth could help many sectors without pretending to own hot reload itself.

### P-0431 moves up modestly

Public-dependency boundary clarity now matters more because supply-chain, semver, and SBOM visibility keep getting more operationally relevant.
A crate that can export effective boundary truth and migration receipts fits the current Rust trajectory better than another abstraction bundle.

## Why several domain mega-lanes stay below the frontier

The territory scan suggests that web, GUI, game, ML, local-first, science, and “enterprise platform” themes are mostly **receiver-rich but boundary-poor** when described as giant umbrella crates.

They become competitive only when reduced to a sharper seam such as:
- packaging and plugin evidence,
- interop/profile evidence,
- support contracts,
- decision receipts,
- or transition/handoff artifacts.

## Practical build queue after the territory pass

1. **P-0509 + P-0536** — freezeable decision packets plus replayable knowledge packs as one front door
2. **P-0486** — make debug support truthful, portable, and importable by later decision stages
3. **P-0472 + P-0484** — hosted docs and target/toolchain truth as durable evidence inputs
4. **P-0537 + P-0489** — iteration truth and build-dir transition truth as boring but widely reusable reality layers
5. **P-0535 + P-0496 + P-0431** — lifecycle, source parity, and public-boundary change as the maintenance/supply-chain ring
6. **P-0538** — keep concurrency contract work hot because async remains central and confusion remains expensive
7. **P-0058 + P-0125 + P-0046** — native/build/SBOM support lanes where substrate reality is concrete enough to exploit

## Promotion rule after this pass

A new proposal should not enter the frontier merely by being broad or important.
It should enter only if it can show at least one of these:
- a reusable artifact family;
- a reusable decision family;
- a narrow sector seam that many teams really repeat;
- or a concrete substrate hook that has recently become buildable.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://doc.rust-lang.org/cargo/reference/build-cache.html
- https://docs.rs/about/builds
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://www.arewewebyet.org/
- https://www.areweguiyet.com/
- https://arewegameyet.rs/
- https://www.arewelearningyet.com/
- https://github.com/rust-embedded/not-yet-awesome-embedded-rust
- https://georust.org/
- https://automerge.org/
- https://blog.rust-lang.org/inside-rust/2025/11/24/safety-critical-rust-in-2025/
