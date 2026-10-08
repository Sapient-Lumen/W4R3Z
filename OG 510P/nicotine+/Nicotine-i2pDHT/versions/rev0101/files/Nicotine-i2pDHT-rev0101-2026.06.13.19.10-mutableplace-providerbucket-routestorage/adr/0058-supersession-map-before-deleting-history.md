# ADR 0058 — Supersession map before deleting history

The cube has historical duplicate doc/ADR prefixes and near-duplicate module names. Deleting them would damage wake-from-amnesia history; ignoring them would hide ambiguity.

Decision: add `HISTORICAL_SUPERSESSION.json` and `supersession.py`; update `cubeaudit.py` so documented historical duplicates become info-level findings.
