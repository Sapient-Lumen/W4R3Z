# Rematch worlds should share decision-packet provenance profiles

The packet layer now supports a second storage rule beyond choosing the smallest **mode**.

Future sessions should also choose the smallest **storage form**.

Inside this archive, rematch decision packets should normally be stored as **archive-local** packets that cite a shared provenance profile instead of repeating the same long provenance block every time.

That rule is justified because the current family `10/20/50/100` proxy uses the same decision-packet provenance for every packet instance:

- the same contract version,
- the same checked-cap set,
- the same oracle script,
- and the same source snapshots.

Repeating that block in every stored packet wastes bytes without adding evidence. The archive-local packet form fixes this by replacing the repeated provenance with a short `profile_ref`, while still allowing exact reconstruction of the canonical standalone packet when one must travel outside the archive.

The new executable support lives in `scripts/analysis/rematch_proxy_delta_decision_packet.py`. It now exposes:

- an archive-local packet kind,
- a shared profile registry,
- round-trip expansion from archive-local back to standalone packets,
- and a storage-form rule distinguishing in-archive retention from portable export.

The practical handoff rule is now two-stage.

First choose the smallest packet **mode** that answers the question.
Then choose the smallest packet **storage form** that fits the transport requirement:

- use `archive_local` inside the long-lived archive,
- use `standalone` only when the packet must remain self-contained outside the archive.

Pointers:
- profile report: `artifacts/reports/rematch_proxy_delta_decision_packet_profile_snapshot_20260307.md`
- packet report: `artifacts/reports/rematch_proxy_delta_decision_packet_snapshot_20260307.md`
- packet script: `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- validator: `scripts/test/check_rematch_delta_decision_packet_profiles.py`
