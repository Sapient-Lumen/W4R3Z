# Rev745 — `s-join` argument-preflight hygiene

The `s-join` hostcall consumes a list of string parts plus a delimiter:

```text
parts "delim" s-join
```

Before rev745, the implementation followed the simplest pop-then-check shape:

1. pop the delimiter;
2. pop the list;
3. walk the list and reject the first non-string element.

That meant a caller bug such as a mixed list lost exactly the evidence needed to
debug it:

```text
["a", 2, "c"] "," s-join
```

A direct embedding saw `s-join: expected list of str, got int`, but the offending
list and delimiter had already been consumed.  This was adjacent to the formatter
work in rev742 through rev744, where `s-format` learned to diagnose arity, plan,
and `%d` data-conversion errors without eating declared formatter data.

Rev745 keeps the change narrow and hostcall-local.  `s-join` now peeks at the
public `(parts delim -- s)` argument shape, validates that the delimiter is a
string, validates that the parts object is a list, and validates every element
before deleting the two public arguments.  Only a fully valid input is consumed
and replaced by the joined output.

The successful path is unchanged:

```text
["a", "b"] "-" s-join  \ -> "a-b"
```

The failure path is more honest:

- a mixed list still reports `s-join: expected list of str, got ...`;
- a non-list parts value still reports a join-specific type error;
- a non-string delimiter reports `s-join: delimiter must be str, got ...`;
- those failures leave the original parts/delimiter data available for
  inspection or recovery.

The point is not to make `s-join` more permissive.  It is to make join data
errors fail at the join boundary without destroying the caller's evidence.
