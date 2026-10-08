# Micromax revision 0964

## Outcome

Rev0964 turns `micromax.screen.v1` from a producer-side shape into a bounded,
independently consumable interface. Public screen requests are finite before
startup or traversal, strict JSON and relational validation fail closed, the
producer cannot emit values its own consumer rejects, and existing viewport
cues now share one tested precedence.

## Product changes

- Added the stdlib-only `micromax-screen` entry point and module with silent
  `--check`, terminal-safe escaped `--text`, and deterministic `--summary` modes.
- Prevented document-supplied ANSI/C1 controls, carriage returns, embedded row
  breaks, and bidi format controls from replaying through the human text view or
  consumer errors; raw v1 JSON remains unchanged for fidelity.
- Refactored closed-object checks to test required fields and then fail on the
  first non-string/unknown member instead of copying and sorting all input keys.
- Required exact JSON built-in container/scalar types for direct validation, so
  caller-defined subclasses cannot run conversion, length, iteration, or repr hooks.
- Added shared public geometry limits: 1..256 lines, 1..512 columns, and at most
  65,536 cells.
- Applied geometry preflight to compact and diagnostic CLI dumps, REPL
  `:screen`, and the contract API before editor startup or model construction.
- Added an 8 MiB JSON input limit, depth 64, exact interoperable integer range,
  cue/tag/token limits, and bounded reads through short stream chunks.
- Rejected duplicate JSON names, invalid UTF-8, unpaired surrogates,
  NaN/infinity, floats, unknown fields, unsupported schemas, and malformed
  cursor/row/source/cue relationships.
- Added an exact 4x16 golden fixture and 24x80 compact, pretty, key-count, and
  row-field ceilings.
- Added explicit v1 compatibility rules: object fields are closed, new valid
  token values are tolerated, and field/semantic/budget changes require a new
  schema discriminator.

## Producer hardening

- Normalized public row kinds, cursor modes, tags, and cue kinds to bounded
  ASCII alphanumeric-hyphen tokens, with the same grammar in the packaged
  schema and strict consumer.
- Replaced unpaired surrogate code points in visible text with U+FFFD.
- Refused source coordinates outside the exactly interoperable integer range.
- Bounded diagnostic source rows before copying and source cue entries before
  normalization or deduplication.
- Rejected duplicate source-row identities rather than silently choosing the
  last row.
- Avoided copying caller-shaped mappings or sequences merely to inspect the
  fixed public fields.

## Renderer audit and refactor

- Added one explicit precedence for implemented viewport layers: docs inline,
  show characters, color column, whitespace diagnostics, brace match, search,
  and current search.
- Shared segment boundaries and attribute composition across ordinary and help
  viewport rows.
- Fixed the non-help fast path so a current-search-only cue cannot disappear.
- Replaced curses color-pair bits by clearing `A_COLOR` before applying a new
  pair; pair identifiers are no longer accidentally OR-combined.
- Made search remove inherited dimming while preserving unrelated emphasis;
  the current match remains independently reverse and bold.
- Removed two chronology-heavy deep-audit pages from the static LLM context;
  they remain discoverable through the revision ledger instead of consuming
  every handoff.

## Honest boundary

`row.text` is still clipped in Python code points rather than terminal cells or
grapheme clusters. Raw row text remains data that downstream programmatic
consumers must encode for their own output context. The bundled consumer validates
one bounded JSON document in memory,
not a streaming row protocol. The precedence resolver covers implemented
viewport cues, not a finished syntax/selection/theme system. Rev0964 does not
claim full RFC 8785 canonical JSON, a complete repository test run, or a
reproducible release pipeline.
