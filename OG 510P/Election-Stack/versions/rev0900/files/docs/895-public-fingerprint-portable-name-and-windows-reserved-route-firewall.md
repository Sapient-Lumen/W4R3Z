# Public-fingerprint portable-name and reserved-route firewall

**Track:** Shared

## Change

rev0862 advances the bounded public-fingerprint helper to profile `1.4`. The helper already rejected symlinked, dangling, casefold-colliding, and Unicode-non-NFC public surfaces. It now also emits stable warnings for cross-platform reserved public path components, including Windows-reserved characters, trailing dots or spaces, and device basenames such as `CON`/`NUL`/`COM1`.

Strict verification-policy lockfiles treat any public-fingerprint warning as fail-closed, so these routes cannot silently satisfy `packet_public_fingerprint_sha256` under a different reviewer filesystem.

## Why this is risk-reducing

The packet public fingerprint is used as a replay boundary for the strongest synthetic policy path. If a packet contains public names that are valid on one filesystem but ambiguous, unrepresentable, or normalized differently on another reviewer machine, two observers could think they are comparing the same public packet while actually seeing different surfaces. The new profile makes that ambiguity explicit and non-authenticating.

## Executable control

`tools/public_fingerprint_report.py` now emits warnings of the form:

```text
public_relpath_portable_component_rejected_for_hash:<relpath>:windows_reserved_character
public_relpath_portable_component_rejected_for_hash:<relpath>:windows_trailing_space_or_dot
public_relpath_portable_component_rejected_for_hash:<relpath>:windows_reserved_device_name
```

`tools/compare_public_fingerprints.py` continues to report `UNSAFE_WARNING` when either compared packet has warnings.

`PacketVerificationReport` advances to `report_version: 1.26.0`, and the current strict policy fixture binds to `packet_public_fingerprint_profile: 1.4`.

## Boundary

This is not filesystem sandbox certification. It is a deterministic warning/fail-closed boundary for the bounded publishable packet surface used by the synthetic verifier policy path.
