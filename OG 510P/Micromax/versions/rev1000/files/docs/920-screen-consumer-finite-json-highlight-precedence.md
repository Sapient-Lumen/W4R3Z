# Screen consumer, finite JSON, and highlight precedence (rev0964)

## Executive judgment

The highest-risk unfinished part of `micromax.screen.v1` was not another model
field. It was the absence of a real receiving side. Micromax could emit a compact
snapshot and package a schema, but no independent program proved that the object
was finite, interoperable, relationally coherent, or useful without importing
editor internals.

Rev0964 turns that producer-only promise into a small end-to-end product seam:

```text
bounded request -> compact producer -> strict JSON boundary -> independent consumer -> safe text view
```

The same pass audited the curses viewport and found two concrete rendering bugs:
color-pair bits were combined rather than replaced, and a current-search-only cue
could take the plain fast path and never render. The refactor now gives existing
viewport cues one tested precedence instead of maintaining separate plain/help
overlay implementations.

This is product work, not a new registry. The evidence is executable: one CLI,
one fixture, relational validation, focused renderer helpers, and subprocess
producer-to-consumer tests.

## Rev0967 follow-on

Rev0967 uses the extension point rev0964 deliberately left open. The existing
Micromax syntax spans and primary/secondary selections now enter the shared
viewport rows, become compatible v1 cue-token values, and paint through the same
reference-TUI resolver. Selected logical newlines receive one visible blank cell.
The v1 object shape, coordinate meaning, consumer, and schema do not change.

The follow-on also removes a renderer-side status reread: prompt cursor placement
now consumes the composed screen cursor, so edit-window horizontal scrolling can
no longer shift the prompt cursor. See
`docs/923-visible-selection-syntax-hierarchy.md`.

## Risks found

### Public screen sizes were unbounded before model work

Micromax-language model hostcalls already apply finite line, column, width, and
cell budgets. The public `--dump-screen`, diagnostic dump, and REPL `:screen`
paths did not. A caller could request a large graph before JSON serialization or
result limits had any opportunity to help.

The public paths now share one preflight and reject before runtime startup or
screen traversal. The REPL prints the refusal and remains live.

### Python's default JSON behavior was too permissive for a contract

The standard decoder accepts repeated object names with last-value-wins behavior,
accepts `NaN` and infinities, accepts unpaired UTF-16 surrogates, and does not add
application-level input, depth, or string limits. Those defaults are useful for a
general library and wrong for a stable machine boundary.

The consumer now rejects duplicate names, non-standard numbers, floating-point
numbers, unpaired surrogates, invalid UTF-8, excessive bytes, excessive nesting,
and integers outside the exactly interoperable `[-(2^53-1), 2^53-1]` range.
`micromax.screen.v1` has no floating-point fields.

### A schema alone did not express the actual contract

Draft 2020-12 captures field shapes, fixed maxima, required fields, and closed
objects. It does not by itself express all dynamic relationships used here:

- `len(rows) == size.lines`;
- row `y` values are contiguous and equal their array indexes;
- visible cursor and cue coordinates are bounded by this snapshot's dimensions;
- hidden cursors omit coordinates;
- cue `end > x`;
- cues are strictly sorted and unique;
- total `lines * cols` is within the cell budget.

The strict stdlib consumer enforces those relationships after decoding. The
packaged schema remains useful for general tooling and now carries the fixed
limits and hidden-cursor rule it can express.

### The producer could emit values its consumer would reject

The diagnostic projection trusted row kinds, cursor modes, source coordinates,
and Python strings more than the public v1 grammar allowed. A malformed or
third-party diagnostic source could therefore make Micromax produce a snapshot
that `micromax-screen` refused.

Projection now normalizes public tokens, replaces unpaired surrogates with
U+FFFD in visible text, and refuses non-interoperable source coordinates. The
normal editor path remains unchanged; the compatibility path can no longer leak
invalid v1 values.

The second-pass audit also found that diagnostic row mappings were copied in
full and cue sequences could be traversed before the final output-count check.
Projection now admits at most one source row per visible line, rejects duplicate
screen-row identities, and charges every source cue entry before parsing or
deduplication. Large irrelevant mappings are no longer copied.

### A short-reading stream could be mistaken for end-of-file

A single `read(maximum + 1)` is sufficient for ordinary buffered files and
pipes, but the binary stream interface permits short reads. The consumer now
loops over bounded chunks until EOF or one witness byte beyond the input limit.
Direct validator calls require exact built-in JSON container and scalar shapes,
so custom mappings, sequences, strings, integers, or booleans cannot hide work or
caller-defined conversion behind validation.

### Human-facing output replayed externally supplied terminal controls

