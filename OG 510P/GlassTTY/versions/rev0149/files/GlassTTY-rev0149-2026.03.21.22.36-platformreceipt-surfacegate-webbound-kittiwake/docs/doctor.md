# GlassTTY doctor

`./scripts/doctor.py` inspects the local GlassTTY environment and prints a JSON report.

## What it checks

- project root and `GLASSTTY_HOME`
- extension manifest basics
- computed unpacked extension ID from `manifest.key`
- native-host wrapper path and executability
- default user-level native-host manifest locations for Chromium/Chrome/Chrome for Testing
- broker socket path existence
- known GlassTTY profiles
- availability of common local tools such as `node`, `npm`, `chromium`, and `playwright`
- fixture-lab routes and quickstart commands

## Usage

```bash
./scripts/doctor.py --pretty
python -m glassttyd.cli doctor --pretty
```

## Why it exists

The most common GlassTTY failures are environmental rather than logical:
- wrong unpacked extension ID
- native-host manifest installed to the wrong browser-specific directory
- non-executable wrapper path
- wrong `GLASSTTY_HOME`
- missing browser binary

## Hints

The report includes a `hints` array. These are lightweight, actionable diagnostics such as missing broker sockets, missing stable extension-ID support, or missing local tooling. Future LLM sessions should read `hints` first when explaining why a live proof is blocked.

## Playwright cache awareness

`doctor.py` now reports the latest cached Playwright browser package (if any), the parsed `python -m playwright install --list` state, a cache-audit report that distinguishes registered vs shadow installs, a repair plan for cache reconciliation, the current persistent-lane launch plan, and a sync preview/offline alignment fallback when the Playwright browser package is missing.

Useful companion commands:

```bash
python scripts/playwright-browsers.py list --pretty
python scripts/playwright-browsers.py inspect --pretty
python scripts/playwright-browsers.py audit --pretty
python scripts/playwright-browsers.py repair --pretty
python scripts/playwright-browsers.py sync --package chromium --include-headless-shell
python scripts/playwright-browsers.py import-cft --version latest
python scripts/playwright-browsers.py import-archive --archive /path/to/chrome-linux64.zip
python scripts/chrome-for-testing.py install --archive-path /path/to/chrome-linux64.zip --version 145.0.7632.6
```

GlassTTY now prepares the Playwright cache `.links` registry *and* writes the current Playwright package reference file before invoking `install --list`, because a never-initialized cache root can otherwise fail with `ENOENT`, and a cache seeded only by local archive/CfT imports can otherwise look empty to upstream Playwright tooling.

## Profile visibility

`doctor.py` now reports each known GlassTTY profile as a structured object instead of only a list of names. When a profile has been launched through the GlassTTY helpers, the report includes the saved `glasstty-profile.json` metadata, the per-profile `glasstty-native-host.json` audit snapshot, any discovered `DevToolsActivePort` state, current loopback attachability, strict and portable relaunch plans, and ready-made `resume-proof` / `capture` / `captures` commands so future sessions can reconstruct how the last CDP-oriented run was started, replay it, freeze the evidence bundle, inspect the profile-local capture ledger, and tell whether it is still usable now. When the saved browser path is missing on the current machine, `doctor.py` now says so explicitly and points at `glasstty-profile.sh reopen --allow-discovered-browser-fallback` instead of making the next session rediscover the workaround by hand.

The profile report now also carries a fleet-level `triage` summary. `./scripts/glasstty-profile.sh triage --pretty` ranks the saved managed profiles by leverage, identifies the current best profile lane, and prints the exact next command to run (`resume-proof`, `reopen_debug`, or the portable fallback reopen) so the next session can move directly from doctor output to action.

Doctor now also preserves fleet snapshot history in `profiles.fleet_capture_history` and hints at `./scripts/glasstty-profile.sh fleet-capture --output-dir ...` / `./scripts/glasstty-profile.sh fleet-captures --pretty`, so the whole managed-profile surface can be frozen and compared between sessions instead of only one profile at a time.

