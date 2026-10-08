# Default card: Conservative portable self-hosted Wasm edge host (2026 Q1)

Latest renewal receipt: `evidence/conservative-portable-self-hosted-wasm-edge-host-2026Q1-renewal-2026-03-22.md`

## Scope
This card applies to:
- HTTP/event-driven products whose deployment unit is a Spin app or Wasm component bundle rather than a conventional long-running Rust server process;
- teams that want **self-hosted or self-managed portability** across laptop, OCI registry, and Kubernetes;
- products where app manifest truth, Wasm runtime truth, and operator/deploy truth all matter alongside Rust code;
- teams that want a conservative boring default for **portable/self-hosted Wasm hosting**, not a managed edge provider.

Assumptions:
- stable Rust for the product code;
- the team wants the clearest boring default for a **self-hosted Wasm application host** rather than a raw custom embedder;
- OCI registries are acceptable as an artifact/distribution surface;
- the product can accept that `spin.toml`, runtime targets, and deployment/operator surfaces are part of the support envelope;
- portability and self-hosting matter more than one provider’s integrated bindings/network edge.

This is **not** the default for:
- Cloudflare Workers / Fastly Compute style managed worker runtimes;
- ordinary full-stack Rust origin servers;
- browser-first web apps or browser-consumed Wasm packages;
- or custom Wasmtime embedding where owning the host API surface is the main point.

## Why this default now
Rust’s latest challenges framing still says ecosystem navigation depends too much on **choice paralysis** and **tacit knowledge**.
https://blog.rust-lang.org/2026/03/20/rust-challenges/

The 2025 State of Rust survey still says online documentation is the preferred canonical reference while editor/LLM-mediated learning rises.
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Spin now explicitly presents itself as an open-source CNCF sandbox project for building and running event-driven microservice applications with Wasm components, built on standards, with implementations for local development, self-hosted servers, Kubernetes, and cloud-hosted services.
https://spinframework.dev/

Spin’s docs also make the practical application lifecycle legible enough to support a boring default:
- `spin up` / `spin watch` provide the local run loop;
- Spin apps can be packaged and run from OCI registries;
- `application.targets` lets `spin build` warn when an app uses APIs unsupported by a target environment;
- plugins make deployment integrations such as `spin kube` explicit rather than magical.
https://spinframework.dev/v3/running-apps
https://spinframework.dev/v3/registry-tutorial
https://spinframework.dev/v3/api-guides-overview
https://spinframework.dev/v3/plugin-authoring

SpinKube’s current docs now make the Kubernetes side concrete: quickstart, Spin Operator, runtime-class management, scaffold generation, OCI-based packaging/deploy, and routing are all explicit.
https://www.spinkube.dev/docs/install/quickstart/
https://www.spinkube.dev/docs/topics/architecture/
https://www.spinkube.dev/docs/topics/packaging/

At the same time, the lower-level component/runtime layer still carries caveats that argue for a higher-level boring default instead of a raw-host baseline:
- `wkg` and the component-model docs make OCI-based WIT/component distribution real;
- Wasmtime’s `serve` subcommand supports `wasi:http/proxy`, but the docs still call that world experimental;
- `cargo component` still says it builds `wasm32-wasip1` modules and adapts them into preview2 components;
- wasmCloud remains serious, but its docs explicitly flag planned changes to scheduling and providers.

Those are exactly the conditions where a bounded self-hosted default card is useful.

## Default lane
For this scope, default to:

**Spin + OCI-packaged Spin apps + SpinKube when Kubernetes is real**

Use it as:
- the primary application/manifest surface (`spin.toml`);
- the primary local run/build/watch surface;
- the primary registry artifact surface;
- and the default self-hosted Kubernetes path when the product actually needs cluster deployment.

Label:
- **default-with-caveats**

## Core slot guidance
### Application/runtime slot
Default to **Spin applications**.

