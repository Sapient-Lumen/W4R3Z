# Frontier salience snapshot — 2026-03-18 (62)

This pass did **not** promote a brand-new ecosystem-wide lane.
It sharpened an existing **shipping and adoption accelerator**:

- **P-0498 Node-API Package & Prebuild Contract Kit** — because the archive still lacked a believable answer to “what exact npm-native support promise is this Rust addon release making, and how can another person review it without replaying CI and loader quirks by hand?”

## Main judgment

The next worthy move here was **not** another binding generator, another package template, or another release action collection.
Those either already exist in real form or are too broad for a believable artifact-bearing `0.1`.

The sharper missing layer is the **Node package shipping contract** above today’s substrate, especially once three more facts are kept explicit:

- **prebuild coverage** — which runtime/platform/libc tuples are actually shipped as native payloads versus left to local builds or unsupported gaps.
- **loader route** — whether the package really loads through `node-addons`, tries native artifacts first, falls back to `default`, or drops into local build / WASM escape hatches.
- **publish identity** — whether the package was published through trusted publishing with provenance, token/manual flows, or other release posture that affects reviewer trust but does not by itself settle runtime support.

That move is better grounded now because:

- Node.js still documents Node-API as the ABI-stable native-addon surface; [Sources: Node-API docs; ABI stability guide]
- Node’s package docs now make `"node-addons"` and `--no-addons` an explicit routing seam, and recommend a more universal `default` path when appropriate; [Sources: Node packages docs]
- Node’s addon docs still keep Worker/context-aware loading and cleanup rules explicit enough that “native addon exists” is not the same as “all runtime paths are equally safe”; [Sources: Node addons docs; CLI/errors docs]
- `napi-rs` v3 and current docs now make cross compilation, generated JS loaders, and WASM fallback stories materially more ordinary; [Sources: napi-rs homepage/docs/blog]
- and npm now documents trusted publishing plus automatic provenance generation for supported public-package flows, which makes publish identity part of the release surface rather than unrelated supply-chain trivia. [Sources: npm trusted publishing docs]

So the gap is no longer “Rust cannot ship Node addons.”
The gap is that teams still rarely get a **reviewable cargo-native npm bundle** above artifact tuples, loader branches, and release-identity facts.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0524 Crate Example Surface Pack Kit** — still one of the highest-leverage first-success lanes.
4. **P-0525 Crate Diagnosis Surface Pack Kit** — still one of the strongest troubleshooting lanes.
5. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
6. **P-0472 Docs.rs Build Parity & Evidence Kit** — still a sharp hosted-build support lane.
7. **P-0466 Python Wheel ABI & Free-Threading ShipKit** — still one of the clearest foreign-package shipping-contract opportunities.
8. **P-0168 Rust Android Mobile Kit** — still a strong mobile/library shipping-kit lane with explicit policy pressure.
9. **P-0206 Wasm Component Contract & Conformance ShipKit** — now one of the clearest Wasm shipping-contract opportunities.
10. **P-0498 Node-API Package & Prebuild Contract Kit** — now one of the clearest npm-facing ship-contract opportunities because the substrate exists but the boring contract above prebuild matrices, loader routing, and publish identity still does not.

## Why this won over adjacent candidates right now

- It beat **another napi-rs helper** because the sharper pain is release-contract truth above existing authoring substrate, not another authoring surface.
- It beat **a generic npm publish bot** because the archive already had enough evidence that publishing automation and support contracts are separate lanes.
- It beat **broader foreign-package generalization** because Node/npm still has ecosystem-specific truths around `node-addons`, local native fallbacks, and provenance-backed publish identity.
- It beat **consumer-side doctoring first** because the producer-side support contract still needs to exist before downstream diagnosis can inherit it cleanly.

## What changed in the archive

Added:
- `entries/2026-03-18-242.md`
- `meta/frontier-salience-2026-03-18-62.md`
- `meta/node-api-package-prebuild-contract-product-plan-2026-03-18.md`
- `fixtures/node-api-package-prebuild-contract-kit/prebuild-coverage.report.schema.json`
- `fixtures/node-api-package-prebuild-contract-kit/loader-route.receipt.schema.json`
- `fixtures/node-api-package-prebuild-contract-kit/publish-identity.report.schema.json`
- `fixtures/node-api-package-prebuild-contract-kit/scenarios/musl_gap_hidden_by_local_build_fallback/`
- `fixtures/node-api-package-prebuild-contract-kit/scenarios/node_addons_native_path_with_default_wasm_fallback/`
- `fixtures/node-api-package-prebuild-contract-kit/scenarios/trusted_publisher_provenance_present_but_manual_runtime_claims_still_need_review/`

Updated:
- `proposals/node-api-package-prebuild-contract-kit.md`
- `INDEX.md`
- `README.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/prioritization.md`

## What this pass deliberately did not do

It did **not** collapse:

- Node-API ABI floors,
- generated loader branches,
- prebuild/native/local-build/WASM routes,
- npm trusted publishing and provenance posture,
- and broader Bun/Deno marketing claims

into one fake “Node addon support” story.

## Sources

- https://nodejs.org/api/n-api.html
- https://nodejs.org/en/learn/modules/abi-stability
- https://nodejs.org/api/addons.html
- https://nodejs.org/api/packages.html
- https://nodejs.org/api/cli.html
- https://nodejs.org/api/errors.html
- https://napi.rs/
- https://napi.rs/docs/introduction/getting-started
- https://napi.rs/docs/cli/build
- https://napi.rs/blog/announce-v3
- https://docs.npmjs.com/trusted-publishers/
- https://docs.npmjs.com/creating-and-publishing-unscoped-public-packages/
