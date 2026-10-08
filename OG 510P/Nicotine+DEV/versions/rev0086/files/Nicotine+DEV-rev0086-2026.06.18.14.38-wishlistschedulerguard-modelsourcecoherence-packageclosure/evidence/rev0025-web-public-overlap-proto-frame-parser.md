# rev0025 public-overlap search — PROTO-FRAME-PARSER-01

Date: 2026-06-13.

## Target

U-137 and U-175:

```text
U-137: Length-prefixed string/bytes fields accept truncated final payloads instead of rejecting malformed messages.
U-175: Server/peer/distributed framed messages do not reject declared lengths smaller than message-code fields.
```

## Searches captured

```text
site:github.com/nicotine-plus/nicotine-plus truncated length-prefixed string message malformed frame
site:github.com/nicotine-plus/nicotine-plus "unpack_string" "truncated"
site:github.com/nicotine-plus/nicotine-plus "message size" "smaller" "message code"
site:github.com/nicotine-plus/nicotine-plus "malformed" "PeerInit" "message"
site:github.com/nicotine-plus/nicotine-plus "MAX_INCOMING_MESSAGE_SIZE"
site:github.com/nicotine-plus/nicotine-plus "maximum uncompressed network message size"
```

Exact GitHub issue search pages captured no direct issue results for:

```text
"truncated" "unpack_string"
"message length" "message code"
"MAX_INCOMING_MESSAGE_SIZE"
```

## Overlap found

No direct public Nicotine+ issue was found for the exact U-137/U-175 combined invariant.

Public/upstream-adjacent context exists:

- The official protocol docs define string/byte fields as length-prefixed and define server-message frames as `uint32 length + uint32 code + contents`.
- 3.3.11 RC release notes mention maximum uncompressed network-message-size enforcement, which is adjacent parser hardening.
- Public issue/discussion history contains generic crash, connectivity, malformed metadata, and search-result load symptoms, but not a direct report of the short-declared-length / too-small-message-code invariant.

## Classification

```text
candidate no direct public match found / public-adjacent generic parser hardening
```

This should be retained as a verified audited-backlog maintainer packet, not a clean novelty or strict disclosure candidate.
