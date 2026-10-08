# Design: Portable self-hosted Wasm edge host default lane (application truth + component/runtime truth + OCI/distribution truth + cluster/operator truth)

## Goal
Add the first maintained **portable self-hosted Wasm edge-host** defaults-corpus card so the archive can answer a recurring practical question:
**what should a serious Rust-involving Wasm web/API product normalize around right now if the team wants provider independence and the clearest boring self-hosted default?**

This lane should not replace the broader `design/web-productization-stack.md`.
It should give that stack one bounded maintained answer for a common project class that the existing worker-first edge card explicitly excluded.

## Why this note is needed now
The archive already has four maintained public web/edge lanes:
- browser-first public web app;
- full-stack Rust web product;
- browser-consumed Wasm package;
- worker-first edge web product.

But it still lacked a maintained answer for **portable self-hosted Wasm application hosting** where the real center is not “a managed worker runtime” and not “an ordinary Rust origin server”, but a Wasm-component-oriented local/OCI/Kubernetes path that stays self-managed and reviewable.

That omission is harder to justify now because:
- Rust’s March 20, 2026 challenges post still frames ecosystem navigation as a problem of **choice paralysis** and **tacit knowledge**;
- the 2025 State of Rust survey still says online documentation is the preferred canonical reference while editor/LLM-mediated learning rises;
- Spin now explicitly presents itself as an open-source CNCF sandbox project built on standards, with implementations for local development, self-hosted servers, Kubernetes, and cloud-hosted services;
- Spin’s docs now make local run/watch, OCI-registry distribution, environment-target compatibility checks, and plugin-based deployment integrations legible enough to support a bounded lane rather than folklore;
- SpinKube’s current docs now make the Kubernetes/operator side concrete: quickstart, Spin Operator, runtime-class management, `spin kube scaffold`, and OCI-based deployment are all explicit;
- the Bytecode Alliance component-model docs now make `wkg`-based WIT/component distribution through OCI registries first-class;
- Wasmtime now has a `serve` subcommand for `wasi:http/proxy` components, but it still explicitly labels that world experimental, which is exactly the kind of lower-level caveat that argues for a higher-level boring default instead of a raw-host baseline;
- `cargo component` remains useful, but its current docs still say it builds with `wasm32-wasip1` and adapts to preview2 components, which is another sign that the lower layer is real but still moving;
- wasmCloud remains a serious self-hosted/distributed alternative, but its own current docs flag planned changes to scheduling and providers, so it is better kept as a serious alternative for the distributed-capability/lattice lane rather than the conservative baseline.

Together those signals say the next worthy move is **not** another generic component-model essay.
It is a bounded boring default card.

## Chosen project class
The first self-hosted Wasm-host card should cover:
- HTTP/event-driven products where the deployable unit is a Spin app or Wasm component bundle and the team wants to self-host or run on their own Kubernetes estate;
- teams that want portability across laptop, OCI registry, and Kubernetes without committing to one managed edge provider;
- platform/application teams that accept app manifest truth, runtime capability truth, and operator/deploy truth as first-class parts of the product;
- products where the goal is to keep Wasm host portability visible, not to hide it behind ordinary container/server conventions.

It should **not** try to cover in one card:
- provider-managed worker runtimes such as Cloudflare Workers or Fastly Compute;
- ordinary full-stack origin hosting where Axum/Actix on a Rust process is the real center;
- browser-first apps or npm/browser package publication;
- or bespoke custom Wasmtime embeddings where the team explicitly wants to own the host API surface itself.

## Default thesis
For this bounded project class, the conservative default should currently be:

**Spin + OCI-packaged Spin applications + SpinKube when Kubernetes is real**

with explicit acceptance that:
- `spin.toml` is part of the product truth;
- OCI distribution is part of the deployment truth;
- cluster/operator/runtime-class configuration is part of the production truth;
- and lower-level component-model / raw-host tools remain important but are not the boring baseline.

Why this is the right first card:
- Spin is the clearest project-level story for “build and run event-driven Wasm components” across local, self-hosted, Kubernetes, and hosted implementations.
- Spin docs now expose app structure, local run/watch, registry distribution, compatibility targets, and plugin integrations in one coherent surface.
- SpinKube gives that path a concrete self-hosted Kubernetes story instead of leaving “portability” as a marketing adjective.
- OCI-based distribution appears in both Spin and component-model (`wkg`) docs, which makes artifact movement reviewable.
- The card can stay honest about lower-layer churn because raw Wasmtime HTTP serving and `cargo component` both still show experimental/adaptation caveats.

## Serious alternatives that must stay visible
### 1. Raw Wasmtime + custom host / `wasmtime serve`
This wins when the team explicitly wants to own the host API surface, HTTP integration, or embedder behavior, and is willing to accept lower-level runtime/component complexity.

### 2. wasmCloud + `wash` + `wadm`
This wins when distributed lattice semantics, provider-like capabilities, host-to-host placement, or multi-environment control planes matter more than the simpler Spin app portability story.

## What the card must keep separate
The maintained card should visibly preserve:
- **application/manifest truth**;
- **component build/runtime truth**;
- **OCI/package/distribution truth**;
- **local-dev/testing truth**;
- **cluster/operator/runtime-class truth**;
- **portability/runtime-boundary truth**;
- **support/docs truth**;
- and **lane judgment** versus project-specific escalation.

## Non-goals
- declaring that WebAssembly hosting has fully converged for all Rust server workloads;
- pretending Spin, raw Wasmtime, and wasmCloud are the same lane;
- hiding Kubernetes/operator/runtime reality behind “just ship a Wasm file” language;
- or turning the corpus into a generic component-model scorecard.

## Archive implications
- Add a first maintained portable-self-hosted-Wasm-host card under `defaults/`.
- Add a first renewal receipt under `evidence/`.
- Refresh corpus/frontier/meta files so the repo treats **portable self-hosted Wasm edge host** as a maintained public lane distinct from **worker-first managed edge runtime**.
- Keep future narrower cards available, especially a separate **raw custom Wasmtime embedder** card or a **browser + Node dual-target Wasm package overlay** if the evidence warrants them later.

## References
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
- SpinKube overview / quickstart / packaging:
  https://www.spinkube.dev/docs/overview/
  https://www.spinkube.dev/docs/install/quickstart/
  https://www.spinkube.dev/docs/topics/architecture/
  https://www.spinkube.dev/docs/topics/packaging/
- Component-model distribution / `wkg`:
  https://component-model.bytecodealliance.org/composing-and-distributing/distributing.html
- Rust component-model runnable components:
  https://component-model.bytecodealliance.org/language-support/creating-runnable-components/rust.html
- `cargo component`:
  https://github.com/bytecodealliance/cargo-component
- Wasmtime docs / CLI serve / WASIp2:
  https://docs.wasmtime.dev/
  https://docs.wasmtime.dev/cli-options.html
  https://docs.wasmtime.dev/examples-wasip2.html
  https://docs.wasmtime.dev/api/wasmtime_wasi_http/
- wasmCloud:
  https://wasmcloud.com/docs/ecosystem/wash/dev/
  https://wasmcloud.com/docs/ecosystem/wadm/model/
  https://wasmcloud.com/docs/concepts/providers/
  https://wasmcloud.com/docs/kubernetes/
