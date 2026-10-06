# Wasm component model + WIT as contract language (polyglot, digestable interfaces)

DeriveBSD keeps coming back to a core idea:

> **crossings are contracts** — and the contract must be a small, digestable review surface.

The WebAssembly Component Model + WIT is a compelling building block for this:
it provides a language-agnostic IDL (*WIT*) and a canonical ABI for high-level types.

References:
- WIT reference (Bytecode Alliance): https://component-model.bytecodealliance.org/design/wit.html
- WIT spec draft (WebAssembly/component-model repo): https://github.com/WebAssembly/component-model/blob/main/design/mvp/WIT.md

## Where this fits in DeriveBSD

### 1) A standard way to define contract surfaces

Today, ecosystems drift into a zoo of IDLs:
- protobuf/thrift/capnp bespoke schemas
- ad-hoc JSON
- handwritten RPC glue

DeriveBSD can pick one “native contract surface”:
- WIT `interface` / `world` becomes the source contract
- the compiled/normalized form becomes the **contract digest input**
- language bindings become derived build artifacts

### 2) Contract digests become mechanical

If `contractset.json` is already a thing, it can include:
- `wit.package` + `world` identifier
- canonicalized WIT bytes digest
- generated-binding digest set (optional)

This lets policy speak about interfaces *precisely*:
- “service may only expose WIT world X”
- “no breaking changes without an allowlist window”
- “consumers must accept digests {A,B} during rollout window”

### 3) Interop with object-capability RPC

DeriveBSD’s object-capability RPC model is a natural fit:
- capability = endpoint handle
- contract = WIT world + digest
- methods = WIT functions

This does **not** force “Wasm everywhere”.
It just standardizes the *interface definition* and encourages a tight, type-safe boundary.

### 4) Test realms + conformance suites

WIT also pairs well with the realm-builder test lane:
- tests can assert conformance against a WIT world
- stubs can be generated automatically from WIT
- recorded-replay fixtures can be validated against the interface schema

## Bake-in-now ecosystem payoff

- contracts become small, reviewable, and diffable
- polyglot components become less painful
- interface drift becomes detectable as “digest drift”
- conformance testing becomes cheap and automatable
