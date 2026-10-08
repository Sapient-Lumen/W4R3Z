# PROTO-FRAME-PARSER-01 maintainer hardening skeleton

Status: **not production-ready disclosure text**. This is a maintainer-oriented regression-hardening skeleton.

## Summary

Current protocol parsing accepts some malformed short fields/frames instead of failing closed:

- final length-prefixed string/bytes fields can be accepted when the declared length exceeds the remaining payload;
- server/peer/distributed frame loops can advance buffers when the declared length is smaller than the mandatory message-code field.

## Current-behavior witness

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q \
  maintainer_artifacts/proto-frame-parser-01/test_protocol_frame_and_truncated_field_reproducer.py
```

Expected current result for archived lanes:

```text
github-tag-3.3.10:   13 passed
github-branch-3.3.x: 13 passed
github-branch-master: 13 passed
```

## Impact framing

Malformed-message/parser robustness and fail-closed behavior. Do not overstate as code execution or file disclosure.

## Suggested fix shape

- Add strict availability checks to length-prefixed field helpers.
- Reject server/peer frames where `msg_size < 4` before reading/using the message code or advancing the buffer.
- Reject peer-init/distributed frames where `msg_size < 1` before reading/using the message code or advancing the buffer.
- Keep maximum-message-size caps separate from minimum-length and declared-field validation.
- Preserve valid empty strings/bytes and valid empty-message classes.

## Regression cases

- Valid empty string and valid empty bytes fields still parse.
- Declared nonzero string length with fewer remaining bytes rejects.
- Declared nonzero bytes length with fewer remaining bytes rejects.
- Server/peer `msg_size` values 0, 1, 2, 3 reject/fail closed.
- Distributed/peer-init `msg_size` value 0 rejects/fail closed.
- Existing large-message caps still close over-budget payloads.
