# Cargo sandbox ambient-input plan — 2026-03-23

This note sharpens **P-0107 Cargo Sandbox & Capability Policy Kit** around one product question:

> what should another engineer receive when compile-time policy says “sandboxed”, but meaning still depends on inherited env/path/toolchain channels and on how the actor was wrapped?

## Main judgment

`0.2` for **P-0107** should elevate three new first-class review objects:

1. `ambient-input.receipt.json`
2. `sanitization-mode.receipt.json`
3. `launcher-route.receipt.json`

That is the smallest next step that keeps policy bundles honest about ingress, sanitization, and enforcement topology.

## Why these objects matter

### 1. `ambient-input.receipt.json`

This artifact should say which ambient channels were actually available to an actor or lane:
- Cargo-set env vars,
- inherited parent env vars,
- config-driven env injection,
- path search roots,
- toolchain selectors / toolchain files,
- wrapper env vars or preload routes,
- and build-script-emitted env channels that can influence later compilation.

The point is to stop “network denied” or “filesystem denied” from implying “no meaningful ingress remained”.

### 2. `sanitization-mode.receipt.json`

This artifact should say whether ingress was:
- inherited wholesale,
- allowlisted,
- rewritten,
- deny-by-default,
- or still manual-review-only.

It should also capture whether project-local opt-out was rejected, ignored, or allowed, and whether toolchain auto-install remained in play.

### 3. `launcher-route.receipt.json`

This artifact should say how the actor was actually sandboxed or wrapped:
- direct execution,
- rustc wrapper,
- preload/interceptor route,
- dedicated runner,
- Cargo-native experiment,
- or manual-review-only.

It should also preserve granularity truth and route-mutation risk, especially when build scripts can still influence later rustc / proc-macro lanes.

## Suggested CLI refinements

### `cargo sandbox-policy capture-ingress`
Capture ambient-input and sanitization receipts without claiming the actor had no other hidden powers.

### `cargo sandbox-policy explain-route`
Render how a given actor was actually wrapped and whether that route is per-actor, shared-lane, or whole-command.

### `cargo sandbox-policy diff`
Emit ingress/sanitization/route drift alongside existing capability and exception drift.

## Recommended proving grounds

1. a `-sys` crate that needs `PKG_CONFIG_PATH`, compiler wrappers, and `OUT_DIR` while network stays denied;
2. a host build where `RUSTFLAGS` bleed into build scripts unless `--target` is used;
3. a runner that forbids project-local config and disables rustup auto-install for untrusted projects;
4. a shared rustc/proc-macro route where one build script can still perturb later proc-macro execution.
