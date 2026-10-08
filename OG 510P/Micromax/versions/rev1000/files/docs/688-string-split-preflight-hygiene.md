# Rev747 — `s-split` argument-preflight hygiene

The `s-split` hostcall turns a string into parts:

```text
source delimiter s-split
```

Rev745 and rev746 made the neighboring `s-join` and `s-replace` helpers more
inspectable by validating their public argument shapes before consuming them.
One adjacent split seam remained.  `s-split` still used the simple pop-then-check
shape:

1. pop the delimiter as a string;
2. pop the source as a string;
3. split the source, with an empty delimiter producing one-character parts.

That meant direct hostcall bugs could erase the evidence needed to debug them.
For example, a bad source could leave the stack empty after a generic
`Expected str, got int`, and a bad delimiter could consume the delimiter while
leaving only the source behind.

Rev747 keeps the change narrow and hostcall-local.  `s-split` now peeks at the
public `( source delimiter -- parts )` shape, checks that both values are
strings, and only then consumes them.  It also reports an explicit
`s-split: not enough arguments` diagnostic for underfilled direct hostcall
invocations.

Successful behavior is unchanged:

```text
"a,b" "," s-split   \ -> ["a", "b"]
"ab" "" s-split     \ -> ["a", "b"]
```

Failure paths are more honest:

- a non-string source reports `s-split: source must be str, got ...`;
- a non-string delimiter reports `s-split: delimiter must be str, got ...`;
- too few public arguments report `s-split: not enough arguments`;
- those failures leave the original split request available for inspection or
  recovery.

The goal matches the rev745/rev746 cleanup: string transformation helpers should
fail at their own boundary without erasing the caller data that explains the
failure.
