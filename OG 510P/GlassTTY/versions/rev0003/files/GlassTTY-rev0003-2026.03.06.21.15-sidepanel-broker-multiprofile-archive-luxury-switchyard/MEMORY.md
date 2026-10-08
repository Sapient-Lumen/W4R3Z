# MEMORY

## Snapshot

GlassTTY is a Chromium-first, Nix-friendly browser-to-terminal toolkit.

It is designed as a generic bridge for browser applications, with Claude.ai as the first real adapter.

## Current shape

- Extension model: Manifest V3 extension for Chromium
- Bridge model: native messaging with a long-lived `connectNative()` port
- Backend model: Python native host plus a local UNIX-socket broker
- Terminal interface: CLI commands backed by the broker socket
- Profile model: dedicated Chromium user-data dirs launched by helper scripts
- Browser operator surface: Chrome side panel backed by `chrome.storage.local`

## Important current assumptions

- Primary browser target is Chromium.
- The first real integration is Claude.ai.
- The browser must stay open and visible in the main workflow.
- Headless or heavier automation may exist later, but is not the core v1 path.
- The side panel is a diagnostics/operator surface, not the main user interface.

## Known unknowns

- final Claude.ai selector strategy
- how often transcript deltas will be too noisy in practice
- exact native-host packaging path under Nix-managed installs on every distro
- whether the broker should evolve toward a richer RPC or event subscription protocol
- when it becomes worth moving any hotspot into Rust

## Current repo intent

This archive is the source of truth and durable memory for the project. Chat history is not sufficient memory.

## Next sharp steps

1. Prove native-host ping from extension background.
2. Use the broker-backed CLI to request `prompt.read` from a live Claude tab.
3. Save real Claude fixtures and document breakage-resistant selectors.
4. Add a second adapter example after Claude is stable enough.
