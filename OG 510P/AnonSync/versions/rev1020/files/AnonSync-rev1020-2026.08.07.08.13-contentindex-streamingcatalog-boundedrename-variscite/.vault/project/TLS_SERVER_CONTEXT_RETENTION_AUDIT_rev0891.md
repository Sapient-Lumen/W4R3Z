# TLS server context retention audit — rev0891

## Scope

The rev0890 accepted-session API borrowed a raw `SSL_CTX*`. The caller was
required by comment to keep it alive and stable while the server allocated an
`SSL` object, waited for a peer, completed the handshake, and ran one durable
application conversation. That was a lifetime contract without a C++ owner.

Rev0891 adds a move-only retained reference:

```text
SyncReplicaFileTlsServerContext
```

The factory validates the pointer, calls `SSL_CTX_up_ref`, and returns a wrapper
whose destructor calls `SSL_CTX_free`. The one-shot server consumes this wrapper
by value. A moved-from wrapper is inactive and rejected.

## Why this matters

OpenSSL documents `SSL_CTX` as reference counted: `SSL_CTX_up_ref` increments
that count and `SSL_CTX_free` decrements it, freeing resources when the count
reaches zero. Borrowing a raw pointer did not mechanically ensure that the
caller's original reference survived until `SSL_new` or the end of the call.
The wrapper closes that use-after-free class without inventing another lifetime
protocol.

The wrapper does not serialize mutation. OpenSSL also documents that an
`SSL_CTX` should not be changed after it has been used to create `SSL` objects
or concurrently from multiple threads because the implementation does not
provide serialization for those cases. Rev0891 repeats this as an explicit
nonclaim. The caller must treat the configured context as immutable while any
retained reference or derived connection is live.

## Accepted-session ordering

The server now performs:

1. require a nonempty diagnostic label;
2. require an active retained context;
3. require an active durable membership authority;
4. prove membership/service identity before accept;
5. bind exact membership generation and digests into the result;
6. allocate `SSL` from the retained context;
7. set server role;
8. spend listener authority and accept one child;
9. bind the accepted descriptor;
10. complete bounded TLS authentication;
11. resolve exact durable membership;
12. run one receiver conversation; and
13. close the accepted child unconditionally.

Allocating `SSL` before `accept4` is intentional. Provider or allocator failure
cannot consume one queued peer before an SSL owner exists. The retained context
itself is acquired even earlier, at the caller-visible factory boundary.

## Ownership matrix

| Object | Owner during call | Terminal action |
|---|---|---|
| listening descriptor | caller | never closed by session |
| listener capability | caller, borrowed by reference | remains reusable if active |
| `SSL_CTX` reference | move-only server-context wrapper | `SSL_CTX_free` decrement |
| accepted descriptor | internal scope owner | one non-retried `close` |
| `SSL` | internal unique owner | `SSL_free` |
| membership authority | consumed move-only value | scope destruction |
| authenticated channel/session | nested exclusive owners | cannot escape call |

The accepted descriptor remains bound to its exact Linux socket lifetime and
`O_NONBLOCK`/`FD_CLOEXEC` policy. Context retention does not weaken those
existing proofs.

## Compiled coverage

The transport test uses static assertions and runtime checks to require:

- no default construction;
- no copying;
- nothrow move construction and assignment;
- null-context rejection;
- moved-from wrapper rejection;
- normal server use through a retained reference; and
- survival of the server call after a dedicated fixture destroys the caller's
  original context reference before `SSL_new`, then reaches a normal bounded
  accept-timeout result through the retained generation.

The source audit requires the `SSL_CTX_up_ref`/`SSL_CTX_free` pair, retained
context by-value server API, pre-accept `SSL_new`, and absence of the retired raw
context parameter.

## Online primary source

OpenSSL documentation accessed on 2026-07-23:

- `SSL_CTX_new` / `SSL_CTX_up_ref`, including reference-count and mutation rules:
  https://docs.openssl.org/3.6/man3/SSL_CTX_new/
- `SSL_CTX_free`, including reference-count decrement behavior:
  https://docs.openssl.org/3.4/man3/SSL_CTX_free/

## Remaining gaps

A production listener should own an immutable configured context generation,
not accept arbitrary retained wrappers at every call. Rotation should publish a
new context generation while old generations drain, with exact certificate,
trust-store, protocol-option, callback, and key evidence. The current wrapper
proves lifetime only. It does not digest context configuration, prevent caller
mutation, attest provider state, isolate OpenSSL callbacks, or establish key-
material provenance.

## Nonclaims

Rev0891 does not claim immutable OpenSSL internals, concurrent-mutation safety,
provider isolation, callback purity, key custody, certificate rotation policy,
live context revocation, process isolation, or a production accept pool. It
closes the narrower raw-pointer lifetime hole with OpenSSL's documented
reference-count ownership.
