# Cargo workspace toolchain route boundaries — 2026-03-21

This note keeps **P-0055 Cargo Workspace Toolchain Manifest Kit** from collapsing tool pinning into fake route certainty.

## The sharper seam

Within **P-0055**, keep these truths separate:

1. **the workspace requested a tool**,
2. **a tool was installed somewhere**,
3. **a particular executable actually won command resolution**,
4. **a specific rustup/toolchain context shaped the run**,
5. **other candidate executables existed but lost**.

Those are related, but they are not the same support claim.

## What belongs in the route-authority seam

The route-authority seam is about questions like:

- Did `cargo foo` resolve to the workspace-managed binary, a global `$CARGO_HOME/bin/cargo-foo`, another PATH entry, or an explicit wrapper path?
- Was the chosen tool installed in a workspace-local root, a shared cache, or a user-global root?
- Did Cargo subcommand precedence or PATH ordering materially change which tool ran?
- Did a rustup directory override, `rust-toolchain.toml`, or `cargo +toolchain` invocation change the execution context even though the binary path stayed the same?
- Are we claiming a project-scoped pinned tool while actually routing through a user-global install?

## What it is not

### 1. Not install-root posture by itself

A workspace can honestly say “tools install into `.toolchain/bin`” and still fail to prove that a given run used that root.
Install-root posture asks **where tools belong**.
Route authority asks **which executable actually won**.

### 2. Not toolchain context by itself

A run can happen under `cargo +beta`, a directory override, or `rust-toolchain.toml` without changing the executable path.
Toolchain context asks **which compiler/runtime environment surrounded the tool**.
Route authority asks **which binary was actually invoked**.

### 3. Not strategy/provenance by itself

A tool may arrive via `cargo install`, `cargo-binstall`, a local path, or a cached artifact.
That provenance matters, but it does not automatically prove what command resolution did later.

### 4. Not a promise to normalize every shell

This seam should not become a shell bootstrapper, environment manager, or hidden PATH mutator.
It stays at the contract/report layer.

## Receiver-facing artifacts to prefer

- `install-root.receipt.json` — exactly what root posture is being claimed
- `tool-route.receipt.json` — which executable won, why it won, and what competing candidates existed
- `tool-run.receipt.json` — the route actually used together with rustup/toolchain context

## Anti-patterns

Do **not** let future revisions treat these as interchangeable:

- “the workspace declared `cargo-nextest`”,
- “`cargo-nextest` was installed somewhere”,
- “`cargo nextest` resolved to the expected binary”,
- “the run used the intended toolchain context”.

They are adjacent truths, not one “tool pinned” fact.
