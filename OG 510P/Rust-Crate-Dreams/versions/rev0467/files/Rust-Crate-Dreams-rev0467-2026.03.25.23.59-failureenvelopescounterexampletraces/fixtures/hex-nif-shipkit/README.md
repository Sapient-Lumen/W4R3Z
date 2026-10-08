# Hex Native NIF ShipKit fixtures

Fixture families now focus on three sharper review objects:
- **checksum residency** — whether the mandatory `checksum-*.exs` file is present in the Hex tarball and aligned with the observed remote assets
- **NIF-version window** — whether the chosen minimum NIF version and OTP support claim agree
- **fallback trigger** — whether unsupported targets or prerelease/dev flows force local compilation and whether that posture is honestly declared

Scenario families:
- `checksum_file_missing_from_hex_tarball/` — CI generated a checksum file, but the published package omitted it
- `nif_version_floor_overclaims_otp_window/` — feature/config choices imply a narrower OTP window than the README/package claim
- `unsupported_target_forces_local_build_without_honest_contract/` — target coverage gap silently pushes users into a local Rust build
