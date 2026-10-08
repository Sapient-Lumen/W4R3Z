# OGG-CONTINUATION-ACCUM-01 maintainer hardening skeleton

## Summary

The Ogg metadata parser assembles continued packets by appending full-lacing page bodies until a lacing value below 255 terminates the packet. A scanned Ogg-like file can therefore make the share metadata parser materialize a very large first packet before metadata classification or rejection.

## Current-behavior witness

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q \
  maintainer_artifacts/ogg-continuation-accum-01/test_ogg_continuation_accumulation_reproducer.py
```

Expected current behavior in archived lanes:

```text
github-tag-3.3.10:   3 passed
github-branch-3.3.x: 3 passed
github-branch-master: 3 passed
```

## Suggested fixed-behavior goals

```text
- Pick a local maximum Ogg metadata packet budget suitable for share scanning.
- Count bytes before appending continuation bodies to previous_page/packet_data.
- Stop, skip, or raise a parse error once the budget is exceeded.
- Preserve ordinary small Vorbis/Opus/Speex/FLAC-in-Ogg files.
- Add tests for normal headers, exact-budget packets, over-budget packets, and
  continuation chains across multiple pages.
```

## Non-goals

```text
- No claim of code execution.
- No claim of peer-only remote exploitability.
- No claim that Ogg page-spanning packets are invalid.
- No claim that network-message-size caps address this local parser path.
- No PR patch included.
```
