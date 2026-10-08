# Checked i64 integer domain and transactional arithmetic (rev0976)

## Why this outranked the other open risks

Rev0973 bounded plugin VM dispatch and rev0974 bounded string results whose size
can be predicted before allocation. The next audit asked for a plugin-accessible
operation that could still monopolize the shared Python process inside one
primitive.

Micromax already documented `Int` as signed 64-bit, but the reference VM did not
enforce that contract. It inherited CPython's arbitrary-precision integers:
source literals, `to-int`, bytecode integer constants, and arithmetic could all
create values outside the promised portable domain. A plugin needed no hostcall,
capability, loop, or large package. Repeated squaring entered one Python
multiplication per VM dispatch; each multiplication could allocate a much larger
integer before fuel got another chance to run.

That was a product and portability defect, not merely a missing resource option:

- a tiny callback could consume rapidly growing memory in the editor process;
- the eventual Rust/Wasm host could not reproduce Python bignum results with an
  `i64` value model;
- overflow, division by zero, and bad conversion consumed operands before
  reporting failure;
- address-space exhaustion surfaced as a blank wrapped `MicromaxError`, which
  made the failure hard to diagnose and left the shared stack damaged.

Regex-child memory and unbounded map-key rendering remain real candidates, but
neither contradicted an already-promised language type as directly as this path.
The smallest honest correction was therefore to make the existing i64 promise
executable everywhere an integer enters or is produced.

## Reproduction against rev0974

The probe started with `2`, executed `dup *` 32 times, and applied a Linux
`RLIMIT_AS` ceiling relative to the child process's current virtual memory. The
same source was used at each headroom level:

```text
2 dup * dup * ...        (32 squarings)
```

Observed on 2026-07-18:

```json
{"elapsed_seconds": 0.506, "headroom_mb": 64,  "message": "", "stack_depth": 0, "type": "MicromaxError"}
{"elapsed_seconds": 1.013, "headroom_mb": 128, "message": "", "stack_depth": 0, "type": "MicromaxError"}
{"elapsed_seconds": 2.119, "headroom_mb": 256, "message": "", "stack_depth": 0, "type": "MicromaxError"}
```

The elapsed time grew with available memory, the error carried no useful
message, and the two multiplication operands had already been removed. VM step
fuel was functioning as designed: it consumed one step before dispatch, but it
cannot preempt Python after entering `a * b`.

## The executable integer contract

Micromax `Int` is now exactly the range:

```text
-9_223_372_036_854_775_808 .. 9_223_372_036_854_775_807
```

The Python host may still possess arbitrary Python objects internally, but a
script-visible value is an `Int` only when it is a non-boolean Python integer in
that range. The shared helpers in `micromax.vm` own this rule:

- `is_portable_int()` is the type predicate;
- `portable_int_value()` validates an existing host value without rendering an
  oversized integer into the error message;
- `checked_portable_int()` validates arithmetic results;
- `parse_portable_int_decimal()` scans decimal text without first constructing
  an arbitrary-precision Python integer.

The parser accepts Unicode decimal digits because Python's documented decimal
literal/conversion model accepts `Nd` digits. Source literals remain strict.
`to-int` intentionally retains its historical surrounding whitespace, leading
`+`, and between-digit underscore conveniences, but every accepted result must
fit i64.

## Entry and re-entry seams

The i64 boundary is checked at every current language/bytecode ingress where a
host bignum could otherwise become executable:

1. source integer tokenization;
2. tier-1 integer token dispatch, even if token objects were host-mutated;
3. `to-int` for both strings and existing host integers;
4. bytecode JSON integer decoding via `json.loads(parse_int=...)`, before
   Python's default `int()` conversion;
5. bytecode integer constants, instruction operands, and source coordinates on
   portable import/export;
6. tier-2 `PUSH`, jump, call, and name-reference operands at dispatch, even if a
   loaded bytecode object was mutated afterward;
7. `pop_int()` and `int?`, which reject booleans and host-injected bignums.

For constant-pool operations, range means more than fitting i64: `PUSH`,
`EXEC_NAME`, and `CALL_Q` operands must also be ordinary zero-based indexes into
the current pool. Import, export, and dispatch reject negative and past-end
indexes so Python's `consts[-1]` behavior cannot leak into the portable VM.

