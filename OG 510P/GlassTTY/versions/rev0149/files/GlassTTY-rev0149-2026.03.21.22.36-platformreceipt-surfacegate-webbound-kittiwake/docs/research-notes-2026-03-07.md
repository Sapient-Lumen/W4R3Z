# Research notes — 2026-03-07

Key takeaways that directly informed recent revisions:

- Native messaging is built around a long-lived `runtime.connectNative()` port, and Chrome passes the caller origin to the host process, so deterministic unpacked extension IDs remain worth preserving.
- `chrome.storage.session` is trusted-only by default, while `local` is broader unless access is reduced; that supports GlassTTY's current trusted-context hardening strategy.
- The Side Panel API remains the right UX surface for a user-driven operator console, with tab-scoped enablement and programmatic open calls.
- `runtime.getContexts()` is part of modern Chrome's own offscreen-document guidance, so it is a sensible primitive for MV3 diagnostics.
- Playwright's documented extension path depends on the `chromium` channel; generic system Chromium is not a dependable substitute for extension automation.
- CDP target visibility is a useful middle layer when a full native-messaging proof is not yet available: it can at least answer whether Chromium loaded the unpacked extension and surfaced a service worker target.

## Additional notes — delivery recovery and tab state

- `tabs.sendMessage()` can target a specific `documentId` or `frameId`; that makes stored sender metadata worth preserving rather than discarding after initial detection.
- Tabs can now be explicitly `discarded` and, in newer Chrome, `frozen`; those are meaningfully different from a missing receiver and should not all be handled as the same messaging failure.
- `chrome.scripting.executeScript()` is the MV3 runtime injection path for host-permitted pages, making it the right recovery tool when a supported tab exists but the content script is absent.
- The Action API supports per-tab badge text/title state, which fits GlassTTY because target routing and tab availability are tab-scoped rather than purely global.

The point here is not just notes, but preserving why the code changed.

## Additional notes — native reconnect and trace-friendly state

- Chrome's service-worker lifecycle guidance explicitly says a native messaging connection keeps the worker alive and recommends calling `chrome.runtime.connectNative()` again from the port's `onDisconnect` handler when the host crashes or shuts down.
- `storage.session` remains one of Chrome's recommended storage areas for service workers and keeps trusted-only state in memory until the extension reloads, updates, or the browser restarts.
- This makes `storage.session` a good place for a bounded diagnostic trace ring: it survives worker restarts within the loaded extension session without spilling untrusted or long-lived data to disk.

## Additional notes — alarms-backed reconnect

- Chrome extension service workers should not rely on `setTimeout()` or `setInterval()` for deferred work because workers can be terminated before the timer fires. Chrome recommends `chrome.alarms` instead.
- Chrome 120 lowered the minimum alarm interval to 30 seconds (`periodInMinutes: 0.5`), which makes alarms viable for reconnect backoff without waiting a full minute.
- Alarms are not guaranteed to survive browser restarts, so reconnect scheduling should be treated as best-effort state and re-established whenever the worker starts again.
- For GlassTTY, this means the best pattern is: immediate reconnect on disconnect, then alarms-backed retries with trace/status evidence if the host is still missing.


## Addendum for rev0018

- Chrome documentation now makes two things especially relevant here: alarms are a viable 30-second minimum timer in Chrome 120+, and alarms may disappear across restarts, so reconnect state must be restored or recreated on worker startup.
- Chrome also documents that `connectNative()` keeps the extension service worker alive while the native port is open, and that reconnect-on-disconnect is the right recovery hook if the host disappears.
- The end-to-end testing docs note that `--headless=new` supports extensions, which makes it worth trying before `xvfb` in CI-like environments even if it still falls short in this container.


## Addendum for rev0019

- Playwright’s own docs continue to push extension testing toward persistent Chromium contexts rather than arbitrary system-browser launches, which keeps GlassTTY’s “Chromium-first, headless as lab space” direction intact.
- Chrome’s testing docs explicitly bless extension pages as testable `chrome-extension://<id>/...` URLs, so a dedicated probe page is a cleaner long-term proof surface than relying only on service-worker enumeration.
- Chromium’s Linux user-data documentation and minidump docs tie profile/crash storage to XDG config locations, which made it worth wiring explicit writable XDG paths into the smoke harness instead of assuming `HOME` alone was enough.
- Crashpad still requires a database path and browser startup can fail before CDP if the environment is hostile, so the validation lane should preserve browser stderr and report environment facts rather than claiming the smoke “just timed out.”


## rev0027 research addendum

- Playwright's extension docs still say side-loaded extensions should use Chromium with a persistent context, and they explicitly recommend the bundled Chromium rather than branded browsers.
- Playwright's BrowserType docs expose `executable_path` for launch and `launch_persistent_context`, but they warn it is a use-at-your-own-risk escape hatch when not using the bundled browser. In GlassTTY, that made the right compromise clear: use `executable_path` for cached Chromium bundles that GlassTTY has staged locally, while continuing to label system-browser fallback as risky.
- The practical lesson from this container was that browser acquisition and browser launch are separate problems. `python -m playwright install chromium` can fail even when Chrome/Chromium itself is present, so GlassTTY benefits from explicit cache-seeding workflows.
