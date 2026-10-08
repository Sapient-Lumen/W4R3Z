# Revision 0964 audit

## Priority judgment

The riskiest unfinished screen work was not another metadata family. Micromax
published a versioned compact snapshot without an independent receiving side,
while public dimensions could reach model construction before any finite-work
check. That left the compatibility promise, interoperability, and resource
boundary largely aspirational. Rev0964 lands one end-to-end seam instead of
expanding the registry surface.

## Corrected findings

1. **Producer-only contract:** a separate stdlib consumer now validates and uses
   snapshots without constructing an editor, loading plugins, or reading init.
2. **Unbounded public geometry:** CLI, diagnostic, REPL, and contract requests
   now share line, column, and cell preflight before startup/model traversal.
3. **Permissive decoder defaults:** repeated names, non-standard numbers,
   floats, invalid UTF-8, unpaired surrogates, excessive bytes/depth, and
   non-interoperable integers now fail closed.
4. **Schema-only trust gap:** the consumer enforces dynamic row count/order,
   cursor visibility, size-relative coordinates, non-empty cue ranges, area,
   and strict cue ordering that the packaged schema does not fully express.
5. **Self-invalid producer output:** token/text normalization and source-number
   refusal prevent diagnostic projection from emitting v1 that the strict
   consumer rejects. Token grammar is now the same explicit portable ASCII rule
   in producer, consumer, and schema rather than Python-specific `isalnum`.
6. **Hidden traversal and allocation:** source row lists and arbitrary row maps
   were copied, and oversized cue sequences could be consumed before the final
   unique-cue count. Source rows and cue attempts are now bounded first, large
   irrelevant mappings are not copied, and duplicate row identities are refused.
7. **Short-read truncation:** one binary `read(n)` can legally return less than
   `n` before EOF. The bounded reader now loops through short chunks until EOF or
   the one-byte over-budget witness.
8. **Terminal-control replay and object-copy waste:** the first human `--text`
   projection printed raw document text, consumer errors could carry external
   controls, and closed-object checks copied/sorted every member name before
   refusal. Text and stderr now neutralize controls, while object checks fail on
   the first invalid member without whole-object key copies. Direct validation
   accepts only exact JSON built-ins, preventing caller-defined scalar/container
   hooks. Raw JSON is preserved.
9. **Current-match disappearance:** the ordinary viewport fast path omitted
   `current_search_spans`; a current-only cue could bypass segmented rendering.
   The shared work predicate now includes every implemented cue source.
10. **Color-pair corruption:** OR-ing curses color-pair values can combine the
   `A_COLOR` bit field into a different pair number. Pair application now clears
   the mask before replacement.
11. **Duplicated overlay policy:** ordinary and help rows assembled overlapping
    attributes independently. Shared segment and resolver helpers now make the
    existing precedence executable and regression-testable.
12. **Context archaeology tax:** two old deep-audit pages remained pinned in
    every generated handoff despite the revision index already preserving them.
    They are no longer static context, restoring the compact-context ceiling
    without deleting history.

## Research reviewed on 2026-07-17

- RFC 8259 for unique-name interoperability, UTF-8, number grammar, numeric
  interoperability, and parser resource limits.
- Python 3.14 `json` compliance notes for duplicate-name, NaN/infinity, and
  surrogate behavior plus the absence of application-level limits.
- JSON Schema Draft 2020-12 core and validation vocabularies for the structural
  layer and its separation from application-owned relational semantics.
- OWASP API4:2023 for request-driven CPU/memory/resource bounds.
- ncurses `curs_color(3X)` for color-pair and `A_COLOR` bit-field semantics.
- SemVer 2.0.0 for separating declared package API meaning from unrelated
  archive and schema identities.
- RFC 8785 for canonical JSON requirements; Micromax deliberately claims only
  deterministic sorted-key test output, not JCS conformance.
- MITRE CWE-150 for neutralizing escape, meta, and control sequences before
  passing externally influenced text to a terminal or other interpreter.

The source links and the specific implications for Micromax are retained in
`docs/920-screen-consumer-finite-json-highlight-precedence.md`.

## Waste avoided

No schema registry, generic renderer framework, third-party JSON dependency,
plugin-loaded validator, theme engine, or speculative v2 field family was added.
The consumer is one small command over the existing contract. Dynamic checks
remain in executable code rather than being forced into an unreadable schema.
The TUI refactor shares only behavior already present and fixes observed defects
instead of pre-registering future syntax or selection layers.

## Cloudtainer observations

- A broad `test_editor_main_cli.py -k dump_screen` run advanced through 13 cases
  but exceeded the five-minute outer command limit. That stopped prefix is not
  counted as a pass.
- The targeted compact/diagnostic/startup CLI cases completed separately.
- `ruff` was not installed in the environment; project-local lint and compile
  checks are recorded separately in the validation report.

## Residual risk

- Python-character width is not terminal-cell or grapheme width; wide and
  combining text can differ across consumers.
- The consumer materializes one complete document after a bounded read.
- Raw contract row text is intentionally preserved; programmatic consumers that
  bypass the safe human projection own output-context neutralization.
- JSON Schema and the strict consumer overlap by design; generic schema tools do
  not prove all v1 relationships.
- The precedence resolver does not yet include syntax or primary/secondary
  selections because those visual layers are not implemented there.
- Tests, wheel, revision archive, and provenance still do not derive from one
  declared reproducible source snapshot. That is the next release-integrity
  risk and should outrank another screen field.
