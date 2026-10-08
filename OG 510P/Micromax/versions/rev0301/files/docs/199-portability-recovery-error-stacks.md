# Rev257: portability follow-up for recovery helpers that mutate the stack before rethrow

This revision does two related things for the portability story:

1. it teaches the JSON portability runner that an expected-error case may also
   pin down the **post-error stack**
2. it uses that slightly richer contract to make a few already-tested recovery
   helpers replayable from JSON alone

The specific Micromax helpers pinned down here are:

```forth
: try?    ( ..a q -- ..a ..b flag )   catch 0= ;
: try     ( ..a body handler -- ..b ) ... ;
: ensure  ( ..a body cleanup -- ..b ) ... ;
: finally ( ..a body cleanup -- ..b ) ensure ;
```

Why this is worth doing:

- current Factor docs still present `recover` and `cleanup` as distinct error-
  handling tools, and the current pitfalls guide explicitly warns that cleanup-
  style code is the right place when you need post-error cleanup plus rethrow
  rather than silent recovery
- Micromax already had honest Python tests for these behaviors, but the older
  JSON corpus could only assert **success stacks** or **error substrings**
- that meant a real portable contract — “cleanup ran, left data behind, and the
  original error still escaped” — was stranded in Python-only tests instead of
  being replayable by future Rust/WASM hosts

The JSON portability corpus now also includes:

- `stdlib-try-question-success-returns-result-and-flag`
- `stdlib-try-success-ignores-handler`
- `stdlib-ensure-failure-reraises-after-cleanup`
- `stdlib-finally-failure-reraises-after-cleanup`

Focused examples:

- `[ 1 2 + ] try?` -> `3 1`
- `1 [ 2 + ] [ drop drop 0 ] try` -> `3`
- `123 [ drop drop ] [ 999 ] ensure` -> error contains `Stack underflow`, stack
  left behind is `123 999`
- `123 [ drop drop ] [ 999 ] finally` -> error contains `Stack underflow`, stack
  left behind is `123 999`

That gives future hosts one more small but realistic recovery contract: cleanup
combinators can both mutate the visible stack and still rethrow the original
failure, and the portability corpus can now express that directly instead of
forcing hand ports to rediscover it from Python tests.