The v1 JSON contract must preserve row text, including unusual characters. The
first `--text` implementation printed that text directly. A document containing
ESC/C1 controls, carriage returns, embedded newlines, or Unicode bidi format
characters could therefore alter the inspecting terminal or visually reorder the
output even though the JSON decoder and contract were valid.

`screen_contract_text()` and `micromax-screen --text` now double literal
backslashes and escape Unicode categories `Cc`, `Cf`, `Zl`, and `Zp`. The only raw
line breaks emitted are the consumer-owned separators between validated rows. Raw
JSON remains unchanged, so this is downstream output neutralization rather than a
lossy schema restriction. Consumers that use `row.text` directly must apply the
appropriate encoding for their own renderer.

The same audit found that closed-object validation collected and sorted every
member name before refusal, then interpolated unknown names into exception text.
Validation now checks required fields first, refuses the first non-string or
unknown member without whole-object copies, accepts only exact JSON built-in
container/scalar types, and neutralizes every consumer error before stderr. This
closes avoidable traversal, caller-defined conversion hooks, and the error-channel
version of the terminal-control problem.

### Viewport cue composition had two real defects

1. Documentation link colors used `base_attr | curses.color_pair(n)`. Color pairs
   occupy the `A_COLOR` bit field, so OR-ing a second pair can produce a different
   pair identifier. The renderer now clears `A_COLOR` before applying the chosen
   pair.
2. The non-help fast path checked the broad search spans but omitted
   `current_search_spans`. A current-only cue could therefore bypass all segmented
   rendering. The shared work predicate now includes every existing viewport cue.

## Landed interface

Install or run the consumer as either an entry point or a module:

```bash
python -m micromax_editor --dump-screen 24 80 \
  | python -m micromax_editor.screen_consumer --check

micromax-screen screen.json --check
micromax-screen screen.json --text
micromax-screen screen.json --summary
```

`--check` is silent on success. `--text` prints one terminal-safe escaped
line per visible row; raw contract JSON is not rewritten. `--summary` is the
default and emits deterministic summary JSON containing size,
cursor, row/cue counts, and kind counts. Input defaults to standard input and may
instead name one file.

The consumer imports only the standard library and the small screen contract
modules. It does not construct an `Editor`, load plugins, read user init, or know
the internal diagnostic graph.

## Version-one compatibility policy

The schema discriminator is exactly `micromax.screen.v1`.

A conforming v1 producer:

- emits exactly the documented top-level and nested fields;
- stays within every v1 budget;
- emits relationally valid rows, cursor, source coordinates, and sorted cues;
- uses UTF-8 JSON with unique object names and no floating-point values;
- may emit new token values for row kinds, cursor modes, tags, and cue kinds.

All public tokens use the cross-language ASCII grammar
`[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*` and are at most 96 characters. Producer,
consumer, and packaged schema enforce the same rule; Unicode remains fully
available in row text rather than in protocol identifiers.

A conforming v1 consumer:

- preserves row text and cursor truth without requiring every token to be known,
  while neutralizing it for the consumer's actual output context;
- ignores unknown *token values* whose syntax is valid;
- rejects unknown object fields, because field additions are not part of v1;
- rejects unsupported schema discriminators rather than guessing.

The following require a new schema discriminator, normally
`micromax.screen.v2`:

- adding, removing, or renaming a field;
- changing a field type, coordinate convention, ordering rule, or meaning;
- lowering a required acceptance budget;
- allowing the producer to exceed a v1 maximum;
- changing required rows, cursor visibility semantics, or source mapping.

A producer bug fix that restores the already-documented v1 behavior does not
require v2. Adding a previously unseen valid token value is compatible; exhaustive
consumer switches are non-conforming.

V1 remains the default until a replacement has its own schema, independent
consumer, fixtures, transition documentation, and an overlap period. There is no
calendar-based deprecation promise in this revision.

The archive revision, Python package version, host API version, and screen schema
are separate identities. SemVer is useful guidance for a declared package API;
it does not silently assign compatibility meaning to `micromax.screen.v1` or to
archive revision 0964.

## Finite contract budgets

| Boundary | V1 limit |
| --- | ---: |
| Lines | 1..256 |
| Columns | 1..512 |
| Screen cells | 65,536 |
| JSON input | 8 MiB |
| JSON container depth | 64 |
| Integer magnitude | 2^53 - 1 |
| Rows | exactly `size.lines`, maximum 256 |
| Cues | 65,536 |
| Tags per row | 32 |
| Token characters | 96 |
| Row text | at most `size.cols` Python characters |

The `lines`, `cols`, and cell limit are applied before startup/model traversal in
the CLI and before model work in the REPL and contract API. The stream consumer
reads through short chunks but retains at most the byte budget plus one witness
byte. Diagnostic projection admits at most one row per visible line and charges
source cue entries against the cue budget before normalization or deduplication.

