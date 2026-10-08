# Auditcompact refute/fork preservation

`auditcompact.py` is a second compaction lane beside `witnesscompact.py`. It works closer to the raw `auditquorum.py` receipts: the compact bundle may summarize positive receipts, but it must retain the receipt digests that carry refute evidence, watch evidence, and same-family fork evidence.

The risky guess is simple: compaction can become moderation amnesia. A node that keeps only the pleasant summary of an audit window can later convince itself that a stale public bridge record, redress gap, or payload fork never happened.

The executable pressure in rev0049 is:

- accepted positive receipts may be summarized;
- redress-gap, stale-public-record, payload-mismatch, or non-accepted receipts must remain as refute digests;
- same-family conflicting payload receipts must remain as fork-evidence digests;
- bundle replay, rollback, same-sequence fork, previous-link mismatch, component digest drift, and cross-scope/request/payload drift quarantine the compact result.

This is not a transparency log. It is local evidence retention before public side-effect dry-runs and outbox staging.