`doctor.py` now also exposes `operator_handoff.commands` and hints at `python scripts/operator-handoff.py capture --output-dir validation/latest/operator-handoff`, which freezes the current doctor/readiness surface, linked ledgers, and core handoff docs into one durable support bundle for future sessions.

The new fused companion is `python scripts/control-plane-report.py --pretty`. Use it when doctor health alone is not enough and you also need the current readiness next action plus support-record review pressure in one place. Its `capture` mode freezes that combined surface under `validation/latest/control-plane-report-capture`.

When bootstrap confusion is the real blocker, use `python scripts/install-receipt.py --pretty` to separate extension materialization, native-host registration, runtime socket truth, and operator reachability into one receipt.

When support prose is the real blocker, use `python scripts/support-surface-snapshot.py --pretty` plus `python scripts/check-support-record-contract.py --pretty` to freeze and lint the current support surface before changing tiers, rollout priority, or release language.


## Native-host audit

```bash
python scripts/native-host-report.py --pretty
```

Use this before a live browser run when you need to confirm that the installed manifest path, allowed extension ID, and wrapper executable all match the current GlassTTY checkout.

The new audit lane is useful when `install --list` looks empty or unstable: it compares on-disk browser directories against `.links` package references and the parsed upstream list output, then surfaces shadow installs, broken links, stale registered paths, and imported installs that are missing `INSTALLATION_COMPLETE` directly.

The new repair-plan lane is the next step after audit: it highlights shadow installs whose metadata matches the current Playwright package expectations closely enough for a safe rename into the package-owned install name and imported installs whose `INSTALLATION_COMPLETE` marker should be restored before the next raw `python -m playwright install …`. On a machine with a cache full of manual copies, `doctor.py` now surfaces the exact `playwright-browsers.py repair --apply ... --write-missing-markers` shortcut instead of only warning that garbage collection is possible someday.


## Raw versus prepared Playwright cache truth

- `python scripts/playwright-browsers.py list --raw --pretty` keeps the cache untouched and shows exactly what upstream Playwright sees before GlassTTY repairs anything.
- `python scripts/playwright-browsers.py list --pretty` still uses the prepared path that creates the current `.links` entry first, which is useful for recovery but should not be treated as the only source of truth.
- `python scripts/doctor.py --pretty` now carries both `install_list_raw` and `install_list_prepared`, and its audit/hints are derived from the raw registry snapshot so missing-current-link cases do not disappear during inspection.


## Native-host overflow visibility

- `python scripts/doctor.py --pretty` now includes `native_host.last_oversized_host_message`, which points at `state/latest/oversized-host-outbound.json` and the referenced artifact when the native host had to spill an oversized reply to disk.
- `python scripts/native-host-report.py --pretty` carries the same summary for browser-aware native-host audits.
- `python -m glassttyd.cli overflow-report` is the operator-facing shortcut for inspecting that state without dumping the full oversized payload by default.
- When historical spill artifacts start piling up, doctor now surfaces the inventory count/bytes and points at `python -m glassttyd.cli overflow-prune ...` so cleanup happens deliberately instead of by guesswork.


## Native-host runtime ownership visibility

- `python scripts/doctor.py --pretty` now includes `native_host.runtime`, which mirrors the live broker-owner metadata saved under `GLASSTTY_HOME/run/daemon-broker-owner.json` when a long-lived native host owns the broker socket.
- `python scripts/native-host-report.py --pretty` carries the same runtime snapshot so future sessions can tell whether a one-shot diagnostic likely came from a secondary helper process or from the current broker owner. After rev0091, a one-shot `bridge.status` or probe helper should no longer create a transient owner/broker when no persistent port is alive; seeing `broker.role = secondary` with no socket is now expected and useful evidence, not a failure to initialize the daemon.

`doctor.py` now also exposes `operator_attempt.commands`, the current `validation/latest/operator-attempt/attempt.json` summary when one exists, and the finished-attempt ledger at `validation/operator-attempts.json`. When an attempt is already in progress, doctor points at the exact `python scripts/operator-attempt.py finish ...` command; otherwise it hints at wrapping the next high-value validation/profile run in `operator-attempt.py start ...` so future sessions inherit a before/after attempt diff instead of unrelated snapshots.
