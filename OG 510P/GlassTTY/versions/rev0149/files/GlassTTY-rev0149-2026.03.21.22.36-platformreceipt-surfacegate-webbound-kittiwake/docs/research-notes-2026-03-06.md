# Research notes — 2026-03-06

This note exists so future sessions do not need to rediscover a few key platform facts from scratch.

## Chrome extension platform facts that influenced this rev

- Native messaging hosts are browser-specific on Linux and macOS; Chromium, Google Chrome, and Google Chrome for Testing use different default manifest directories.
- `connectNative()` keeps a native host process alive for the life of the port, while `sendNativeMessage()` starts a fresh host process per request.
- Native messaging is available from extension pages and the service worker, not from content scripts.
- The Side Panel API supports tab-specific enablement and user-gesture opening from commands or other extension interactions.
- `storage.local` is exposed to content scripts by default, but Chrome supports restricting it to trusted contexts with `setAccessLevel()`.
- Playwright extension support is Chromium-only and wants a persistent context with bundled Chromium.

## Product implications

- Keep the service worker as the bridge coordinator.
- Keep the side panel as a real operator surface.
- Keep bridge state out of content-script reach unless there is a strong reason not to.
- Keep installer tooling aware of Chromium vs Chrome vs Chrome-for-Testing.
- `storage.session` is in-memory, not persisted to disk, is recommended for service-worker use cases, and is not exposed to content scripts by default.
- `sidePanel.open()` can be triggered from explicit user interactions including keyboard shortcuts and context menus.

## Product implications added later in the day

- Prefer `storage.session` for live bridge state and selected-target memory.
- Context menus are a good ergonomic fit because they stay user-driven while making in-browser operator actions cheaper.

