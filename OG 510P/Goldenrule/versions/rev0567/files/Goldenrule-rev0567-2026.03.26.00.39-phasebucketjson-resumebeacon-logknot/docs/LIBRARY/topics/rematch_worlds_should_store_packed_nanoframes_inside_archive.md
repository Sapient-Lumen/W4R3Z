# Rematch worlds should store packed nanoframes inside the archive

Tagged microframes solved the JSON object-key overhead problem.
They made first writes and repeats much smaller than coded seeds and coded references.

There was still one fixed overhead left on both paths.
Microframes still spent bytes on string mode tags, string route and signature payloads, and a 12-hex repeat prefix.
That is still readable, but it is not the smallest durable archive form once the archive already preserves a slightly richer local codec.

The new rule is:

- keep one **packed seed** for the first durable write,
- keep one **packed reference** for later in-archive repeats,
- keep **micro seeds** and **micro references** as the clearer tagged-array fallback tier,
- keep **coded seeds** and **coded references** as the clearer object-wrapped fallback tier,
- and keep full exported **references** only for archive-boundary travel.

In the current family10 proxy, a packed seed is a numerically tagged JSON array.
For declaration-first packets it mainly saves the mode-tag bytes.
For black-box probe packets it does more: finite route and signature strings collapse to tiny integers.
A packed reference stores the shortest unique even-length local fingerprint prefix as an 8-character base64url payload behind a numeric tag.

So the in-archive storage ladder is now:

- `packed_seed` for the smallest first-write body,
- `micro_seed` for the clearer tagged-array fallback,
- `coded_seed` for the clearer object-wrapped fallback,
- `semantic_core` for the clearer semantic fallback,
- `packed_reference` for the smallest repeat pointer,
- `micro_reference` for the clearer tagged-array repeat fallback,
- `coded_reference` for the clearer object-wrapped repeat fallback,
- `archive_local_reference` for the explicit local pointer,
- `reference` for export.

Pointers:
- packed snapshot: `artifacts/reports/rematch_proxy_delta_decision_packet_packed_snapshot_20260307.md`
- packed snapshot builder: `scripts/report/build_rematch_proxy_delta_decision_packet_packed_snapshot.py`
- packet script: `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- validator: `scripts/test/check_rematch_delta_decision_packet_packed.py`
