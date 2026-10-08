# rev0008 worklog

## Main result

U-123 crossed the missing proof gate from rev0007. The new local harness exercises the duplicate-token path through:

```text
TransferRequest -> FileTransferInit -> stale first timeout -> progress callback -> close callback
```

across all three source lanes. The duplicate-token path leaves the second transfer in `Transferring` with an F socket and file handle, but without an `active_users[username][token]` mapping after the first stale timer fires. Progress and close callbacks for that second session are ignored.

## Strict document change

`docs/HIGH-PRIORITY-HIGH-QUALITY.md` now has **1 promoted report-candidate**: U-123.

This is not marked production-ready disclosure text. It still needs private/maintainer overlap checking and a cleaner unit-test packaging pass.

## Cube audit/refactor performed

The transfer lifecycle cluster was pruned:

- U-123 is now TR-01a lead.
- U-169 and U-170 are supporting context/tests, not standalone first reports.
- U-158 and U-166 remain separate because their protocol messages are not the same token-bearing session path.
- U-269 and U-270 are next-candidate lanes, not part of this report.

Machine-readable refactor: `data/rev0008_transfer_cluster_refactor.csv`.

## Files added

```text
docs/U123-SOCKET-LIMBO-STRICT-CANDIDATE.md
docs/AUDITED-BACKLOG-REV0008-ADDENDUM.md
evidence/rev0008-u123-socket-limbo-probe.md
evidence/rev0008-u123-socket-limbo-probe.jsonl
evidence/rev0008-u123-source-trace.md
evidence/rev0008-web-public-overlap-u123-refresh.md
data/rev0008_ranked_audit_queue.csv
data/rev0008_u123_socket_limbo_probe_summary.csv
data/rev0008_transfer_cluster_refactor.csv
data/rev0008_strict_promotions.csv
tools/probe_rev0008_u123_socket_limbo.py
```

## Next work

Stay narrow one more turn if possible: package U-123 as a maintainer-grade unit test/report skeleton. After that, choose either U-269 for transfer-lifecycle continuation or U-270 for search-response parser/lifetime proof.
