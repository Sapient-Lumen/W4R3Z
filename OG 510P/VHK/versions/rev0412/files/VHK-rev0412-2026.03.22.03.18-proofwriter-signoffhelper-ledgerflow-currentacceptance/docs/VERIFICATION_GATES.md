# Verification gates

`vhk plan-project` now emits `verification_gates`.

This surface turns the strategy output into a per-capability shipping checklist.
Instead of stopping at “pointer automation is helper-boundary” or “hotkeys are
 desktop-shaped”, it asks the next question: what should a team verify before
claiming that capability is ready to ship?

Each gate is capability-shaped rather than environment-shaped so it can later be
reused by scaffold/init/studio/CI flows.

## What each gate should contain

At minimum, each item should expose:

- `id`
- `title`
- `capability`
- `category`
- `priority`
- `gate_type`
- `summary`
- `acceptance_checks`
- `commands`
- `artifacts`
- `target_environments`
- `fallback_path`
- `recommended_toolchain`
- `evidence`

## Current gate classes

- `baseline` — broad/portable capabilities that should still be explicitly checked
- `capability` — conditional capabilities that need desktop-aware validation
- `helper-boundary` — features that must stay behind helper/uinput/portal seams
- `desktop-profile` — desktop/compositor-specific integration surfaces
- `portability` — X11-first or migration-sensitive capabilities
- `opt-in` — experimental features that should never silently become a baseline dependency

## Why this matters

Linux-native automation tends to fail at the edge where capabilities meet a
specific desktop family, not at the level of an entire project. Verification
needs to model that reality too.

Examples:

- a text-heavy project may be ready to ship even if generic pointer automation is not
- hotkeys may be shippable through WM/compositor exports even if portal shortcuts are missing
- vision flows may be viable as long as capture and selector assets are validated
- raw input capture may remain experimental while remap/export paths are ready now

That makes `verification_gates` a better long-term target for CI and Studio UX
than a single binary “project supported on Linux” claim.
