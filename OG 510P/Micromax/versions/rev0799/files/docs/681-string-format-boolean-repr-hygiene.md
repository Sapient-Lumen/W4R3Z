# String format boolean representation hygiene (rev740)

Rev739 closed the most visible `s-format` boolean data leak: `%d` no longer
accepts direct Python `False` / `True` values as integer formatter data. One
adjacent representation leak remained in `%s`.

`%s` is deliberately the permissive formatter surface: it can render strings,
integers, lists, maps, cells, quotations, and other host objects into stable text.
Before rev740, that path used Python's ordinary `isinstance(x, int)` check before
considering host-language sentinels. Because `bool` subclasses `int`, a direct
hostcall caller could still get this misleading output:

```text
True  -> "1"
False -> "0"
```

That is not a portable Micromax value boundary. VM scripts can still spell
integer data as real integer cells, but a host embedding should not get an
extra truth-value spelling that looks identical in formatted output.

Rev740 keeps `%s` permissive while making this boundary visible:

- `True` renders as `<bool True>`;
- `False` renders as `<bool False>`;
- nested list/map rendering uses the same explicit witness;
- ordinary integers still render as integer text.

The behavior is intentionally representation-only. `%d` remains stricter and
continues to reject Python booleans because `%d` promises integer data. `%s` can
still display arbitrary direct host values; it just no longer lets host booleans
masquerade as `0` / `1`.
