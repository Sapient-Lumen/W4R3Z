# Tier-2 inline caching and dict-version (rev19)

Micromax tier-2 bytecode preserves **late-binding** semantics: `EXEC_NAME` resolves names through the current search order at *runtime*.

To keep compiled code fast without drifting semantically, tier-2 uses a tiny **per-call-site inline cache**.

## dict-version

The VM maintains a single integer:

- `dict_version` — bumped whenever:
  - any word is added/redefined in any wordlist
  - the search order changes

A new core word exposes it for tooling:

- `dict-version ( -- n )`

## WordRef call-site cache

When compiling tokens into bytecode, each `EXEC_NAME` instruction stores a `WordRef` object rather than a raw string name.

A `WordRef` caches:

- the last resolved word (or a cached miss)
- the `dict_version` at which it was resolved

At runtime:

- if `dict_version` is unchanged, the cached resolution is reused
- otherwise, the name is resolved again through the current search order

This keeps semantics identical to tier-1 while making the common case (no dictionary/search-order changes) cheaper.

## Porting note (Rust/WASM)

In Rust, `WordRef` can become a small struct stored in bytecode:

- interned name id (or pointer into a constant pool)
- cached xt index/pointer (optional)
- cached `dict_version`

Even the simplest implementation can keep the same behavior: validate cached version, otherwise fall back to dictionary lookup.
