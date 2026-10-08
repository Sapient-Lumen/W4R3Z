
# Frontier salience snapshot — 2026-03-21-147

This pass did **not** add another plugin runtime, Wasm marketplace, or general FFI crate.
It deepened **P-0081 Stable Plugin Host Kit**.

## Why this frontier moved up

The current substrate now makes the missing layer much sharper:

- `abi_stable` explicitly supports Rust-to-Rust FFI, runtime-loaded libraries, and plugin systems with load-time type-checking;
- `abi_stable::library` documents root-module loading plus compatibility checking over the root module and referenced types;
- prefix types now make additive module/vtable evolution concrete enough to treat as a first-class contract fact;
- `libloading` remains the low-level loader substrate, but its docs are explicit that library initialization and termination routines behave like unknown foreign code from a safety perspective;
- adjacent crates such as `cglue`, `safer_ffi`, and `interoptopus` prove there is real FFI substrate, but they do not by themselves give another team one boring native-plugin support contract;
- Cargo’s 2026 “plugin of the cycle” framing is another reminder that plugin surfaces remain strategically important even when Cargo itself cannot absorb every workflow.

That combination means “supports native plugins” is now too vague as a crate claim.
A worthy crate in this frontier should publish at least:

1. **ABI surface truth**,
2. **capability-negotiation truth**,
3. **lifecycle / unload / reload truth**,
4. **compatibility-witness truth**,
5. and one portable manifest that can honestly say which substrate was imported.

## Main conclusion

Promote **P-0081** upward, but keep it narrow.
The sharper next move is not a new loader, not a new stable ABI effort, and not a plugin marketplace.
It is a boring contract that keeps **surface**, **negotiation**, **lifecycle**, and **compatibility witness** separately reviewable.

## Ranked near-term frontier from this pass

1. **P-0532 Async Runtime Assurance Profile Kit** — still strongest because runtime-family and qualification posture remain major ecosystem gaps.
2. **P-0002 Wasm Plugin Kit** — still strong because receiver-facing plugin contracts remain fragmented.
3. **P-0081 Stable Plugin Host Kit** — strengthened because native-plugin substrate is real, but honest ABI/lifecycle/compatibility contracts are still fragmented.
4. **P-0003 Array API** — still strong because receiver-facing numerics contracts remain fragmented.
5. **P-0106 Test Run Artifact Standard Kit** — still strong because portable run-contract truth remains fragmented.

## Keep these boundaries sharp

- **P-0081** is ABI surface + capability negotiation + lifecycle posture + compatibility witness truth.
- Wasm plugin lanes are separate.
- lower-level loaders and FFI helpers are substrate.
- general sandbox policy engines are adjacent but separate.
- a universal stable Rust ABI effort is separate language/toolchain work.

Do not let “native plugin support” flatten those into one fake crate.
