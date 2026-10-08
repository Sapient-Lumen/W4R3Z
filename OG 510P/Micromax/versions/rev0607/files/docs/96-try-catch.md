# `try` / `recover` / `ensure` helpers (rev72)

Micromax exposes a small, *Forth-like* exception mechanism:

- `catch ( q -- ior )` runs a quotation. On error, it **restores the data stack** to the depth
  it had at `catch` entry and returns a nonzero `ior`.
- `throw ( ior -- )` raises when `ior` is nonzero.
- `last-error ( -- s )` returns a formatted error message for the most recent VM error.

This mirrors standard Forth’s `CATCH`/`THROW` contract: on `THROW`, control returns as if the
corresponding `CATCH` returned the code, and the stack depth is restored.

## Convenience combinators

These are defined in `src/micromax/stdlib/core.mx` and are intentionally tiny.

### `try?`

```
try? ( ..a q -- ..a ..b flag )
```

Runs `q`. On success, leaves results and `flag=1`. On failure, restores the stack and leaves `flag=0`.
Details are available via `last-error`.

Example:

```
[ 1 2 + ] try?   \ => 3 1
123 [ drop drop ] try?  \ => 123 0   (stack restored)
```

### `try` / `recover`

`try` runs a handler quotation on failure, passing `(ior msg)`:

- body:    `( ..a -- ..b )`
- handler: `( ..a ior msg -- ..b )`

Example:

```
1 [ drop drop ] [ drop drop 999 ] try   \ => 1 999
```

`recover` is an alias for `try` (some folks prefer that naming).

## Notes

- This is meant to make the **common** pattern ergonomic, not to “hide” errors.

## `ensure` / `finally`

```
ensure  ( ..a body cleanup -- ..b )
finally ( ..a body cleanup -- ..b )   \ alias
```

Runs `body` and **always runs `cleanup`**, then rethrows the original error if `body` failed.

- On success, `cleanup` runs with the post-body stack (`..b`).
- On failure, `cleanup` runs with the pre-body stack (`..a`) because `catch` restores the stack.
- If `cleanup` errors, that error wins.

Example:

```
[ 1 ] [ 2 + ] ensure    \ => 3
```


## References
- Standard Forth `THROW` notes stack depth restoration: https://forth-standard.org/standard/exception/THROW
