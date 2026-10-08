# rev0890 research record

## Question investigated

After rev0889 established a one-shot accepted TLS session, the remaining
membership boundary still accepted arbitrary application code after TLS
authentication and while a live accepted socket and `SSL` object were owned by
the server path. The research question was whether certificate-path validation
alone should be treated as application actor authorization, and whether a
post-handshake callback was an appropriate authority mechanism.

## Primary-source constraints

### OpenSSL peer verification and certificate ownership

OpenSSL 3.5 documents `SSL_CTX_set_verify()` as the mechanism that requests and
checks peer certificates according to configured verification mode. In server
mode, client-certificate requirements depend on flags and the configured trust
store. This is certificate-path verification, not an AnonSync actor-membership
policy.

OpenSSL also documents that obtaining a peer certificate does not itself report
whether verification succeeded; verification state must be checked separately,
and reference ownership must be respected.

- https://docs.openssl.org/3.5/man3/SSL_CTX_set_verify/
- https://docs.openssl.org/3.5/man3/SSL_get_peer_certificate/

### Application authorization remains application-specific

RFC 5280 explains that a certification path accepted by the baseline path
validation algorithm may still be unsuitable for a particular application and
that applications can impose further restrictions. That supports the explicit
separation used in rev0890: TLS trust establishes a verified key/certificate
context, while an immutable AnonSync membership snapshot maps the exact SPKI
digest to an actor for one receiver service.

- https://www.rfc-editor.org/info/rfc5280

RFC 9001 likewise makes peer-authentication requirements dependent on the
application protocol and deployment. It does not turn possession of any valid
certificate into application membership.

- https://www.rfc-editor.org/info/rfc9001

RFC 9525 distinguishes service-identity matching from certification-path
validity. The rev0890 snapshot therefore binds folder ID and local actor in
addition to the remote SPKI-to-actor mapping; using a snapshot for another
receiver service fails before listener authority is spent.

- https://www.rfc-editor.org/info/rfc9525

Sources were accessed in the cloudtainer on 2026-07-23.

## Design conclusions

1. The post-handshake AnonSync membership decision should be a total lookup in a
   validated immutable value, not arbitrary caller code with reentrant access to
   process state while a live child socket is in scope.
2. Removing the application membership callback does not make the TLS handshake
   callback-free. OpenSSL callbacks configured on the caller-owned `SSL_CTX`
   remain part of the caller's trust stack and are outside this narrower claim.
3. A sorted, domain-separated digest gives stable evidence for the exact
   snapshot used, but a caller-provided positive `policy_epoch` is labeling—not
   freshness, monotonicity, provenance, or rollback protection.
4. Multiple exact SPKI pins may map to one actor to permit bounded rotation
   overlap. One SPKI mapping to multiple actors is ambiguous and is rejected.
5. The next durable design needs a membership configuration owner with signed or
   otherwise authenticated updates, monotonic generation, prior-digest chaining,
   revocation, recovery, restart reconstruction, and explicit overlap policy.

## Speculation and remaining risk

An immutable in-process snapshot removes one dangerous reentrancy boundary but
does not protect against a hostile process that can mutate memory, replace the
`SSL_CTX`, or alter the executable. It also does not provide anonymity,
unlinkability, endpoint hiding, or traffic-analysis resistance.

The highest remaining arbitrary callback is payload acquisition. It is fenced
before SQLite writer and network-write frontiers and followed by channel and
exact-claim re-attestation, but its time and temporary-resource consumption are
unbounded while a durable outbox lease exists. A bounded content-addressed
payload handle or reader capability is the preferable production interface.
