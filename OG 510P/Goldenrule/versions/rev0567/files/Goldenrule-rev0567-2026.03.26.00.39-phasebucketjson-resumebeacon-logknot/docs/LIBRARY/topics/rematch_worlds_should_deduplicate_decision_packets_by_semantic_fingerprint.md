# Rematch worlds should deduplicate decision packets by semantic fingerprint

Minimal packet modes and shared provenance profiles solve only **per-packet** bloat.
The next archive problem is repeat storage: the same rematch decision can reappear in multiple sessions or in multiple storage forms.

That means future inheritors should stop treating these as different long-lived objects when their semantic content is the same.

The new rule is simple.

- Expand any archive-local packet back to the canonical standalone packet.
- Hash that canonical expanded packet.
- Store one archive-local packet body for that fingerprint.
- For later repeats of the same decision, store only a tiny reference packet keyed by the semantic fingerprint.

In the current family `10/20/50/100` proxy this matters immediately because the same decision can show up as either:

- a standalone packet brought in from outside the archive, or
- an archive-local packet regenerated inside the archive.

Those byte strings differ, but they should collapse to the same semantic object once expanded and hashed.

The new executable helpers live in `scripts/analysis/rematch_proxy_delta_decision_packet.py`:

- `expand_packet(...)`
- `packet_semantic_fingerprint(...)`
- `packet_reference(...)`
- `packet_archive_write_plan(...)`

The archive consequence is practical.

Packet minimization answers **what is the smallest body worth storing once**.
Semantic fingerprinting answers **whether the archive needs to store that body again at all**.

Pointers:
- fingerprint report: `artifacts/reports/rematch_proxy_delta_decision_packet_fingerprint_snapshot_20260307.md`
- fingerprint builder: `scripts/report/build_rematch_proxy_delta_decision_packet_fingerprint_snapshot.py`
- packet script: `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- validator: `scripts/test/check_rematch_delta_decision_packet_fingerprints.py`
