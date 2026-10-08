# rev0064 — retrypublish-idempotencymesh-deliveryrepair

rev0064 starts at the next public-edge risk after late ACK / retry settlement / egress-journal compaction: a retry may look settled, but that does not mean another public publication is safe.

New surfaces:

- `retrypublish.py` stages retry or withdraw publication only after retry settlement and egress journal agree.
- `idempotencymesh.py` keeps original ACK, retry settlement, retry publication, and contradiction evidence in one local lineage.
- `deliveryrepairmesh.py` requires remote witness pressure before duplicate-delivery ambiguity is treated as benign or repairable.
- `retrypublishfold.py` audits the rev0064 path and preserves rev0063 `lateackfold` predecessor history.

Strong sentence: **idempotency is not magic; duplicate delivery is sticky evidence until local lineage, publication staging, remote witness, and repair state agree at one exact boundary.**
