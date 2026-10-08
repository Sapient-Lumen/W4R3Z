# Rematch worlds should store mode-coded seeds inside the archive

Semantic cores solved the larger first-write problem.
They removed deterministic result fields and kept only the semantic input needed to reconstruct a decision packet.

There is still another fixed overhead left inside the archive itself.
Each semantic core repeats long wrapper strings such as the packet kind, the semantic-core contract version, and the full mode name.
That is good for self-description, but it is not the smallest durable object when the archive already preserves the executable expander and the local codebook.

The new rule is:

- keep one **mode-coded seed** per semantic fingerprint as the default smallest long-lived body,
- keep **semantic cores** as the more self-describing fallback tier,
- materialize **archive-local packets** when a readable packet view is useful,
- and export **standalone packets** only when the decision must travel outside the archive.

In the current family10 proxy, the codebook can compress:

- `oracle_coordinates` to mode code `oc`,
- `oracle_weights` to `ow`,
- robustness fixed signatures to `rf`,
- robustness adaptive routes to `ra`,
- strict adaptive routes to `sa`,
- and exact checked-cap paths to `xp`.

So the long-lived storage ladder is now:

- `coded_seed` for the smallest archive-local body,
- `semantic_core` for the self-describing machine seed,
- `archive_local` for the readable packet view,
- `standalone` for export.

Pointers:
- coded-seed report: `artifacts/reports/rematch_proxy_delta_decision_packet_coded_seed_snapshot_20260307.md`
- coded-seed builder: `scripts/report/build_rematch_proxy_delta_decision_packet_coded_seed_snapshot.py`
- packet script: `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- validator: `scripts/test/check_rematch_delta_decision_packet_coded_seeds.py`
