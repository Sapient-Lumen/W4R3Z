# Rev743 — `s-format` format-plan preflight hygiene

The `s-format` hostcall consumes an explicit number of data arguments below the
public format tail:

```text
... "fmt" n s-format
```

Rev742 made one arity edge visible by checking that `n` data cells exist before
popping them.  One adjacent trust edge remained: once enough data cells existed,
the formatter still popped them before it discovered malformed format strings or
a mismatch between `n` and the number of real format conversions.

For example, these caller bugs used to remove the visible formatter data before
raising an error:

```text
1 "%q" 1 format
1 "%" 1 format
1 "%d %d" 1 format
1 2 "%d" 2 format
```

Rev743 keeps the change narrow.  After `s-format` pops and validates the public
`fmt n` control tail, it scans the format plan before consuming any data cells:

- `%%` is a literal percent and consumes no argument;
- `%s` and `%d` are the only active conversions;
- trailing `%` still reports `s-format: trailing %`;
- unknown conversions still report `s-format: unknown specifier %x`;
- too few declared arguments still report `s-format: not enough arguments`;
- too many declared arguments still report `s-format: too many arguments`.

The successful formatting path is unchanged.  The point is only to make
formatter-plan mistakes fail at the formatter boundary while leaving the
caller's declared data arguments untouched for inspection/recovery.
