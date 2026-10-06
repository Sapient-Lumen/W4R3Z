# Shared browser/CDP fixture

Revision: rev0028

Rev0009 extracts browser test boilerplate into `tools/browser_cdp_fixture.mjs`.
The fixture is not a daemon and is not expected to persist across turns. It is a
one-shot helper for selected browser tasks.

## Why this belongs in the cube

Browser tests are expensive in the cloudtainer window. Duplicating server,
policy, Chromium, CDP, and teardown logic would make every new browser slice
fragile. The shared fixture turns those concerns into a single test substrate.

## Owned lifecycle

Each browser task owns:

```txt
local server
COOP/COEP headers
managed policy relaxation and restoration
Chromium profile
Chromium process group
CDP connection
page evaluation
teardown timing
artifact capture
```

The fixture should be reused inside one command, not across turns.

## Future improvements

- one command may eventually run multiple browser probes against one launched
  browser, but only if the manifest task declares that combined cost;
- screenshot support can be added for rendering slices;
- console/network traces can be normalized for replay;
- fixture failure reports should include enough state to reproduce the browser
  command locally inside the cube.

## Current fixture hardening

During packaging, the boot probe exposed a timing race where Chromium's
`/json/list` endpoint could answer before the page target included a
`webSocketDebuggerUrl`. `tools/browser_cdp_fixture.mjs` now polls for a page
target with a usable websocket URL before connecting. This keeps the browser
slice strict while avoiding a false failure caused by early CDP target listing.
