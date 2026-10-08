# Rev671 / rev730 — regex hostcall start hygiene

Micromax's regex hostcalls expose a deliberately tiny boundary:

- `re-search` takes `( hay pattern start flags -- m|0 )`.
- `re-findall` takes `( hay pattern start flags -- ms )`.

That `start` value is visible caller intent. Before rev730, negative starts were
silently clamped through `max(0, start)`, so a bug such as `-1` behaved like
`0` and searched from the beginning of the haystack. That is convenient, but it
is not trustworthy: a caller can ask for one offset and get another offset
without any visible feedback.

Rev730 keeps the policy narrow and portable:

- negative `start` values fail before regex execution with
  `re: start must be non-negative, got N`;
- `0` and positive starts keep their existing behavior;
- positive starts beyond the haystack remain ordinary empty searches (`0` for
  `re-search`, `[]` for `re-findall`);
- flag parsing, match maps, capture absence, and replacement templates are
  untouched.

The trust rule is simple: an explicit index argument should not be silently
rewritten to a different index.


Rev734 closes one follow-up hidden by host-engine details: Python clamps a
`pos` greater than `len(hay)` back to the final insertion point for zero-width
patterns. Micromax now checks `start > len(hay)` after compiling the pattern and
flags, but before executing the search, so positive out-of-range starts are
empty searches even for `""`, `$`, and lookahead-only patterns.


Rev736 extends this same boundary to Python embedding sentinels: `False` and
`True` are rejected as `start` values instead of being accepted through Python's
`bool`/`int` subclass relationship. Integer `0` remains the portable spelling for
the beginning of the haystack.
