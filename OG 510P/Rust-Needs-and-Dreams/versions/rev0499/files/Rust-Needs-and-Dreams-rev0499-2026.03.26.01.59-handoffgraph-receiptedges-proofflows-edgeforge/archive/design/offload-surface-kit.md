# Design: Offload Surface Kit (`cargo offloadsurf`, `offload-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **accelerator/offload surfaces** in Rust: experimental compiler offload, host-orchestrated GPU compute, shader crates, vendor-specific CUDA/HIP lanes, multi-backend compute systems, and CPU fallback paths.

This should help answer questions like:
- what kernels exist and how are they paired with the host-side API,
- what device/backend/runtime assumptions must hold before launch,
- what host/device transfer and mapping semantics apply,
- what happens when a backend or device feature is missing,
- how synchronization, completion, and visibility are expressed,
- and what evidence shows the offloaded lane is correct and portable enough.

It should **not** replace accelerator runtimes themselves, define one kernel language, or force WebGPU, SPIR-V, CUDA, HIP, Metal, and `std::offload` into one fake common denominator.

## Why now
This seam has become strategically relevant because Rust now spans several real but incompatible offload shapes at once:
- the official project goals include finishing `std::offload`, and the 2025 offload work already has frontend intrinsics, CI work, and a path toward nightly experimentation;
- `wgpu` gives a safe host-side cross-platform lane, but its buffer and synchronization model is semantically sharp enough that the docs must spell out mapping and submission constraints;
- `rust-gpu` already treats shader crates as a distinct artifact type from host runners and already relies on compile/differential testing to keep semantics honest;
- CubeCL already spans WebGPU, CUDA, ROCm, Metal, Vulkan, and CPU with runtime dispatch based on device properties;
- CUDA-focused Rust stacks still expose streams, modules, device memory, and vendor libraries in a very different shape;
- and higher-level stacks like Burn increasingly depend on this substrate without making the substrate itself reviewable.

So the ecosystem is past the point where “just pick a backend” is a sufficient organizing principle.

Sources:
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://blog.rust-lang.org/2026/01/05/project-goals-2025-december-update/
- https://docs.rs/wgpu/latest/wgpu/struct.Buffer.html
- https://rust-gpu.github.io/rust-gpu/book/testing.html
- https://docs.rs/cubecl/latest/cubecl/
- https://docs.rs/cudarc/latest/cudarc/

## Core artifact family

### 1) `offload-surface/v0`
Top-level package identity for an offloaded surface.

Fields:
- crate/workspace/package id
- surface kind (`host-only-orchestrator`, `host-plus-kernels`, `kernel-crate`, `runtime-backend`, `adapter-layer`)
- problem family (`graphics`, `compute`, `tensor`, `simulation`, `media`, `general-purpose`, etc.)
- declared host API entrypoints
- declared kernel families
- claimed deployment lanes (`browser`, `native desktop`, `server`, `embedded accelerator`, `vendor toolkit`, `cpu fallback`)
- attached profiles and reports

### 2) `kernel-map/v0`
Named kernel/module inventory.

Fields:
- kernel/module id
- source kind (`wgsl`, `spirv-rust`, `ptx-rust`, `generated-cpp`, `std-offload`, `vendor-ir`, `other`)
- host-visible name / symbol / entrypoint
- specialization constants / launch-parameter shape
- artifact/bundling strategy (`embedded`, `built-at-runtime`, `compiled-aot`, `driver-jit`, `browser-provided`)
- compatibility notes (backend/device/toolchain expectations)
- source attachments (optional)

### 3) `backend-device-profile/v0`
Backend, runtime, and device assumptions.

Fields:
- backend family (`webgpu`, `vulkan`, `metal`, `d3d12`, `cuda`, `hip`, `opencl`, `cpu`, `experimental-offload`)
- runtime/provider crate(s)
- compile mode (`aot`, `jit`, `driver-jit`, `mixed`)
- required device features / limits / capabilities
- queue/stream model
- browser/native restrictions
- MSRV/toolchain/channel requirements
- unsupported-device behavior

### 4) `buffer-transfer-profile/v0`
Host↔device memory and transfer truth.

Fields:
- resource kinds (`buffer`, `texture`, `image`, `tensor`, `module`, `graph`, `stream-owned memory`)
- mapping rules (exclusive CPU/GPU access, mapped-at-creation, async map, driver-managed, opaque vendor objects)
- staging policy (`explicit staging`, `implicit staging`, `zero-copy when available`, `driver-dependent`)
- ownership/lifetime rules
- transfer directions and visibility timing
- alignment/layout/packing notes
- safety caveats or runtime panics/errors on misuse

### 5) `launch-sync-profile/v0`
Dispatch and synchronization truth.

