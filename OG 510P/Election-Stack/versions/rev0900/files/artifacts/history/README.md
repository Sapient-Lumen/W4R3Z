# Retrievable compacted history

`rev0894-superseded-v892-v893-artifacts.tar.gz` retains the exact pre-compaction bytes behind the v892-v893 historical JSON and source-byte checksum/workpack stubs shipped in this carrier. The bundle is deterministic, release-manifest governed, and not current election evidence.

Recover and verify one original object without extracting arbitrary archive paths:

```sh
python3 tools/retrieve_compacted_history.py \
  --path artifacts/reports/source-byte-cache-batch-ingest-rev0893.json \
  --output /tmp/source-byte-cache-batch-ingest-rev0893.json
```

The same command works for compacted historical `.sha256` paths. Each stub binds the bundle member, original byte count, and SHA-256. `artifacts/reports/rev0894-retrievable-history-compaction.json` records scope and metrics.
