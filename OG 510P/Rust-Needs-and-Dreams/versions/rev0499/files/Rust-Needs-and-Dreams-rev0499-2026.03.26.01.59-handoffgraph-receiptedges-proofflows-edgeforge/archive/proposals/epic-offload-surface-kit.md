# Epic proposal: Offload Surface Kit

## Thesis
One of the more worthy Rust ecosystem contributions now would be a **portable review layer for accelerator/offload surfaces**.

Not another backend wrapper.
Not another “write kernels in Rust” project.
Not another model runtime.

The missing layer is a way to publish, diff, and verify:
- what kernels exist,
- which backends/devices they actually target,
- how resources move between host and device,
- how synchronization and completion behave,
- what happens on unsupported hardware,
- and what evidence shows parity or portability claims are real.

That contribution would be unusually leveraged because it can serve graphics-adjacent compute, ML runtimes, scientific kernels, media pipelines, browser compute, server-side GPU workloads, and future compiler-native offload work at once.

## Why this could be epic
Rust now has unusually broad accelerator motion, but not yet a shared review layer:
- official Rust goals now include **finishing `std::offload`**,
- a separate project goal already pushed GPU offloading experimentation in LLVM/rustc,
- `wgpu` has become the dominant safe cross-platform device API lane,
- `rust-gpu` keeps pushing Rust-authored shader crates,
- CubeCL exposes a single Rust kernel language across multiple backends,
- CUDA-specific Rust projects continue to matter because real workloads still depend on vendor tooling,
- and high-level consumers like Burn sit above all this.

That is exactly the moment when a **surface contract** becomes more valuable than one more runtime.

Sources:
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/GPU-Offload.html
- https://blog.rust-lang.org/2026/01/05/project-goals-2025-december-update/
- https://docs.rs/wgpu/latest/wgpu/
- https://rust-gpu.github.io/rust-gpu/book/
- https://docs.rs/cubecl/latest/cubecl/
- https://rust-gpu.github.io/rust-cuda/

## What the contribution should look like in practice
The contribution should probably be a **tool + schema family + reference adapters + example packs**.

### 1) Tooling
A `cargo offloadsurf` command that can:
- scaffold the artifact family,
- inspect a workspace for likely host/kernel/backend lanes,
- run bounded compile/parity/device vectors,
- diff support claims over time,
- and export one portable `offload-pack/v0`.

### 2) Schemas
At minimum:
- `offload-surface/v0`
- `kernel-map/v0`
- `backend-device-profile/v0`
- `buffer-transfer-profile/v0`
- `launch-sync-profile/v0`
- `dispatch-fallback-profile/v0`
- `offload-adapter-profile/v0`
- `offload-vector-set/v0`
- `offload-check-report/v0`
- `offload-pack/v0`

### 3) Reference adapters
The project becomes much more real if it ships reference adapters for:
- `wgpu` compute
- `rust-gpu` shader/runners
- CubeCL/Burn backend lanes
- one CUDA-focused host/device crate family

### 4) Example packs
Ship real examples that deliberately differ in shape:
- browser/native WebGPU compute with CPU fallback,
- Rust-authored shader crate plus runner,
- multi-backend tensor kernel lane,
- vendor-only CUDA lane with no fallback.

Those examples should prove the surface layer can represent disagreement honestly instead of smoothing it away.

## Design principles
1. **Do not lie about portability.** “Runs on GPU” is not enough; backend/device/runtime assumptions must be explicit.
2. **Do not lie about fallback.** CPU fallback, reduced-feature fallback, and “unsupported” are different things.
3. **Keep host/device boundaries first-class.** Buffer mapping, staging, ownership, and synchronization are semantic surfaces.
4. **Keep kernel identity first-class.** A host API without a reviewable kernel map is not a serious offload contract.
5. **Prefer attachable evidence over prose promises.** Compile tests, difftests, and bounded device matrices matter more than README claims.
6. **Do not flatten backend diversity.** WebGPU, SPIR-V, CUDA, HIP, Metal, and compiler-native offload should remain visibly different.

## Why existing projects are not enough
The point projects are real, but they leave a coordination gap:
- `wgpu` is an API/runtime layer, not a support-claim contract,
- `rust-gpu` is a shader toolchain/project, not a multi-stack review schema,
- CubeCL is a compute system, not a portable evidence/report format,
- CUDA wrappers are vendor-specific by design,
- and `std::offload` is still experimental.

The ecosystem therefore still lacks a common answer to “what exactly does this accelerated crate support, and how do we know?”

## Likely first users
- performance-sensitive Rust libraries shipping optional GPU lanes,
- model runtimes and tensor libraries,
- scientific/linear-algebra kernels,
- browser/native compute tools using `wgpu`,
- Rust-authored shader projects,
- CUDA/HIP-focused internal platforms that still need honest support docs and CI evidence.

## Risks
- **Too early / too unstable:** `std::offload` and some compiler-native lanes are still moving.
  - Response: keep the contract backend-agnostic and artifact-first, not tied to one frontend.
- **Too broad:** the space spans graphics, compute, ML, and vendor stacks.
  - Response: focus on public support truth, not one universal runtime.
- **Too much ceremony:** accelerator teams may resist more metadata.
  - Response: start with high-value adapters and auto-inspection, plus minimal MVP profiles.
- **Benchmark theater:** people may try to turn the kit into a leaderboard.
  - Response: bias toward bounded parity/support vectors and only modest perf-budget evidence.

## Phased plan
### Phase 1: representation
- finalize schemas,
- implement scaffold/inspect/export,
- ship adapters for `wgpu`, `rust-gpu`, CubeCL/Burn, and one CUDA lane.

### Phase 2: checking
- add compile/parity/device vectors,
- emit `offload-check-report/v0`,
- add diff support for support-claim regressions.

### Phase 3: ecosystem composition
- integrate with Model Surface Kit, Media Surface Kit, Vector Surface Kit, and Runtime Capability Kit,
- let downstream crates attach `offload-pack/v0` in release and CI flows,
- add archaeology/migration support for backend shifts.

## Interaction with the rest of this archive
This proposal should stay distinct from:
- **Vector Surface Kit** — vector semantics are not the same thing as heterogeneous device execution.
- **Model Surface Kit** — model artifacts/runtimes are downstream consumers, not the whole offload substrate.
- **Runtime Capability Kit** — device/runtime authority and sandboxing matter, but they are not kernel maps or transfer truth.
- **Synchronization Surface Kit** — queue/stream/fence behavior overlaps, but host/device execution has different public support questions.
- **Compile-Time Capabilities / Build Extension** — build-tooling concerns are real, but they are not the same as public accelerator support claims.

## Bottom line
A genuinely worthy Rust contribution here would be:

> **Offload Surface Kit** — one reviewable boundary for kernels, backends/devices, host↔device resource truth, dispatch/fallback posture, and evidence across `std::offload`, `wgpu`, `rust-gpu`, CubeCL/Burn, CUDA-focused stacks, and future accelerator lanes.

That would be “epic” not because it replaces today’s projects, but because it could make the whole heterogeneous Rust story far easier to publish, compare, verify, and build on.
