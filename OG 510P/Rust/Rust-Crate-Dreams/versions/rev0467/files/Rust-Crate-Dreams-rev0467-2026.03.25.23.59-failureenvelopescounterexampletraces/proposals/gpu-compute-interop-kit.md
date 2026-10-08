---
id: P-0085
title: GPU Compute Interop Kit (CUDA/ROCm/WGPU compute, unified ergonomics)
status: idea
domains: [gpu, compute, hpc, interop, cuda, rocm, wgpu]
last_reviewed: 2026-03-04
evidence:
  - https://rust-gpu.github.io/blog/2025/05/27/rust-cuda-update/
  - https://news.ycombinator.com/item?id=44692876
  - https://crates.io/crates/rocm-rs
---

# Problem

Rust has strong foundations for graphics (`wgpu`) and increasing activity around CUDA/ROCm bindings, but **“GPU compute as a dependable product surface”** remains hard:
- toolchains are fragmented,
- kernel compilation and packaging are inconsistent,
- portability is unclear,
- and ergonomic gaps make Rust feel “not worth it” for many compute developers.

There is active work in Rust CUDA, and community sentiment that key CUDA developer affordances are still missing. There are also early efforts toward safe ROCm wrappers (e.g. `rocm-rs`). These are ingredients, not a unified, cargo-native compute stack.

Sources: Rust CUDA project update; HN discussion noting missing CUDA parts; `rocm-rs` crate listing.

# Users & user stories

- **ML/compute engineer**: “I want to write kernels + host code in Rust with reproducible builds and decent debugging.”
- **Game/graphics dev**: “I want compute shaders / GPU kernels integrated with my renderer without rewriting everything.”
- **Research/science**: “I need a portable ‘runs on my lab’s AMD/NVIDIA mix’ plan.”
- **Library author**: “I want a crate that abstracts device selection, memory management, and kernel dispatch without forcing a single backend.”

# Prior art (and why it’s insufficient)

- **Rust CUDA**: enables writing CUDA kernels in Rust via NVVM IR, but end-to-end ergonomics (packaging, debugging, tooling) are still evolving. Source: Rust CUDA update.
- **Community bindings**: wrappers exist (CUDA, ROCm), but differ in safety/ergonomics and often lack a unified “kernel packaging + dispatch” story. Source: `rocm-rs` listing.
- **Graphics-first stacks**: `wgpu` is excellent, but compute users often want “compute-first” workflows and interoperability with existing CUDA/ROCm ecosystems.

# Design goals

1. **Backend-agnostic core** API for device selection, buffers, command submission, kernel dispatch.
2. **Pluggable backends**:
   - `gpu-kit-cuda`
   - `gpu-kit-rocm`
   - `gpu-kit-wgpu` (compute shaders)
3. **Cargo-native kernel packaging**:
   - build kernels as artifacts (`.ptx`, `.cubin`, ROCm code objects, SPIR-V)
   - embed + cache with build-ids
   - support cross-compilation story where possible
4. **Interop-first**:
   - share buffers with `wgpu` where possible
   - allow calling into existing CUDA libs (cuBLAS/cuDNN) and ROCm equivalents via feature-gated adapters
5. **Debuggability**:
   - trace kernel launches
   - capture timing and memory transfer stats
   - optional integration with profiling tools (Nsight/rocprof) via adapters
6. **Correctness testing**:
   - “conformance vectors” for ops (like BLAS-level primitives) across backends
   - CPU reference implementations for verification

# Non-goals

- Replacing mature vendor libraries.
- Solving “write once, run everywhere with identical performance”.
- Building a full ML framework.

# Architecture & API sketch

**Crates:**
- `gpu-kit-core`: traits + common types (`Device`, `Queue`, `Buffer`, `KernelModule`).
- `gpu-kit-kernel`: build tooling + artifact schema; `cargo gpu` plugin.
- `gpu-kit-cuda`: runtime bindings + module loading; supports PTX and cubin.
- `gpu-kit-rocm`: runtime bindings; supports code objects; leans on safe wrappers where possible.
- `gpu-kit-wgpu`: compute pipeline adapter.

**Kernel definition approaches:**
- **Option A (portable)**: SPIR-V compute shaders (wgpu backend).
- **Option B (vendor)**: Rust CUDA / ROCm kernels compiled per backend.
- Provide a “kernel manifest” describing entry points, params, and required features.

# Security / safety model

- GPU kernels are arbitrary code; treat module loading as untrusted boundary in plugin scenarios.
- Provide capability flags: forbid dynamic module loading unless enabled.
- Encourage signed kernel artifacts in production settings.

# Maintenance & governance plan

- Keep `gpu-kit-core` small and stable.
- Backends can move faster; versioned compatibility per backend.
- Conformance suite required for backend additions.

# Milestones

1. MVP: core + wgpu compute backend + artifact manifest + `cargo gpu build`.
2. CUDA backend integrating with Rust CUDA artifacts.
3. ROCm backend integrating with `rocm-rs`-style wrappers or equivalent.
4. Conformance suite + CI matrix on available runners.
5. Interop with wgpu buffers + basic profiler hooks.

# Open questions

- Best stable kernel ABI schema for parameters across backends.
- How to keep build times acceptable (cache layers).
- How to handle device-specific features without exploding complexity.

# Sources

- https://rust-gpu.github.io/blog/2025/05/27/rust-cuda-update/
- https://news.ycombinator.com/item?id=44692876
- https://crates.io/crates/rocm-rs
