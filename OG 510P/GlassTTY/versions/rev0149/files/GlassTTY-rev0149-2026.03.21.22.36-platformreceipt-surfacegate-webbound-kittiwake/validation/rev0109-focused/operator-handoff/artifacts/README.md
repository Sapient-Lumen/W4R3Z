# GlassTTY

GlassTTY is a user-driven bridge between a live browser tab and a local terminal workflow.

The project is intentionally **browser-app agnostic**. Claude.ai is the first real adapter we care about, but the architecture treats it as one adapter among many.

## What this archive now includes

- a Chromium-first Manifest V3 extension in TypeScript
- a Python native host with a local UNIX-socket broker
- a side-panel operator surface inside Chromium
- a dedicated extension probe page for live diagnostics and smoke-proof automation
- tab targeting and supported-tab memory
- trusted-context storage hardening for mirrored bridge state
- session-scoped bridge state plus persistent target-tab selection
- user-driven Chromium context menus for targeting, reading, and write-selection flows
- Nix development shell setup
- scripts for launching isolated Chromium profiles, recording per-profile launch/debug metadata, listing and inspecting profiles, auditing archive size, packaging releases, and managing a local Chrome-for-Testing lab browser cache
- docs, decisions, and session-memory files designed to survive multi-session LLM collaboration
- a durable operator-handoff bundle lane that freezes the current doctor/readiness surface, linked ledgers, and the key archive-memory docs into one support pack for future sessions
- a paired operator-attempt lane that freezes before/after doctor/readiness/handoff state around one real live or profile run so future sessions inherit a true attempt diff instead of two unrelated snapshots
- a durable fixture-lab smoke capture lane that freezes `e2e-fixturelab.py` reports, copied trace/screenshot siblings, and current-vs-previous drift into a replayable handoff bundle
- browser-smoke interruption forensics that preserve in-flight browser launches as durable report evidence instead of collapsing them into a thin failed summary
- a light-weight Playwright lab landing zone for later Chromium automation work
- deterministic dev extension ID tooling via `manifest.key`
- native-host wrapper plus auto-ID install helper
- deferred broker ownership so one-shot native diagnostics do not accidentally create a transient CLI broker
- fixture-lab localhost server for adapter and content-script testing
- fixture capture CLI for saving rich page fixtures to disk
- browser-smoke helpers that can inspect a `chrome-extension://…/probe/index.html` page through raw CDP, with Playwright reserved for a bundled-Chromium persistent lab lane, saved trace artifacts for that lane, checkpointed atomic JSON reports, service-worker/context telemetry plus worker-health polling/recovery in the Playwright lane, and CDP attach remaining experimental
- Chrome-for-Testing resolution/install helpers so GlassTTY can prefer a hermetic raw-browser lab over ad hoc system Chromium when available
- hidden offscreen DOM tooling that can now summarize saved HTML and build a generic fixture-like capture through the extension itself
- native-messaging budget tooling so saved fixtures can be checked against Chrome's message-size limits before live browser runs surprise us
- reversible dynamic content-script experiments so frame-coverage hypotheses can be tested at runtime without repackaging the extension

## Working principles

- **User-driven first.** The browser stays open and visible.
- **No credential scraping.**
- **No network reverse engineering.**
- **Native messaging bridge.** Browser extension ↔ local daemon.
- **Generic core, site-specific adapters.**
- **CLI-friendly local state.** JSONL plus a local broker socket.
- **Nix-friendly dev environment.**
- **Rust-friendly protocol boundaries.** Hotspots can move later without changing the whole design.

## What is newly real in this rev

