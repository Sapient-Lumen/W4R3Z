# rev0082 focused validation summary

- baseline: `GlassTTY-rev0081-2026.03.17.07.36-playwrightregistry-upstreamtruth-linkheal-siskin.zip`
- core change: added Playwright cache audit/reporting (`audit_playwright_cache`, `playwright-browsers.py audit`, doctor integration) and fixed extension version-marker drift with archive verification coverage
- honest environment note: the container still does not prove a live Playwright-managed Chromium/native-host/browser round-trip; the new proof is cache-truth and release-hygiene focused

## Commands and results

- `python -m pytest -q tests/test_playwright_browsers.py -k 'audit or install_list or registry_link or playwright_browsers_script_import_archive_and_inspect'`
  - result: passed (`validation/rev0082-focused/pytest-playwright-cache.txt`)
- `python -m pytest -q tests/test_package_release.py -k 'version_marker_mismatch or verify_package_passes_for_minimal_good_archive'`
  - result: passed (`validation/rev0082-focused/pytest-package-version.txt`)
- `npm --prefix extension run typecheck`
  - result: passed (`validation/rev0082-focused/extension-typecheck.txt`)
- `npm --prefix extension run build`
  - result: passed (`validation/rev0082-focused/extension-build.txt`)
- raw `python -m playwright install --list`
  - result: still fails against the default cache root with `ENOENT ... /.links`, preserved in `validation/rev0082-focused/raw-playwright-install-list.stdout.txt`
- `python scripts/playwright-browsers.py audit --root <temp-root> --pretty`
  - result: successfully reports one shadow install plus stale registered browser paths in `validation/rev0082-focused/playwright-audit-shadow.json`
- `python scripts/doctor.py --pretty`
  - result: now surfaces cache-audit counts/hints in `validation/rev0082-focused/doctor-pretty.json`

## Key evidence

- shadow installs are now called out explicitly instead of hiding behind an empty `install --list` result
- broken/stale Playwright registry state now appears in doctor hints
- extension version markers are aligned at `0.1.38`, and `verify-package.py` will now fail future archives if `manifest.json`, `package.json`, and `package-lock.json` drift again

- package release + verifier
  - archive: `/mnt/data/GlassTTY-rev0082-2026.03.17.03.52-playwrightaudit-shadowtruth-versionlock-wryneck.zip`
  - verifier: passed (`validation/rev0082-focused/verify-package.json`)
  - package proof: `validation/rev0082-focused/package-proof.json`
