# rev0889 research record

## Primary-source constraints used

The accepted-session and migration work was reviewed against primary protocol,
library, kernel, and database documentation rather than inferred solely from
local tests.

### SQLite transaction and migration authority

- `BEGIN IMMEDIATE` starts a write transaction immediately and can fail with
  `SQLITE_BUSY` when another writer already owns the database:
  https://sqlite.org/lang_transaction.html
- SQLite's atomic-commit design is the basis for treating the v2 metadata-table
  replacement and v3 metadata insertion as one all-or-nothing database change:
  https://sqlite.org/atomiccommit.html
- `sqlite3_set_authorizer()` is invoked while statements are prepared and can
  deny an operation. Rev0889 uses that mechanism only as deterministic test
  fault injection after schema replacement and before the v3 metadata insert:
  https://sqlite.org/c3ref/set_authorizer.html

The compiled rollback test is the cloudtainer evidence for this exact build. The
documentation constrains the design but does not substitute for runtime proof or
power-loss testing on every filesystem.

### TLS and socket lifetime authority

- TLS 1.3 closure alerts and `close_notify` semantics:
  https://datatracker.ietf.org/doc/html/rfc8446#section-6.1
- OpenSSL nonblocking server-handshake behavior:
  https://docs.openssl.org/3.5/man3/SSL_accept/
- OpenSSL same-thread/no-intervening-call requirements for `SSL_get_error()`:
  https://docs.openssl.org/3.5/man3/SSL_get_error/
- OpenSSL shutdown and close-notify behavior:
  https://docs.openssl.org/3.5/man3/SSL_shutdown/
- Linux atomic accept flags and inherited descriptor policy:
  https://man7.org/linux/man-pages/man2/accept.2.html
- Linux polling semantics and advisory readiness:
  https://man7.org/linux/man-pages/man2/poll.2.html

These sources support the separation implemented here: local application
terminal state is not rewritten by later shutdown diagnostics, readiness does
not prove protocol progress, and an accepted descriptor is born nonblocking and
close-on-exec rather than repaired after a race window.

## Speculative design conclusions

1. A useful per-principal quota cannot safely be keyed only by transient actor
   epoch. It needs a versioned membership principal with explicit rotation,
   revocation, and recovery semantics. Rev0889's `device_id` aggregation is a
   bounded intermediate defense, not that final identity model.
2. Reclaiming retained payloads merely because they are old would destroy exact
   duplicate reconciliation and audit evidence. Safe reclamation needs causal
   stability, a checkpoint/compaction authority, and an explicit full-rejoin
   rule for replicas excluded from the stable frontier.
3. The full-history file-effect owner should remain an oracle. A production
   owner should add indexed counters and reservations, then be continuously
   differentially tested against the oracle rather than replacing it in-place.
4. Quotas alone do not provide fairness. A protected reserve, bounded
   per-principal reservations, scheduler policy, dead-letter lifecycle, and
   operator-visible pressure evidence are separate authority decisions.
5. The project name still overstates implemented privacy. Current work protects
   authenticated convergence and receiver effects; it does not yet establish
   anonymity, unlinkability, endpoint hiding, or traffic-analysis resistance.
