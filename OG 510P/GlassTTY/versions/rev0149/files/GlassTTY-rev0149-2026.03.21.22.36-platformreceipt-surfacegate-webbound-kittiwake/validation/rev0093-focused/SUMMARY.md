# rev0093 focused validation

- extension `npm run typecheck`
- extension `npm run build`
- `node extension/scripts/native-lane-check.mjs`
- `node extension/scripts/persistent-history-check.mjs`
- `python scripts/archive-audit.py --pretty .`
- `python scripts/verify-package.py <final zip>`

No fresh live Chromium/native-host/browser round-trip was proven in this container.
