# Rev675 / rev734 — regex hostcall out-of-range start hygiene

Micromax's regex search hostcalls take an explicit `start` index:

- `re-search` takes `( hay pattern start flags -- m|0 )`.
- `re-findall` takes `( hay pattern start flags -- ms )`.

Rev730 made negative starts visible errors and documented positive out-of-range
starts as ordinary empty searches. One host-specific edge still leaked through:
Python's regex engine clamps `pos > len(hay)` to `len(hay)` for zero-width
patterns. A script could ask to search from `99` in `"abc"` and still get an
EOF match for `""`, `$`, or `(?=)`.

That is surprising because the caller's visible search space is already beyond
the haystack. Rev734 keeps the boundary explicit:

- pattern and flag validation still happen first, so invalid regexes and invalid
  flag dialects stay visible;
- after compilation, `start > len(hay)` returns `0` for `re-search`;
- after compilation, `start > len(hay)` returns `[]` for `re-findall`;
- `start == len(hay)` still allows legitimate EOF zero-width matches.

The trust rule is small: a positive start past EOF should mean no search space,
not a host-clamped search from EOF.
