# FLAC-STREAMINFO-BLOCK-BUDGET-01 maintainer hardening skeleton

## Summary

The FLAC duration parser reads the advertised STREAMINFO metadata-block payload with `fh.read(size)` before validating the fixed 34-byte STREAMINFO record. A malformed FLAC-like file can therefore make the local share metadata scanner materialize a bytes object matching the advertised STREAMINFO block length before duration parsing uses the fixed fields.

## Current-behavior witness

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q   maintainer_artifacts/flac-streaminfo-block-budget-01/test_flac_streaminfo_block_budget_reproducer.py
```

Expected current behavior in archived lanes:

```text
github-tag-3.3.10:   4 passed
github-branch-3.3.x: 4 passed
github-branch-master: 4 passed
```

## Suggested fixed-behavior goals

```text
- Validate native FLAC STREAMINFO advertised block length before reading payload
  bytes; exact length should be 34 bytes.
- Preserve ordinary exact-34-byte FLAC duration extraction.
- Reject or stop duration parsing for 33-byte, 35-byte, over-budget, and
  truncated STREAMINFO blocks before materializing large payloads.
- Keep variable-length FLAC metadata blocks on their own budget/streaming path.
- Add tests for exact, short, overlong, large, and truncated STREAMINFO cases.
```

## Non-goals

```text
- No claim of code execution.
- No claim of peer-only remote exploitability.
- No claim that all large FLAC metadata blocks are invalid.
- No claim that network-message-size caps address this local parser path.
- No PR patch included.
```
