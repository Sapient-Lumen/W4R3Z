# rev0081 focused validation

- targeted Playwright registry tests passed individually: archive import extract, CfT import, registry-link creation, list prep, raw upstream list visibility after import, and skip-path registry repair
- extension typecheck: passed
- extension build: passed
- real temp-root `python -m playwright install --list` now recorded an imported `chromium-1208` path after GlassTTY archive import repaired the Playwright registry link
- real `python scripts/playwright-browsers.py list --root ... --pretty` now preserves the same upstream-visible browser path plus registry-link state
- packaged archive verified successfully: `/mnt/data/GlassTTY-rev0081-2026.03.17.07.36-playwrightregistry-upstreamtruth-linkheal-siskin.zip`
- package sha256: `3038b6186964ea70f25ca5a1f521d7f6223f8581449334e6248d48137cc25b4a`
