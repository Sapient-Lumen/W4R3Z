# Two-tier execution plan (interpreter now, bytecode later)

Micromax is built to stay tiny and hackable *today*, while allowing a later move to a compact,
fast VM (Rust/WASM) without changing language semantics.

## Goals

- **Semantics stability**: scripts behave the same under interpreter and bytecode.
- **Debuggability**: keep the token interpreter as a reference implementation and debugging tool.
- **Portability**: the compiled tier must be implementable in a small Rust/WASM codebase.

## Tier 1: token interpreter (reference)

The reference VM executes token streams directly:

- parsing produces tokens with spans (filename/line/col)
- quotations store token lists
- `call` executes a quotation by running its token list

This tier is optimized for readability and great error messages.

## Tier 2: compiled execution (rev13: first working slice)

We now have a minimal tier-2 executor:

- `Code` optionally carries `bytecode` compiled from the same tokens.
- `call` / `if` / `when` / `while` route through `VM._execute_code`, so compiled quotations run in tier-2 automatically.
- `compile` attaches tier-2 bytecode to a quotation (or colon word) in place.

### Current bytecode model (intentionally tiny)

Bytecode today is a **constant pool** plus a linear instruction list with per-instruction spans:

- `PUSH <k>` — push `consts[k]`
- `EXEC_NAME <k>` — execute a name using the same rules as tier-1 (usually via a cached `WordRef`)
- `CALL_Q <k>` — execute a quotation constant directly (without pushing it first)
- `JMP <off>` / `JZ <off>` — relative control flow for tier-2 hot paths

This is closer to "threaded code" than a rich register VM: the goal is to keep the model compact
and easy to port.

In rev22, the compiler also performs a tiny, semantics-preserving peephole transform for:

- `flag [t] when`
- `flag [t] [f] if`
- `[cond] [body] while`

This avoids the runtime overhead of pushing quotation values and calling `if/when/while` in hot loops,
while preserving late binding inside the quotations.

### Current limitation: token-stream parsing words

Some words rely on reading the *next token* at runtime (e.g. `module`, `constant`, `local@`).
Tier-2 does **not** provide a token stream yet, so compiled code currently rejects such words.

That is acceptable for the intended hot path: runtime quotations used by keybindings/actions.
File loading and defining new words continues to run in tier-1.

Future path options:

- move parsing words into an explicit compile-time phase, or
- provide non-parsing equivalents (e.g. `find`) for runtime use

## Compatibility constraints (things we must preserve)

- quoting and `call` behavior (quotations are first-class values)
- wordlists/search order resolution rules
- locals scoping rules
- structured error reporting + call trace semantics

## Next steps

1. Expand bytecode to cover more runtime operations efficiently (while keeping identical semantics).
2. Decide the long-term story for parsing words in compiled code.
3. Add a Rust VM that consumes the same `Code` semantics and passes the Python test suite.
4. Optional: add debug tables to map bytecode back to token spans for richer tooling.
