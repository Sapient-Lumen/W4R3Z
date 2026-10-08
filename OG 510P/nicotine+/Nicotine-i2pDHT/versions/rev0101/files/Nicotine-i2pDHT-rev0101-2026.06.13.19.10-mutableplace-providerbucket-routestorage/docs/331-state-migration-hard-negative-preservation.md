# State migration hard-negative preservation

`migrationlane.py` treats local upgrade/restart migration as a protocol boundary.

Hard negative state is not a cache. It is local memory that protects future decisions:

```text
provider_false
tombstone
revocation
key_crisis
witness_fork
```

A migration manifest signs:

```text
from_schema -> to_schema
input state digest
output state digest
preserved hard-negative digests
dropped soft count
generation / sequence / previous manifest
validity window
```

The assessment checks bad signatures, expiry, input/output digest mismatch, dropped hard negatives, scope widening, sequence rollback, soft-drop count mismatch, replayed manifests, and same-sequence manifest forks.

The strongest local rule:

```text
If a migration forgets why we distrusted something, the migration is a protocol attack surface.
```