- background now remembers recently supported tabs, supports a persistent selected target tab, and can still target an explicit `tab_id`
- side panel shows supported tabs, can persistently select or clear the target tab, and can write or submit into that tab
- bridge state now lives in `chrome.storage.session`, with trusted-context hardening for both `session` and `local` storage areas
- user-driven Chromium context menus now support opening the side panel, targeting a tab, reading prompt/latest, and writing selected text into the prompt draft
- the background now keeps a recent in-memory bridge trace, attempts immediate native-port reconnect on `onDisconnect`, and falls back to `chrome.alarms` reconnect backoff when the host is still unavailable
- CLI now supports `bridge-status`, `contexts`, `trace`, `probe`, `content-script-experiment`, `set-content-script-experiment`, `clear-content-script-experiment`, `list-tabs`, `select-tab`, `clear-target-tab`, `submit-prompt`, `read-selection`, `state-snapshot`, `--tab-id`, and `--text`
- native-host install helper is OS-aware for Linux and macOS user-level defaults
- `./scripts/refresh-archive.py` now refreshes the machine-readable archive manifest, and it can now target copied/staged worktrees with `--root` plus a chosen release identity via `--archive-name`
- package verification now checks transitive extension-module imports, HTML-linked assets, and `web_accessible_resources` patterns inside packaged release zips instead of trusting only a small allowlist
- a single `./scripts/smoke.sh` runs extension typecheck/build plus Python tests
- research notes and Playwright-lab breadcrumbs were added for future sessions
- a combined `bridge.probe` diagnostic path now mirrors manifest/status/contexts/trace data for live-browser verification, and it can now attach a one-shot native-host-local status snapshot so browser-visible diagnostics include compact overflow inventory without reprinting large spill artifacts
- one-shot native-host diagnostics no longer compete for the broker socket: the long-lived `connectNative()` host now claims broker ownership explicitly, while `sendNativeMessage()` helper processes report themselves as secondary host instances instead of rebinding `GLASSTTY_HOME/run/daemon.sock`
- broker ownership is now decided lazily from the first native message intent instead of eagerly at host process start, so `sendNativeMessage()` status/probe helpers stay secondary even when no persistent bridge is currently connected and the broker socket does not yet exist
- explicit `bridge.status` / `bridge.probe` calls now opportunistically reseat the long-lived `connectNative()` lane when one-shot native diagnostics prove the host is reachable, and bridge state carries a compact `nativeConnection.laneDiagnosis` summary so future sessions can see whether GlassTTY is healthy, degraded, one-shot-only, reconnect-pending, or currently unreachable
- `bridge.probe.receiverAudit` and live `fixture.capture` metadata now preserve receiver resolver audit evidence (`resolverPolicy`, `receiverResolution`, `rankedMatches`) so future live proof bundles can explain *why* a receiver won
- bridge state now also carries a worker-pulse snapshot so MV3 boot churn is easier to detect during diagnostics
- GlassTTY now treats Chrome for Testing as a first-class lab browser with official-catalog resolution, local bundle install support, doctor visibility, and browser-launch preference when a local CfT bundle is present
- Playwright browser-cache sync can now pull the exact expected browser archive straight from the current Playwright dry-run URLs (with structured fallback/error reporting) instead of requiring a preseeded local archive or local Chrome-for-Testing install
- Playwright cache inspection now has a first-class installed-state lane: GlassTTY prepares the cache `.links` registry *and* the current Playwright package reference file before running `python -m playwright install --list`, so offline/imported cache entries appear in upstream tooling instead of living as shadow installs; the parsed state is exposed through `doctor.py`, `python scripts/playwright-browsers.py list --pretty`, and the new `python scripts/playwright-browsers.py audit --pretty` cache-truth report
- Playwright cache repair can now align repairable shadow installs with the current package-owned install names, prune broken registry links, and restore `INSTALLATION_COMPLETE` via `python scripts/playwright-browsers.py repair --apply ...`, which both makes previously invisible manual copies show up in upstream `install --list` and keeps imported browsers from being garbage-collected as stale on the next real `python -m playwright install …`
- the native host now treats Chrome's 1 MB host→extension ceiling as a recoverable runtime condition instead of a fatal bridge crash: oversized outbound messages are spilled to `GLASSTTY_HOME/state/fixtures/oversized-host-outbound-*.json`, mirrored in `latest/oversized-host-outbound.json`, surfaced in `bridge.status`, and replaced on the wire with a compact `error.report` that points at the saved artifact
- Playwright smoke now waits for a *healthy* MV3 extension worker instead of trusting the first worker handle, which makes worker-restart/stale-context failures visible in the report via `service_worker_wait` and `service_worker_initial_snapshot`
- best-effort browser smoke now preserves `browser_attempt_inflight`, converts interrupted launch attempts into durable `browser_attempts[]` entries, and carries those interruption details into capture/history summaries so killed runs still say what browser mode was being attempted
- GlassTTY's hidden offscreen document can now build generic fixture-like captures from saved HTML, not just coarse DOM summaries

