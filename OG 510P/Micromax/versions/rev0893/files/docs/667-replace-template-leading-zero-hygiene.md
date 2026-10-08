# Rev667 / rev726 — replace template leading-zero hygiene

Rev726 is a small replacement-template parser cleanup that follows directly
from rev725's braced-token validation.  Micromax's replacement dialect is
visible and dollar-based: `$0`, `$1`, `$name`, `${name}`, and `$$` are the
active forms users can reason about, while everything outside that dialect is
literal user text.

Python's replacement parser accepts generated references such as `\g<01>` and
normalizes them to group 1.  Before rev726, Micromax passed `$01` and `${01}`
through to that layer, so the token the user saw was not quite the token that
actually ran.  That is a trust problem in a bulk-edit path: typo-shaped numeric
references should not quietly choose a nearby capture group.

The fix keeps the public dialect small and explicit:

1. numeric references are active only in canonical decimal form: `$0`, `$1`,
   `$12`, `${0}`, `${1}`, `${12}`;
2. leading-zero numeric forms such as `$00`, `$01`, and `${01}` stay literal;
3. named references and valid missing-group diagnostics are unchanged;
4. raw backslashes in literalized tokens still stay literal before Python's
   replacement parser sees the final replacement string.

The goal is not to add a new escaping rule.  It is to ensure that when Micromax
activates a numeric replacement token, the visible spelling and the underlying
regex group reference agree.

## Focused tests

- `tests/test_regex_hostcalls.py`
- `tests/test_editor_core.py`
- `tests/test_editor_query_replace.py`
