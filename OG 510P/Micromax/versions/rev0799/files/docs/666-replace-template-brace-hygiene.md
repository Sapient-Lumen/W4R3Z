# Rev666 / rev725 — replace template brace hygiene

Rev725 is a small replacement-template parser cleanup that follows directly
from rev724's sentinel-free rewrite.  Micromax's replacement dialect documents
three active reference forms — `$1`, `$name`, and `${name}` — plus `$$` for a
literal dollar.  Rev724 made that parser single-pass, but the braced form still
accepted any non-empty body and generated Python's `\g<...>` replacement syntax
from it.

That mattered because Python uses `>` as the generated reference delimiter.  A
malformed Micromax template such as `${x>tail}` became `\g<x>tail>`, expanding
capture group `x` and leaving `tail>` as literal replacement text.  Similarly,
`${$1}` could travel through the wrong layer instead of staying literal user
text.

The fix keeps the public dialect small and explicit:

1. `${...}` becomes an active group reference only when the body is a valid
   Micromax group token: ASCII digits or an ASCII identifier;
2. `${name}` and `${1}` remain active, so valid missing groups still report
   through the existing invalid-replacement diagnostics;
3. malformed closed braced forms such as `${x>tail}`, `${$1}`, and `${1abc}`
   are emitted as one literal segment, so nested `$...` text inside them does
   not become active accidentally;
4. raw backslashes inside malformed braced forms are still escaped before the
   result reaches Python's replacement parser, preserving rev723's backslash
   literal contract.

The goal is not to add syntax.  It is to make the existing `${name}` syntax mean
only what the docs say, without inheriting Python's delimiter grammar.

## Focused tests

- `tests/test_regex_hostcalls.py`
- `tests/test_editor_core.py`
- `tests/test_editor_query_replace.py`
