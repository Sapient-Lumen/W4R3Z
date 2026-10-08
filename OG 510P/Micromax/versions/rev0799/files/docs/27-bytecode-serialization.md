# Bytecode serialization (rev21 draft)

Micromax tier-2 bytecode now has a constant pool (`consts`) + linear instruction list (`instrs`).
This document describes a **tooling-first JSON encoding** for that structure.

Goals:
- make offline caching possible (optional)
- make Rust/WASM ports easier to validate (generate JSON in Python, load in Rust, compare behavior)
- keep the shape **simple to parse** (lists + tags, no fancy objects)

Non-goals:
- committing to a stable binary format yet
- supporting every possible Python value (only tier-2-safe constants)

## JSON schema (ver=1)

Top-level object:

```json
{
  "magic": "micromax-bc",
  "ver": 1,
  "consts": [ ... ],
  "instrs": [ ... ]
}
```

### Spans

Spans are encoded as:

```json
["filename", line, col]
```

### Constant entries

Each constant entry is a list with a string tag in position 0:

- `[
  "i", n
]`  — integer

- `[
  "s", text
]` — string

- `[
  "wr", name
]` — `WordRef` (inline-cache placeholder). Only the name is serialized.

- `[
  "q", span, bc
]` — quotation constant, encoded as:
  - `span`: span list
  - `bc`: nested bytecode object (same schema)

Notes:
- nested quotations are compiled eagerly during serialization
- this encoding is intended to remain *portable* to Rust/WASM

### Instruction entries

Each instruction is:

```json
[op, arg_or_null, span]
```

Where:
- `op` is a string like `"PUSH"` or `"EXEC_NAME"`
- `arg_or_null` is:
  - an integer index into `consts` for `PUSH`/`EXEC_NAME`/`CALL_Q`
  - a signed relative instruction offset for `JMP`/`JZ` (measured from the next instruction)
  - or `null` for ops with no operand
- `span` is a span list

## VM words

- `bytecode-json ( xt -- s )`
  - compiles `xt` if needed
  - returns a deterministic JSON string

- `bytecode-load-json ( s -- q )`
  - parses JSON into a quotation backed only by tier-2 bytecode

## Stability

This is a **draft** (rev21). We will treat this as stable enough for tooling and tests,
but we may revise it if the tier-2 instruction set grows.
