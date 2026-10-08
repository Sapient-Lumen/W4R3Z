---
id: P-0029
title: audio-graph-kit — real-time safe DSP graph primitives + adapters for Rust
status: idea
domains: [audio, dsp, realtime, systems, creative]
last_reviewed: 2026-03-01
evidence:
  - https://github.com/RustAudio/audio-ecosystem
  - https://github.com/RustAudio/vst-rs/issues/193
  - https://raphlinus.github.io/synthesizer/2018/09/19/synth-update.html
  - https://users.rust-lang.org/t/rf-signal-processing-in-rust/79660
---

# Problem

Rust has many audio crates, but the ecosystem is still described as fragmented and limited in capability.
Meanwhile, major plugin/host ecosystems shift over time (e.g., VST2’s end-of-life and related maintenance decisions),
stranding developers who need stable, safe primitives.

What’s missing is a *small, reusable foundation* for real-time DSP graphs:
a correct-by-default model for audio callbacks, buffer lifetimes, parameter automation, and graph scheduling,
with adapters to existing I/O crates and hosts.

# Users & user stories

- **App developers**: “I want to build a real-time synth/effects pipeline without accidental allocations or audio dropouts.”
- **DSP/SDR developers**: “I want reusable primitives for filters/resampling/FFT pipelines and streaming graphs.”
- **Library authors**: “I want a common processor/graph contract so crates can interoperate.”

# Prior art (and why it’s insufficient)

- RustAudio’s ecosystem overview highlights fragmentation and limited capability; there isn’t a widely-adopted “graph core.”
- Many projects are monoliths (engines) or narrow slices (I/O, DSP ops) without a shared graph contract.

# Design goals

1. **Real-time safety by construction** (no allocations, no locks on audio thread; explicit message passing).
2. **Composable graph model**: nodes/processors + connections + compile step to a stable schedule.
3. **Parameter automation**: sample/block-accurate parameter streams with smoothing.
4. **Adapters over ownership**: integrate with existing I/O backends rather than replacing them.
5. **Testability**: offline graph runner + deterministic processing tests.

# Non-goals

- A full DAW, plugin format, or UI framework.
- Picking one “best” DSP algorithm set; focus on graph plumbing and contracts.
- Enforcing a single sample format (support f32 first; extensible later).

# Architecture & API sketch

## Core traits

- `AudioProcessor`: stateless-ish per-block processor contract
- `ProcessContext`: sample rate, block size, time, parameter inputs
- `AudioBuffer`: borrowed slices with explicit channel layout

```rust
trait AudioProcessor {
    fn prepare(&mut self, cfg: PrepareConfig) -> Result<()>;
    fn process(&mut self, ctx: &ProcessContext, inputs: &[AudioBuffer], outputs: &mut [AudioBuffer]);
}
```

## Graph

- `GraphBuilder`: add nodes, connect ports, declare latencies
- `CompiledGraph`: frozen schedule + buffers preallocated
- `GraphRunner`: runs in audio callback or offline

## Real-time control plane

- `RtMailbox<T>`: lock-free single-producer/single-consumer for control messages
- Parameter changes delivered as bounded queues or per-block slices

# Security / safety model

- Core is safe Rust; avoid unsafe unless strictly necessary for performance with well-audited encapsulation.
- Provide debug assertions to detect accidental allocation on the audio thread (feature-gated).
- Make “unsafe real-time patterns” explicit and opt-in.

# Maintenance & governance plan

- Keep scope tight: graph contracts + scheduling + control plane.
- Host adapters as optional crates: `audio_graph_cpal`, `audio_graph_midir`, etc.
- Seek RustAudio community alignment early (avoid another fragment).

# Milestones

- **0.1**: core `AudioProcessor` + `GraphBuilder` + offline runner + golden tests.
- **0.2**: real-time callback runner + one I/O adapter (e.g., cpal) + example synth graph.
- **0.3**: parameter automation + smoothing + benchmark suite.
- **0.4**: ecosystem integration docs (“how to wrap your DSP crate as a node”).

# Open questions

- What’s the best default buffer layout (interleaved vs planar) for interoperability?
- Should the graph support dynamic topology changes, or require rebuild/compile?
- How to represent latency and delay compensation without becoming a DAW?

# Sources

- RustAudio overview (fragmentation/limitations): https://github.com/RustAudio/audio-ecosystem
- vst-rs deprecation (ecosystem shifts/maintenance risk): https://github.com/RustAudio/vst-rs/issues/193
- Audio infrastructure commentary: https://raphlinus.github.io/synthesizer/2018/09/19/synth-update.html
- DSP needs in Rust (filters/resampling/FFT): https://users.rust-lang.org/t/rf-signal-processing-in-rust/79660
