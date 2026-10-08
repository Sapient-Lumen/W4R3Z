---
id: P-0161
title: XR App Framework & Runtime Doctor Kit
status: idea
domains: [graphics, vr, ar, xr, gamedev, devtools, portability]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/Ralith/openxrs
  - https://registry.khronos.org/OpenXR/specs/1.0/loader.html
  - https://github.com/KhronosGroup/OpenXR-SDK-Source/blob/main/BUILDING.md
---

# Problem

Rust has capable **OpenXR bindings** (notably `openxrs`), but shipping a robust XR app still requires rebuilding a lot of glue:

- Runtime selection/debugging is fragile across OSes and vendor runtimes; when the wrong runtime is active, symptoms look like graphics/input bugs. The loader’s selection rules (e.g., `XR_RUNTIME_JSON`) are powerful but under-tooled.
- Action sets, controller profiles, haptics, and input mapping are repetitive and hard to validate.
- Swapchain + composition layers + frame pacing + “best practice” render loops are boilerplate-heavy.
- QA is hard: there’s no standard **XR bug bundle** that captures enough state to reproduce a user’s environment.

We’re missing a **batteries-included XR application framework layer** that stays small, focuses on correctness/portability, and makes XR debugging *artifact-based*.

# What it should provide

## 1) A portable XR bug bundle format

A standard `xrbundle.zip` with:

- `manifest.json` (schema version, OS/driver/runtime identifiers, OpenXR loader selection details)
- `runtime.json` (active runtime path; if overridden, record `XR_RUNTIME_JSON`)
- `extensions.json` (available/enabled extensions, instance/system properties)
- `input/` (action sets + bindings + controller profiles actually resolved)
- `graphics/` (swapchain formats, recommended sizes, layer config)
- `logs/` (OpenXR loader/runtime logs when available)
- `repro.md` (auto-generated steps + minimal code snippet pointers)

Goal: maintainers can say “attach an `xrbundle.zip`” and immediately know whether this is a runtime-selection issue, missing extension, input binding mismatch, etc.

## 2) `cargo xr doctor`

A cargo-native CLI that:

- Prints loader/runtime resolution (including whether `XR_RUNTIME_JSON` is set and what it points to)
- Verifies required extensions for common pipelines (OpenGL/Vulkan/D3D) and warns on known footguns
- Checks action-set completeness (unbound actions, missing suggested bindings)
- Emits a redacted `xrbundle.zip` suitable for issue trackers

## 3) A small XR app framework core

**Not** a game engine. A minimal “XR kernel” that provides:

- A canonical frame loop with correct `xrWaitFrame`/`xrBeginFrame`/`xrEndFrame` sequencing
- Swapchain management helpers (triple-buffering heuristics; format selection)
- Composition layer helpers (projection + optional quad layers)
- Input mapping helpers (actions, haptics, per-profile defaults)
- Optional integrations (feature flags): `winit`, `wgpu`, raw `ash`, `glow`

## 4) Conformance + regression kits

- Golden “action binding packs” for common controller profiles
- A minimal “XR smoke scene” that runs on any runtime and outputs stable diagnostics
- CI-mode validator that compares bundle fields against expected invariants (e.g., required extension present)

# MVP scope (2–4 weeks)

- `xrbundle.zip` schema v0 + redaction rules
- `cargo xr doctor` with:
  - runtime selection report (incl. `XR_RUNTIME_JSON`)
  - extension listing + basic pipeline checks
  - bundle creation
- `xr-kernel` crate with minimal frame loop + projection layer

# v1 scope (2–3 months)

- `wgpu` integration path + canonical swapchain/layer helpers
- Input binding packs (OpenXR interaction profiles)
- “smoke scene” app template + CI harness
- Better logging adapters (where runtimes expose logs)

# Non-goals

- Competing with Bevy/Unity/Unreal-level engines
- Owning rendering abstraction choices; this should stay modular

# Why this is an “epic” crate

It would reduce XR application development in Rust from “bindings + weeks of glue” to “template + clear diagnostics”, and it creates an ecosystem contract: **XR bugs become portable artifacts**, not screenshots and guesswork.
