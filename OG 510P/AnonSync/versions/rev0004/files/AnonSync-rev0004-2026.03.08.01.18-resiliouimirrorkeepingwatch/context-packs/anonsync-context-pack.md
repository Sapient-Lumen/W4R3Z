# AnonSync Context Pack

## Identity
- project: AnonSync
- revision: rev0004
- archive: AnonSync-rev0004-2026.03.08.01.18-resiliouimirrorkeepingwatch.zip
- stage: design_skeleton_with_ui_workstream

## Vision
A Rust-first, privacy-oriented peer-to-peer file synchronization system with bundled Tor and bundled I2P via i2pd, aiming for a sealed one-product user experience.

## Invariants
- Preserve archive continuity
- Update metadata when project facts change
- Keep sync core decoupled from transport internals
- Keep local validation cheap and repeatable
- Keep transport complexity hidden from noob users
- Keep adaptive behavior bounded and measurable
- Keep product-surface claims grounded in current Resilio docs when claiming alignment

## Architecture choices
- i2p_entrypoint: bundled_i2pd_via_sam
- tor_entrypoint: bundled_stable_tor_daemon
- core_transport_coupling: forbidden
- packaging_posture: sealed_one_product_with_internal_supervised_processes
- user_exposure_to_transports: forbidden_by_default
- invite_model: folder_device_permission_bundle
- sharing_posture: invite_only
- lan_discovery_default: enabled
- lan_discovery_beacon_semantics: invite_derived_rotating_token
- mobile_default_transport: tor
- mobile_i2p_policy: opt_in
- mobile_sync_default: selective_sync_placeholders
- change_detection_model: watchers_plus_durable_index_plus_periodic_rescan
- encrypted_peer_staging: encrypted_sink_before_untrusted_live_peer
- permission_model: resilio_like_ro_rw_owner
- arti_posture: deferred_future_migration
- resource_profile_posture: explicit_profiles_with_measured_adaptation
- small_file_transfer_posture: direct_send_fast_path_with_hard_ram_cap
- index_database_posture: local_sqlite_wal
- hashing_posture: blake3_default
- i2p_transit_posture: notransit_default_share_zero
- ui_surface_posture: shared_local_web_ui_across_desktop_mobile_and_nas_packaging
- resilio_research_posture: continuous_ui_behavior_and_changelog_tracking_required

## Next priorities
- Draft the shared UI information architecture and first screen flows
- Define the invite and capability schema with examples
- Define LAN beacon token format, rotation windows, and replay boundaries
- Benchmark resource profiles and discovery backoff rules
- Specify supervised runtime orchestration for bundled tor and i2pd
- Define index, placeholder, and periodic rescan semantics

## Must reads
- README.md
- MUST_READ_FIRST.md
- PROJECT_CHARTER.md
- ROADMAP.md
- docs/context/current-brief.md
- docs/runbooks/llm-runbook.md
- docs/research/must-reads.md
- docs/decisions/0001-bundled-runtime-product-posture.md
- docs/decisions/0002-invite-and-lan-discovery.md
- docs/decisions/0003-sync-detection-and-mobile-defaults.md
- docs/decisions/0004-performance-profiles-and-adaptation.md
- docs/decisions/0005-ui-surface-and-resilio-research-practice.md
- docs/architecture/0005-ui-surface.md
- docs/research/2026-03-08-resilio-ui-and-change-practice.md
- docs/runbooks/resilio-research-watch.md

## Reminder
Regenerate this file whenever project direction or canonical metadata changes.
