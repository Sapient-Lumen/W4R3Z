# Renewal receipt: Conservative portable self-hosted Wasm edge host (2026-03-22)

Card under review:
- `defaults/conservative-portable-self-hosted-wasm-edge-host-2026Q1.md`

Review goal:
- decide whether the archive should publish a first maintained **portable self-hosted Wasm edge-host** card;
- decide whether the clearest boring current default for the bounded self-hosted Wasm-host lane is **Spin + OCI-packaged Spin apps + SpinKube when Kubernetes is real**;
- and keep application truth, component/runtime truth, OCI/distribution truth, cluster/operator truth, portability truth, and support/docs truth visibly separate.

## Canon import checked
- Rust challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Spin overview:
  https://spinframework.dev/
- Spin running apps:
  https://spinframework.dev/v3/running-apps
- Spin registry support:
  https://spinframework.dev/v3/registry-tutorial
- Spin API support / targets:
  https://spinframework.dev/v3/api-guides-overview
- Spin plugins:
  https://spinframework.dev/v3/plugin-authoring
- Spin testing:
  https://spinframework.dev/v3/testing-apps
- SpinKube docs / quickstart / architecture / packaging:
  https://www.spinkube.dev/docs/
  https://www.spinkube.dev/docs/install/quickstart/
  https://www.spinkube.dev/docs/topics/architecture/
  https://www.spinkube.dev/docs/topics/packaging/
- Component-model distribution / `wkg`:
  https://component-model.bytecodealliance.org/composing-and-distributing/distributing.html
- Rust runnable components:
  https://component-model.bytecodealliance.org/language-support/creating-runnable-components/rust.html
- `cargo component`:
  https://github.com/bytecodealliance/cargo-component
- Wasmtime CLI / WASIp2 / wasi-http:
  https://docs.wasmtime.dev/cli-options.html
  https://docs.wasmtime.dev/examples-wasip2.html
  https://docs.wasmtime.dev/api/wasmtime_wasi_http/
- wasmCloud:
  https://wasmcloud.com/docs/ecosystem/wash/dev/
  https://wasmcloud.com/docs/ecosystem/wadm/model/
  https://wasmcloud.com/docs/concepts/providers/
  https://wasmcloud.com/docs/kubernetes/

## Fresh observations
1. Official Rust signals still say the ecosystem-navigation problem is partly about **choice paralysis** and **tacit knowledge**, which supports publishing a bounded self-hosted Wasm-host default rather than leaving this lane to component-model folklore.
2. Spin is now explicit enough about what it is and is not: an open-source CNCF sandbox project for building and running event-driven applications with Wasm components, with implementations for local, self-hosted, Kubernetes, and hosted services.
3. Spin’s practical product surfaces are now concrete enough to support a boring default: local run/watch, registry packaging, environment-target compatibility warnings, and plugin-based extensions all exist as documented parts of the lane.
4. SpinKube’s docs make the Kubernetes/operator layer reviewable rather than magical: Spin Operator, runtime-class management, `spin kube scaffold`, and OCI-based deploy all have a documented place in the workflow.
5. The component-model layer is real but still not the boring baseline by itself: `wkg` makes OCI distribution of components/WIT concrete, but raw Wasmtime HTTP serving is still explicitly experimental and `cargo component` still documents adaptation from `wasm32-wasip1` to preview2 components.
6. wasmCloud remains serious enough that it must stay visible, but its own docs still flag planned changes to scheduling and providers, which weakens its case as the conservative baseline for this narrower lane.

## Slot-by-slot review
### Application truth
`spin.toml` should be treated as part of the product contract in this lane.
It carries app structure, targets, component boundaries, and deployment assumptions.

### Local-dev truth
`spin up` and `spin watch` are the clearest boring local loop.
`spin test` is promising, but the docs still describe it as under active development and installed from a canary release, so it should remain an adjunct rather than the lane baseline.

### OCI / distribution truth
Spin apps being packaged and distributed as OCI artifacts is a major reason this lane deserves its own card.
It creates a reviewable bridge from local app to registry to cluster.

### Cluster / operator truth
SpinKube is the clearest boring answer once Kubernetes is actually part of the product.
The operator/runtime-class path is explicit and therefore reviewable.

### Component/runtime truth
The lower-level component layer is important but not yet the boring project-level default.
`wkg`, `cargo component`, raw Wasmtime run/serve, and direct host embedding remain escalation tools rather than the first answer.

### Portability truth
This lane is about **portable self-hosting**, not “universal Wasm portability.”
It stays honest by keeping Spin/SpinKube as the default while retaining raw Wasmtime and wasmCloud as explicit alternatives for different goals.

## Serious alternatives retained
- **Raw Wasmtime + custom host / `wasmtime serve`** — strongest alternative when host ownership and embedder control are the point.
- **wasmCloud + `wash` + `wadm`** — strongest alternative when lattice/distributed-capability semantics are central enough to justify more operational and control-plane complexity.

## Judgment
Publish the card as a maintained public default.

Label:
- **default-with-caveats**

Why:
- the project class recurs often;
- the worker-first managed edge card already made the split conceptually necessary;
- the current docs are finally concrete enough to support a bounded self-hosted boring default;
- and the evidence supports a conservative Spin-centered answer without pretending the entire self-hosted component-host landscape has converged.

## Replay notes
- renew when Spin or SpinKube changes enough to move the boring default for this bounded scope;
- renew when raw Wasmtime HTTP/component hosting matures enough to justify a narrower, more central custom-host card;
- renew when wasmCloud roadmap items land strongly enough to change the conservative alternative ranking;
- and keep the boundary with the **worker-first managed edge runtime** card explicit rather than letting the two lanes drift back together.
