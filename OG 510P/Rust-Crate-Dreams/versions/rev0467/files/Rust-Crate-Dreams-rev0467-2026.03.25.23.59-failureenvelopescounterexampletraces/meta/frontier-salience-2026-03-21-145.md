# Frontier salience snapshot — 2026-03-21-145

This pass did **not** add another runtime, marketplace, or native ABI-stable dylib lane.
It deepened **P-0002 Wasm Plugin Kit**.

## Why this frontier moved up

The current substrate now makes the missing layer much sharper:

- the Rust project’s 2026 goals explicitly elevate Wasm Components as a flagship area;
- Wasmtime now documents a real application-with-plugins pattern using components;
- Wasmtime’s component embedding API makes WIT worlds and generated bindings first-class;
- the component-model docs now make packages, worlds, and distribution/fetching part of the normal mental model;
- `cargo component` is real and useful, but it still explicitly says it is experimental and may break projects;
- Extism now documents concrete plugin-system concepts, manifests, immutable host config, allowlisted hosts/paths, and pooled plugin instances;
- Wasmtime’s own docs also make execution-budget choices concrete: fuel is deterministic but slower, while epochs are coarser and typically faster.

That combination means “supports Wasm plugins” is now too vague as a crate claim.
A worthy crate in this frontier should publish at least:

1. **plugin interface truth**,
2. **capability grant truth**,
3. **execution budget truth**,
4. **instance lifecycle truth**,
5. and one portable manifest that can honestly say what runtime/tooling assumptions were imported.

## Main conclusion

Promote **P-0002** sharply upward, but keep it narrow.
The sharper next move is not a new runtime or plugin marketplace.
It is a boring contract that keeps **interface world**, **capability grants**, **execution budgets**, and **instance lifecycle/state reuse** separately reviewable.

## Ranked near-term frontier from this pass

1. **P-0532 Async Runtime Assurance Profile Kit** — still strongest because runtime-family and qualification posture remain major ecosystem gaps.
2. **P-0002 Wasm Plugin Kit** — strengthened because the component/plugin substrate is real now, but receiver-facing plugin contracts are still fragmented.
3. **P-0106 Test Run Artifact Standard Kit** — still strong because portable run-contract truth remains fragmented.
4. **P-0533 Error Surface Contract Kit** — still strong because identity/audience/remediation/sensitivity remain broadly under-specified.
5. **P-0076 Local-first Sync Kit** — still strong because durable state, presence, and history truth remain under-contracted.

## Keep these boundaries sharp

- **P-0002** is interface world + capability grants + execution budgets + instance lifecycle truth.
- runtimes are separate substrate.
- native ABI-stable plugins are a separate adjacent lane.
- registries/OCI distribution are separate substrate.
- sandbox policy engines are adjacent but separate product lanes.

Do not let “plugin support” flatten those into one fake crate.
