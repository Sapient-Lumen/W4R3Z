# Evidence derivative bridge — rev0071

rev0070 exposed two bulky raw files that were blocked only because they lacked compact derivatives:

```text
rev0021 ranker training dataset raw table   15,585,040 bytes
rev0021 C++ batch trace-row raw table        1,322,823 bytes
```

rev0071 adds `src/muc5/evidence_derivatives.py` and `scripts/run_rev0071_evidence_derivatives.py` to profile those files into compact summaries:

```text
data/rev0021_ranker_summary.json
data/rev0021_cpp_batch_summary.json
```

The ranker derivative records row count, unique decisions, chosen-action distribution, offered-action distribution, action-count shape, source checksum, and chosen-row feature means. The C++ batch derivative records trace count, support status, C++ match status, fingerprint status, action-kind counts, source checksum, and skipped-reason counts.

## Measured result

```text
ranker rows profiled:           33,184
ranker unique decisions:        16,085
trace rows profiled:             8,898
trace C++ mismatch rows:             0
source bytes profiled:      16,907,863
```

The evidence index now classifies both former missing-derivative blockers as archive candidates. The linked core still keeps the raw files in rev0071, but the migration state is better:

```text
rev0070 active blockers:             73
rev0070 missing-derivative blockers:  2
rev0070 archive candidates:           3

rev0071 active blockers:             73
rev0071 missing-derivative blockers:  0
rev0071 archive candidates:           5
rev0071 archive-candidate bytes:      21,214,367
```

This is byte-movement preparation, not deletion. The next safe migration pass can move the five archive candidates into an immutable evidence bundle once an external content-addressed location is assigned.
