# Cargo Sandbox & Capability Policy Kit — lane boundaries (2026-03-22)

This note prevents **P-0107** from swallowing every security, sandbox, or build-time problem in the archive.

## P-0107 is for

- policy authority,
- actor capability scope,
- enforcement mode,
- exception ownership,
- and policy drift for compile-time execution.

## P-0107 is not for

### 1. Runtime crate authority surfaces

That belongs primarily to **P-0519 Crate Authority Surface Pack Kit**.
If the main question is “what powers does this library need when my application runs?”, do not force it into P-0107.

### 2. Delegated build-unit topology and output ownership

That belongs primarily to **P-0508 Cargo Build Script Delegation Kit**.
If the main question is “which build unit produced this metadata or artifact?”, do not force it into P-0107.

### 3. Proc-macro migration toward future Wasm/native substrate

That belongs primarily to **P-0040 proc-macro-sandbox-kit**.
If the main question is “is this macro ready for a future proc-macro execution model?”, do not force it into P-0107.

### 4. Host-vs-target flag and execution-scope truth

That belongs primarily to host/target scope and target-support lanes.
P-0107 can reference actor scope, but it should not become the main source of cross-target support truth.

### 5. Generic OS sandbox runtimes or policy engines

Those belong to lower-level sandbox/capability substrate proposals.
P-0107 sits above them as a Cargo-facing review contract.

## Core anti-flattening rule

Do not collapse these distinct claims into one fake “sandboxed build works” verdict:

1. **the policy source is explicit**,
2. **the actor scope is explicit**,
3. **the enforcement mode is explicit**,
4. **the exceptions are owned**,
5. **and drift is reviewable**.

A workflow can satisfy one or two of those and still be unreviewable.
