# Expressions

VHK uses a small, intentionally limited expression language for:

- `If.condition`
- `While.condition`
- `SetVar.value` (when the value is a string)
- various fields that accept strings (after `${var}` interpolation)

The goal is **predictable scripting** that is powerful enough for automation logic,
without turning the macro format into an arbitrary Python execution surface.

## Syntax

The expression language is Python-like:

- literals: `123`, `3.14`, `'text'`, `True/False/None` (also accepts JSON-style `true/false/null/none`)
- arithmetic: `+ - * / % **`
- comparisons: `== != < <= > >= in not in is is not`
- boolean ops: `and`, `or`, `not`
- lists / dicts: `[1,2]`, `{'a': 1}`
- indexing + slicing: `items[0]`, `items[1:4]`

VHK also recognizes **lowercase JSON-style constants** `true`, `false`, `null`, and `none`.
They behave like `True`, `False`, and `None` and are treated as reserved identifiers.

## Expressions in numeric fields

Many step fields accept either an integer **or** a string (e.g. `Delay.ms`,
`RandomWait.min_ms`, `WaitForProcessExit.pid`).

When you provide a string, VHK will:

1. interpolate `${var}` tokens, then
2. attempt to evaluate the result as an expression, then
3. coerce the final value to an integer.

This makes data-driven timing and process steps less verbose:

```yaml
- type: SetVar
  name: jitter
  value: 37

- type: Delay
  ms: "250 + jitter"  # -> 287
```

### Variables

Names are resolved from the runner context.

```yaml
- type: SetVar
  name: i
  value: 0

- type: SetVar
  name: i
  value: i + 1
```

### Dict attribute access

For convenience, **dict values support dotted access** via attribute syntax:

```text
user.name
macro.name
project.name
```

This is equivalent to `user['name']` (and returns `None` if the key is missing).

> Note: attribute access on non-dicts is intentionally disallowed.

## Allowed functions

VHK only allows calling a small whitelist of helpers:

### Regex

- `re_search(pattern, text, flags=...) -> bool`
- `re_match(pattern, text, flags=...) -> bool`
- `re_findall(pattern, text, flags=...) -> list[str]`

### Basic utilities

- `len(x)`
- `int(x, base=10)`, `float(x)`, `str(x)`, `bool(x)`
- `abs(x)`, `round(x, ndigits=0)`
- `min(...)`, `max(...)`
- `sum(xs)`

### Strings

- `lower(s)`, `upper(s)`, `strip(s)`
- `replace(s, old, new, count=-1)`
- `split(s, sep=None, maxsplit=-1)`
- `join(sep, items)`
- `startswith(s, prefix)`, `endswith(s, suffix)`
- `contains(haystack, needle)`

### JSON

- `json_loads(s)`
- `json_dumps(obj, **kwargs)`


### Time

- `now_ns()` — current wall-clock time as epoch nanoseconds (best for comparing with filesystem `mtime_ns`).
- `now_ms()` — epoch milliseconds.
- `monotonic_ns()` — monotonic clock nanoseconds (best for measuring durations).
- `monotonic_ms()` — monotonic milliseconds (intentionally AHK-like: mirrors AutoHotkey’s `A_TickCount`).

## Examples

```yaml
- type: If
  condition: "re_search('^OK', ocr_text) and match_score >= 0.9"
  then_steps:
    - type: Log
      message: "Looks good"
  else_steps:
    - type: Log
      message: "Not yet"
```

```yaml
- type: SetVar
  name: parts
  value: split(strip(raw_line), ',')

- type: SetVar
  name: slug
  value: replace(lower(join('-', parts)), ' ', '-')
```
