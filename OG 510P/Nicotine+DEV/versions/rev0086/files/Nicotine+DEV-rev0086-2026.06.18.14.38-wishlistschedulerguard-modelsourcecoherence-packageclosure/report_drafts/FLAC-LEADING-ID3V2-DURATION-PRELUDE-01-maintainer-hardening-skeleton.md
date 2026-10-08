# Maintainer hardening skeleton — FLAC leading ID3v2 duration-only prelude

Status: **not production-ready disclosure text**.

## Summary

When the share scanner asks TinyTag for `.flac` duration metadata with `tags=False`, stable/3.3.x TinyTag still parses a leading ID3v2 prelude using an ID3 helper whose tag parsing remains enabled. A mapped `TIT2` frame can be read, decoded, and applied to the FLAC tag before native STREAMINFO duration extraction. Master propagates `tags=False` and avoids applying/reading the mapped text frame body, but still traverses the leading ID3v2 envelope.

## Suggested hardening

```text
- In stable/3.3.x Flac.load(), propagate tags=False into the leading ID3 helper,
  or skip/seek over the leading ID3v2 envelope when only duration is requested.
- Preserve duration extraction for FLAC files with a leading ID3v2 envelope.
- Avoid applying ID3 fields and avoid decoding large ID3v2 text frames when
  tags=False.
- Add regression tests for tags=False and tags=True leading-ID3 FLAC paths.
```

## Evidence in cube

```text
maintainer_artifacts/flac-leading-id3v2-duration-prelude-01/test_flac_leading_id3v2_duration_prelude_reproducer.py
evidence/rev0034-flac-leading-id3v2-duration-prelude-pytest-run.txt
evidence/rev0034-flac-leading-id3v2-duration-prelude-source-trace.md
```
