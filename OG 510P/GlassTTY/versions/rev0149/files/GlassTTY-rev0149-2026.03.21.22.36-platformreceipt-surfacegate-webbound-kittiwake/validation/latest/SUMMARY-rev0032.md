# rev0032 validation summary

## Passed

- `pytest -q tests/test_cdp_inspect.py`
- `pytest -q tests/test_e2e_fixturelab.py`
- `pytest -q tests/test_validate_release.py`
- `npm --prefix extension run typecheck`
- `npm --prefix extension run build`
- manual `scripts/cdp-inspect.py --watch 1 --attach 1` capture against headless-new Chromium

## Manual artifact highlights

- `validation/latest/manual-rev0032-cdp-attach.json` proves the browser-level auto-attach lane attached to the unpacked extension probe page
- the same artifact preserves a detached session record and a lightweight in-target evaluation attempt
- that evaluation still landed on `chrome-error://chromewebdata/` here, so rev0032 does not claim a clean extension-runtime attach

## Remaining gaps

- no service-worker target seen
- no clean probe JSON/browser-context artifact captured manually here
- no live native-host round-trip
- no fresh full end-to-end smoke JSON report
