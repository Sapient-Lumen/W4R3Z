# Frontier salience snapshot — 2026-03-18 (61)

This pass did **not** promote a brand-new ecosystem-wide lane.
It sharpened an existing **shipping and adoption accelerator**:

- **P-0206 Wasm Component Contract & Conformance ShipKit** — because the archive still lacked a believable answer to “what exact component contract is this Rust-built Wasm artifact shipping, and how do we review or rerun it without re-deriving the whole toolchain story?”

## Main judgment

The next worthy move here was **not** another Wasm runtime, another builder wrapper, or another generic component tutorial layer.
Those either already exist in real form or are too broad for a believable artifact-bearing `0.1`.

The sharper missing layer is the **Wasm component shipping contract** above today’s substrate, especially once three more facts are kept explicit:

- **tooling lineage** — whether the artifact came from a native target build, a transitional `cargo-component` path, or native build plus explicit composition.
- **world lock** — the exact package/world/interface/version contract rather than best-effort inference.
- **composition closure** — whether the component is actually closed and runnable, still depends on host-supplied imports, or still has transitive open edges.

That move is better grounded now because:

- current Rust component-model docs say `cargo-component` is in the process of being deprecated because native tooling can be used directly; citeturn843414search0turn204112search0turn204112search5
- Rust’s 2026 goals explicitly treat Wasm Components as a flagship area; citeturn843414search1turn843414search6
- the component composition docs warn that tools are early and inconsistent about interface-version inference/injection; citeturn735786search0
- Wasmtime already supports running component exports through `wasmtime run --invoke`; citeturn215469search1turn215469search2turn215469search5
- the rustc book says `wasm32-wasip3` outputs a component and remains explicitly transitional; citeturn300361search0
- and Wasmtime’s recent security advisory plus release notes show that component-model async/runtime behavior is still moving enough that exercise posture must remain explicit. citeturn843414search2turn843414search5

So the gap is no longer “Rust cannot ship Wasm components.”
The gap is that teams still rarely get a **reviewable cargo-native component bundle** above target choice, WIT/package versioning, composition steps, and runtime/exercise drift.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0524 Crate Example Surface Pack Kit** — still one of the highest-leverage first-success lanes.
4. **P-0525 Crate Diagnosis Surface Pack Kit** — still one of the strongest troubleshooting lanes.
5. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
6. **P-0472 Docs.rs Build Parity & Evidence Kit** — still a sharp hosted-build support lane.
7. **P-0466 Python Wheel ABI & Free-Threading ShipKit** — still one of the clearest foreign-package shipping-contract opportunities.
8. **P-0168 Rust Android Mobile Kit** — still a strong mobile/library shipping-kit lane with explicit policy pressure.
9. **P-0206 Wasm Component Contract & Conformance ShipKit** — now one of the clearest **Band B shipping-kit** opportunities because the substrate exists but the boring contract above tooling shifts and composition drift still does not.
10. **P-0451 Cfg Availability Ledger Kit** — still the sharpest item-level conditional-support truth lane.

## Why this won over adjacent candidates right now

- It beat **another Wasm runtime helper** because the sharper pain is contract truth above runtimes, not one more runtime abstraction.
- It beat **another cargo-component wrapper** because the current docs already point away from treating `cargo-component` as the forever center of gravity.
- It beat **broader plugin/distribution ambitions** because a compact component contract bundle is more believable than a giant Wasm-platform bet.
- It beat **more generic FFI/component proposals** because the current Rust/WIT/component transition already provides a concrete proving ground.

## What changed in the archive

Added:
- `entries/2026-03-18-241.md`
- `meta/frontier-salience-2026-03-18-61.md`
- `meta/wasm-component-artifact-conformance-product-plan-2026-03-18.md`
- `fixtures/wasm-component-artifact-conformance-kit/README.md`
- `fixtures/wasm-component-artifact-conformance-kit/tooling-lineage.report.schema.json`
- `fixtures/wasm-component-artifact-conformance-kit/world-lock.report.schema.json`
- `fixtures/wasm-component-artifact-conformance-kit/composition-closure.report.schema.json`
- `fixtures/wasm-component-artifact-conformance-kit/scenarios/cargo_component_transitional_build_repacked_with_wac/`
- `fixtures/wasm-component-artifact-conformance-kit/scenarios/package_version_inference_breaks_interface_match/`
- `fixtures/wasm-component-artifact-conformance-kit/scenarios/native_wasip2_component_still_requires_host_supplied_imports/`

Updated:
- `proposals/wasm-component-artifact-conformance-kit.md`
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

- native `wasm32-wasip2`/`wasm32-wasip3` builds,
- transitional `cargo-component` workflows,
- package/world/version locks,
- composition steps and dependency closure,
- `wasi:cli/run` runnable components,
- `--invoke`-only exercise surfaces,
- and async/runtime caveats

into one fake “Wasm component support” story.

## Sources

- https://component-model.bytecodealliance.org/language-support/rust.html
- https://github.com/bytecodealliance/cargo-component
- https://github.com/bytecodealliance/cargo-component/releases
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://component-model.bytecodealliance.org/composing-and-distributing/composing.html
- https://component-model.bytecodealliance.org/running-components/wasmtime.html
- https://bytecodealliance.org/articles/invoking-component-functions-in-wasmtime-cli
- https://doc.rust-lang.org/rustc/platform-support/wasm32-wasip3.html
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-xjhv-v822-pf94
- https://github.com/bytecodealliance/wasmtime/releases