The 24x80 blank-screen regression budget is:

- compact sorted JSON: at most 1,536 bytes;
- indented sorted JSON: at most 3,072 bytes;
- recursive object-key count: at most 96;
- fields on any row: at most five.

`tests/fixtures/screen-v1/blank-4x16.json` is the exact small golden fixture. The
larger checks are ceilings rather than exact byte hashes so status wording can
improve without reopening sparse-schema growth.

## Current viewport precedence

For implemented cues, low to high precedence is:

```text
syntax
docs inline
show-character marks
color column
whitespace diagnostics
brace match
ordinary search
secondary selection
primary selection
current search
```

Syntax is a reading layer. Search and direct selection clear inherited dimming;
secondary and primary selections remain distinct; the current match adds bold
and underline last so query-replace stays visible inside an active selection.
Color-pair choice remains replacement, not pair-bit accumulation. This is one
small reference hierarchy, not a general theme system.

## Research basis reviewed on 2026-07-17

Primary sources:

- RFC 8259, JSON grammar, unique-name interoperability, UTF-8, numeric limits,
  and parser limits: https://www.rfc-editor.org/rfc/rfc8259.html
- Python 3.14 `json` compliance notes on duplicate names, NaN/infinity,
  surrogates, and absent application limits:
  https://docs.python.org/3/library/json.html#standard-compliance-and-interoperability
- JSON Schema Draft 2020-12 core and validation vocabularies:
  https://json-schema.org/draft/2020-12/json-schema-core
  https://json-schema.org/draft/2020-12/draft-bhutton-json-schema-validation-00
- OWASP API4:2023 on bounding CPU, memory, storage, and other request-driven
  resources:
  https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- ncurses color-pair and `A_COLOR` semantics:
  https://invisible-island.net/ncurses/man/curs_color.3x.html
- Semantic Versioning 2.0.0 on declaring a public API before assigning version
  meaning: https://semver.org/spec/v2.0.0.html
- RFC 8785 on canonical JSON and deterministic property sorting:
  https://datatracker.ietf.org/doc/html/rfc8785
- MITRE CWE-150 on neutralizing escape, meta, and control sequences before
  output reaches a terminal or other interpreter:
  https://cwe.mitre.org/data/definitions/150.html

Micromax uses sorted-key golden serialization for deterministic tests; it does
**not** claim full RFC 8785/JCS canonicalization.

## Evidence in this revision

- `tests/test_screen_budget.py` proves pre-traversal CLI/API/REPL rejection and a
  live REPL after refusal.
- `tests/test_screen_consumer.py` covers the exact fixture, strict parsing,
  relational failures, bounded and short stream reads, exact JSON built-in
  shapes, fail-fast closed-object validation, terminal-safe text/error escaping,
  all consumer modes, and a real
  producer process piped into a separate consumer process.
- `tests/test_screen_contract.py` pins compact ceilings, validates complex cues,
  proves the compact path avoids the diagnostic graph, and checks malformed
  projection normalization/refusal, schema/token agreement, and pre-dedup source
  traversal limits.
- `tests/test_tui_highlight_precedence.py` pins overlap behavior, current-only
  work, dim removal, attribute preservation, and color-pair replacement.
- Existing match-brace and color-column slices remain green after the shared
  overlay refactor.

A broad `test_editor_main_cli.py -k dump_screen` attempt advanced through 13
cases but exceeded the five-minute cloudtainer command deadline. No full CLI-file
or repository-suite claim is made from that stopped prefix.

## Honest boundaries and speculation

- `row.text` is bounded in Python characters, not Unicode terminal cells. Wide,
  combining, and grapheme-cluster fidelity remains a renderer/protocol gap.
- The consumer validates one complete JSON document in memory after a bounded
  read. It is not a streaming row renderer.
- The JSON contract intentionally preserves raw row text. Programmatic consumers
  that bypass the safe text view remain responsible for neutralizing their own
  terminal, HTML, log, or other downstream output context.
- JSON Schema and the strict consumer intentionally overlap. The schema serves
  generic tooling; the consumer owns v1's dynamic invariants and safe parser
  behavior.
- The TUI precedence now covers the implemented syntax, docs, diagnostic,
  search, and primary/secondary selection layers. Terminal palette quality,
  cursor shape/focus, and cross-renderer cell semantics remain outside it.
- An independent consumer makes visual regression tools, remote inspection, and
  assistive adapters plausible. That is speculation, not a commitment to expand
  v1. A real downstream should first prove which fields it needs.
- The next highest project risk is ordinary release source truth: tests, wheel,
  archive, and provenance still do not derive from one declared reproducible
  source snapshot. That work should come before another screen field family.
