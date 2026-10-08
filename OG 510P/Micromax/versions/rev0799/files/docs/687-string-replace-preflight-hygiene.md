# Rev746 — `s-replace` argument-preflight hygiene

The `s-replace` hostcall rewrites visible string spans:

```text
source old new s-replace
```

Rev738 already made the most important semantic boundary explicit: an empty
`old` needle is not a real substring replacement, so it fails as
`s-replace: empty search` instead of delegating to Python's zero-width insertion
behavior.

One adjacent trust seam remained.  The implementation still followed the simple
pop-then-check shape:

1. pop `new`;
2. pop `old`;
3. pop `source`;
4. then reject `old == ""` or let `pop_str()` report generic type failures.

That meant direct hostcall failures destroyed the exact rewrite request that
needed inspection.  A caller could see `s-replace: empty search` or `Expected str,
got int`, but the source/old/new evidence was already gone.

Rev746 keeps the change narrow and hostcall-local.  `s-replace` now peeks at the
public `( source old new -- result )` shape, validates that all three arguments
are strings, validates that `old` is non-empty, and only then consumes the three
arguments and pushes the replacement result.

Successful replacements are unchanged:

```text
"abab" "a" "x" s-replace  \ -> "xbxb"
```

Failure paths are more inspectable:

- a non-string source reports `s-replace: source must be str, got ...`;
- a non-string old needle reports `s-replace: old must be str, got ...`;
- a non-string new value reports `s-replace: new must be str, got ...`;
- an empty old needle still reports `s-replace: empty search`;
- those failures leave the original source/old/new data available for
  inspection or recovery.

The goal matches rev745's `s-join` cleanup: data-shape errors in string helpers
should fail at the helper boundary without erasing the evidence that explains
them.