## Repository map

```text
.
├── AGENTS.md
├── CHANGELOG.md
├── DECISIONS.md
├── MEMORY.md
├── ROADMAP.md
├── STATUS.md
├── TASKS.md
├── docs/
├── adapters/
├── daemon/
├── extension/
├── native-host/
├── playwright/
├── scripts/
├── tests/
└── flake.nix
```

## Quick start

### 1) Enter the dev shell

```bash
nix develop
```

### 2) Run the local smoke suite

```bash
./scripts/smoke.sh
```

### 3) Launch an isolated Chromium profile for GlassTTY

```bash
./scripts/glasstty-profile.sh open main chrome://extensions/
```

This creates and reuses a dedicated Chromium user-data directory under `~/.local/share/glasstty/profiles/main` unless `GLASSTTY_HOME` is set. Every launch now records `glasstty-profile.json` metadata **and** a browser-aware `glasstty-native-host.json` preflight snapshot inside the profile directory so future sessions can see which browser binary, browser family, start URL, remote-debugging mode, and native-host target state were in play. `glasstty-profile.sh info` also derives an attachability hint from `DevToolsActivePort`, local TCP reachability, strict relaunch recipes, portable fallback relaunch commands, and any saved MV3 restart-proof summary so the next session can tell whether that profile is ready for `resume-proof` right now, needs a replayed reopen, or only failed because the original browser path does not exist on this machine anymore.
When multiple managed profiles exist, `./scripts/glasstty-profile.sh triage --pretty` now ranks them by the most useful next operator action and emits the exact next command (for example `resume-proof`, strict `reopen_debug`, or portable fallback `reopen_debug_portable`) so the next session does not have to inspect each profile by hand. `./scripts/glasstty-profile.sh fleet-capture --output-dir ...` then freezes that entire fleet view — triage, doctor, all profile summaries, and a fleet-level drift comparison against the previous snapshot — into one handoff bundle.

For CDP/browser-target work without guessing a port ahead of time:

```bash
./scripts/glasstty-profile.sh open lab --remote-debugging-port auto http://127.0.0.1:8765/
./scripts/glasstty-profile.sh info lab --pretty
./scripts/glasstty-profile.sh reopen lab --remote-debugging-port auto
./scripts/glasstty-profile.sh resume-proof lab --output validation/latest/mv3-worker-resume-lab.json --timeout 25
./scripts/glasstty-profile.sh capture lab --output-dir validation/latest/profile-capture-lab
./scripts/glasstty-profile.sh captures lab --pretty
./scripts/glasstty-profile.sh fleet-capture --output-dir validation/latest/profile-fleet-capture
./scripts/glasstty-profile.sh fleet-captures --pretty
```

`glasstty-profile.sh capture` writes a durable handoff bundle for that managed profile: the current profile summary, full `doctor.py` report, browser-aware native-host reports for the current/saved/effective browser choices, copied profile-local artifacts, a profile-local capture ledger entry, and a comparison against the previous bundle when one exists. Use it immediately after any live replay or restart-proof run so future sessions inherit evidence instead of another archaeology task. `glasstty-profile.sh captures` then shows the saved ledger for that profile so the next session can compare proof bundles instead of rediscovering them one by one.

