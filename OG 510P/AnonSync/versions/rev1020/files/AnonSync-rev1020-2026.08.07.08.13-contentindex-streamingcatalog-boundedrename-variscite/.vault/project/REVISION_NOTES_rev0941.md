# AnonSync rev0941

Mission: replace Resilio Sync with a practical C++ folder-sync product whose
shipping peer service supports direct, Tor, and I2P routes.

## Product change

- Protocol v2 carries exact contiguous payload ranges instead of rejecting every
  file above the inline payload ceiling.
- Maximum admitted file size is 64 MiB; one wire range is at most 4 MiB.
- Partial prefixes survive client/server restart and continue from the exact
  durable offset.
- Complete SHA-256 verification precedes payload publication and remote operation
  admission.
- One verified source payload snapshot is retained only for the authenticated
  serve session, avoiding a full private-store scan on every continuation.

## Correctness corrections

- Incomplete payload durability no longer advances shared operation history.
- A mixed response page retains the cursor for its completed operation prefix
  when a later large file needs another range.
- TLS handshake-expiry tests no longer treat a diagnostic attempt count as
  authentication authority at an absolute deadline.

## Explicit limits

This is sequential range resume, not block reuse or delta synchronization. A
one-byte edit still retransmits the full file. Receiver staging still performs
broad private-store reconciliation. Retained ranges and payloads have no
reachability/garbage-collection owner. The current protocol is pre-alpha and is
not wire-compatible with protocol v1.

Archive: `AnonSync-rev0941-2026.07.29.06.03-rangeresume-payloadfirst-prefixcursor-rosecurrent.zip`
