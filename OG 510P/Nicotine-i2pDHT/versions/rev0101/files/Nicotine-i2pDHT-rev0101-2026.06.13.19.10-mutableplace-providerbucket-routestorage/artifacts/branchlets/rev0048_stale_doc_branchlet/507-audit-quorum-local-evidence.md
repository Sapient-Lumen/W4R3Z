# Audit quorum as local evidence

`auditquorum.py` uses the word quorum cautiously. It is not consensus and not global truth. It is a local receipt set that can increase confidence in a bridge-shadow side effect only when receipts are fresh, scoped, diverse, and non-contradictory.

Audit receipts can observe publication, withdrawal, repair, stale public records, payload mismatch, or redress gaps. Payload mismatch and stale public records block the side effect. Redress gaps can turn acceptance into watch if local policy allows carrying that debt.

This keeps the garden-node rule intact: witnesses preserve evidence; they do not rule.