`glasstty-profile.sh fleet-capture` is the same idea at the whole-GlassTTY level: it writes `fleet-triage.json`, `profiles.json`, `doctor.json`, `fleet-history.json`, `fleet-diff.json`, and `SUMMARY.md`, while also updating the root-level `glasstty-profile-fleet-captures.json` ledger. That makes the answer to "what changed across all managed profiles since the last session?" durable instead of conversational.

`python scripts/validate-release.py --out-dir validation/latest` now also accepts `--pytest-faulthandler-timeout` and `--pytest-durations`, so long pytest validation steps leave traceback and slow-test diagnostics inside their saved step logs instead of stalling as silent black boxes. `python scripts/validate-release-capture.py --source-dir validation/latest --output-dir validation/latest/validate-release-capture` then freezes the current wrapper report, step logs, running-step checkpoint, and current-vs-previous drift into one durable bundle backed by the root ledger `validation/validate-release-captures.json`.

`python scripts/operator-attempt.py start --output-dir validation/latest/operator-attempt --planned-command "..."` is the new paired-attempt wrapper for any high-value live/profile/validation run. It freezes the current doctor report, readiness board, operator-handoff artifact index, and tracked next-action summary *before* the attempt, then `python scripts/operator-attempt.py finish --output-dir validation/latest/operator-attempt --outcome success` captures the corresponding *after* state, writes `attempt-diff.json` plus `history-diff.json`, and updates the root ledger `validation/operator-attempts.json`. That turns “I tried this exact command” into a durable before/after bundle instead of leaving future sessions to compare separate snapshots by hand.

### 3b) Audit archive size before you cut a handoff

```bash
python scripts/archive-audit.py --pretty
```

By default, `scripts/package-release.sh` now excludes redundant validation `.zip` / `.patch` blobs so the handoff archive stays slim. Set `GLASSTTY_PACKAGE_INCLUDE_VALIDATION_BINARIES=1` only when you intentionally want a forensic package with those heavy artifacts included.
When the output zip basename itself is a real `GlassTTY-rev####-...` name, the packager now stages the archive under that exact root name so the bundle identity matches the release filename instead of leaking an older extracted-folder basename.

### 4) Load the unpacked extension

Open Chromium to `chrome://extensions`, enable Developer mode, and load the `extension/` directory.

### 5) Install the native-host manifest

Once the extension has an ID, install the native-host manifest:

```bash
./scripts/install-native-host.sh \
  --target chromium \
  --extension-id YOUR_EXTENSION_ID \
  --host-exe "$PWD/daemon/.venv/bin/python -m glassttyd.native_host"
```

### 6) Use the broker-backed CLI

```bash
python -m glassttyd.cli socket-status
python -m glassttyd.cli bridge-status --wait
python -m glassttyd.cli trace --wait --limit 25
python -m glassttyd.cli list-tabs
python -m glassttyd.cli select-tab 123 --wait
python -m glassttyd.cli read-prompt --wait --text
python -m glassttyd.cli read-latest --wait --text
python -m glassttyd.cli write-prompt "hello from terminal" --wait
python -m glassttyd.cli submit-prompt --wait
python -m glassttyd.cli capture-fixture --tab-id 123 --timeout 10
python -m glassttyd.cli offscreen-dom fixtures/claude/sample-thread.html --base-url https://claude.ai/chat/example --selector textarea
python -m glassttyd.cli offscreen-fixture fixtures/claude/sample-thread.html --base-url https://claude.ai/chat/example --selector main
python -m glassttyd.cli plan-fixture fixtures/corpus/claude-synthetic-thread.json
python -m glassttyd.cli native-message-budget fixtures/corpus --pretty
python -m glassttyd.cli clear-target-tab --wait
```

