# Rev665 / rev724 — replace template parser hygiene

Rev724 is a small replacement-template trust cleanup that follows directly from
rev723's backslash-literal fix.  The shared converter had the right public
dialect after rev723 — `$1`, `$name`, `${name}`, and `$$` — but its internal
implementation still protected pieces of user text with private sentinel
strings such as NUL-delimited `DOLLAR` and `REF` markers.

Those sentinels were only private by convention.  Replacement templates are
user data, especially through regex hostcalls, so a literal template containing
the same bytes could be changed even though it did not use the documented
dollar dialect.  In particular, sentinel-like text could collapse into a
literal `$`, and `REF`-shaped text could be rewritten into a capture expansion
when the same placeholder was generated for a real `$1` reference nearby.

The fix removes the placeholder layer entirely.
`convert_replacement_template(...)` now scans the template once and emits output
as it goes:

1. `$1`, `$name`, and `${name}` become generated Python `\g<...>` references;
2. `$$` becomes one literal dollar sign;
3. raw user-authored backslashes are escaped immediately so Python keeps them
   literal;
4. every other byte/codepoint is copied through unchanged.

The parser intentionally keeps the same ASCII `$name` / `$1` recognition surface
as the previous regex.  Non-ASCII text next to `$` remains literal unless the
user explicitly chooses `${name}` syntax and Python accepts that group name at
expansion time.

## Focused tests

- `tests/test_regex_hostcalls.py`
- `tests/test_editor_core.py`
- `tests/test_editor_query_replace.py`
