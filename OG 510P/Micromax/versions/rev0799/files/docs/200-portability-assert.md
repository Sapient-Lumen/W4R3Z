# Rev258: portability follow-up for `assert`

This revision does **not** add a new VM primitive. Instead, it makes the last
still-unpinned boot-stdlib helper explicitly replayable from the JSON
portability corpus:

```forth
: assert ( flag "msg" -- ) swap 0= [ error ] [ drop ] if ;
```

Why this is worth pinning down:

- current small/embedded Forth projects still commonly describe the path from a
  tiny kernel to a more usable system as “define richer words on top of the base
  system”, which fits Micromax's current source-visible-stdlib preference
- current Factor testing docs still split “quotation produces these outputs” from
  “quotation must fail”, which matches Micromax's current portability style of
  pinning down both success and failure contracts as tiny replayable cases
- Micromax already had the needed kernel pieces (`swap`, `0=`, `if`, `error`), so
  keeping `assert` source-visible matches the repo's current preference for a
  tiny inspectable VM plus replayable stdlib contracts
- future Python/Rust/WASM hosts should not have to infer whether a failing
  `assert` consumes only its own flag/message pair while preserving older stack
  items from `core.mx` or ad hoc tests during bring-up

The JSON portability corpus now includes:

- `stdlib-assert-true-drops-message-and-keeps-outer-stack`
- `stdlib-assert-false-throws-message-and-preserves-outer-stack`

Focused examples:

- `123 1 "ok" assert` -> `123`
- `123 0 "boom" assert` -> error contains `boom`, stack left behind is `123`

That gives future hosts one more tiny but realistic failure-path contract:
`assert` is still just stdlib sugar over `error`, but its visible stack behavior
is now replayable from JSON instead of being rediscovered from source.
