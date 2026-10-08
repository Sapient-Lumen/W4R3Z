# rev0887 protocol research and speculation

The transport profile continues to reject resumed sessions and disable TLS 1.3 early data. RFC 8446 section 8 treats 0-RTT application data as replayable and places anti-replay responsibility on the application. Receiver idempotency is defense in depth, not permission to silently enable early data.

OpenSSL documents that `SSL_read_ex` and `SSL_write_ex` retries after `SSL_ERROR_WANT_READ` or `SSL_ERROR_WANT_WRITE` must preserve the operation and arguments. Rev0887 therefore retains heap-stable continuation state and enters the shared poll owner only after a genuine WANT. The record-I/O policy audit also freezes observable `SSL*` options/modes/shutdown policy at authentication and re-proves them at operation frontiers; it explicitly cannot detect a transient mutate-and-restore race without exclusive raw-SSL ownership.

Primary references:

- RFC 8446 section 8, 0-RTT and anti-replay: https://www.rfc-editor.org/rfc/rfc8446#section-8
- OpenSSL 3.5 early-data API: https://docs.openssl.org/3.5/man3/SSL_read_early_data/
- OpenSSL `SSL_read_ex`: https://docs.openssl.org/3.5/man3/SSL_read/
- OpenSSL `SSL_write_ex`: https://docs.openssl.org/3.5/man3/SSL_write/

Speculation for the next design cycle:

1. Keep one application conversation per authenticated channel until explicit conversation identifiers and durable sequencing exist. Connection reuse is cheaper, but implicit stream position after an abandoned response is not acceptable authority.
2. Add a resumable 8-byte prefix continuation or a typed post-effect transport-failure outcome before building a long-running event loop. This preserves exact diagnostics after durable publication without pretending the peer received anything.
3. Add per-peer and per-folder quotas, staged-payload expiry, fairness, and dead-letter ownership before opening a listener to untrusted or merely buggy peers. Bounded frame size alone does not bound aggregate retained work.
4. Do not switch transport families merely to obtain multiplexing. QUIC or another substrate may improve head-of-line behavior, but it does not solve canonical evidence, receiver effect idempotency, terminal receipts, membership epochs, or retry authority.
5. Preserve the current full-history owners as differential oracles. Optimize with an indexed owner only when generated histories, crash frontiers, and restart tests demonstrate the same canonical digests and cutpoints.
