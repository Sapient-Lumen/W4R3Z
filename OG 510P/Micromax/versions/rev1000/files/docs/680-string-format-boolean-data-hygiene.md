# String format boolean data hygiene (rev739)

Micromax's `s-format` hostcall accepts a tiny printf-like surface:

```forth
10 "%d" 1 s-format  \ "10"
```

Rev737 already tightened the control slot: direct hostcall callers cannot pass
Python `False` / `True` as the `n` argument count. One adjacent data-slot leak
remained in `%d`: Python booleans subclass `int`, so the formatter used to accept
`False` as `0` and `True` as `1` when a direct embedding put those objects on the
VM stack.

That is a trust problem for the same reason as rev737's count/index boundary:
portable Micromax values spell integers as explicit integer cells, not host-language
truth-value sentinels. A direct embedding should not get an extra Python-only way
to produce integer formatter data.

Rev739 keeps the rule narrow:

- `%d` rejects Python `False` / `True` as formatter data;
- ordinary integer `0`, `1`, and larger integers still format normally;
- string-to-int `%d` coercion is unchanged;
- `%s` remains the general string representation surface for non-string values; rev740 makes Python boolean sentinels explicit there instead of displaying them as integer-looking text.

The diagnostic is intentionally local and action-specific:

```text
s-format: %d expects int, got boolean True
```

This keeps the reference hostcall dialect portable while preserving normal VM-facing
integer formatting behavior.
