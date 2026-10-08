# Proof obligation rev0073

The rev0073 proof obligation is intentionally local:

```text
summary receipt + import archive + lineage prune
  -> summary publication intent
  -> redaction witness receipts
  -> import-prune audit
```

The tests must show happy-path acceptance and rejection of raw leaks, digest drift, boundary drift, missing witness classes, and contradiction drops.
