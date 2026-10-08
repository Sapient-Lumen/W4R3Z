# rev0030 summary

- Added browser-target-aware CDP inspection so GlassTTY preserves extension truth from the browser-level DevTools target graph, not only `/json/list`.
- Focused tests passed for the new CDP/browser-target path and the existing Playwright/package helpers.
- Manual validation in this container proved a headless-new Chromium run where `inspect_cdp()` saw the extension probe page through both `/json/list` and browser-level `Target.getTargets`; see `manual-browser-target-cdp-rev0030.json`.
- This still does not prove native-host socket availability or a full live bridge round-trip.
