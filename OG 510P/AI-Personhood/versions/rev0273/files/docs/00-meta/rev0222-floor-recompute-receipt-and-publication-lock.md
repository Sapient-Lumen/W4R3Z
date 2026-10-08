# rev0222 floor recompute receipt and publication lock

rev0222 closes the last live-floor overclaim seam in the current first-real-artifact route: after quorum participation, the computed floor snapshot itself must not become a writable ledger, stale rollback surface, or partial-quorum reliance upgrade.

The new `live-receipt-floor-recompute-receipt` is a publication gate. It hashes the computed snapshot, compares it to a fresh `tools/compute_live_receipt_floor.py` replay, checks failed-gate summaries, checks manual override/stale quorum flags, and confirms that cross-critical quorum and reliance posture match the recomputed required-class vector.

This receipt still has no direct floor effect. It can publish a zero/stayed snapshot, or class-local evidence as stayed, but it cannot increment the floor by itself and cannot upgrade reliance unless every required live class survives recomputation.

The concrete waste corrected here is late-stage ambiguity: previous gates made upstream evidence hard to launder, but the publication surface still relied too much on trusting the computed snapshot as already safe. The new receipt makes the last step auditable and hash-bound.

Validation surfaces added in this revision are `tools/prepare_live_receipt_floor_recompute_receipt.py`, `tools/audit_live_receipt_floor_recompute_receipt.py`, `schemas/live-receipt-floor-recompute-receipt.schema.json`, and `examples/live-receipt-floor-recompute-receipt-rev0222-zero-floor-stayed.json`.
