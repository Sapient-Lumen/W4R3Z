# meta-0468 — Field signal, material outcome, source-health taxonomy-pressure pass

Rev0788 deliberately avoided starting another broad doctrine family. The pass raised the evidence receipt floor using two concrete public signals—UI claimant observation/survey evidence and NYC right-to-counsel household outcome evidence—while preserving the rule that aggregate evidence cannot close the affected-person gap.

Changed files include `archive/986-*`, `metadata/evidence_receipts.json`, `schema/evidence_receipts.schema.json`, `sources/source_keys.json`, `sources/source_catalog.json`, `metadata/source_health.json`, `metadata/gap_ledger.json`, `metadata/note_metadata.json`, `tools/build_evidence_receipts.py`, `tools/build_source_health.py`, and `tools/lint_archive.py`.

The refactor target was source-health taxonomy pressure: generated output now exposes normalized health-status and volatility counts without rewriting historical raw labels. This gives future vocabulary work a measured starting point while avoiding destructive cleanup.
