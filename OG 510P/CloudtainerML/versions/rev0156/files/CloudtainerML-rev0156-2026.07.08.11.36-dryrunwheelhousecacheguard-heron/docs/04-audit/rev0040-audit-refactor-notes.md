# Audit/refactor notes — rev0040

- Added `MISSION-KERNEL.md` with evidence tiers and non-overridable promotion vetoes.
- Added `EVIDENCE-STATUS.json`; four rev0039 lanes are quarantined, negative/mislabeled, or symbolic-only.
- Added `tools/evidence_integrity_audit.py` and storage-debt reporting.
- Refactored smoke validation to distinguish governance/package integrity from scientific validity.
- Refactored sparse/hard-gate reports so field presence is not called readiness and quarantines affect status.
- Added `SOURCE-ALIASES.json` rather than destructively renumbering duplicate source IDs.
- Removed checked-in Python bytecode/cache debris and converted `OPEN_QUESTIONS.md` into a compatibility pointer.
- No rev0039 scientific output was copied to a rev0040 filename.
