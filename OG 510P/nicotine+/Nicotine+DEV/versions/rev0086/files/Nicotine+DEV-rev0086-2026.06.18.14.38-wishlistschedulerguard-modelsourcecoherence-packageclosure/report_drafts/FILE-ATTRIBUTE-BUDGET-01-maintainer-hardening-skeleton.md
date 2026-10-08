# FILE-ATTRIBUTE-BUDGET-01 maintainer hardening skeleton

## Summary

Search, browse, and folder-content result parsers currently walk a peer-supplied per-file attribute count. Nicotine+ only retains a small known set of file attributes, but the parser loop itself is not bounded to that semantic budget.

## Current-behavior witness

```bash
PYTHONPATH=/path/to/source-tree pytest -q \
  maintainer_artifacts/file-attribute-budget-01/test_file_attribute_budget_reproducer.py
```

Expected current behavior in archived lanes:

```text
github-tag-3.3.10:   3 passed
github-branch-3.3.x: 3 passed
github-branch-master: 3 passed
```

## Suggested fixed-behavior goals

```text
- Define a small semantic cap for file-attribute pairs per file.
- Enforce it in the shared file-attribute unpacker.
- Preserve known attributes used by current clients: bitrate, length/duration,
  vbr, sample rate, and bit depth.
- Decide and document duplicate valid-attribute behavior.
- Decide whether excess pairs are skipped boundedly or reject the message as malformed.
- Keep broad decompressed-message byte limits as an outer resource bound.
- Add regression tests for FileSearchResponse, SharedFileListResponse, and
  FolderContentsResponse.
```

## Non-goals

```text
- No claim of code execution.
- No claim that broad uncompressed-message caps are absent.
- No PR patch included.
- No recommendation to break ordinary clients that send known audio metadata.
```
