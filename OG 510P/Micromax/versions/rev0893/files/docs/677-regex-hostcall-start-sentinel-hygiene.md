# Rev677 / rev736 — regex hostcall start sentinel hygiene

Micromax's search-style regex hostcalls expose an explicit start index:

- `re-search` takes `( hay pattern start flags -- m|0 )`.
- `re-findall` takes `( hay pattern start flags -- ms )`.

Earlier start hygiene made the visible integer boundary more honest: negative
starts fail, and starts past the haystack are empty searches instead of host
engine EOF clamps. Rev735 did the same kind of cleanup for the `flags` slot by
rejecting Python-only sentinels such as `None` and booleans.

One adjacent Python embedding leak remained: `bool` is a subclass of `int`, so a
direct hostcall user could pass `False` or `True` as `start`. That silently meant
`0` or `1`, even though non-Python ports and Micromax scripts do not have a
reason to spell an index as a truth value.

Rev736 keeps the fix small:

- `re-search` rejects `False` / `True` as start values;
- `re-findall` rejects `False` / `True` as start values;
- normal integer starts, including `0`, keep their behavior;
- negative-start and out-of-range-start behavior from rev730/rev734 is unchanged;
- direct hostcall failures pop the full search argument shape before reporting
  the boolean-start error, so stale haystack/pattern values are not left behind.

The trust rule is the same as the flag-dialect rule: hostcall argument slots
should accept values the portable VM contract can name, not Python-specific
convenience sentinels.
