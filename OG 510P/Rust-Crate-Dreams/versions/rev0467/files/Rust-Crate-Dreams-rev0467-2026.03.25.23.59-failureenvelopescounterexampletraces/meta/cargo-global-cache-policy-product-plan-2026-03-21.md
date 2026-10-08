# Cargo Global Cache Policy & GC Receipt Kit — product plan (2026-03-21)

This note sharpens **P-0480 Cargo Global Cache Policy & GC Receipt Kit** into a more implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0480** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not try to become a universal disk janitor, mutate `target/` layouts, or pre-implement Cargo’s future user-wide build cache.
It should provide one boring, reviewable **recovery-aware cleanup contract** above today’s Cargo-home global cache substrate.

`0.1` should make five things first-class:

1. **inventory basis** — what Cargo-home classes were actually scanned;
2. **cache surface** — whether a plan concerns Cargo home, target-dir final artifacts, build-dir intermediate artifacts, or a future cache surface;
3. **recovery obligation** — whether eviction implies local recreation, remote redownload, plugin fetch, or manual review;
4. **policy + exemptions** — what may be cleaned, what must be kept, and why;
5. **offline / compatibility posture** — when cleanup is riskier because the user is offline-heavy or mixes older Cargo versions.

## What `0.1` should provide other people

- one compact `cache-policy.toml`
- one compact `cache-inventory.json`
- one compact `gc-plan.json`
- one compact `cache-surface.receipt.json`
- one compact `recovery-obligation.report.json`
- one compact `gc.receipt.json`
- one compact `cache-diff.json`
- one rendered `cache-policy.summary.md`
- a redacted export bundle for support tickets or CI review

## Commands worth shipping first

- `cargo cache-policy scan`
- `cargo cache-policy plan`
- `cargo cache-policy explain`
- `cargo cache-policy diff`
- `cargo cache-policy doctor`
- `cargo cache-policy bundle`

## What to import, not reinvent

- Cargo-home directory facts and stable config (`cache.auto-clean-frequency`)
- nightly manual `cargo clean gc -Zgc` when available
- Cargo’s own last-use tracking semantics and offline caveats
- optional inventory imports from existing tools such as `cargo-cache`, but normalized into Cargo-grounded classes

## Suggested `0.1` doctor warnings

- `global_cache_plan_applied_to_target_dir_claim`
- `redownload_only_entries_cleaned_under_offline_heavy_policy`
- `older_cargo_versions_may_hide_recent_access`
- `registry_cache_and_registry_src_collapsed_into_one_cost_class`
- `future_user_wide_cache_claim_without_surface_receipt`
- `mixed_surface_bundle_missing_manual_review`

## First proving-ground scenarios

1. **Offline-heavy developer keeps redownload-only registry data longer than locally recreatable source trees**
2. **Shared `CARGO_TARGET_DIR` cleanup is not misreported as Cargo-home GC policy**
3. **Future user-wide build cache/plugin route stays distinct from current Cargo-home download cache**
4. **Mixed old/new Cargo usage forces a compatibility caveat instead of fake precision**
5. **CI bundle shows what will be downloaded again versus what will just be rebuilt**

## What to leave for later

- direct deletion by default
- target/build-dir mutation or cleanup orchestration
- remote cache servers or authenticated cache appliances
- organization-specific bandwidth pricing models
- pretending Cargo-home, target-dir, and future user-wide caches already share one stable contract
