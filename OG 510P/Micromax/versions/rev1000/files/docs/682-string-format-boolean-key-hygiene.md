# Rev741 — `s-format` boolean map-key representation hygiene

Rev740 made the `s-format` `%s` representation path honest for direct Python
boolean sentinels used as values.  A direct hostcall caller could no longer
format `True` as integer-looking text `1`, and nested list/map values used the
same explicit witness:

```text
<bool True>
<bool False>
```

One adjacent representation leak remained in dictionary keys.  The map renderer
kept keys JSON-ish by stringifying them before quoting the key label.  That is
fine for ordinary portable keys, but for direct Python booleans it produced:

```text
{"True": "yes", "False": "no"}
```

That output hides the same host-language truth sentinel that rev740 exposed for
values.  It also makes a boolean key look like ordinary string text that a
portable script might have pushed deliberately.

Rev741 keeps the fix narrow:

- boolean dictionary keys render as quoted explicit witnesses, for example
  `"<bool True>"` and `"<bool False>"`;
- ordinary string and integer keys keep the existing JSON-ish stringified-key
  surface;
- nested boolean values still use the rev740 `<bool ...>` representation.

This is a presentation-boundary fix only.  It does not add a new map type or
change VM dictionary semantics; it simply keeps direct host booleans visible
when `%s` renders arbitrary host-provided data.
