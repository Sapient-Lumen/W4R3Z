# Rev679 / rev738 — string replace empty-needle hygiene

Micromax's reference string hostcalls include `s-replace`:

- stack effect: `( s old new -- s2 )`;
- intended behavior: replace visible occurrences of `old` inside `s` with `new`.

Before rev738 the helper delegated directly to Python's `str.replace`.  Python
allows an empty `old` needle and treats it as a request to insert at every
zero-width boundary:

```text
"ab" "" "X" s-replace  \ before rev738: "XaXbX"
```

That behavior is powerful, but it is not a visible substring replacement.  It
matches the same class of invisible insertion points that the editor
`replace`/`replaceall` and VM `re-sub`/`re-subn` paths already reject.  Keeping
`old == ""` implicit in `s-replace` would let string scripts produce a bulk edit
with no positive-width match and no clear caller intent.

Rev738 made the semantic boundary narrow and explicit, and rev746 later made
the failure path inspectable:

- `old == ""` fails as `s-replace: empty search`;
- as of rev746, `s-replace` validates `source`, `old`, and `new` before
  consuming them, so empty-search and type failures leave the original rewrite
  data on the stack for direct hostcall callers;
- positive-width replacements are unchanged;
- `s-index`, `s-contains?`, and `s-split` keep their existing empty-string
  semantics because they are search/split helpers, not bulk rewrite helpers.

The trust rule matches the replacement-family work from rev719 through rev733:
rewrite helpers should operate on visible spans that were actually found, not on
implicit zero-width boundaries.
