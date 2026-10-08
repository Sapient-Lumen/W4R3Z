# Rev744 — `s-format` data-conversion preflight hygiene

The `s-format` hostcall consumes an explicit number of data arguments below the
public format tail:

```text
... "fmt" n s-format
```

Rev742 and rev743 made formatter arity and format-plan mistakes visible before
consuming those declared data cells.  One adjacent trust edge remained: after a
valid plan had been accepted, `%d` conversion errors still popped the declared
data before reporting the type problem.

For example, these caller bugs used to remove the value that explained the
failure:

```text
"not-an-int" "%d" 1 format
10 "bad" "%d %d" 2 format
```

Direct hostcall embeddings could hit the same edge with host-language values,
such as a Python boolean sentinel or unsupported object in a `%d` slot.

Rev744 keeps the change narrow.  After `s-format` pops and validates the public
`fmt n` control tail, it now peeks at the declared data cells, renders against
that snapshot, and only deletes those cells once the whole output string is known
to succeed.  If `%d` conversion fails, the public control tail has still been
consumed, but the declared formatter data remains on the stack for inspection or
recovery.

The successful formatting path is unchanged:

- `%s` still formats strings directly and uses the existing representation helper
  for non-strings;
- `%d` still accepts ordinary integers and decimal strings;
- `%%` still produces a literal percent;
- Python boolean `%d` data still fails with the explicit boolean diagnostic.

The point is only to keep formatter type errors honest: failing conversions
should not eat the evidence needed to understand the failure.
