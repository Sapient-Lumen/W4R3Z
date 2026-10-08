# Cargo sandbox ambient-input frontier — 2026-03-23

## Main judgment

The compile-time containment lane is stronger when it stops flattening three different kinds of truth:

1. **capability grants** — what filesystem/network/process powers a policy explicitly granted or denied;
2. **ambient inputs** — what env/path/toolchain/wrapper channels still reached an actor even without a named grant;
3. **launcher routes** — what wrapper/interceptor/runner path actually enforced (or failed to enforce) the policy.

Current primary sources make this separation worth freezing into first-class artifacts:
- Cargo documents a large environment-variable surface and still says host build scripts / proc macros can inherit compiler flags unless `--target` splits the lanes.
- Cargo’s permanently-unstable `--compile-time-deps` mode proves the compile-time-only lane is a real target for tooling.
- Cargo’s host-config and env-sanitization issues remain open evidence that ingress and sanitization are not solved folklore problems.
- Rust release notes still record environment-route mistakes such as the old `env!("OUT_DIR")` build-time behavior being wrong under cross-compilation.
- `cargo-sandbox` and `cackle` prove real runner value while also exposing shared-lane and ambient-ingress limits.

## The sharper missing artifact layer

The archive should now treat **P-0107 Cargo Sandbox & Capability Policy Kit** as owning three additional review objects:

1. `ambient-input.receipt.json`
2. `sanitization-mode.receipt.json`
3. `launcher-route.receipt.json`

These belong above current runner backends because they let another engineer answer:

- which env/path/toolchain inputs still existed,
- how those channels were sanitized or left open,
- and what route actually wrapped the actor.

## What adjacent lanes still own

- **P-0508 Cargo Build Script Delegation Kit** owns delegated unit topology and output-lane ownership, not containment ingress.
- **P-0484 Toolchain & Target Support Contract Kit** owns whole-project support posture and host/target readiness, not compile-time policy enforcement.
- **P-0519 Crate Authority Surface Pack Kit** owns runtime/library authority posture, not build-time sandbox routes.
- **P-0040 Proc Macro Sandbox Kit** can still own migration/readiness work for future proc-macro isolation designs, not today’s reviewable ingress/sanitization contract.
