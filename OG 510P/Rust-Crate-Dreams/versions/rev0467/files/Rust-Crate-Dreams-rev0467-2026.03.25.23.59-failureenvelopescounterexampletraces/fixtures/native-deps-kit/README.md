# Native Deps Kit fixtures

This fixture family exists to make **P-0058 native-deps-kit** more concrete.

The goal is to describe a native dependency contract once, probe it through one or more backends, and produce a doctor/report artifact that another human can review.

## Intended first scenarios

1. `pkg_config_only_linux` — declarative Linux system package flow.
2. `vcpkg_only_windows` — declarative Windows/MSVC flow with emitted include paths.
3. `pkg_config_then_vendored` — preferred system path fails, vendored fallback succeeds.
4. `offline_policy_failure` — network/vendored path would be required but policy forbids it.
5. `links_override_handoff` — external override or predeclared metadata bypasses the live probe.
6. `feature_unification_forces_vendoring_blocked_by_policy` — additive vendoring intent exists, but policy refuses to allow it silently.
7. `build_internal_env_forces_vendored_mode` — env or CI intentionally forces internal-build mode and the crate freezes that choice.

## Minimal bundle for 0.1

- `native-contract.toml`
- `resolution-mode.lock.json`
- `vendoring-policy.report.json`
- `native-resolution.report.json`
- `backend-attempts.receipt.json`
- `consumer-doctor.txt`

## Design rule

Prefer an **honest backend-attempt receipt** over pretending one probing backend is universal across all platforms.
## Included example

- `scenarios/links_override_handoff/` — shows that override-based success is part of the contract story, not an edge case to hide.

## New 0.1 emphasis

The sharpest missing value is now often the **mode/policy artifact**:

- who asked for system vs vendored vs override behavior,
- whether that came from features, env, config, or explicit policy,
- and whether the outcome should be treated as exact, blocked, or manual-review-required.
