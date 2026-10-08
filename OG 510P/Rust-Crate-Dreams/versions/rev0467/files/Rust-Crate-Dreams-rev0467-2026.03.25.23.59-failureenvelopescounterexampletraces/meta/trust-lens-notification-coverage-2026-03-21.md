# Trust Lens — notification-channel coverage note (2026-03-21)

This note sharpens **P-0017 Trust Lens** around a narrower but newly important question:

> if the trust posture changed tomorrow, which channel would tell us, and what classes of change would it miss?

## Main judgment

A worthwhile next iteration should **not** try to become a full incident feed service or a registry moderation backend.
It should add one small, reviewable watch layer above the signals Trust Lens already imports.

The reason is now concrete:

- crates.io Security tabs expose RustSec advisories on crate pages;
- Trusted Publishing Only Mode changes release-identity posture in crate settings;
- but the crates.io team now says routine malicious-crate removals will no longer each get a blog post and that RustSec advisories / RSS are the always-on route for those removals.

So the missing value is not “more trust data”.
It is a **watch-coverage receipt** that says which channels were actually consulted and what kinds of trust changes those channels can honestly cover.

## What the crate should provide other people

For application teams, platform/security teams, crate-curation workflows, and future pathfinder importers, the crate should now also provide:

1. **One notification-channel report** instead of assuming blog posts, crate pages, and advisory feeds all carry the same information.
2. **One change-class coverage answer** instead of flattening vulnerabilities, routine malware removals, high-signal campaign incidents, and publish-identity drift into one watch surface.
3. **One feed-gap warning** instead of quietly letting a partial watch configuration look complete.
4. **One diffable watch posture** so policy changes, feed additions, or removed watch channels can be reviewed like other trust changes.

## New first-class review object

### `notification-channel.report.json`

Named channel classes for the first version should stay small and boring:

- `rustsec_database`
- `rustsec_rss_feed`
- `cratesio_security_tab`
- `cratesio_trusted_publishing_setting`
- `rust_blog`
- `audit_import`
- `local_policy_import`

Named coverage classes should answer what kind of change a channel can be relied on to surface:

- `known_vulnerability`
- `routine_malware_removal`
- `high_signal_malware_incident`
- `publish_identity_posture`
- `audit_import_change`
- `manual_review_only`

Named status classes for the first version should stay conservative:

- `consulted`
- `not_configured`
- `derived_only`
- `manual_review_required`

This report should answer:

- which channels were explicitly consulted,
- which change classes each consulted channel is being trusted to cover,
- which decisive change classes currently have no configured watch route,
- and whether the current trust posture should be downgraded because the watch surface is incomplete for the claim being made.

## Recommended `0.1` command additions

### `cargo trust-lens capture --watch`
Capture watch-channel facts alongside the existing trust bundle and emit:
- `notification-channel.report.json`

### `cargo trust-lens explain --watch`
Render a human-readable summary of:
- channels consulted,
- covered change classes,
- missing change classes,
- and why the current posture is still `manual_review_required` if it is.

### `cargo trust-lens diff`
Compare two trust bundles and show watch-surface changes such as:
- RSS feed added,
- blog-only monitoring removed,
- trusted-publishing posture now imported,
- or a formerly covered class now missing.

## Recommended crate/workspace split update

Keep the existing split and add one small import/normalization layer:

- `trust_lens_watch`

This crate should remain tiny: its job is to normalize channels and coverage classes, not to build a full polling system.

## `0.1` artifact set update

Core artifacts should now include:
- `notification-channel.report.json`

alongside:
- `identity-risk.report.json`
- `signal-basis.report.json`
- `assumption-register.report.json`
- `review-debt.report.json`
- `policy-decision.report.json`

## Preferred fixture families

- a graph where the team watches the Rust blog but not RustSec RSS, so routine malware-removal coverage is incomplete;
- a graph where Security-tab imports and Trusted Publishing posture exist, but no advisory watch route is configured;
- a graph where advisory watch is configured, but publish-identity posture is still not imported;
- a graph where channels are present but one decisive change class remains `manual_review_required`.

## Non-goals

- not a replacement for RustSec or crates.io notifications,
- not a background polling service,
- not a global incident dashboard,
- not proof that every relevant change will be discovered automatically.

## Sources

- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://rustsec.org/
