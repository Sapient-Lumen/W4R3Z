# GlassTTY readiness board

- grade: `blocked-by-validation`
- primary next kind: `resume_validate_release`
- primary next command: `python scripts/validate-release.py --out-dir validation/latest --resume`

## Top actions

- [10] `resume_validate_release` → `python scripts/validate-release.py --out-dir validation/latest --resume` — The latest validate-release run is incomplete around 'the current required step'; resume before starting a fresh umbrella pass.
- [20] `capture_validate_release` → `python scripts/validate-release-capture.py --source-dir validation/latest --output-dir validation/latest/validate-release-capture` — The current validate-release state is not yet frozen into the validation capture ledger.
- [30] `capture_fixture_smoke` → `python scripts/e2e-fixturelab-capture.py --report validation/latest/e2e-fixturelab.json --output-dir validation/latest/e2e-fixturelab-capture` — A latest fixture-lab smoke report exists but has not been frozen into the smoke ledger yet.
- [45] `capture_profile_fleet` → `./scripts/glasstty-profile.sh fleet-capture --output-dir validation/latest/profile-fleet-capture` — No fleet-level managed-profile snapshot has been frozen yet.
- [60] `repair_playwright_browser_inventory` → `python scripts/playwright-browsers.py sync --package chromium` — The persistent-context extension lane is blocked because no Playwright-managed browser package is currently available.

## Commands

- report: `python scripts/readiness-report.py --pretty`
- capture: `python scripts/readiness-report.py capture --output-dir validation/latest/readiness-report-capture`
- history: `python scripts/readiness-report.py history --pretty`