If Playwright Python is installed but its browser cache is empty, GlassTTY can now try to bootstrap the expected browser package directly from Playwright's current dry-run URL metadata:

```bash
python scripts/playwright-browsers.py sync --package chromium --download
python scripts/playwright-browsers.py audit --pretty
python scripts/playwright-browsers.py repair --apply --align-shadow-installs --prune-broken-links --write-missing-markers --pretty
```

To target a specific supported tab:

```bash
python -m glassttyd.cli read-prompt --tab-id 123 --wait
```

## First things to verify on a live machine

1. `health.ping` round-trip: extension ↔ native host
2. broker socket creation at `GLASSTTY_HOME/run/daemon.sock`
3. side-panel status view reflects active tab, selected target tab, and supported-tab memory
4. `list-tabs` and `select-tab` behave coherently in a multi-tab session
5. `prompt.read` from Claude.ai
6. `transcript.latest` from Claude.ai
7. `prompt.write` and `prompt.submit` into a selected supported tab

## LLM hygiene

If an LLM is driving changes in this repo, it should read these files first:

1. `README.md`
2. `STATUS.md`
3. `MEMORY.md`
4. `DECISIONS.md`
5. `AGENTS.md`
6. `TASKS.md`

Then update `STATUS.md`, `MEMORY.md`, `TASKS.md`, and `CHANGELOG.md` at the end of a work session, refresh `ARCHIVE_MANIFEST.json` with `./scripts/refresh-archive.py --archive-name GlassTTY-rev....`, and verify the finished bundle with `python scripts/verify-package.py ...` so manifest/root identity drift gets caught before handoff.

## New in rev0011

- extension now ships real side-panel and options-page HTML entrypoints
- `scripts/extension-id.py` computes the unpacked Chromium extension ID from `manifest.key`
- `scripts/install-native-host.sh` now defaults to `--target auto`, supports `--all-recommended`, and defaults to the absolute `scripts/native-host-wrapper.sh` executable
- `scripts/native-host-report.py` audits installed native-host manifests, expected wrapper paths, and browser-aware target recommendations, and now summarizes whether the recommended target is actually ready
- `scripts/fixture-lab.py` serves a deterministic local page for adapter testing at `127.0.0.1:8765`
- CLI gained `capture-fixture` plus `--timeout` on broker-backed commands


## Playwright cache truth

- `python scripts/playwright-browsers.py list --raw --pretty` shows the raw upstream `install --list` view without creating the current `.links` entry first.
- `python scripts/playwright-browsers.py inspect --pretty` and `python scripts/doctor.py --pretty` preserve both raw and prepared install-list views so a missing current-package link does not get hidden by cache prep.

## Native-host overflow operator loop

- `python -m glassttyd.cli overflow-report` summarizes the latest oversized host→extension spill artifact without dumping the full payload by default.
- `python -m glassttyd.cli overflow-report --artifact /path/to/oversized-host-outbound-....json --include-message` is the explicit escape hatch when you do want the preserved full message.
- `python -m glassttyd.cli overflow-prune --keep 3 --max-disk-bytes 2000000` dry-runs a retention plan for saved oversized spill artifacts; add `--apply` to delete the planned historical artifacts while protecting the current latest linked artifact by default.
- `python scripts/doctor.py --pretty` and `python scripts/native-host-report.py --pretty` now surface the latest overflow summary directly so archive handoffs do not need to grep `state/latest/oversized-host-outbound.json` manually.
- `bridge.status` / `bridge.probe` can now carry a compact one-shot native-host status snapshot, including overflow inventory counts and recent artifact summaries, which makes the side panel and probe page more useful during browser-only diagnostics.
- those one-shot snapshots now also report native-host process identity plus broker role (`owner` versus `secondary`), so future sessions can tell when a diagnostic snapshot came from a fresh helper process rather than the long-lived bridge host.
