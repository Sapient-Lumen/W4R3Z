# rev0884 primary-source research, inference, and speculation

Research was checked online on 2026-07-22 against the OpenSSL 3.5 documentation
used by this cloudtainer; the observed runtime is OpenSSL 3.5.5.

## SSL_read / SSL_read_ex

Primary source: <https://docs.openssl.org/3.5/man3/SSL_read/>

OpenSSL documents that a nonblocking read may require either read or write
readiness and that a retryable operation must be repeated with the same
arguments. Applied inference: the output pointer and requested byte count are
part of the continuation identity. A public C++ wrapper may move only if the
actual application buffers supplied to OpenSSL remain at one stable address.

## SSL_get_error

Primary source: <https://docs.openssl.org/3.5/man3/SSL_get_error/>

The error classification depends on the exact preceding I/O call and the
thread-local OpenSSL error queue. Applied inference: clear the queue immediately
before one `SSL_read_ex` and call `SSL_get_error` immediately after a failed
result, on the same owner thread, without certificate/exporter or unrelated SSL
calls in between.

## SSL_pending

Primary source: <https://docs.openssl.org/3.5/man3/SSL_pending/>

`SSL_pending` reports already processed application bytes buffered in the SSL
object. It is not a complete socket-readiness oracle and may be zero while an
unprocessed TLS record is available. Applied inference: it cannot replace typed
WANT_READ/WANT_WRITE results or the external event loop.

## OpenSSL thread safety

Primary source: <https://docs.openssl.org/3.5/man7/openssl-threads/>

General library thread safety does not make one mutable object safe for
simultaneous arbitrary use. Applied inference: AnonSync should retain one
process/thread-affine owner and one channel-wide record reservation until it has
a separately reviewed serialized two-direction scheduler. Rejecting concurrent
full-duplex use is a throughput tradeoff, not a claim that TLS fundamentally
forbids it.

## Speculation and next experiments

The next useful abstraction is a bounded poll/epoll service, not another free
function. One connection owner should hold exactly one read continuation and at
most one write continuation, expose desired readiness, cap decoded-frame memory,
and forbid SQLite transactions while waiting for socket readiness. Complete
canonical messages should cross into durable receiver authority; partial TLS
record positions should not, because a dead TCP/TLS session cannot truthfully
resume at that byte offset.

A useful next adversarial matrix would combine socket readiness with durable
receiver cutpoints: peer close before and after canonical admission, duplicate
operation delivery on a fresh TLS session, crash before/after immutable staging,
rename and directory durability, terminal receipt byte frontiers, stale receipt
replay, and bounded queue pressure. Differential tests should continue to use
the full-history SQLite owner as the correctness oracle while an indexed
production owner is introduced.

The project name still exceeds its implemented privacy properties. TLS with
pinned identities provides authenticated channel confidentiality; it does not
provide anonymity, unlinkability, endpoint hiding, traffic-shape concealment, or
resistance to a global observer. Those properties require an explicit threat
model and separate protocol work rather than inference from encryption.
