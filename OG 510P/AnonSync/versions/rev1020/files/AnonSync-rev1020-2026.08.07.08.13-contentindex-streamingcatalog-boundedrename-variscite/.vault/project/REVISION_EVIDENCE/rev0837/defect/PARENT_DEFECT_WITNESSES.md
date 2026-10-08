# Exact rev0836 bounded-reader defect witnesses

`parent_helper.slice.cpp` is the exact helper body extracted from the sealed
rev0836 parent; its SHA-256 is recorded independently. The witness translation
unit embeds that body without changing it and supplies two tests around it.

- `parent-prefix.log`: a deterministic linker-wrap script reports an initial
  regular-file size of three, returns `abc`, and records one simulated trailing
  byte. The helper returns success after exactly one three-byte read. It never
  asks for EOF and therefore accepts an incomplete prefix as a complete
  observation.
- `parent-fifo.log`: a no-writer FIFO is passed to the exact helper under an
  external one-second `timeout`. Exit 124 proves the helper remained blocked in
  its pathname open before it could inspect and reject the non-regular object.

The compiled witness binary is intentionally excluded from the release. The
source, exact helper slice, hashes, and observations are sufficient to rebuild
and inspect the reproduction.
