# Browser OPFS block-store proof slice

Current revision: rev0054

Task id: `browser:opfs-block-store-proof`

This explicit browser/full-tier slice runs `tools/browser_opfs_block_store_probe.mjs` through the managed Chromium/CDP fixture. It is intentionally outside broad release to keep release browser-light.

## What the slice does

1. Starts a local server with COOP/COEP headers.
2. Temporarily relaxes managed Chromium URL policy if needed.
3. Launches Chromium with a temporary profile.
4. Imports BrowserRT in a cross-origin-isolated page.
5. Creates `OpfsAsyncBlockStore` under `browserrt/rev0039/opfs-block-store-proof`.
6. Cleans the prefix.
7. Writes two blocks and one duplicate block.
8. Reads and verifies both blocks.
9. Calls storage estimate.
10. Reloads the page.
11. Reads the same blocks through a new provider instance.
12. Deletes both blocks and verifies absence.
13. Cleans up the prefix and tears down the fixture.

## Required evidence

- Content-addressed block refs.
- Duplicate put dedupe.
- Page-reload readback in one temporary profile.
- Checksum verification.
- Delete and post-delete absence.
- Trace events.
- Policy restoration.

## Non-claims

The proof is not a durability claim, not a browser restart or crash-recovery proof, not a quota/eviction test, not a sync-handle test, not multi-tab coordination, not storage-lane integration, not cross-browser conformance, and not a performance benchmark.
