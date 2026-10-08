# Cooperation benchmark programs should publish remaining primary verify and refresh target semantic counts in handoff packs

If a compact-card handoff pack already publishes direct first verify and first refresh target summaries, it should also publish the remaining typed report counts that those summaries are derived from.

The goal is to keep first-machine-step auditability machine-readable: inheritors and tools should not have to parse English summaries or reopen retained JSON just to recover the rest of the locally relevant report counts.

For the canonical compact-card handoff pack, that means publishing `primary_verify_target_citation_lineage_count`, `primary_verify_target_unresolved_lineage_count`, `primary_refresh_target_verified_delta_receipt_count`, and `primary_refresh_target_latest_known_card_count` as strict aliases of counts already retained in the citation-surface and inventory reports bound by the pack.
