# Epic proposal: Portable self-hosted Wasm edge host default lane

## Thesis
Add a maintained defaults-corpus card for **portable self-hosted Wasm edge-hosted web/API products** so the archive can answer a common practical question with a bounded current recommendation instead of only broad component-model / Wasm-host theory.

## Proposed artifact family
- `design/portable-self-hosted-wasm-edge-host-default-lane.md`
- `defaults/conservative-portable-self-hosted-wasm-edge-host-2026Q1.md`
- `evidence/conservative-portable-self-hosted-wasm-edge-host-2026Q1-renewal-2026-03-22.md`
- frontier/meta refresh tying the new card back to `design/web-productization-stack.md`

## Initial lane judgment
For the narrow self-hosted/portable Wasm-host scope, publish:
- **Spin + OCI-packaged Spin apps + SpinKube** as the conservative default;
- **raw Wasmtime + custom host / `wasmtime serve`** and **wasmCloud + `wash` + `wadm`** as serious alternatives for different scopes;
- explicit separation of application/manifest truth, component/runtime truth, OCI/distribution truth, cluster/operator truth, portability/runtime-boundary truth, and support/docs posture.

## Why this is epic-worthy
- It turns a long-promised “portable/self-hosted Wasm host” split into a reusable current answer.
- It covers a recurring real adoption lane rather than an edge case.
- It gives the archive a way to talk honestly about self-hosted Wasm application hosting without pretending that raw component tooling, managed edge runtimes, and conventional Rust servers are the same thing.
- It is exactly the kind of contribution the ecosystem is currently missing: not another Wasm host, but a reviewable boring default with the real runtime/operator boundaries left visible.

## Non-goals
- declaring one Wasm runtime or control plane the universal winner;
- collapsing managed edge runtimes, self-hosted Spin apps, raw custom Wasmtime embeddings, and wasmCloud lattices into one card;
- or replacing `design/web-productization-stack.md`.