Fields:
- launch geometry semantics
- queue/stream/encoder usage
- fence/event/barrier posture
- completion model (`blocking`, `poll`, `callback`, `future`, `join`, `event-based`)
- error-surface shape (compile error, runtime launch error, validation error, device loss, panic)
- ordering/visibility guarantees promised to callers

### 6) `dispatch-fallback-profile/v0`
Backend choice and fallback posture.

Fields:
- backend selection rules
- device capability detection strategy
- kernel selection rules
- unsupported-instruction or missing-feature behavior
- CPU/scalar fallback posture
- parity expectations between lanes
- performance caveats that materially alter support claims

### 7) `offload-adapter-profile/v0`
Interop and migration between offload stacks.

Fields:
- source/target stacks (`wgpu`↔`rust-gpu`, CubeCL↔Burn, CUDA wrapper↔model runtime, etc.)
- artifact conversions
- layout/typing assumptions
- synchronization/ownership caveats
- lossy areas
- migration notes

### 8) `offload-vector-set/v0`
Reviewable vectors.

Kinds of vectors:
- kernel compile vectors
- backend/device capability vectors
- transfer/mapping vectors
- CPU-vs-device parity vectors
- cross-backend comparison vectors
- failure/unsupported-feature vectors
- smoke/perf-budget vectors (bounded, not leaderboard-shaped)

### 9) `offload-check-report/v0`
Machine-readable results.

Fields:
- vectors attempted / skipped
- backend/device/toolchain matrix actually exercised
- pass/fail/unsupported outcomes
- numerical tolerance / parity notes
- artifact digests
- logs or trace attachments

### 10) `offload-pack/v0`
Bundle tying the above together for docs, CI, audits, migration work, and downstream review.

## Proposed commands
- `cargo offloadsurf init` — scaffold artifact set for a crate/workspace.
- `cargo offloadsurf inspect` — infer candidate kernels, backend crates, and runtime lanes from source/build metadata.
- `cargo offloadsurf check` — run validation/parity/device vectors and emit `offload-check-report/v0`.
- `cargo offloadsurf diff` — compare offload claims between revisions.
- `cargo offloadsurf export` — bundle `offload-pack/v0` for release/docs/CI.

## Review questions this makes tractable
- Is this crate actually cross-platform, or just multi-backend in theory?
- Are kernels bundled, JIT-compiled, or driver-compiled at runtime?
- Is CPU fallback real, partial, or absent?
- When can the host touch a resource, and when must it wait for the device?
- What happens on unsupported hardware or missing features?
- Which backend/device/toolchain matrix was actually tested?
- Do parity claims hold across CPU and accelerator lanes?

## Example use cases

### A) `wgpu` compute library
Publish:
- a host-side `offload-surface/v0`
- WGSL `kernel-map/v0`
- WebGPU/Vulkan/Metal backend profiles
- a buffer-transfer profile documenting mapping/unmap/staging rules
- parity vectors against a CPU implementation

### B) `rust-gpu` shader workspace
Publish:
- one kernel-crate surface for shader crates
- one adapter profile linking shaders to runner crates
- SPIR-V kernel maps
- compiletest + difftest-backed check reports

### C) CubeCL/Burn backend lane
Publish:
- multi-backend profiles for WebGPU/CUDA/ROCm/Metal/Vulkan/CPU
- dispatch-fallback truth documenting runtime device selection
- parity vectors across CPU and chosen device backends
- adapter profiles feeding higher-level tensor/model surfaces

### D) CUDA-focused systems crate
Publish:
- CUDA-specific backend/device profile
- stream/module/memory transfer posture
- explicit vendor-library and driver assumptions
- fallback truth that says “none” when none exists

## Why this is better than today
Today, downstream users infer support from README claims like “GPU accelerated”, “supports CUDA”, or “works with WebGPU”.
Those phrases hide the most important questions:
- which kernels exist,
- how data moves,
- what synchronization the user must respect,
- whether CPU fallback is honest,
- and what evidence actually ran.

Offload Surface Kit makes those questions first-class without requiring every stack to converge on one runtime or one compiler path.

## Non-goals
- No attempt to define one universal kernel language.
- No attempt to replace `wgpu`, `rust-gpu`, CubeCL, CUDA wrappers, or `std::offload`.
- No attempt to reduce accelerator support to benchmark charts.
- No attempt to hide backend-specific hazards when they materially affect support truth.

## MVP shape
The first practical MVP should target four lanes:
1. `wgpu` compute crates,
2. `rust-gpu` shader + runner workspaces,
3. CubeCL/Burn backend-based compute crates,
4. CUDA-focused host/device crates.

That MVP would already be enough to prove whether one reviewable artifact family can sit above today’s heterogeneous accelerator ecosystem without flattening it.
