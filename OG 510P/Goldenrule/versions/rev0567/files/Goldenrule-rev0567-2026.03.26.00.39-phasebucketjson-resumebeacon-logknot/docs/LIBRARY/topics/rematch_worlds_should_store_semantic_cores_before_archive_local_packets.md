# Rematch worlds should store semantic cores before archive-local packets

Shared provenance profiles solved repeated citation overhead.
Semantic fingerprints solved duplicate packet bodies.
There is still one avoidable cost left: the **first** body the archive keeps for a new decision can itself be smaller than an archive-local packet.

The archive already contains the executable family10 decision-packet module.
That means the long-lived object does not need to be a fully materialized packet body when the decision can be reconstructed deterministically from a smaller semantic seed.

The new rule is:

- keep one **semantic core** per semantic fingerprint as the default long-lived body,
- reconstruct an archive-local packet when a directly readable in-archive packet view is useful,
- reconstruct a standalone packet only when the decision must travel outside the archive.

Examples in the current family10 proxy:

- declaration-first coordinate packets can shrink to just `(B,H)` plus mode,
- declaration-first weight packets can keep the declared weights and drop derived coordinates plus deterministic result fields,
- exact checked-cap packets can keep only the exact signature,
- adaptive probe packets can keep only the observed route.

So the storage ladder is now clearer.

- `semantic_core` is the smallest durable in-archive body.
- `archive_local` is the readable in-archive packet view.
- `standalone` is the portable export form.

Pointers:
- semantic-core report: `artifacts/reports/rematch_proxy_delta_decision_packet_core_snapshot_20260307.md`
- semantic-core builder: `scripts/report/build_rematch_proxy_delta_decision_packet_core_snapshot.py`
- packet script: `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- validator: `scripts/test/check_rematch_delta_decision_packet_cores.py`
