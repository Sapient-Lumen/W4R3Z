# Data model (rev0976)

Micromax’s value model should stay *small*, *portable*, and *useful for editor scripting*.

## Core value types (commitment)

These are the types the Rust/WASM VM must support.

- **Int**: signed 64-bit integer (`i64`), enforced by every current source, conversion, bytecode, and integer-consumer boundary.
  - Range: `-9_223_372_036_854_775_808` through `9_223_372_036_854_775_807`.
  - `+`, `-`, `*`, and `/` fail on overflow before consuming operands.
  - `/` rounds toward negative infinity and `mod` is the paired Python-style remainder; future Rust/Wasm hosts must implement this explicitly rather than inherit truncation-toward-zero native division.
  - Python booleans and host-injected arbitrary-precision integers are not Micromax `Int` values.
- **String**: Unicode text (UTF-8 in storage/interop).
- **List**: mutable, heterogenous array of values.
- **Map**: mutable string-keyed dictionary (portable hash map).
  - Keys must be strings in portable mode.
- **Cell**: a mutable box holding a single value (used for variables / state).
- **Quotation**: a first-class executable value; backed by `Code` (tokens now, bytecode later).
- **XT**: an “execution token” (a reference to a word).
- **Error**: structured error value (message + trace); surfaced via `catch`/`throw` and tooling.

## Booleans and nil

- **Booleans**: convention: `0` is false; any non-zero int is true.
- **Nil**: do not add a dedicated nil yet. Prefer:
  - empty string / empty list where natural
  - `0` for false/none in boolean contexts
  - or an explicit sentinel word if needed later (`none`), implemented in stdlib.

## Host values

Hosts may expose **opaque host objects** internally, but **hostcalls should not push opaque objects onto the script-visible stack** in portable mode.

For editor scripting, prefer returning/passing:
- ints, strings, lists of primitives (e.g. cursor lists), cells, and maps

## Deferred types (not committed yet)

These are likely useful, but we’re explicitly postponing them:

- **Bytes**: may be useful for binary IO, but editor scripting can stay text-first.
- **Float**: omit unless a concrete editor/plugin use-case demands it.

When/if added, each new type must:
- appear in the portability ledger (Rust/WASM plan)
- come with small primitive surface + tests
- have a clear story for serialization / printing / debugging

## Span metadata

Tokens carry `Span` (filename/line/col). For debugging/tooling, executable values may also retain an optional span:

- `Quotation.span` points at the `[` token
- `ColonWord.span` points at the `:` token

This is metadata (not a stack value type) but should remain portable and stable.
