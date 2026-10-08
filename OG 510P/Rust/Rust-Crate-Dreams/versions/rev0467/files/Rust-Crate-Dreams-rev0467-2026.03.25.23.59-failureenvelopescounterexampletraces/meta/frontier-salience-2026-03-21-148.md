
# Frontier salience snapshot — 2026-03-21-148

This pass did **not** add another deterministic runtime, another generic trace spec, or another test artifact format.
It deepened **P-0073 Async Replay Debugger Kit**.

## Why this frontier moved up

The current substrate now makes the missing layer much sharper:

- the Rust project explicitly says first-class support for debugging `async` code is still missing from the overall debugging experience;
- `console-subscriber` and `tokio-console` now make rich runtime telemetry practical, but that path remains Tokio-specific today and depends on experimental runtime instrumentation;
- Tokio docs are concrete enough to classify both cooperative task scheduling and paused/auto-advanced test time as useful but narrower truths than whole-incident replay;
- `tracing` gives structured spans/events plus explicit future instrumentation, which in turn makes lineage/coverage gaps classifiable instead of hand-wavy;
- `loom` and `shuttle` prove that schedule control and deterministic repro are real, but they do not by themselves answer effect-boundary or export-fidelity questions;
- `sturgeon` proves that narrow async effect slices can be recorded and replayed with timing, which sharpens the distinction between slice replay and whole-incident replay.

That combination means “supports async debugging” and “supports replay” are now too vague as crate claims.
A worthy crate in this frontier should publish at least:

1. **schedule-basis truth**,
2. **time-basis truth**,
3. **instrumentation-coverage truth**,
4. **effect-boundary truth**,
5. **replay-fidelity truth**.

## Main conclusion

Promote **P-0073** upward, but keep it narrow.
The sharper next move is not a universal time-travel debugger and not a whole new runtime.
It is a boring contract that keeps **schedule**, **time**, **coverage**, **effects**, and **fidelity** separately reviewable.

## Ranked near-term frontier from this pass

1. **P-0532 Async Runtime Assurance Profile Kit** — still strongest because runtime lock-in and qualification posture remain major ecosystem gaps.
2. **P-0002 Wasm Plugin Kit** — still strong because receiver-facing plugin contracts remain fragmented.
3. **P-0073 Async Replay Debugger Kit** — strengthened because the async debugging substrate is real, but honest replay-support contracts are still fragmented.
4. **P-0081 Stable Plugin Host Kit** — still strong because native-plugin support surfaces remain fragmented.
5. **P-0003 Array API** — still strong because numerics contracts remain fragmented.

## Keep these boundaries sharp

- **P-0073** is schedule basis + time basis + coverage + effects + replay fidelity truth.
- harness/minimization lanes are separate.
- artifact-spec lanes are separate.
- generic run/test bundle lanes are separate.
- runtime assurance / shutdown / qualification lanes are separate.

Do not let “async replay” flatten those into one fake crate.
