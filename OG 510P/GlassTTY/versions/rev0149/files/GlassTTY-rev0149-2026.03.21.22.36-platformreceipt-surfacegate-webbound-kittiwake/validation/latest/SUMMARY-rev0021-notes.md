# rev0021 validation notes

- targeted pytest passed for the new Playwright probe helper plus related validation/native-host helpers
- manual raw headless Chromium proof reached DevTools and listed the unpacked probe page
- manual Playwright `connect_over_cdp()` attach connected, but the attached page list only surfaced `chrome-error://chromewebdata/`
- native-host daemon socket proof is still pending in this environment
