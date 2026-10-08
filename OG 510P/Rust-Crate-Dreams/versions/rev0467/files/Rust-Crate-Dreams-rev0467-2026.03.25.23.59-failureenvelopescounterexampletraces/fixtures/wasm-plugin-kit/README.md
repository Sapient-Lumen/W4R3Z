# Wasm Plugin Kit fixtures

These fixtures support **P-0002 Wasm Plugin Kit**.

They exist to keep four receiver-facing truths separate:

1. **plugin interface** — what package/world or host-function surface is actually authoritative;
2. **capability grant** — what filesystem/network/host-function/configuration rights really exist;
3. **execution budget** — how interruption, time, memory, and pool/store limits are actually enforced;
4. **instance lifecycle** — whether calls are fresh, pooled, or state-reusing.

The scenarios are deliberately small and comparative.
They are designed to stop future passes from flattening “uses Wasm plugins / uses `cargo component` / uses Extism / has a timeout” into one fake plugin-support story.
