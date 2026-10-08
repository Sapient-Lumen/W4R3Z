# Rev742 — `s-format` argument-underflow hygiene

The `s-format` hostcall takes a variable number of data arguments followed by a
format string and an explicit argument count:

```text
... "fmt" n s-format
```

Earlier string-hostcall trust slices tightened the integer count slot and the
formatter's boolean representation behavior.  One arity edge remained: if `n`
claimed more data cells than were actually present, the implementation tried to
pop those cells immediately.  That leaked the VM's low-level `Stack underflow`
diagnostic and consumed any available formatter data before failing.

For example, this caller bug:

```text
1 "%d %d" 2 format
```

now fails at the formatter boundary as:

```text
s-format: not enough arguments
```

Rev742 keeps the change narrow:

- `s-format` still pops and validates the public `fmt n` control tail first;
- negative counts and boolean count sentinels keep their existing diagnostics;
- the formatter checks that `n` data cells are available before consuming them;
- valid counted formatting is unchanged.

This is mostly a diagnostic and trust-boundary cleanup.  Variable-arity hostcalls
should explain their own arity mismatches instead of exposing an accidental lower
level stack-pop failure.