JSON `true` is no longer accepted as bytecode version `1` or as a tagged integer
constant merely because Python's `bool` subclasses `int`.

## Checked arithmetic and failure-before-mutation

`+`, `-`, `*`, `/`, `mod`, `<`, `>`, and `0=` inspect typed operands before
changing the stack. Arithmetic computes from two already-bounded i64 operands,
checks the finite result, and commits the stack replacement only on success.
Division-by-zero and overflow therefore leave the request intact.

The original amplification now stops at the first result outside i64:

```text
error: integer overflow: * exceeds signed 64-bit range
stack: 4294967296 4294967296
```

The same rule applies to interpreted and compiled code because tier-2 executes
the same checked primitives. A failed plugin callback still uses rev0973's
budget/rollback owner; the new language boundary prevents bignum growth before
that callback can damage the Python process.

## Division semantics are deliberate

Micromax historically used Python floor division and its paired remainder:

```text
-3  2 /   => -2
 3 -2 /   => -2
-3  2 mod =>  1
 3 -2 mod => -1
```

Rust's ordinary signed `/` truncates toward zero, and WebAssembly signed integer
division follows truncating signed semantics. Silently replacing Python `//`
with native Rust/Wasm `/` would therefore drift on negative operands.

Rev0976 does not change the language underneath existing scripts. It pins the
floor-division rule and matching remainder in the portability corpus. A future
Rust/Wasm host must implement that rule explicitly and must treat
`i64::MIN / -1` as overflow. `i64::MIN mod -1` remains `0`.

## Waste removed rather than added

This landing adds no integer policy registry, bignum mode, plugin option,
worker, IPC protocol, capability, schema migration, or alternate numeric type.
It removes an accidental second numeric model: “portable i64 in documentation,
arbitrary Python integer in execution.” One small boundary is reused by source,
core words, bytecode, and plugins.

The decimal parser also avoids the wasteful sequence “allocate an unbounded
integer, then reject it.” It accumulates only while the magnitude remains within
the target bound and continues scanning solely to distinguish malformed input
from a well-formed out-of-range number.

## Evidence

The new regression lane covers:

- exact min/max literals, Unicode digits, leading zeros, and 20,000-digit denial;
- checked add/subtract/multiply/divide, zero division, and preserved operands;
- the repeated-squaring denial under only 16 MiB of added Linux address space;
- interpreted and compiled arithmetic parity;
- `to-int` boundary, syntax, Unicode, and non-mutating denial behavior;
- host-injected bignums and booleans;
- bytecode JSON pre-decoding, direct portable objects, mutable constants,
  mutable operands, and source coordinates;
- real plugin callback invocation plus post-failure VM usability;
- 15 new replayable portability cases, including negative division semantics.

## Current official references checked on 2026-07-18

- Python numeric types: <https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex>
  documents arbitrary-precision Python integers and floor division toward minus
  infinity.
- Python JSON decoding: <https://docs.python.org/3/library/json.html#json.loads>
  documents that `parse_int` receives each JSON integer as source text and that
  the default is `int(num_str)`.
- Python resource limits: <https://docs.python.org/3/library/resource.html#resource.RLIMIT_AS>
  defines the address-space limit used only by the Linux regression probe.
- Rust `i64`: <https://doc.rust-lang.org/std/primitive.i64.html> documents the
  fixed signed-64-bit range, checked operations, `MIN / -1` overflow, and
  truncation-toward-zero ordinary division.
- WebAssembly Core Specification: <https://webassembly.github.io/spec/core/>
  defines `i64` as a 64-bit integer value type and signed numeric operations.

These sources select implementation constraints; Micromax's floor-division
semantics remain a project decision pinned by its own corpus.

## Residual risk and next honest cuts

This is not total Python-heap containment. Existing strings, lists, maps, cells,
quotations, and opaque host values can still retain memory. Very large source or
JSON text still costs linear scanning within the separate input-size policies.
Generic equality and user-provided map keys can still perform host-object work.
Regex workers still lack an operating-system memory ceiling. Python/native
crashes, blocking calls, syscalls, and interpreter compromise remain outside the
in-process boundary.

The next resource change should again begin with a transcript. The leading
candidates are a reproducible regex-child memory peak, map-key rendering that
crosses the bounded value-text contract, or a truly blocking native call. Do not
add a generic quota registry merely because those categories exist.
