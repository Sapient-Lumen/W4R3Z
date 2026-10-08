# Evidence migration audit — rev0069

rev0068 identified the byte problem. rev0069 turns it into a concrete dependency audit.

`src/muc5/evidence_index.py` scans bulky evidence files over 1 MiB, hashes them, counts rows where practical, classifies their kind, searches source/scripts/tests/docs/data for live references, and records compact derivatives. `scripts/run_rev0069_evidence_index.py` emits:

```text
data/rev0069_evidence_index.json
data/rev0069_evidence_index.csv
```

## Measured result

The scan found 78 bulky evidence files totaling 844.324 MiB:

```text
cpp_transition_table: 34 files, 718,221,428 bytes
replay_jsonl:         36 files,  57,394,359 bytes
segment_table:         2 files,  31,623,838 bytes
trace_row_table:       3 files,   3,803,789 bytes
training_dataset:      3 files,  74,294,385 bytes
```

The important result is not the byte count; it is the blocker count:

```text
blocked_by_live_reference: 75 files, 881,031,295 bytes
evidence_archive_candidate: 3 files,   4,306,504 bytes
```

Most of the large evidence cannot be safely removed yet because current scripts, tests, docs, or audit surfaces still name the raw paths directly. The next migration step is therefore not deletion. It is to redirect historical audits to compact derivatives plus content-addressed evidence-index records.

## Refactor implication

This explains why previous retention policy stayed aspirational. The cube does not merely carry old evidence; its audit and documentation surfaces still depend on many old raw filenames. A safe migration must first make raw-path references go through an index contract.
