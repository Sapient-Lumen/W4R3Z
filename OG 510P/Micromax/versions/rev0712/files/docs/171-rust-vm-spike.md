# Rust VM spike plan (rev229)

The current worklist still keeps one explicit long-range TODO alive:

> **Minimal Rust VM spike.**

This archive does **not** currently ship a verified Rust implementation, because
this container snapshot does not include `rustc`/`cargo`, and Micromax should not
pretend an untested second implementation is real.

What rev229 does instead is make the spike path much sharper and smaller.

## Goal

Build the *smallest* Rust VM that can honestly claim to validate the portable
Micromax contract.

That means:

1. start with the existing JSON portability corpus
2. support only the stable portable kernel slices first
3. keep host boundaries tiny and explicit
4. avoid editor integration until the kernel replay story is boring

## Suggested crate shape

When a Rust toolchain is available, the first honest layout is:

```text
rust/
  Cargo.toml              # workspace or single package root
  micromax_vm/
    Cargo.toml
    src/lib.rs
    src/value.rs
    src/stack.rs
    src/parser.rs
    src/vm.rs
    tests/portability.rs
```

This is intentionally small:

- one library crate first
- no plugin/editor surface yet
- no bytecode tier yet
- no WASM host ABI yet

## First milestone

Make `cargo test` pass for a **tiny replay loop** over a narrow filtered slice of
`portability/kernel_cases.json`.

Recommended first slice:

- stack ops
- arithmetic
- quotations + `call`
- `if`
- `catch` / `throw`
- return-stack basics

Only once that passes should the spike expand into:

- wordlists/search order
- maps/lists
- stdlib combinators
- `dict-version`
- portable host-feature inventory

## Non-goals for the first spike

Do **not** start with:

- the editor hostcalls
- filesystem hostcalls
- the Python bytecode tier
- JIT/inline caching
- plugin loading
- TUI integration
- WASM packaging

Those all become easier once the portable kernel replay loop is already stable.

## Bring-up discipline

The Rust spike should reuse the same project values as the Python reference VM:

- tiny trusted core
- explicit data model
- offline evolution by hand
- heavily replayable tests
- clear separation between portable semantics and host conveniences

## Practical first commands

When Rust is available again, the first boring path should look like:

```bash
cargo new --lib rust/micromax_vm
cargo test
python tools/mxportable.py --tag stacks --json
python tools/mxportable.py --tag recovery --json
```

The point is not to grow a large Rust tree quickly.
The point is to establish a second implementation that can replay the same tiny,
curated contract Micromax already treats as portable truth.
