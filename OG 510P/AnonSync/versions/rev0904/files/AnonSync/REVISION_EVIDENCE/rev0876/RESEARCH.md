# AnonSync rev0876 primary-source research

Research was used to constrain the implementation and its nonclaims; it is not
substitute authority for the checked-in runtime tests.

- RFC 9266, *Channel Bindings for TLS 1.3*: exporter-based channel binding uses
  `EXPORTER-Channel-Binding`, an empty context, and application-selected output
  length. <https://datatracker.ietf.org/doc/rfc9266/>
- OpenSSL peer verification: verification mode must be configured; a result
  value alone does not prove peer verification was requested.
  <https://docs.openssl.org/3.5/man3/SSL_CTX_set_verify/>
- OpenSSL exporter API: exporter output is derived from the negotiated TLS
  session and label/context inputs.
  <https://docs.openssl.org/3.4/man3/SSL_export_keying_material/>
- OpenSSL `SSL_clear()`: an `SSL` object may be reset and reused, which means an
  application capability must not silently survive a later handshake.
  <https://docs.openssl.org/3.3/man3/SSL_clear/>
- RFC 8446, TLS 1.3: early data has weaker replay guarantees; rev0876 disables
  0-RTT and rejects resumed sessions rather than claiming those semantics.
  <https://datatracker.ietf.org/doc/html/rfc8446>
- RFC 7301, ALPN: the selected application protocol is negotiated inside the TLS
  handshake. Rev0876 requires one exact private protocol identifier.
  <https://datatracker.ietf.org/doc/html/rfc7301>
- SQLite isolation: a successful `BEGIN IMMEDIATE` obtains the write
  transaction used for the receiver admission/cutpoint serialization point.
  <https://sqlite.org/isolation.html>
- RFC 9420, Messaging Layer Security: MLS may later inform multi-device group
  key epochs, but it assumes separate authentication/delivery services and does
  not replace durable application effect semantics.
  <https://datatracker.ietf.org/doc/rfc9420/>

## Design implication

Authentication of a live TLS channel is necessary but not sufficient for an
independently durable receipt. The next effect-terminal receipt should bind the
operation, payload commitment, receiver actor/key epoch, exact published effect
and cutpoint, and should be signed or MACed under an explicitly durable
receiver authority so it remains verifiable after the transport session ends.
