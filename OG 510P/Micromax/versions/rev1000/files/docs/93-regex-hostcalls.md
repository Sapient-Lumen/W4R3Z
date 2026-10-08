# Regex hostcalls (rev68)

Micromax's editor embedding exposes a small set of regular expression helpers
as **hostcalls**.

Why hostcalls?

- Regex engines differ across hosts (Python, Rust, WASM, RE2, etc.)
- We want the portable kernel to stay tiny

This set is meant to align with the editor’s `replace` / `replaceall` behavior:
regex by default, literal mode as a separate toggle.

## Feature flag

Scripts can probe availability:

```forth
"mx.regex" host.feature?  ( -> 1 if available )
```

## Hostcalls

All helpers accept `flags` as `0` or a string containing any of:

- `i` ignorecase
- `m` multiline
- `s` dotall

Python `None`, booleans, and non-zero Python integer flags are rejected. The hostcall
surface is meant to stay portable and quiet, so embedding-only sentinel values
and host-specific flag bits such as Python's `re.DEBUG` are not part of the
public dialect.

Search-style helpers require a non-negative integer `start` position. Python
booleans are rejected even though `bool` subclasses `int`, because `False` /
`True` are embedding-only sentinels rather than portable index spellings. Starts
strictly beyond the haystack are ordinary empty searches (`0` for `re.search`,
`[]` for `re.findall`), even for zero-width patterns that Python would otherwise
clamp to the final insertion point. Negative starts are rejected instead of being
silently clamped to `0`.

### `re.search`

Stack effect: `( hay pattern start flags -- m|0 )`

`start` must be a non-negative integer; Python boolean sentinels are rejected. A
`start` value greater than `len(hay)` returns `0` before the host regex engine
can clamp it to EOF. Otherwise returns `0` if not found, or a small map if found:

```text
{ "start": n, "end": n, "group": "...", "groups": ["..." ...], "groupdict": { ... } }
```

Unmatched optional captures inside `groups` / `groupdict` are reported as `0`;
captures that participate but match the empty string remain `""`.

### `re.findall`

Stack effect: `( hay pattern start flags -- ms )`

`start` must be a non-negative integer; Python boolean sentinels are rejected. A
`start` value greater than `len(hay)` returns `[]` before the host regex engine
can clamp it to EOF. Otherwise returns a list of the same match maps as
`re.search`.

### `re.sub`

Stack effect: `( hay pattern repl flags -- out )`

Zero-width matches are rejected before producing output.  This keeps substitution
hostcalls aligned with editor `replace` / `replaceall`: replacements rewrite
visible spans, not invisible insertion points.  Missing or malformed active
replacement references fail as `re.sub: invalid replacement: ...`.

### `re.subn`

Stack effect: `( hay pattern repl flags -- out n )`

Returns the replacement count as `n`.  Like `re.sub`, zero-width matches are
rejected before output is produced, and missing or malformed active replacement
references fail as `re.subn: invalid replacement: ...`.

### `re.escape`

Stack effect: `( s -- s2 )`

## Replacement templates

Replacement strings follow a small, editor-aligned convention:

- `$1`, `$2`, ... expand numbered capture groups
- `$name` or `${name}` expand named capture groups
- malformed braced forms such as `${x>tail}`, `${$1}`, or `${$1` stay literal
- `$$` is a literal `$`
- raw backslashes stay literal; Python-only templates such as `\1` are not
  replacement backreferences in Micromax's dialect

Implementation is shared with the editor command dispatcher so the semantics
don’t drift. The shared converter is a single-pass parser, not a sentinel-based
rewrite, so literal user text is not treated as a private placeholder. Active
references to groups that do not exist fail explicitly as invalid replacement
templates on both editor and hostcall surfaces.

## Implementation pointers

- `src/micromax/host_regex.py`
- `src/micromax/regex_tools.py` (shared template conversion)
- `src/micromax_editor/command_dispatcher.py` (replace/replaceall)
