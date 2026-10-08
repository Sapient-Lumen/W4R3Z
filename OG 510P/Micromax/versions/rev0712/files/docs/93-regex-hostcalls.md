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

### `re.search`

Stack effect: `( hay pattern start flags -- m|0 )`

Returns `0` if not found; otherwise returns a small map:

```text
{ "start": n, "end": n, "group": "...", "groups": ["..." ...], "groupdict": { ... } }
```

### `re.findall`

Stack effect: `( hay pattern start flags -- ms )`

Returns a list of the same match maps as `re.search`.

### `re.sub`

Stack effect: `( hay pattern repl flags -- out )`

### `re.subn`

Stack effect: `( hay pattern repl flags -- out n )`

Returns the replacement count as `n`.

### `re.escape`

Stack effect: `( s -- s2 )`

## Replacement templates

Replacement strings follow a small, editor-aligned convention:

- `$1`, `$2`, ... expand numbered capture groups
- `$name` or `${name}` expand named capture groups
- `$$` is a literal `$`

Implementation is shared with the editor command dispatcher so the semantics
don’t drift.

## Implementation pointers

- `src/micromax/host_regex.py`
- `src/micromax/regex_tools.py` (shared template conversion)
- `src/micromax_editor/command_dispatcher.py` (replace/replaceall)
