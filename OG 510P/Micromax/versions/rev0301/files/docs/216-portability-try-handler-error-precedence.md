# Rev274: replayable handler-error precedence for `try` / `recover`

Rev274 extends the JSON portability corpus with one more small but real recovery
contract: if the recovery **handler** quotation itself fails, that newer
handler error should be the error that escapes, while any stack effects the
handler already performed stay visible.

Micromax already behaved this way in the reference VM because `try` is a tiny
stdlib combinator layered on `catch`, `last-error`, and a normal `call` into
the handler quotation. But until this rev, that rule only lived implicitly in
runtime behavior and ad hoc local experiments.

The new replayable cases are:

- `stdlib-try-handler-error-wins-on-failure`
- `stdlib-recover-handler-error-wins-on-failure`

Focused examples:

- `123 [ drop drop ] [ drop drop 999 "handler boom" error ] try`
  - raises `handler boom`
  - leaves stack `123 999`
- `123 [ drop drop ] [ drop drop 999 "handler boom" error ] recover`
  - raises `handler boom`
  - leaves stack `123 999`

That shape matters for future Python/Rust/WASM hosts because it makes two tiny
truths replayable from JSON alone:

1. the original body failure really was handed off to the recovery quotation
2. if that quotation fails after doing some work, its newer failure replaces
   the old one instead of being hidden behind it

This keeps the Micromax portability corpus aligned with the existing stdlib
story:

- `try` / `recover` are **recovery** combinators
- `ensure` / `finally` are **cleanup + rethrow** combinators
- later failures inside the quoted helper that actually runs are the ones that
  escape

Focused coverage lives in:

- `tests/test_portability_suite.py`
- `tests/test_try_combinator.py`
- `tests/test_vm_rev11.py`
- `tests/test_mxcontext.py`
