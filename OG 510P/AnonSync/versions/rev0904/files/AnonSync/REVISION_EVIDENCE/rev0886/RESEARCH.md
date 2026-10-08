# rev0886 primary-source research and inference

The detailed source applications and rejected alternatives are in `TLS_TRANSPORT_ANCHOR_AUTHORITY_AUDIT_rev0886.md`, `TLS_INCREMENTAL_WRITE_AUDIT_rev0886.md`, and `TLS_DUPLEX_POLL_AUTHORITY_AUDIT_rev0886.md`. The load-bearing primary references are:

- OpenSSL `SSL_get_error`: https://docs.openssl.org/3.5/man3/SSL_get_error/
- OpenSSL `SSL_write_ex`: https://docs.openssl.org/3.5/man3/SSL_write/
- OpenSSL mode controls: https://docs.openssl.org/3.5/man3/SSL_CTX_set_mode/
- OpenSSL BIO ownership and chain release: https://docs.openssl.org/3.5/man3/BIO_free_all/
- Linux `poll(2)`: https://man7.org/linux/man-pages/man2/poll.2.html
- POSIX `poll`: https://pubs.opengroup.org/onlinepubs/9799919799/functions/poll.html

The implementation inference is deliberately narrower than those specifications. OpenSSL requires same-thread immediate error classification and exact retry arguments for a pending operation; Linux/POSIX readiness is advisory and may be interrupted. Therefore AnonSync retains the exact continuation, uses readiness only to authorize one attempted advance, re-proves the target across every retry of the wait syscall, and leaves TLS close/error meaning to OpenSSL after the transport's own session/BIO/socket re-attestation.

These sources do not prove this code, scheduler behavior, kernel correctness, absence of races, peer receipt, durability, product integration, or privacy. Runtime tests, sanitizers, source audits, and package hashes are separate evidence classes with explicit limits.
