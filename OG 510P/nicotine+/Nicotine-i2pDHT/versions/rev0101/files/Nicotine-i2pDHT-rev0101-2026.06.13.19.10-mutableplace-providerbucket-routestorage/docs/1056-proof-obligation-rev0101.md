# Proof obligation rev0101

The local obligation is to show that three accepted rev0100 records can move into local state only through typed rev0101 gates:

- mutable record -> mutable observation placement, not latestness
- provider record -> bounded provider-index bucket, not content truth
- routing record -> I2P route storage/replacement cache, not routing authority

The tests pin acceptance and representative failure paths for tombstones, missing previous links, content-storage attempts, full buckets, replacement cache, and authority drift.
