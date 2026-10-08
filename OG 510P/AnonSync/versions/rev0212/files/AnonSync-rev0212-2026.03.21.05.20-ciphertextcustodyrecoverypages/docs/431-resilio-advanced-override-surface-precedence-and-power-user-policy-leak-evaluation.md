# Resilio advanced-override surface precedence and power-user policy leak evaluation

## What current official docs still make clear

Another current Resilio pass again strengthens the main archive conclusion rather than weakening it.

Current official docs still show real product substance:

- a live v3 line with `3.1.2.1076`
- a current **Power user preferences** page that explicitly says it covers today's latest Sync version
- explicit advanced controls for destructive guardrails, including `disable_remove_from_all_devices` and `recreate_placeholders_on_removal`
- explicit advanced controls for retention and operational memory, including `peer_expiration_days`, `sync_trash_ttl`, and `keep_expired_transfer_days`
- explicit advanced controls for discovery and refresh cadence, including `config_refresh_interval`, `folder_rescan_interval`, `folder_defaults.use_tracker`, `folder_defaults.use_relay`, and `folder_defaults.known_hosts`
- explicit advanced controls for runtime bias, including `disk_low_priority`, `disk_worker_per_job`, `prefer_net_over_disk_operations`, `worker_threads_count`, `disk_worker_pool_size`, `parallel_indexing`, and `transfer_job_verify_downloaded_files`
- explicit source/precedence truth that advanced preferences can be supplied through `sync.conf`
- explicit configuration-mode truth that declaring shared folders in config disables WebUI and overrides folders previously added from WebUI
- explicit special-case truth that a LAN-only tightening still needs more than ordinary folder preferences: current docs say you must change both share preferences and power-user settings, then temporarily set peer expiration to `0`, restart, and restore the prior value to clear cached public endpoints
- explicit restart truth for some advanced toggles such as profiler capture
- explicit surface mismatch truth that some advanced safety behavior is still ignored in Linux WebUI

That is not weak product thinking.
It is useful operational truth.

## What still should not be cloned

The ordinary operator answer is still fragmented.
Current docs still require hopping across the advanced-preferences table, config-mode guide, folder-preferences page, LAN-only article, and assorted support notes to answer four basic questions:

1. **Which hidden overrides are currently shaping this seat or subject at all?**
2. **Which visible controls are shadowed, ignored, or outranked by those overrides?**
3. **Which changes apply immediately, which need restart, and which need explicit cache or route-memory clearance?**
4. **What safety, retention, discovery, or runtime-cost side effects does each hidden override actually buy?**

Resilio still has strong ideas here.
It still does **not** earn direct interface cloning.

The reason is the same clone-veto rule applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads advanced-override truth across Power user preferences, configuration-mode docs, LAN-only instructions, folder preferences, and warning articles.
So the product idea stays strong while the page contract still fails.

## Why this matters for AnonSync

AnonSync should borrow four important habits directly:

- **say openly when hidden advanced overrides materially change destructive behavior, retention, route discovery, or runtime bias**
- **say openly when config-declared state outranks or disables interactive control surfaces**
- **say openly when a surface ignores a toggle or when a change requires restart or explicit cache clearance**
- **say openly what side-effect budget a performance or integrity bias spends**

But AnonSync should refuse four weaker habits:

- learning active policy primarily from a giant advanced-preferences table
- learning precedence primarily from config-mode documentation rather than one exact current-state page
- learning restart and cache-clearance requirements only from special-case help articles
- learning runtime-bias side effects only after the system feels slow, noisy, or unexpectedly re-downloads work

## Replacement pages added for this seam

This revision therefore adds four narrower replacement pages:

- `432` — Advanced override inventory
- `433` — Safety override
- `434` — Peer memory override
- `435` — Runtime bias override

These pages keep the Resilio candor and reject the hidden-table-first operator reconstruction path.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that advanced overrides, config precedence, restart boundaries, and runtime bias are real operational truths; refuse any interface contract where `what hidden policy is active`, `what currently outranks the visible UI`, `what requires restart or memory clearance`, and `what side effects this bias buys` still depends on advanced-preferences tables, config snippets, and special-case support articles.
