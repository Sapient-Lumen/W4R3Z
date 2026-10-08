# Rev664 / rev723 — replace template backslash hygiene

Rev723 is a small replacement-template dialect cleanup that follows directly
from rev722's invalid-template error handling.  The visible editor and regex
hostcall docs say replacement templates use Micromax's dollar-based dialect:
`$1`, `$name`, `${name}`, and `$$`.  But the converter still passed raw
user-authored backslashes through to Python's `re` replacement parser.

That made two surprising things possible:

- `replace 'a([0-9])' '\1'` could behave like a Python replacement backref,
  even though `\1` is not documented Micromax template syntax;
- `replaceall 'a([0-9])' '\q'` could fail as a Python bad replacement escape
  instead of replacing matches with the literal text the user typed.

The same leak existed in `qreplace` and the VM regex hostcalls because all of
those paths share `micromax.regex_tools.convert_replacement_template(...)`.

The fix keeps the public dialect intentionally small.  The converter now:

1. protects Micromax `$...` references as internal placeholders;
2. escapes every raw user-authored backslash so Python treats it literally;
3. reinserts only the generated `\g<...>` references that came from Micromax
   `$1`, `$name`, or `${name}` syntax;
4. still turns `$$` into one literal dollar sign.

This means `$1` keeps expanding capture group 1, while `\1`, `\q`, and other
backslash text stay literal replacement text across editor commands and hostcalls.
It also means rev722's invalid-template diagnostics still apply to Micromax's
own bad `$...` references, without also exposing Python's backslash template
syntax as an undocumented second language.

## Focused tests

- `tests/test_editor_core.py`
- `tests/test_editor_query_replace.py`
- `tests/test_regex_hostcalls.py`
