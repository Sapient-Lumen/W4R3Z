# PROTO-FRAME-PARSER-01 coherence/refactor — rev0025

## Canonical packet

```text
PROTO-FRAME-PARSER-01 = U-137 + U-175
```

This packet should stay a parser-boundary regression-hardening packet, not a scattered set of per-message findings.

## Folded items

### U-137

Length-prefixed string/bytes field truncation. Verified in final string fields for server, peer, and distributed messages plus the low-level bytes helper.

### U-175

Framed server/peer/distributed messages do not reject declared sizes smaller than their mandatory message-code fields before consuming part of the input buffer.

## Keep separate

```text
U-164 / F-CONN-FRAME-01:
  fixed-width F-message partial-fragment behavior. Similar parser theme, but different frame format and transfer consequence.

U-02:
  maximum uncompressed message size / decompression budgets. Maximum-size caps are not a substitute for minimum-length and declared-field validation.

U-154:
  embedded distributed-message parser isolation. Related, but specifically about parser exception isolation and embedded-message routing.

U-111 / U-92:
  list/count mismatch crash behavior in specific server messages. These should be tested later as structured-count invariants, not merged into U-137/U-175.

U-199:
  file-attribute count semantic budget. This is a semantic field-count cap, not malformed-short-frame validation.
```

## Fix-composability notes

A central parser policy should provide reusable helpers:

```text
require_available(offset, needed, message_len, context)
unpack_string_strict(...)
unpack_bytes_strict(...)
validate_frame_minimum(conn_type, msg_size, required_code_bytes)
finish_message_strict(offset, message_len, allow_trailing=False)
```

This avoids a future state where server messages reject short strings, peer messages accept them, and distributed messages drift again.

## Strict-lane decision

Do not promote in rev0025. The packet is verified and useful, but the consequence is malformed-message hardening and parser correctness. It is better as a maintainer regression-hardening packet unless a future harness proves a specific high-impact state mutation or peer-only consequence.
