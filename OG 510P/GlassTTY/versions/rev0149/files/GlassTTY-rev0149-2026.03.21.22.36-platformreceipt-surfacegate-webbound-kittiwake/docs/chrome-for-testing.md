# Chrome for Testing in GlassTTY

GlassTTY now treats **Chrome for Testing (CfT)** as a first-class lab browser instead of assuming that the system `chromium` binary is always the best choice.

## Why this exists

Recent Chrome guidance recommends Chrome for Testing for automation-oriented scenarios, and Chrome’s remote-debugging changes increasingly assume a non-default automation/browser profile story.

For GlassTTY this matters because:

- the proof harness already uses isolated user-data directories
- the native-host install script already knows about the `chrome-for-testing` Native Messaging target
- current Chrome docs also note an important compatibility wrinkle: Chrome for Testing used Google Chrome native-host locations until Chrome 146
- the most fragile part of the lab has been “which browser binary are we really proving against?”

## What GlassTTY now supports

### Inspect local browser state

```bash
python scripts/chrome-for-testing.py inspect --pretty
```

This reports:

- the GlassTTY-managed CfT cache root
- the detected platform tag
- any locally installed CfT bundles
- the browser GlassTTY would currently use by default

### Resolve an official download URL

```bash
python scripts/chrome-for-testing.py resolve --channel stable --binary chrome --pretty
python scripts/chrome-for-testing.py resolve --version 136.0.7103.92 --binary chromedriver --pretty
```

### Install a local CfT bundle

```bash
python scripts/chrome-for-testing.py install --channel stable --binary chrome --pretty
python scripts/chrome-for-testing.py install --channel stable --binary chromedriver --pretty
```

By default GlassTTY installs into:

```text
$GLASSTTY_HOME/browsers/chrome-for-testing/
```

with the usual fallback:

```text
~/.local/share/glasstty/browsers/chrome-for-testing/
```

## Browser resolution order

GlassTTY now resolves a browser executable in this order:

1. `GLASSTTY_CHROMIUM_BIN`
2. `CHROMIUM_BIN`
3. latest local CfT `chrome` bundle
4. system `chromium` / `google-chrome`

That resolution is surfaced in:

- `python scripts/doctor.py --pretty`
- `python scripts/chrome-for-testing.py inspect --pretty`
- `python scripts/e2e-fixturelab.py ...` reports
- `./scripts/launch-chromium-profile.sh`

## What is still unproven here

This archive does **not** claim that CfT was downloaded and used successfully in this container. The improvements here are:

- the resolver/install tooling
- better doctor output
- a more hermetic path for future browser proof work

The next machine with ordinary network and disk access should try:

1. install local CfT `chrome`
2. check `python scripts/doctor.py --pretty` for the recommended native-host target(s) for that exact browser
3. install the native host using the recommended target (for current stable CfT this may still be `chrome`)
4. rerun `scripts/e2e-fixturelab.py`
5. compare the result against the older system-Chromium artifacts

## Important distinction

Chrome for Testing is now GlassTTY’s preferred hermetic browser for the raw browser/CDP lab lane. It is **not** the same thing as the supported Playwright extension-testing browser. For that lane, current Playwright guidance still points to the Playwright-managed browser package installed via `python -m playwright install chromium`. In current Playwright releases that package is Chrome-for-Testing-backed, and dry-run reveals concrete install names like `chromium-1208`.


## Use the Playwright sync helper when CfT is already local

When a same-version local Chrome for Testing install already exists, GlassTTY can now align the Playwright cache to the current Playwright package matrix with one command instead of separate per-package imports:

```bash
python scripts/playwright-browsers.py sync --package chromium --include-headless-shell
```

That keeps the Playwright lab aligned with current dry-run package names such as `chromium-1208` and `chromium_headless_shell-1208` while preserving Chrome for Testing as the browser-family source of truth for local/offline seeding.
It also now repairs the Playwright cache `.links` registry reference for the current Playwright package, so a later raw `python -m playwright install --list` run can see those imported installs instead of reporting an empty cache.

When no same-version local Chrome for Testing install is available, GlassTTY can now also try the current Playwright download URL directly:

```bash
python scripts/playwright-browsers.py sync --package chromium --download
```

That direct-download lane is intentionally explicit and still reports structured `download-error` results when the environment cannot reach Playwright's browser CDN, which keeps the operator path honest in offline or DNS-constrained labs.

## Trace artifacts

When `scripts/e2e-fixturelab.py` succeeds through the supported Playwright persistent lane, it now leaves a sibling `...playwright-trace.zip` artifact beside the JSON report. Keep that trace with the report, screenshot, and profile/native-host snapshots; it is the fastest post-failure breadcrumb for future sessions.

The report itself now also preserves worker-side breadcrumbs when Playwright gets far enough: `service_worker_snapshots`, worker console/close events, service-worker request breadcrumbs, plus context-level console/weberror events. It also records `service_worker_wait` and `service_worker_initial_snapshot` so you can tell whether Playwright had to recover from a stale MV3 worker handle before the probe page loaded. Keep those with the trace when you are debugging MV3 startup or native-host timing.


## Cache audit

After any manual import or directory surgery, use:

```bash
python scripts/playwright-browsers.py audit --pretty
```

This compares three views of the cache root: browser directories that exist on disk, `.links` registry references that Playwright actually traverses, and the parsed `install --list` output. It also flags imported browser directories that are missing `INSTALLATION_COMPLETE`, because those can still be treated as stale by a later raw `python -m playwright install …` even when the registry link is correct.

If that audit shows repairable shadow installs or broken links, GlassTTY can now reconcile the cache directly:

```bash
python scripts/playwright-browsers.py repair --pretty
python scripts/playwright-browsers.py repair --apply --align-shadow-installs --prune-broken-links --write-missing-markers --pretty
```

This does not invent arbitrary new Playwright ownership. It only renames manual/offline copies when their metadata matches the current package expectation closely enough (for example the same Chromium revision), restores `INSTALLATION_COMPLETE` where GlassTTY already owns the install directory, and removes broken `.links` entries that upstream Playwright would likely delete later anyway.
