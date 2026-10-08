# Rev678 / rev737 — string hostcall integer sentinel hygiene

Micromax's reference string hostcalls expose a small VM-facing helper surface:

- `s-slice` takes `( s start end -- s2 )`;
- `s-format` takes `( ... fmt n -- s )`.

Those control slots are integer counts or indexes. VM scripts spell them as
ordinary integers such as `0`, `1`, and `2`. Direct Python embeddings, however,
can place Python objects on the stack before invoking `hostcall`, and Python's
`bool` type is a subclass of `int`. Before rev737, that meant `False` and `True`
were silently accepted as integer control values.

That is a small portability leak: another host or port does not have a reason to
spell a string index or format-argument count as a truth value, and accepting it
can hide a caller bug at exactly the host boundary where Micromax wants values to
be explicit.

Rev737 keeps the fix narrow:

- `s-slice` rejects `False` / `True` as the start index;
- `s-slice` rejects `False` / `True` as the end index;
- `s-format` rejects `False` / `True` as the `n` argument count;
- ordinary integer `0`, `1`, and other integer counts/indexes keep working;
- `s-slice` boolean failures pop the full public slice argument shape before
  reporting the error, so direct hostcall callers do not keep stale slice
  arguments on the stack.

The trust rule is the same as the regex start/flag sentinel fixes: portable
hostcall control slots should accept values the VM contract can name directly,
not Python-specific convenience sentinels.
