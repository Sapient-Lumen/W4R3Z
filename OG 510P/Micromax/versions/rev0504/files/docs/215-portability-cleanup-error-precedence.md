# Rev273 — portability cases for cleanup-error precedence in `ensure` / `finally`

Rev257 already made one important recovery behavior replayable from JSON: expected-
error cases can pin down the **post-error stack** instead of leaving that truth in
Python-only tests.

But Micromax's stdlib docs had one more explicit cleanup contract that still was
not replayable through the portable corpus:

- `ensure` / `finally` always run cleanup
- if the **body** fails, the stack is restored before cleanup runs
- if **cleanup itself** fails, **that cleanup error wins**

This revision closes that gap.

## New replayable cases

The portability corpus now carries four small cases:

- `stdlib-ensure-cleanup-error-wins-on-success`
- `stdlib-ensure-cleanup-error-wins-on-failure`
- `stdlib-finally-cleanup-error-wins-on-success`
- `stdlib-finally-cleanup-error-wins-on-failure`

Focused examples:

- `[ 1 ] [ "cleanup boom" error ] ensure` → error contains `cleanup boom`, stack `[1]`
- `123 [ drop drop ] [ "cleanup boom" error ] ensure` → error contains `cleanup boom`, stack `[123]`
- `[ 1 ] [ "cleanup boom" error ] finally` → error contains `cleanup boom`, stack `[1]`
- `123 [ drop drop ] [ "cleanup boom" error ] finally` → error contains `cleanup boom`, stack `[123]`

## Why this matters

The older corpus already covered the sibling rule that when cleanup succeeds after
a **body** failure, `ensure` / `finally` rethrow the original body error with the
post-cleanup stack. The missing portability question was the other branch: what
happens when cleanup throws first?

Pinning that down in JSON matters for future Python/Rust/WASM hosts because it
prevents a subtle family of mismatches:

- incorrectly preserving the original body error instead of the cleanup error
- incorrectly running cleanup on the wrong visible stack shape
- incorrectly flattening the visible stack when cleanup throws

The practical result is small but leverage-heavy: future hosts can now replay the
full tiny `ensure` / `finally` precedence story from JSON alone instead of
inferring the last branch from stdlib comments or Python-only tests.