Why:
- it is the clearest project-level story for building and running Wasm-component web/event products across local, self-hosted, Kubernetes, and hosted implementations;
- the application manifest is explicit and reviewable;
- the local-dev loop, registry path, and deployment integrations are already documented in one place.

### Local-dev slot
Default to **`spin up` + `spin watch`**.

Why:
- the run/watch/build path is explicit;
- logs, registry-run behavior, and local file-vs-registry behavior are documented;
- the developer loop is opinionated enough to be teachable.

Caveat:
- treat `spin test` as a serious but not-yet-boring adjunct because the docs still describe it as under active development and distributed through a canary release path.

### Distribution slot
Default to **OCI-packaged Spin apps**.

Why:
- Spin directly supports pushing apps to OCI-compliant registries and running/deploying from them;
- SpinKube packaging/deploy guidance is already written around OCI artifacts;
- OCI keeps the artifact story portable instead of provider-specific.

### Kubernetes slot
Default to **SpinKube** when Kubernetes is actually part of the product.

Why:
- SpinKube makes the self-hosted operator/runtime-class path explicit;
- `spin kube scaffold` and `spin kube deploy` keep the bridge between app and cluster concrete;
- the docs spell out Spin Operator, Runtime Class Manager, and the containerd shim rather than hiding cluster truth.

### Build/component slot
Default to **Spin-first app build surfaces**, not raw custom-component plumbing first.

Why:
- the self-hosted host lane is about the product/runtime shell, not about maximizing component-tooling cleverness;
- raw `cargo build --target wasm32-wasip2`, `cargo component`, and manual WIT/package composition are still important but remain lower-level tools.

Caveat:
- escalate when WIT package resolution, component composition, or non-Spin host interoperability is central enough that `wkg` / `cargo component` become part of the main product truth.

## Serious alternatives and when they win
### Raw Wasmtime + `wasmtime serve` / custom embedder wins when
- the team explicitly wants to own the host API surface;
- HTTP handling, sandbox policy, or embedding behavior must be customized deeply;
- or Spin’s application-level conventions feel too high-level for the runtime being built.

Caveat:
- keep the experimental state of `wasi:http/proxy` and the lower-level embedder burden visible.

### wasmCloud + `wash` + `wadm` wins when
- lattice/distributed deployment semantics are the point;
- capability/provider-style application composition is central;
- or the product needs wasmCloud’s control-plane and multi-host operational model more than Spin’s simpler app portability story.

Caveat:
- keep current roadmap-visible changes to scheduling and providers visible rather than narrating wasmCloud as a fully settled boring baseline.

## Escalate to a project-specific brief when
- the product should probably just be a normal Rust origin server;
- the product needs a raw custom Wasmtime embedder rather than an application framework;
- WIT package distribution and component composition are the real center of gravity;
- the team is genuinely deciding between Spin/SpinKube and wasmCloud because distributed capabilities/lattice semantics matter;
- or compliance/ops constraints make Kubernetes/operator/runtime-class details dominant.

## Canonical references
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
- Component-model distribution:
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

## Renewal inputs
Recheck before renewal:
- whether Spin + OCI-packaged apps + SpinKube still remains the clearest boring default for this self-hosted Wasm-host scope;
- whether raw Wasmtime HTTP hosting matured enough to justify a separate narrower but more central default card;
- whether `cargo component` and the component-model packaging/tooling moved enough to change the build/component guidance;
- whether Spin target-compatibility, registry, test, or Kubernetes guidance materially shifted;
- whether wasmCloud stabilized enough that the boring default should narrow toward distributed-lattice self-hosting instead;
- whether the boundary with the **worker-first managed edge runtime** card remains right.

## Non-goals
This card is not:
- a universal WebAssembly server verdict;
- a claim that all self-hosted Wasm stories have converged;
- a replacement for project-specific ops/compliance review;
- or permission to smuggle a conventional container/origin-server architecture into a Wasm-host card.
