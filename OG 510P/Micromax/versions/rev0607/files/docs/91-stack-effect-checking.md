# Dev-mode stack effect checking (rev67)

Micromax treats stack effects as **documentation-first**.

This doc describes the **starter kit** for checking them in dev mode.

## Goals

- catch “my docstring effect is lying” bugs early
- make quotations usable as *debuggable units* (keybindings, hooks, actions)
- keep the implementation tiny, deterministic, and easy to port

This is not Factor-style global inference. It is a small, practical on-ramp.

## What exists now

### 1) Toggle: `stackcheck!` / `stackcheck@`

```
( n -- )  stackcheck!
( -- n )  stackcheck@
```

Modes:

- `0` = off (default)
- `1` = warn to stderr
- `2` = raise error

In warn/error modes, Micromax checks **closed** effects for:

- Words with closed effects (e.g. `( x -- x x )`)
- Quotations whose *leading paren-comment* contains a closed effect

The check is currently “net stack delta matches the declared delta”.
That’s simple but surprisingly useful.

### 2) Quote effect annotations now work

Quotations preserve comment tokens now, so you can do:

```
[ ( x -- x x ) dup ]
```

Tooling surfaces:

- `xt-effect` shows the quotation’s annotated effect
- dev-mode `stackcheck!` can validate it at runtime

### 3) Tools: `infer-effect` + `check-effect`

```
( xt -- s|0 )  infer-effect
( xt -- flag ) check-effect
```

`infer-effect` is **best-effort** and intentionally conservative:

- it succeeds only for straight-line code that calls other **closed-effect** words
- it returns `0` if anything is unknown or stack-polymorphic

`check-effect` compares the **declared** effect counts to the **inferred** counts.

## “Closed” vs stack-polymorphic effects

Micromax uses a tiny convention borrowed from concatenative systems:

- closed effect: `( x y -- z )`  → eligible for strict checking
- stack-polymorphic / row-variable: uses `..` (e.g. `..a`) or `...` or `*`

Examples:

- `dup` can be closed: `( x -- x x )`
- `call` is stack-polymorphic: `( ..a q -- ..b )` because the quotation changes the stack

The checker deliberately **skips** non-closed effects for now.

## Limitations (by design)

- no global inference across control flow
- no checking for polymorphic combinators beyond “skip”
- define-time checking only works when inference succeeds (no unknown words)

This is meant to be a small lever that improves doc honesty and debugging.

## Where to look

- `src/micromax/vm.py`: effect parsing, quotation effect extraction, inference, runtime checking
- `src/micromax/core.py`: `stackcheck!`, `stackcheck@`, `infer-effect`, `check-effect`, and updated polymorphic docs
- `tests/test_stack_effect_checking.py`
