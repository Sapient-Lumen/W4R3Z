# Audit quorum local receipts

`auditquorum.py` keeps quorum local. It is not consensus, not global reputation, and not DHT truth.

The receipts are scoped observations about a bridge shadow: publication observed, withdrawal observed, repair observed, stale public record, payload mismatch, or redress gap. The lane rejects stale public record receipts, payload mismatch receipts, replay, signature failure, scope/request drift, shadow digest drift, and one-family contradictions.

The design goal is to make public bridge visibility expensive enough to accept locally without creating a blessed oracle.
