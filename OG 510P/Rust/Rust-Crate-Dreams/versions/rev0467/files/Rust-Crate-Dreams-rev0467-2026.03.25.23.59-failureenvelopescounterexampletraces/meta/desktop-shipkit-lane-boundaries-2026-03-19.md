# desktop shipkit lane boundaries — 2026-03-19

This note exists to stop future passes from collapsing several related but distinct ideas into one fake “desktop app shipping crate”.

## Main judgment

The current sharp opportunity is **P-0012 Desktop ShipKit**.
That does **not** mean the missing value is simply “package the app.”
The Rust ecosystem already has meaningful release, packaging, and updater substrate.

The sharper remaining gap is the **contract layer** above that substrate:

- release-identity receipts,
- update-channel contracts,
- crash-symbol handoff manifests,
- drift reports,
- and compact support bundles.

## Keep these lanes separate

### 1. Packaging / artifact production
Questions here:
- can installers or bundles be produced,
- which formats are supported,
- and what per-platform build knobs exist?

This lane should import cargo-dist, cargo-packager, Tauri bundle flows, and other packagers.
It is not the whole missing product anymore.

### 2. Signing / notarization / identity truth
Questions here:
- what was signed,
- by whom,
- with what continuity or rotation posture,
- and what notarization/store-policy facts apply?

This lane is not the same as producing the installer.

### 3. Update-channel topology
Questions here:
- what channels exist,
- which artifact families belong to each,
- whether delta/full artifacts diverge,
- and where store-vs-direct routes stop being interchangeable.

This is not the same as package production.

### 4. Crash-symbol handoff
Questions here:
- what debug sidecars exist,
- whether `strip` / `split-debuginfo` changed diagnosability,
- and where support is supposed to fetch symbols.

This is not the same as updater truth.

### 5. Crash-reporting backend / telemetry product lanes
Examples:
- Sentry/Crashpad integrations
- in-house crash upload services
- privacy/redaction pipelines

These should sit adjacent to Desktop ShipKit support bundles, not be flattened into them.

## Future-pass checklist

When a future pass touches desktop release/distribution ideas, ask first whether the missing value is primarily:

1. packaging output,
2. signing/notarization identity,
3. update-channel topology,
4. crash-symbol handoff,
5. support-bundle export,
6. or backend crash-reporting/telemetry.

If the answer is “more than one,” keep the boundary explicit rather than flattening them into one generic proposal.
