# Manual validation notes — rev0021

## Commands captured

- `cd extension && npm run typecheck`
- `cd extension && npm run build`
- `python -m py_compile scripts/e2e-fixturelab.py scripts/e2e_fixturelab.py`
- `pytest -q tests/test_e2e_fixturelab.py -k 'not fixturelab_e2e_smoke'`
- `pytest -q tests/test_validate_release.py`
- `pytest -q tests/test_native_host.py`
- manual raw headless Chromium launch with `/json/version` and `/json/list` capture
- manual Playwright `connect_over_cdp()` attach against the same style of headless Chromium launch

## Honest result

Static/build/test coverage passed. The best browser proof improved materially: raw headless Chromium now has preserved DevTools artifacts that show the unpacked extension probe page. The Playwright lane remains experimental here: attachment worked, but the page list degraded to `chrome-error://chromewebdata/` and did not yet provide a trustworthy probe-page read. Native-host/socket proof is still not complete in this container.
