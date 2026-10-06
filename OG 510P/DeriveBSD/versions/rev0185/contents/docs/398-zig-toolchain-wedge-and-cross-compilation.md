# Zig toolchain wedge (cross-compiling C/C++ dependencies without bespoke cross toolchains)

**Tier:** C (Optional lane)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, supply-chain, operability
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate, Quarantine→Promote  

DeriveBSD wants a bootstrappable, reproducible toolchain story.
Even if the core implementation bias is Rust, the ecosystem reality is that **a lot of dependency mass is C/C++**.

A pragmatic greenfield move is to add an *optional* lane that uses **Zig as a C/C++ toolchain wedge**:

- one downloadable artifact (pinned in Lock)
- ships its own libc headers/shims for many targets
- acts as a drop-in C/C++ compiler driver (`zig cc`, `zig c++`)
- supports cross compilation without building a traditional cross toolchain per target

This is not “Zig everywhere”. It’s “Zig as a sharp, reproducible wedge.”

## Non-goals

- Rewriting base/system code in Zig.
- Treating Zig as a magical trust anchor.
- Hiding toolchain complexity. The goal is to **make it explicit and reducible**.

## Why this fits DeriveBSD

DeriveBSD already treats the toolchain as an explicit input with trust tiers.
Zig can reduce the number of *bespoke* host-specific toolchain dependencies when:

- building foreign-arch packages in builder pools
- cross-building microVM kernels/userlands
- producing reproducible “foreign ABI” compatibility layers

See also:
- `docs/156-toolchain-bootstrap-rust.md`
- `docs/191-diverse-double-compiling-and-bootstrappable-toolchains.md`

## Proposed lane

### Input

- `toolchain.zig.bundle` (pinned, signed artifact)
  - includes Zig binary + target metadata
  - includes an explicit `zig env` capture for reproducibility

### Policy knobs

- `toolchain.zig.enabled` (default: false)
- `toolchain.zig.allowedTargets` (explicit list)
- `toolchain.zig.trustTier` (0/1/2; same posture as Rust toolchains)

### Outputs / evidence

- `toolchain.zig.buildrecord` (how the wedge was built / verified)
- `toolchain.zig.surface.registry` (optional): record the wedge’s target/libc surface so upgrades are reviewable

## Threat model notes

Zig is still a large compiler toolchain, and it uses LLVM.
The point of a Zig wedge is *not* “smaller TCB”; it is:

- **simpler operational bootstrapping** (fewer ad-hoc cross toolchains)
- **explicit pinning** (one bundle per lane)
- **better reproducibility leverage** (single artifact, repeatable across builders)

If the lane is enabled, it should:

- run under the same hostile-builder constraints
- be subject to witness rebuilds (optional)
- be reviewed using the same “new code ingestion” surfaces (`closure.diff`)

## Prior art / references

- Zig overview: drop-in C/C++ compiler and cross-compilation posture:
  https://ziglang.org/
- Zig learn/overview (caching + compiling C; libc shipping motivation):
  https://ziglang.org/learn/overview/
- Zig `zig cc` as GCC/Clang-compatible driver (historical explanation):
  https://andrewkelley.me/post/zig-cc-powerful-drop-in-replacement-gcc-clang.html
- Zig release notes: FreeBSD cross-compilation improvements (example of why pinning matters):
  https://ziglang.org/download/0.15.1/release-notes.html

