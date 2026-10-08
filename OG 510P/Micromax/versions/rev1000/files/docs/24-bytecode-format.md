# Bytecode format (rev0976)

Micromax tier-2 bytecode is intentionally minimal at first.

## Why "minimal first"?

- preserve semantics by delegating name execution to the same runtime rules as tier-1
- keep the reference implementation tiny and readable
- keep a clear path to a compact Rust/WASM VM (or Rust → WASM)

## Constant pool

Tier-2 bytecode uses a **constant pool** (`consts`) plus a linear instruction stream (`instrs`).
Many VMs do this to keep the instruction stream compact and make binary encodings simpler.

Reference: *Crafting Interpreters*, “Chunks of Bytecode”.

## Integer domain

Every integer in the portable JSON/bytecode contract is a signed 64-bit value.
That includes tagged integer constants, instruction operands, format version,
and source-span line/column coordinates. JSON decoding routes integer source
text through the bounded i64 parser before Python's arbitrary-precision
`int()` can materialize an oversized value. Export and tier-2 dispatch recheck
mutable bytecode objects, so host mutation cannot bypass the serialized boundary.
JSON booleans are not integers.

Constant-pool operands are additionally required to be nonnegative and smaller
than the current pool length at import, export, and dispatch. Python's negative
list-index convention is not part of Micromax bytecode semantics.

## Instruction operands

Operands are intentionally simple:

- For ops that refer to constants (`PUSH`, `EXEC_NAME`, `CALL_Q`), `arg` is an **index into `consts`**
- For control-flow ops (`JMP`, `JZ`), `arg` is a **signed relative instruction offset**, measured from the **next** instruction

This keeps the instruction format uniform (one optional integer operand), while still enabling control flow.

## Current instruction set

### `PUSH <k>`
Push `consts[k]` onto the data stack.

### `EXEC_NAME <k>`
Execute a name using tier-1 rules (locals shadow dictionary words; `.name` expands to `"name" send` unless a real `.name` exists).

- `consts[k]` is normally a `WordRef` (per-call-site inline cache), but a raw string is allowed for back-compat.

### `CALL_Q <k>`
Execute a quotation constant directly (without pushing it first).

- `consts[k]` must be a `Quotation`.

### `JMP <off>`
Unconditional jump. Adds `off` to the instruction pointer (relative to the next instruction).

### `JZ <off>`
Conditional jump on *falsey*. Pops an int flag; if it is `0`, jumps by `off` (relative to the next instruction).

## Tier-2 control-flow compilation (rev22)

The compiler uses a small peephole transform to preserve semantics while avoiding the runtime cost of pushing quotations + calling `if/when/while` in hot paths.

Patterns:

- `flag [t] when` compiles to: `JZ skip ; CALL_Q t`
- `flag [t] [f] if` compiles to: `JZ else ; CALL_Q t ; JMP end ; CALL_Q f`
- `[cond] [body] while` compiles to a loop: `CALL_Q cond ; JZ end ; CALL_Q body ; JMP loop`

Reference: *Crafting Interpreters*, “Jumping Back and Forth” (jump patching).

## Inline caching (implementation detail)

Tier-2 `EXEC_NAME` keeps late binding, but uses a per-call-site inline cache (`WordRef`) that is
invalidated by `dict-version`.

- name resolution still consults the current search order
- redefining words or changing search order bumps `dict-version` and invalidates caches

See `docs/25-inline-caching.md`.

## Tooling

- `compile` attaches bytecode to a quotation/colon word
- `compiled?` checks whether bytecode is present
- `disasm` prints a best-effort listing with token spans

## Serialization

For tooling and optional offline caching, bytecode can be serialized to a small JSON
format (see `docs/27-bytecode-serialization.md`).

- `bytecode-json` returns bytecode JSON for an XT (compiling if needed)
- `bytecode-load-json` parses JSON into a quotation backed only by tier-2 bytecode

## Future directions (not committed)

- compact opcode encoding + debug tables
- more peephole transforms (only when they are obviously semantics-preserving)
- JSON stays as the debug/interop format; a binary format can come later
