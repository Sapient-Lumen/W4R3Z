# Testing

## In-container tests currently possible

### Python

```bash
python -m pytest -q
```

Covers:
- native-messaging framing
- state persistence
- broker request/response

### Extension TypeScript

```bash
cd extension
npm run typecheck
npm run build
```

This repo now includes local stub typings so typecheck/build do not depend on downloaded `@types/chrome` just to validate the scaffold.

## Live-browser tests still needed

- load unpacked extension in Chromium
- install native-host manifest with real extension ID
- verify side panel
- verify broker-backed CLI round trips
- verify Claude adapter selectors
