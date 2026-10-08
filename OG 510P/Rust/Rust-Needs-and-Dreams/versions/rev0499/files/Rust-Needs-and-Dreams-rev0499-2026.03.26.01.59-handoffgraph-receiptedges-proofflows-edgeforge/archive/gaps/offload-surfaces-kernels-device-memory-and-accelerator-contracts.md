# Gap: offload surfaces, kernel maps, device-memory truth, and reviewable accelerator contracts

## What is missing
Rust now has **real accelerator/offload lanes**, but the ecosystem still lacks a **portable way to describe what an offloaded surface actually promises**.

Today there is no standard way to say:
- whether a library is shipping host-only orchestration, host + kernel code, or a CPU fallback plus optional accelerator lanes,
- which kernel languages or IRs are in play: WGSL, SPIR-V, PTX/NVVM, generated C++/HIP/Metal, or an experimental `std::offload` path,
- what the actual execution targets are: WebGPU, Vulkan, Metal, CUDA, ROCm/HIP, CPU fallback, or some narrower subset,
- how device memory, staging buffers, mapping, copy semantics, and host/device synchronization behave,
- whether unsupported hardware is a compile-time error, runtime dispatch to a different backend, a scalar/CPU fallback, or a silent feature drop,
- how kernels are named, versioned, bundled, or paired with the host-side API,
- whether a crate assumes one queue/stream model, many queues/streams, implicit synchronization, or explicit fences/events,
- and what evidence actually checked the claims: shader compilation tests, differential tests across backends, numerical parity checks, device-matrix runs, or CPU-vs-GPU comparison vectors.

That gap matters because Rust already has meaningful point solutions:
- the Rust project is actively trying to **finish `std::offload`** and has also run a project goal for GPU offloading,
- `wgpu` provides a safe cross-platform GPU API over Vulkan/Metal/D3D12/OpenGL/WebGPU,
- `rust-gpu` lets people write shader crates in Rust and already distinguishes GPU crates from host-side runners,
- CubeCL exposes a single Rust kernel language across WebGPU, CUDA, ROCm, Metal, Vulkan, and CPU,
- CUDA-specific projects expose still-different host/device shapes around streams, modules, memory, and vendor libraries,
- and ML stacks like Burn already ride those backends without making the accelerator contract itself legible.

So the missing contribution is not another GPU wrapper or another backend-specific runtime.
It is a **reviewable offload-surface layer** for publishing kernel maps, backend/device assumptions, memory-transfer truth, fallback posture, and evidence honestly.

Sources:
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/GPU-Offload.html
- https://blog.rust-lang.org/2025/11/19/project-goals-update-october-2025/
- https://blog.rust-lang.org/2026/01/05/project-goals-2025-december-update/
- https://docs.rs/wgpu/latest/wgpu/
- https://docs.rs/wgpu/latest/wgpu/struct.Buffer.html
- https://rust-gpu.github.io/rust-gpu/book/
- https://rust-gpu.github.io/rust-gpu/book/testing.html
- https://docs.rs/cubecl/latest/cubecl/
- https://docs.rs/cudarc/latest/cudarc/
- https://rust-gpu.github.io/rust-cuda/

## The current seam is awkward
Rust already has real diversity in offload style, but today most of it is published as framework docs, feature flags, or folklore:
- the Rust goals work shows `std::offload` is becoming real enough to have frontend intrinsics, CI work, and usage instructions, but is still experimental and still carries target/configuration complexity;
- `wgpu` gives a clean cross-platform host API, but buffer mapping and transfer semantics are sharp enough that the docs have to explain exactly when CPU and GPU may access a buffer and when submissions panic;
- `rust-gpu` already makes a strong structural distinction between **GPU crates** and host-side **runner** crates, which is evidence that host/device boundaries are not just implementation details;
- `rust-gpu` also already runs compile tests and differential tests against WGSL, which means evidence posture is a first-class part of this seam today;
- CubeCL exposes a multi-platform kernel language and says unsupported instructions can become runtime compilation failures, with launch logic responsible for dispatching the right kernel based on device properties;
- `cudarc` and the Rust CUDA project expose yet another shape centered on streams, modules, device memory, and vendor library wrappers rather than graphics-style adapters/devices or browser-facing WebGPU portability.

