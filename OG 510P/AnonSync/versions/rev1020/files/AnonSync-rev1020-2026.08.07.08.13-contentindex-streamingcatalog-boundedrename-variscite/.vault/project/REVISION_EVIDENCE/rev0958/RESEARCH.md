# Rev0958 research notes

The implementation decision was checked against primary documentation for three
adjacent systems. These are design analogies, not compatibility or equivalence
claims.

- PostgreSQL documents the write-ahead ordering principle: durable change
  records precede data-page writes so recovery has an earlier persistent fact.
  Rev0958 applies only the ordering lesson—durable scrub intent precedes the
  first scrub read—and does not claim transactional WAL semantics.
  https://www.postgresql.org/docs/current/wal-intro.html
- Btrfs documents scrub as an online read-and-verify operation over allocated
  data and metadata, with repair only when another good copy exists. AnonSync's
  payload scrub is narrower: digest-named regular files, no filesystem repair,
  and bounded application-level continuation.
  https://btrfs.readthedocs.io/en/latest/btrfs-scrub.html
- OpenZFS exposes scrub checkpointing/pausing parameters and persistent scan
  progress. That supports treating scan continuation as durable scheduling state,
  while not treating the checkpoint itself as proof that bytes are good.
  https://openzfs.github.io/openzfs-docs/man/master/4/zfs.4.html

The shared inference is conservative: optional integrity work may be delayed,
but any durable state left before a crash must make the next authority decision
safer rather than merely reschedule the same optional work. The `Prepared`
record is therefore a restart revocation fence for one active digest, not an
assertion that the payload is valid or corrupt.
