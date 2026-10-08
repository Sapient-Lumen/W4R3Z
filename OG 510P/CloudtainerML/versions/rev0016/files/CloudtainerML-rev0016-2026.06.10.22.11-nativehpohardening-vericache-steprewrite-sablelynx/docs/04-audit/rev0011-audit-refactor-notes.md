# Rev0011 audit/refactor notes

Added `tools/traceability_report.py` to check source -> idea -> cell connectivity, P0 orphan gaps, cell-note coverage, probe file counts, and probe output counts.

Updated smoke validation to require rev0011 probes and audit/report artifacts. The dashboard tools remain heterogeneous by design; traceability is the new re-entry guard.

## Source dedupe pass

Canonicalized seven duplicate arXiv source rows and rewrote idea/cell references to the first source IDs. Canonical rows record `deduped_from` for reversibility.
