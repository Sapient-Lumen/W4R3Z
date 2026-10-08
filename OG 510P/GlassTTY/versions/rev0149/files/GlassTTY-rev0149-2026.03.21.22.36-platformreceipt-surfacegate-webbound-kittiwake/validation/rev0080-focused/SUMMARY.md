# rev0080 focused validation

- targeted Playwright browser-cache tests: `8 passed`
- extension typecheck: passed
- extension build: passed
- real `playwright-browsers.py list --pretty` recorded a valid empty installed-browser report
- fresh-root comparison recorded the key behavior change: raw Playwright `install --list` failed on missing `.links`, while GlassTTY's list command created `.links` and succeeded
- real `playwright-browsers.py inspect --pretty` and `doctor.py --pretty` now carry parsed install-list state
- packaged archive verified successfully: `/mnt/data/GlassTTY-rev0080-2026.03.17.03.03-playwrightlist-linksprep-cachetruth-godwit.zip`
- package sha256: `54bdc26dbcbc6109a5f0327677aec300964ca9105de07944b013d7750c464dd7`
