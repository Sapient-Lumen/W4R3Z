# GlassTTY profile fleet capture

- captured_at: 2026-03-17T23:33:46Z
- profile_count: 2
- best_profile: alpha
- best_tier: portable-reopen
- best_score: 82
- best_next_command: ./scripts/glasstty-profile.sh reopen alpha --allow-discovered-browser-fallback --remote-debugging-port auto
- fleet_capture_count: 1

## Ranked profiles

- alpha: tier=portable-reopen score=82 next=`./scripts/glasstty-profile.sh reopen alpha --allow-discovered-browser-fallback --remote-debugging-port auto`
- beta: tier=portable-reopen score=82 next=`./scripts/glasstty-profile.sh reopen beta --allow-discovered-browser-fallback --remote-debugging-port auto`

## Fleet history

- ledger_path: `/mnt/data/GlassTTY-rev0102-2026.03.17.23.11-profiletriage-bestnext-fleetlane-whimbrel/validation/rev0103-focused/sample-home/glasstty-profile-fleet-captures.json`
- comparison_summary: no previous fleet snapshot exists yet

## Recommended commands

- triage: `./scripts/glasstty-profile.sh triage --pretty`
- fleet_capture: `./scripts/glasstty-profile.sh fleet-capture --output-dir validation/latest/profile-fleet-capture`
- fleet_captures: `./scripts/glasstty-profile.sh fleet-captures --pretty`
- doctor: `./scripts/doctor.py --pretty`
- best_profile_next: `./scripts/glasstty-profile.sh reopen alpha --allow-discovered-browser-fallback --remote-debugging-port auto`

## Bundle files

- `fleet-triage.json`
- `profiles.json`
- `doctor.json`
- `fleet-history.json`
- `fleet-diff.json`
- `bundle-summary.json`
