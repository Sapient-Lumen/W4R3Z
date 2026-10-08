# desktop-shipkit fixtures

This fixture pack exists to make **P-0012 Desktop ShipKit** concrete.

The goal is not to prove every desktop release pipeline.
The goal is to make three truths reviewable:

1. **release identity truth** — what package families, routes, and trust posture are actually being claimed,
2. **update-channel truth** — what channels and artifact families are really present,
3. **crash-symbol truth** — what symbol-support path actually exists after release.

## Core artifacts

- `release-identity.receipt.schema.json`
- `update-channel.contract.schema.json`
- `crash-symbol-handoff.manifest.schema.json`

## Scenario families

- `windows_signed_installer_update_key_rotated_without_migration/`
- `macos_direct_download_release_missing_dsym_handoff/`
- `linux_mixed_format_release_channel_drift/`
