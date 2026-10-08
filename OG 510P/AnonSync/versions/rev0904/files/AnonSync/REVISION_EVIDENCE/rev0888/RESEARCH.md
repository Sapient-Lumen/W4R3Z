# rev0888 protocol research and speculation

## OpenSSL retry identity

OpenSSL 3.5 documents that after `SSL_write_ex` returns `SSL_ERROR_WANT_READ` or `SSL_ERROR_WANT_WRITE`, the write must be repeated with the same arguments unless moving-write-buffer mode is enabled. It also documents partial-write behavior separately through `SSL_MODE_ENABLE_PARTIAL_WRITE`.

Rev0888 keeps the exact pending phase, pointer, offset, and length in one heap-stable owner regardless of the configured modes. Prefix and body share that owner. A successful operation may advance its owned cutpoint; a WANT does not. This avoids depending on caller-buffer lifetime or wrapper object address.

Primary references:

- OpenSSL 3.5 `SSL_write_ex`: https://docs.openssl.org/3.5/man3/SSL_write/
- OpenSSL 3.5 mode controls: https://docs.openssl.org/3.5/man3/SSL_CTX_set_mode/

## Atomic wait predicate

The C++ atomic-wait rules are value based: `wait(old)` may block while the atomic still equals `old`, and notification is not a durable queued ticket. A worker that initializes `old` from already-published work can therefore lose that work. Rev0888's test helper uses requested and completed ticket state instead of treating notification as authority.

Primary reference:

- Current C++ draft, atomic waiting: https://eel.is/c++draft/thread#atomics.wait

## Design speculation

1. Keep the guarded sender prefix adapter fail-closed until the outbox has an explicit durable `PreparedButPrefixPending` state. Polling while holding a SQLite writer is worse than reconnecting and exact-releasing a provably pre-prefix attempt.
2. Build one long-running listener/session owner before adding more operation types. It should authenticate membership epoch, invoke exactly one bounded conversation, close or discard terminal streams, and persist typed retry/dead-letter state.
3. Treat per-peer and per-folder capacity as authority, not tuning. Bound staged bytes, staged age, concurrent conversations, retry age/count, and dead-letter retention before exposing remote acceptance.
4. Keep the current full-history owners as correctness and repair oracles. Introduce indexed hot-path owners only behind differential tests that compare canonical state after generated delivery, crash, retry, and rejoin schedules.
5. Do not infer anonymity from encrypted payloads. Endpoint, timing, size, relay, membership, and retry metadata require a separate threat model and explicit mechanisms.

These references constrain design choices but do not prove this implementation, kernel scheduling, OpenSSL internals, peer behavior, durable effects, package integrity, or privacy properties.
