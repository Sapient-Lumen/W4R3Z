# Cargo Global Cache Policy & GC Receipt Kit fixtures

This fixture family is for `P-0480 Cargo Global Cache Policy & GC Receipt Kit`.

Core fixture artifacts:
- `cache-policy.schema.json`
- `cache-surface.receipt.schema.json`
- `recovery-obligation.report.schema.json`

Suggested fixture cases:
- developer laptop cache inventory with registry and git classes
- shared CI cache with explicit exemptions
- mixed-toolchain cache compatibility warning
- dry-run cleanup plan showing eligible vs exempt entries
- offline-heavy policy that keeps redownload-only entries longer than locally recreatable ones
- target-dir housekeeping that stays distinct from Cargo-home GC policy
- future user-wide build-cache/plugin scenarios that remain explicit manual-review surfaces
