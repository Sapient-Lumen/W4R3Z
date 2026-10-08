# AnonSync rev0877 primary-source research

Primary sources constrained the implementation and its deliberate nonclaims.
They do not replace the checked-in runtime tests.

- OpenSSL `SSL_new()`/reference counting: an `SSL` object is reference counted;
  `SSL_up_ref()` increments that count and `SSL_free()` decrements it. OpenSSL
  also recommends a fresh `SSL` handle for each connection where practical.
  <https://docs.openssl.org/3.5/man3/SSL_new/>
- OpenSSL `SSL_clear()`: an `SSL` object can be reset and reused, while reuse can
  retain settings and is unsafe when the application assumes immutable session
  identity. A service authority therefore cannot be a static snapshot detached
  from current live-session revalidation.
  <https://docs.openssl.org/3.5/man3/SSL_clear/>
- OpenSSL `SSL_write()`: after WANT_READ/WANT_WRITE, retry semantics require the
  same arguments unless partial-write/moving-buffer modes change the contract.
  An interrupted application record therefore needs an explicit write state
  machine; rev0877's blocking one-shot adapter poisons instead of pretending a
  safe retry frontier.
  <https://docs.openssl.org/3.5/man3/SSL_write/>
- OpenSSL `SSL_get_error()`: it must be called in the same thread as the I/O call
  and with no intervening OpenSSL operation that changes the error queue. This
  supports exact thread ownership and immediate error classification.
  <https://docs.openssl.org/3.5/man3/SSL_get_error/>
- OpenSSL `SSL_read()`: reads may return WANT_READ or WANT_WRITE and can require
  bidirectional readiness. A future event-loop adapter must own both readiness
  directions and preserve exact record progress.
  <https://docs.openssl.org/3.5/man3/SSL_read/>
- RFC 9266 defines the TLS 1.3 `tls-exporter` channel binding using
  `EXPORTER-Channel-Binding`, empty context, and 32 output bytes. The value binds
  application evidence to one TLS connection but is not a secret key and does
  not replace membership or durable receipt authentication.
  <https://www.rfc-editor.org/rfc/rfc9266>
- RFC 8446 defines TLS 1.3 connection and exporter machinery, not AnonSync's
  framing, replay, durable cutpoints, membership, retry, or effect semantics.
  <https://www.rfc-editor.org/rfc/rfc8446>

## Design implications and speculation

The next transport should be a single-thread-owned connection/session actor that
owns one fresh `SSL` object, socket, authenticated policy snapshot, framed-record
state machine, poison/close state, deadlines, and reconnect classification.
External aliases should not be able to mutate its OpenSSL state.

Before reconnect sophistication, AnonSync needs a durable membership owner with
actor/key epochs, enrollment, rotation, revocation, rollback protection, and a
monotonic policy generation. A channel authority should eventually bind that
generation or consult a revocation observer.

An effect-terminal receipt should be independently verifiable after the TLS
session disappears. A likely canonical object would bind folder, operation,
payload commitment, exact effect identity, receiver actor/key epoch, membership
policy generation, durable effect cutpoint, and request/attempt identity, then
be signed or MACed under an explicitly durable receiver authority.