These are not minor details. They determine whether downstream users can rely on a library on a given accelerator stack, whether CPU fallback is honest, whether kernels are portable or vendor-bound, and whether test results on one device mean anything on another.

Sources:
- https://blog.rust-lang.org/2026/01/05/project-goals-2025-december-update/
- https://docs.rs/wgpu/latest/wgpu/struct.Buffer.html
- https://rust-gpu.github.io/rust-gpu/book/building-rust-gpu.html
- https://rust-gpu.github.io/rust-gpu/book/testing.html
- https://docs.rs/cubecl/latest/cubecl/
- https://docs.rs/cudarc/latest/cudarc/
- https://rust-gpu.github.io/rust-cuda/

## Why this matters
This gap matters because accelerator/offload choices cut across several important Rust futures at once:
1. **performance portability** — the same host API may target very different hardware, compiler paths, and fallback rules.
2. **library honesty** — “GPU accelerated” can mean optional compute shaders, vendor-specific CUDA kernels, cross-platform JIT kernels, or experimental compiler offload.
3. **safety and correctness** — host/device memory access, staging, mapping, and synchronization rules are public semantic surfaces.
4. **ecosystem reuse** — models, media pipelines, simulation, graphics, and scientific code all need some reusable vocabulary above backend-specific crates.
5. **evidence quality** — parity checks, backend matrices, and differential tests matter more than marketing benchmarks when heterogeneous execution is involved.

A worthy contribution here is therefore not another tensor runtime, another shader tutorial, or another “write once run anywhere” promise.
It is a way to treat accelerator/offload surfaces as **reviewable ecosystem infrastructure**.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h1/GPU-Offload.html
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://docs.rs/wgpu/latest/wgpu/struct.Buffer.html
- https://rust-gpu.github.io/rust-gpu/book/testing.html
- https://docs.rs/cubecl/latest/cubecl/

## What “good” looks like
A worthy contribution here is **not** one universal GPU crate that erases meaningful differences.

It is a shared offload-surface boundary:
- one `offload-surface/v0` describing the top-level surface identity, host/kernels split, intended workloads, and whether the package is host-only orchestration, host-plus-kernel, or kernel-first,
- one `kernel-map/v0` for named kernels/modules, source language or IR, entry signatures, specialization constants, bundling/embedding strategy, and version compatibility,
- one `backend-device-profile/v0` for supported backends/devices, feature requirements, queue/stream model, compilation mode (ahead-of-time, JIT, driver JIT, browser/runtime-provided), and target/runtime assumptions,
- one `buffer-transfer-profile/v0` for memory spaces, mapping rules, staging/copy posture, ownership/lifetime rules, zero-copy versus copy semantics, and CPU↔device synchronization expectations,
- one `launch-sync-profile/v0` for dispatch geometry, synchronization/fence/event/stream posture, error surfaces, and completion/visibility rules,
- one `dispatch-fallback-profile/v0` for backend selection, runtime feature detection, CPU/scalar fallback posture, unsupported-instruction behavior, and parity expectations,
- one `offload-adapter-profile/v0` for bridges between `wgpu`, `rust-gpu`, `std::offload`, CUDA-focused wrappers, ML runtimes, and vendor/IR-specific build lanes,
- one `offload-vector-set/v0` for kernel compilation, device capability, transfer, parity, and multi-backend vectors,
- one `offload-check-report/v0` recording which vectors actually ran on which devices/backends/toolchains,
- and one `offload-pack/v0` bundle for docs, CI, migration notes, and archaeology.

That would let Rust teams review “accelerated” claims using explicit artifacts instead of guessing from README badges, benchmark screenshots, or backend feature lists.

## Non-goals
This gap should not be used to:
- define all heterogeneous programming in Rust,
- replace `wgpu`, `rust-gpu`, CubeCL, Burn, CUDA wrappers, or future `std::offload`,
- flatten graphics shaders, compute kernels, ML backends, browser WebGPU, native CUDA, and CPU fallback into one fake universal runtime,
- or turn backend support into a shallow benchmark or device leaderboard.

The job is smaller and sharper:
**make offload/accelerator surfaces legible, honest, and checkable across kernels, backends, memory models, fallback lanes, and evidence.**
