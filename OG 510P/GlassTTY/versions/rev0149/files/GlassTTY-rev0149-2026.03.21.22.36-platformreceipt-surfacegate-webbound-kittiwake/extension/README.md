# Extension

## Current scope

- Manifest V3
- Chromium first
- native messaging from background/service worker
- side panel for diagnostics and quick actions
- Claude content adapter as first real adapter

## Build

```bash
npm run typecheck
npm run build
```

The build outputs JavaScript under `dist/`.

## Load unpacked

- open `chrome://extensions`
- enable Developer mode
- choose “Load unpacked”
- select this `extension/` directory

## Notes

The native host manifest must allow the actual extension ID of the unpacked extension.
