# Redaction witness receipts

`redactionwitness.py` gives redaction its own evidence lane.

Witnesses can observe that boundary data was redacted, payload data was redacted, digest binding survived, contradiction memory survived, and the audience is scoped. They remain local evidence rather than global truth.

This intentionally avoids treating one accepted publication intent as proof that redaction was actually preserved across all subsequent handling. Redaction witness receipts are signed-ish toy local observations with sequence, previous-link, family, and path pressure.

Audit needle: redaction witness.
