# Rev672 / rev731 — regex substitution zero-width hygiene

Micromax's regex hostcalls are intentionally small and are documented as aligned
with the editor's `replace` / `replaceall` behavior where practical.  The editor
already rejects zero-width replacement matches before mutation because they are
invisible insertion points rather than visible text spans.  Before rev731, the VM
substitution hostcalls still forwarded those patterns straight to Python:

- `"abc" "" "X" "" re-sub` inserted at every boundary;
- `"abc" "^" "X" "" re-subn` rewrote an anchor match;
- `"abc" "(?=b)" "X" "" re-sub` changed text at a zero-width lookahead.

That was useful Python behavior, but it was not the same trust boundary as the
editor replacement commands.  A script could ask for a substitution and receive
an output produced from invisible positions, while adjacent replacement surfaces
would have stopped and explained the problem.

Rev731 keeps the fix deliberately narrow:

- `re-sub` and `re-subn` preflight their matches before producing output;
- the first zero-width match fails with
  `re.sub: zero-width matches are not supported` or
  `re.subn: zero-width matches are not supported`;
- positive-width substitutions keep their existing behavior and replacement
  count;
- zero-width-capable patterns that have no match remain ordinary no-ops;
- search-style hostcalls, flag parsing, match maps, and template parsing are
  untouched.

The trust rule is simple: substitution hostcalls should rewrite visible spans,
not silently manufacture output from invisible match positions.
