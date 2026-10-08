# Gap: Portable self-hosted Wasm edge hosts still lack a reviewable boring default for app/package/runtime/cluster truth

## The missing thing
Rust now has several real Wasm-hosting stories, but the ecosystem still lacks a **reviewable boring default** for teams asking:
**how should we ship a serious self-hosted Wasm web/API product in Rust without turning every project into a component-runtime folklore exercise?**

## Why the gap is real
Current signals all point to the same missing layer:
- Rust’s official challenges framing still names **choice paralysis** and **tacit knowledge** in ecosystem navigation.
- Spin now explicitly claims a standards-based path across local development, self-hosted servers, Kubernetes, and cloud-hosted services.
- Spin’s docs now make local run/watch, registry packaging, compatibility targets, and plugin extensions concrete enough to be operational guidance instead of vague promise.
- SpinKube makes the self-hosted Kubernetes/operator/runtime-class story explicit rather than hidden.
- The component-model docs now make OCI-based distribution of components and WIT packages real through `wkg`.
- Wasmtime’s self-hosted HTTP/component surface is real, but its `serve` story still carries experimental caveats.
- `cargo component` remains useful, but its own docs still expose adaptation and preview churn.
- wasmCloud remains serious, but its current docs also expose planned changes to scheduling and providers.

The ecosystem therefore does **not** mainly lack “another Wasm runtime”.
It lacks a portable way to keep the following truths reviewable at once:
- which application/manifest is actually the supported unit,
- how components are built and run,
- how artifacts move through OCI registries,
- how Kubernetes/operator/runtime-class reality enters the product,
- where portability ends and raw-host complexity begins,
- and when a team should stay on a Spin-style host instead of building a custom host or adopting a lattice/control-plane story.

## Why this deserves a maintained card instead of only a stack note
This project class recurs often.
Teams repeatedly ask some variant of:
- should we use Spin,
- raw Wasmtime,
- wasmCloud,
- or just run a normal Rust service somewhere?

Without a bounded maintained answer, guidance collapses back into hype, whichever Wasm demo was most recent, or one platform team’s prior familiarity.
That is exactly the kind of tacit-knowledge failure the archive is trying to reduce.

## Proposed correction
Publish a maintained defaults-corpus card for **portable self-hosted Wasm edge host** with:
- **Spin + OCI-packaged Spin apps + SpinKube** as the conservative default for the narrow self-hosted Wasm-host scope;
- **raw Wasmtime + `wasmtime serve` / custom host** and **wasmCloud + `wash` + `wadm`** as explicit serious alternatives;
- a receipt that keeps application truth, component/runtime truth, OCI/distribution truth, cluster/operator truth, portability/runtime-boundary truth, and support/docs truth visibly separate.

## References
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://spinframework.dev/
- https://spinframework.dev/v3/running-apps
- https://spinframework.dev/v3/registry-tutorial
- https://spinframework.dev/v3/api-guides-overview
- https://spinframework.dev/v3/plugin-authoring
- https://spinframework.dev/v3/testing-apps
- https://www.spinkube.dev/docs/install/quickstart/
- https://www.spinkube.dev/docs/topics/architecture/
- https://www.spinkube.dev/docs/topics/packaging/
- https://component-model.bytecodealliance.org/composing-and-distributing/distributing.html
- https://component-model.bytecodealliance.org/language-support/creating-runnable-components/rust.html
- https://github.com/bytecodealliance/cargo-component
- https://docs.wasmtime.dev/cli-options.html
- https://docs.wasmtime.dev/examples-wasip2.html
- https://docs.wasmtime.dev/api/wasmtime_wasi_http/
- https://wasmcloud.com/docs/ecosystem/wash/dev/
- https://wasmcloud.com/docs/ecosystem/wadm/model/
- https://wasmcloud.com/docs/concepts/providers/
- https://wasmcloud.com/docs/kubernetes/
