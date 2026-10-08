# Rev676 / rev735 — regex hostcall sentinel flag hygiene

Micromax's regex hostcalls document a tiny portable flag dialect:

- integer `0` means no flags;
- a string containing `i`, `m`, and/or `s` enables ignorecase, multiline, and
  dotall;
- whitespace inside the string is ignored for readability.

Rev729 rejected non-zero Python integer flags so host-specific bits such as
`re.DEBUG` could not leak through the VM boundary. A couple of embedding-only
sentinel values still remained: Python `None` and `False` could be treated as no
flags, while `True` was rejected only because it normalized to integer `1`.
Those values are convenient in Python code, but they are not part of the
VM-facing contract and future hosts cannot necessarily spell or distinguish them
the same way.

Rev735 keeps the fix small:

- `parse_re_flags(None)` now raises a stable flag-dialect error;
- `parse_re_flags(False)` and `parse_re_flags(True)` now raise stable boolean
  flag-dialect errors instead of relying on Python's `bool`/`int` relationship;
- direct hostcall invocations with those sentinel values are normalized as
  `invalid regex: flags must be 0 or a string of ims flags, ...`;
- integer `0`, `""`, whitespace-only strings, and documented `i`/`m`/`s`
  strings keep their existing behavior;
- non-zero integer flags and unknown string flags keep their rev729 behavior.

The trust rule is simple: the regex hostcall flag slot should accept only values
that Micromax scripts and non-Python ports can name portably.
