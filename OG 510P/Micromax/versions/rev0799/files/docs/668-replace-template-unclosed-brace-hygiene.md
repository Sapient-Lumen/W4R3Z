# Rev668 / rev727 — replace template unterminated-brace hygiene

Rev727 is a small replacement-template parser cleanup that follows directly
from the recent dollar-dialect hardening. Micromax's replacement syntax treats
`$0`, `$1`, `$name`, `${name}`, and `$$` as the visible active forms, and keeps
malformed text literal instead of letting Python's replacement parser invent a
second interpretation.

Closed malformed braced forms such as `${x>tail}` and `${$1}` already stayed
literal after rev725. One nearby edge remained: if the user omitted the closing
brace, the parser fell back to character-by-character parsing after the `$`. A
template such as `${$1` therefore became literal `${` plus an active `$1`
reference. That was surprising because the visible replacement looked like one
malformed braced placeholder, but part of it still executed as replacement
syntax.

The fix is intentionally narrow:

1. when the parser sees `${` with no matching `}`, it emits the rest of the
   template as one literal segment;
2. nested dollar-shaped text inside that unterminated span, such as `${$1` or
   `${x$1`, does not expand;
3. raw backslashes inside the literalized span remain protected before Python's
   replacement parser sees the final string;
4. valid `${name}` / `${1}` references, malformed closed `${...}` literals, and
   canonical numeric references keep their existing behavior.

The goal is simple: braces should be a clear delimiter for an active
replacement reference, not a half-open region where a later `$...` token can
still surprise the user.

## Focused tests

- `tests/test_regex_hostcalls.py`
- `tests/test_editor_core.py`
- `tests/test_editor_query_replace.py`
