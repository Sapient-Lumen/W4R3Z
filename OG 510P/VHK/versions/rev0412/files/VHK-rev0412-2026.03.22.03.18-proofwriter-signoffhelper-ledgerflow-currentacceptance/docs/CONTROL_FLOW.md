# Control flow and error handling

VHK now has structured blocks so macros do not need to fake loops and recovery with shell snippets.

## `While`

```yaml
- type: SetVar
  name: i
  value: 0
- type: While
  condition: "i < 5"
  max_iterations: 20
  steps:
    - type: Log
      message: "i=${i}"
    - type: SetVar
      name: i
      value: "i + 1"
```

Notes:
- `condition` uses the same safe expression evaluator as `If`.
- `max_iterations` defaults to `1000` to prevent accidental infinite loops.
- `out_iterations` stores how many iterations actually ran.

## `Break`, `Continue`, `Return`

These behave like their counterparts in Python / Robot Framework style loop control:

```yaml
- type: While
  condition: "True"
  steps:
    - type: If
      condition: "retries > 3"
      then_steps:
        - type: Break
```

```yaml
- type: Return
  value_expr: "'done:' + status"
  out_var: result
```

`Return` exits the current macro immediately. If that macro was called with `CallMacro`, any vars already set in the child context can still be returned via `returns:`.

## `Try`

```yaml
- type: Try
  steps:
    - type: RunShell
      command: "python risky_task.py"
  catch_pattern: "timed out|not found"
  catch_steps:
    - type: Notify
      summary: "Recovering from transient failure"
  finally_steps:
    - type: Log
      message: "cleanup done"
```

Behavior:
- `catch_steps` run only when the error matches `catch_pattern` (or when no pattern is set).
- `finally_steps` always run.
- The caught error is exposed in `last_error` and also in `out_error` (defaults to `last_error`).

## Expression-friendly `SetVar`

`SetVar` still supports plain literals and interpolation like `${name}`, but it now also accepts simple expressions directly:

```yaml
- type: SetVar
  name: total
  value: "total + price"
```

That keeps loop bodies small and avoids forcing users into shell snippets for simple arithmetic or list/dict lookups.
