# Candidate artifact origin and revalidation — rev0086

The current Search Again prototype was created in rev0085 and its bytes remain
unchanged in rev0086. Earlier candidate validation required the *current*
revision string to appear in the artifact path. That encouraged copying
identical patches to a new filename on every rollover, weakening rather than
strengthening lineage.

Rev0086 separates two facts:

```text
origin revision
  encoded by the artifact ID and immutable path

validated revision
  listed in validated_revisions and backed by current evidence records
```

The rev0085 Search Again artifact therefore remains at its immutable rev0085
path while `rev0086` is added to its validation history. The validator still
rejects a mutable `current.patch` alias because the origin revision must match
the artifact ID and path. It now rejects current use when the live revision is
missing from `validated_revisions`, rather than demanding duplicate bytes.
