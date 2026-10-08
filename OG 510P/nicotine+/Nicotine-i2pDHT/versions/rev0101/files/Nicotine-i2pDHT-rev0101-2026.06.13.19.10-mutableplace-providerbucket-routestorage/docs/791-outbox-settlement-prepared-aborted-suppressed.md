# Outbox settlement prepared / aborted / suppressed

`outboxsettlement.py` joins the active summary outbox / publish fence path with the folded summarysettlement / publicledger / redactiongc branchlet.

It rejects component digest drift, contradiction drops, hard-negative pressure, replay, rollback, same-sequence fork, previous-link mismatch, and low family/path diversity.

Keywords: outbox settlement, outboxsettlement, summarysendcanary, summarysettlement, publicledger, redactiongc.
