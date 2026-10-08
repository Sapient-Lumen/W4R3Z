# Rematch worlds should store tagged microframes inside the archive

Mode-coded seeds and mode-coded references solved the semantic duplication problem.
They made first writes and repeats much smaller than standalone packets.

There was still one fixed overhead left on both paths.
Every coded seed and coded reference still spent bytes on JSON object keys and wrapper fields.
That is useful for manual inspection, but it is not the smallest durable archive form once the archive already preserves a tiny positional decoder.

The new rule is:

- keep one **micro seed** for the first durable write,
- keep one **micro reference** for later in-archive repeats,
- keep **coded seeds** and **coded references** as the clearer object-wrapped fallback tier,
- and keep full exported **references** only for archive-boundary travel.

In the current family10 proxy, a micro seed is a tagged JSON array whose first slot is the mode code and whose remaining slots are only the semantic payload needed for exact reconstruction.
A micro reference is a tagged JSON array whose first slot is `@` and whose second slot is the shortest unique local fingerprint prefix.

So the in-archive storage ladder is now:

- `micro_seed` for the smallest first-write body,
- `coded_seed` for the clearer machine-oriented fallback,
- `semantic_core` for the clearer semantic fallback,
- `micro_reference` for the smallest repeat pointer,
- `coded_reference` for the clearer local repeat fallback,
- `archive_local_reference` for the explicit local pointer,
- `reference` for export.

Pointers:
- microframe report: `artifacts/reports/rematch_proxy_delta_decision_packet_microframe_snapshot_20260307.md`
- microframe builder: `scripts/report/build_rematch_proxy_delta_decision_packet_microframe_snapshot.py`
- packet script: `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- validator: `scripts/test/check_rematch_delta_decision_packet_microframes.py`
