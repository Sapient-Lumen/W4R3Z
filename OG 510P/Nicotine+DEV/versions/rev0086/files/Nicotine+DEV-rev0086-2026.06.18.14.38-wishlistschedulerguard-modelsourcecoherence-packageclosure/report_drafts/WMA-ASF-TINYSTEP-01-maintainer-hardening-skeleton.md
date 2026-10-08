# WMA-ASF-TINYSTEP-01 maintainer hardening skeleton

## Summary

The WMA/ASF metadata parser accepts nonzero ASF object sizes smaller than the 24-byte ASF object header. For unknown object ids, the parser consumes the header and then seeks by `object_size - header_len`. An under-header size such as `8` therefore creates overlapping/tiny-step parsing instead of advancing by at least one full object header.

## Current-behavior witness

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q   maintainer_artifacts/wma-asf-tinystep-01/test_wma_asf_tinystep_reproducer.py
```

Expected current behavior in archived lanes:

```text
github-tag-3.3.10:   3 passed
github-branch-3.3.x: 3 passed
github-branch-master: 3 passed
```

## Suggested fixed-behavior goals

```text
- Treat 24 bytes as the minimum ASF object size before object-specific parsing.
- Reject or stop on 0 < object_size < 24 before any relative seek.
- Preserve the existing behavior for object_size == 0 and object_size > filesize,
  unless maintainers prefer raising a parse error instead of breaking.
- Add tests for zero, under-header nonzero sizes, exact-minimum unknown objects,
  oversized objects, truncated headers, and normal WMA metadata.
```

## Non-goals

```text
- No claim of code execution.
- No claim of peer-only remote exploitability.
- No claim that this supersedes broader source or ASF parser-class public overlap.
- No PR patch included.
```
