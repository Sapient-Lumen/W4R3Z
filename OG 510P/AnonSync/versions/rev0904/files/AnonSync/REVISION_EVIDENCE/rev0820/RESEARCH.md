# Rev0820 research notes

The implementation and tests are grounded in current upstream SQLite behavior;
these references do not turn local observations into universal filesystem or
portability claims.

- `sqlite3_deserialize()` reopens a schema as an in-memory database. With
  `SQLITE_DESERIALIZE_FREEONCLOSE`, SQLite frees the buffer when the connection
  closes and also frees it when deserialization itself fails. The documentation
  explicitly warns that a WAL-mode image may deserialize successfully but fail
  with `SQLITE_CANTOPEN` when used:
  <https://www.sqlite.org/c3ref/deserialize.html>
- SQLite's database header stores file-format write and read versions at offsets
  18 and 19. Current rollback-journal databases use 1/1 and WAL databases use
  2/2. WAL and rollback journals are part of database state during recovery and
  cannot be treated as unrelated residue:
  <https://www.sqlite.org/fileformat.html>
- `PRAGMA journal_mode=DELETE` requests rollback-journal mode and returns the
  mode actually selected. WAL mode is persistent across connections. Rev0820
  therefore canonicalizes the producer through SQLite and verifies the returned
  mode instead of rewriting authenticated header bytes in the verifier:
  <https://www.sqlite.org/pragma.html#pragma_journal_mode>
- SQLite's online backup API promises a consistent snapshot when the operation
  completes, but it copies database pages, including page-1 format state. The
  empirical rev0820 probe demonstrates that a destination may inherit a 2/2 WAL
  header and then create WAL sidecars until explicitly canonicalized:
  <https://www.sqlite.org/backup.html>

## Design inference

A path string, a prior `stat`, and a successful close do not grant authority to
delete whatever later occupies that name. The smallest robust correction for
verification is to stop owning cleanup names: acquire exact bytes through a
retained source descriptor, prove their geometry and digest, and make all later
SQLite views process-local.

The verifier deliberately rejects 2/2 rather than applying SQLite's documented
byte-patching workaround. The bytes may be signed or manifest-bound; changing
header bytes inside verification would make the parser consume a different
object from the one whose digest authorized the transition. Producer-side
canonicalization preserves the evidence relation.

## Speculation and next experiments

The resident image should eventually cross into a disposable hostile-database
worker with CPU, address-space, descriptor, wall-clock, syscall, and filesystem
limits. A typed result should return to the long-lived process rather than a
live SQLite handle. Differential tests should cover multiple bundled SQLite
versions because deserialize, PRAGMA, and backup edge behavior can evolve.

Resident capture also creates bounded memory amplification: one sealed image
plus one SQLite-owned copy per open connection. A future worker protocol could
use one connection per request and a strict concurrent-byte budget. Secure
memory erasure is not claimed; ordinary allocator and SQLite copies can retain
payload remnants until reuse.
