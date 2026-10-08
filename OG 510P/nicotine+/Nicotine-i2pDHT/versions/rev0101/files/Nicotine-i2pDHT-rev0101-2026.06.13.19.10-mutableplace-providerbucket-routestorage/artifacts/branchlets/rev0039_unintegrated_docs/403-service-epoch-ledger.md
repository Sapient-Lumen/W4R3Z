# Service epoch ledger

`serviceepochledger.py` records repeated garden-service observations after a continuity pass.  A service can only become sticky when epochs are fresh, monotonic, diverse, not refusal-only, and not contradicted by active withdrawal or quarantined branch evidence.
