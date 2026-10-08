# Decompiler surfaces: `see`, `disasm`, `disasm-rows` (rev68)

Micromax deliberately keeps its VM inspectable.

This doc describes the current state of the decompiler / disassembler tooling.

## `see`

`see NAME` prints a **source-ish** reconstruction of a named word.

For colon definitions, if tier-2 bytecode is attached, `see` now also prints:

- a compact disassembly (`\\ disasm` section)
- the const pool (`\\ consts` section)

The output is intentionally comment-prefixed so tooling that wants to parse
only the first `: ... ;` line can do so.

## `disasm`

`disasm XT` prints the tier-2 disassembly for a quotation or colon word.

Notes:

- jump ops show both relative offset and computed target (`+3 -> 0007`)
- consts are rendered at the bottom

## `disasm-rows`

`disasm-rows XT` returns a structured representation suitable for UIs.

Return value:

- `0` if uncompiled or not disassemblable
- otherwise `[[pc op arg span] ...]`

Where:

- `pc` is an integer program counter
- `op` is an opcode string
- `arg` is:
  - for `JMP`/`JZ`: signed relative offset
  - otherwise: the constant value referenced by the instruction
  - `0` if no argument
- `span` is `[file line col]` or `0`

This avoids having UIs parse the free-form `disasm` string.

## Future work

- add a "token span" mode so you can map disassembly back to the original
  source tokens more directly

## Implementation pointers

- `src/micromax/core.py`: `see`, `disasm`, `disasm-rows`
- `src/micromax/vm.py`: tier-2 bytecode definitions
