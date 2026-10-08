# Rematch worlds should store mode-coded repeat references inside the archive

Mode-coded seeds solved the new-body problem.
They made the first durable write as small as the archive could safely keep while still allowing exact packet reconstruction.

There was still one fixed overhead left on repeats.
Archive-local prefix references already stopped repeating the full exported hash string, but they still carried a long self-describing wrapper on every duplicate write.
That is good for readability, but it is not the smallest durable repeat artifact once the archive already preserves a local reference codebook.

The new rule is:

- keep one **mode-coded seed** per semantic fingerprint for the first durable write,
- keep one **mode-coded repeat reference** for later in-archive duplicates,
- keep **archive-local prefix references** as the clearer fallback tier,
- and keep full exported **references** only for archive-boundary travel.

In the current family10 proxy, the repeat-reference codebook can shrink the duplicate pointer to a tiny wrapper around the same shortest unique local fingerprint prefix.
So the repeat-storage ladder is now:

- `coded_reference` for the smallest archive-local repeat pointer,
- `archive_local_reference` for the clearer local pointer,
- `reference` for export.

Pointers:
- coded-reference report: `artifacts/reports/rematch_proxy_delta_decision_packet_coded_reference_snapshot_20260307.md`
- coded-reference builder: `scripts/report/build_rematch_proxy_delta_decision_packet_coded_reference_snapshot.py`
- packet script: `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- validator: `scripts/test/check_rematch_delta_decision_packet_coded_references.py`
