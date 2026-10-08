# Headless screen dump and `micromax.screen.v1`

The editor exposes two different screen surfaces:

- a compact, versioned product contract for ordinary tools;
- the full internal diagnostic graph for explicit debugging.

## Producer

```bash
python -m micromax_editor FILE --dump-screen 24 80
python -m micromax_editor FILE --dump-screen 24 80 --dump-screen-detail compact
python -m micromax_editor FILE --dump-screen 24 80 --dump-screen-detail diagnostic
```

Compact output is the default and has schema discriminator
`micromax.screen.v1`. It contains only:

- `size`: visible line and column dimensions;
- `cursor`: visibility, mode, and visible coordinates when present;
- `rows`: one row per screen line with kind, visible text, optional source
  mapping, and optional semantic tags;
- `cues`: sorted non-empty visual spans using zero-based coordinates and an
  exclusive `end`.

Cue kinds are open token values inside the closed v1 object shape. Current
examples include `syntax-kw`, `syntax-comment`, `selection-secondary`, and
`selection-primary`. A selected logical newline is represented as a one-character
cue on the visible blank immediately after end of line; no row-text byte is
invented for it.

Diagnostic output is intentionally not a compatibility contract. It exposes the
large internal screen graph used by focused tests and debugging.

Public screen requests are preflighted before editor startup or model traversal:
1..256 lines, 1..512 columns, and at most 65,536 cells. Invalid requests exit 2
from the CLI. REPL `:screen` reports the error and remains live.

## Consumer

A strict stdlib-only consumer is installed with the package:

```bash
python -m micromax_editor --dump-screen 24 80 \
  | python -m micromax_editor.screen_consumer --check

micromax-screen screen.json --check
micromax-screen screen.json --text
micromax-screen screen.json --summary
```

Input defaults to standard input. `--check` is silent on success. `--text`
prints one terminal-safe escaped line per visible row, and the default
`--summary` emits deterministic kind/count JSON.

Raw JSON remains the fidelity-bearing contract. The human text projection doubles
backslashes and escapes Unicode control, format, and line-separator characters
(categories `Cc`, `Cf`, `Zl`, and `Zp`) using readable `\b`, `\t`, `\n`,
`\f`, `\r`, `\xNN`, `\uNNNN`, or `\UNNNNNNNN` forms. Document text
therefore cannot replay ANSI/C1 terminal controls, carriage returns, embedded
row breaks, or bidi controls through this command. A programmatic consumer that
renders raw `row.text` into another output context still owns that context's
neutralization policy. Consumer error output applies the same control/format
neutralization, so malicious field names, paths, or I/O failures cannot replay
terminal controls through stderr. Closed-object validation checks required fields
first and then refuses the first non-string or unknown member without collecting
or sorting every caller-supplied key. Exact scalar types prevent direct validator
calls from invoking caller-defined conversion, length, iteration, or repr hooks.

The consumer rejects unsupported schema versions, unknown fields, duplicate
JSON names, invalid UTF-8, unpaired surrogates, NaN/infinity, floating-point
numbers, excessive bytes/depth, non-interoperable integer magnitudes, invalid
cursor/row/source coordinates, non-contiguous rows, and unsorted/duplicate cues.
It reads through valid short stream reads up to one witness byte beyond the
budget; direct validator calls require exact built-in JSON `dict`, `list`,
`str`, `int`, and `bool` shapes rather than caller-defined subclasses.

The producer also bounds diagnostic source rows and cue entries before copying,
normalization, or deduplication. Duplicate source rows fail closed instead of
silently choosing one. Visible selection projection considers at most 4096 cursor
sources, retaining the primary, and visible Micromax syntax scans at most 4096
characters from the start of each visible logical line. These diagnostic losses
are exposed in the internal model; compact v1 remains finite and shape-stable.

## Compatibility

V1 objects are closed: adding, removing, renaming, or changing a field requires
a new schema discriminator. Consumers must tolerate unknown valid *token values*
for row kinds, cursor modes, tags, and cue kinds; they must not guess when the
schema discriminator is unknown. Tokens use the portable ASCII grammar
`[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*` and are at most 96 characters.

Changing coordinate meaning, ordering, required rows, cursor semantics, or v1
budgets also requires a new contract version. V1 remains the default until a
replacement has an independent consumer, fixtures, transition documentation,
and an overlap period.

The packaged Draft 2020-12 schema is
`micromax_editor.schemas/micromax-screen-v1.schema.json`. Dynamic invariants such
as row count matching `size.lines`, coordinates relative to the current size,
and strict cue ordering are additionally enforced by `micromax-screen`.

## Determinism and limits

The compact producer sorts cues and the CLI serializes keys deterministically.
A blank 24x80 screen is guarded by compact/pretty byte ceilings and a field-count
ceiling; `tests/fixtures/screen-v1/blank-4x16.json` is the exact golden fixture.
Sorted JSON is used for repeatable tests and is not a claim of full JCS
canonicalization.

Row text currently uses Python-character clipping, not terminal-cell or grapheme
width. Wide/combining-character fidelity is a known boundary for future renderer
work.

The detailed audit, research, compatibility rules, budgets, and highlight
precedence are in
`docs/920-screen-consumer-finite-json-highlight-precedence.md`.
