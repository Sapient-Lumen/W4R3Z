## rev0073 research note — archive identity is part of runtime hygiene

- Chrome’s extension packaging docs remain strict that upload zips must have the extension manifest at the zip root, not hidden inside extra folders; even though GlassTTY handoff archives are source bundles rather than Web Store uploads, the broader lesson is the same: package shape is part of correctness, not a cosmetic afterthought.
- Chrome’s service-worker lifecycle docs still make the native-host/service-worker channel operationally fragile enough that future debugging should not also have to guess which revision a bundle *really* represents. That pushed rev0073 toward deterministic archive identity and explicit drift checks rather than another browser-only tweak.

## rev0072 research note — profile-scoped native-host preflight

- Chrome’s native-messaging docs now explicitly say host-manifest lookup varies by browser family and that Chrome for Testing used the Google Chrome locations until Chrome 146; GlassTTY should therefore preserve the browser-specific native-host audit *with* each launched profile instead of assuming a later reader can reconstruct it from global state.
- Chrome’s March 2025 remote-debugging hardening still reinforces the same operational pattern: use a non-default user-data-dir and treat the launched browser/profile combination as the debugging unit, not a generic browser process.

# Research notes — 2026-03-16

## Additional Chrome docs findings that changed rev0070

- Chrome's current remote-debugging security note says `--remote-debugging-port` and `--remote-debugging-pipe` are ignored against the default Chrome data directory from Chrome 136 onward unless a non-standard `--user-data-dir` is also supplied.
- Chrome's current ChromeDriver capabilities docs still present `user-data-dir` as the way to point Chrome at a custom profile for automation or testing.
- Chrome's current offscreen API docs still say an extension can only have one offscreen document open per profile, which increases the value of treating a GlassTTY profile as a durable debugging boundary instead of a disposable launch detail.

## Additional product implications

16. GlassTTY should preserve per-profile launch/debug metadata directly inside the profile tree, because current Chrome guidance makes the custom `user-data-dir` a security and debugging requirement rather than just a convenience flag.
17. `doctor.py` should surface profile launch/debug state explicitly, so future sessions can inspect whether a failed browser run even asked for remote debugging before they start spelunking lower-level traces.

## Chrome extension docs findings that changed this revision

- Chrome's current `chrome.scripting` API docs say dynamically registered content scripts default `persistAcrossSessions` to `true`, so GlassTTY's runtime experiments should keep forcing `persistAcrossSessions: false` to remain truly session-scoped. The current docs also state that `unregisterContentScripts()` **does not remove scripts or styles that have already been injected**, which raises the value of an explicit before/after comparison tool and a package/runbook warning that a reload or renavigation is part of the proof recipe.
- Chrome's current content-script docs say `match_origin_as_fallback` requires a `*` path and takes priority over `match_about_blank`, which validates GlassTTY's path-widening experiment logic and argues for preserving that widening in saved experiment-comparison artifacts rather than hiding it in trace output.
- Chrome's instant-navigation guidance still says `documentId` is the safer identity than `frameId` across navigations and that `frameId == 0` is not a sufficient outermost-frame test once prerendered or cached pages exist. That continues to support GlassTTY's lifecycle-aware receiver and coverage-audit posture.

## Product implications

1. A saved experiment plan is more useful if GlassTTY can compare it directly against a later post-reload artifact; otherwise future sessions keep recomputing the same reasoning by hand.
2. Release packaging needs to keep the built extension bundle (`extension/dist`) in the archive, because GlassTTY's unpacked MV3 workflow depends on those files at load time.
3. Archive manifests should advertise the exact archive identity and validation summary directly, because future LLM sessions should not need to reverse-engineer those fields from folder names or chat history.


## Additional Chrome docs findings that changed rev0064

- Chrome's current `webNavigation` API docs still say a `frameId` can remain constant across multiple navigations while `documentId` changes per document, and the docs explicitly call `documentId` useful for lifecycle transitions between prerender, active, and cached pages. That means a reload-driven coverage comparison should not trust frame IDs as a durable identity on their own.
- Chrome's instant-navigation guidance also says `frameId == 0` is no longer a universal top-frame test because prerendered/cached pages can create multiple outermost frames in one tab. That reinforces GlassTTY's broader move toward shape/lifecycle-aware evidence instead of old single-frame assumptions.

## Additional product implications

4. Coverage-experiment comparison should preserve shape-oriented warnings even when the raw remaining-gap count matches the baseline prediction, because count-only success can hide a different surviving frame problem after reload churn.
5. Package verification should treat manifest/HTML references as part of archive integrity, otherwise a zip can look complete while still omitting a runtime bundle that an unpacked MV3 load path expects.


## Additional Chrome docs findings that changed rev0065

- Chrome's current manifest reference for `web_accessible_resources` says resources are relative to the extension root, may use wildcard patterns, and each rule must map those resources to specific `matches` origins and/or `extension_ids` instead of globally exposing them.
- Chrome's current content-script manifest reference also says content-script JS and CSS file paths are relative to the extension root.

## Additional product implications

6. Package verification should validate declared resource patterns, not just hard-coded file names, because MV3 manifest/resource mistakes can survive packaging while still breaking the unpacked extension at runtime.
7. Package verification should walk transitive module imports from packaged entrypoints, because a zip can contain every top-level `main.js` and still fail if one bundled relative import is missing.


## Additional Chrome docs findings that changed rev0066

- Chrome's current content-script docs say that extension files used from a content script must be exposed as web-accessible resources, and the docs show both `chrome.runtime.getURL()` and `chrome-extension://__MSG_@@extension_id__/...` as the asset-addressing patterns for images/fonts loaded from content-script code or CSS.
- The current content-script and manifest docs still say JS and CSS paths are relative to the extension root, which means packaged verification can safely treat stylesheet entrypoints the same way it already treats manifest JS bundles: as roots of a dependency graph rather than as terminal files.

## Additional product implications

8. Package verification should inspect CSS dependency paths (`@import`, `url(...)`) instead of stopping at the top-level stylesheet file, otherwise a packaged extension can pass manifest/HTML/module checks while still missing a font, image, or nested CSS file that a content script needs at runtime.
9. Content-script CSS asset checks should be separated from generic extension-page asset checks, because only the content-script-facing assets need `web_accessible_resources` coverage.


## Additional Chrome docs findings that changed rev0067

- Chrome's current runtime docs still present `chrome.runtime.getURL()` as the supported way to build fully-qualified extension asset URLs, especially when a content script or page needs to inject an extension-hosted image or other packaged resource into a page.
- Chrome's current content-script docs still say content-script JS/CSS file paths are relative to the extension root and that assets used from content scripts must be declared as web-accessible resources.

## Additional product implications

10. Package verification should treat JS-discovered asset paths as first-class package dependencies, because a packaged extension can pass manifest/HTML/CSS checks while still failing at runtime when a built bundle reaches for an image, font, stylesheet, or worker only through `runtime.getURL()` or `new URL(..., import.meta.url)`.
11. Package creation should never target a file inside the directory currently being zipped; staging outside the repo tree is safer and easier to reason about for both humans and LLM operators.


## Additional Chrome docs findings that changed rev0068

- Chrome's current extension service worker basics doc still says service workers can import scripts either with the `import` statement or with `importScripts()`, while dynamic `import()` is not supported in extension service workers.
- Chrome's current runtime API doc still presents `chrome.runtime.getURL()` as the supported way to build fully qualified extension URLs, especially when content scripts or extension pages need packaged assets.

## Additional product implications

12. Package verification should treat `importScripts(...)` as a first-class dependency edge whenever GlassTTY verifies packaged worker-side JS, otherwise a classic worker can fail even when the top-level bundle and module graph look intact.
13. Release validation needs a resumable operator lane because container or CI interruptions are now a bigger practical bottleneck than missing archive metadata.


## Additional Chrome docs findings that changed rev0069

- Chrome's current extension service-worker lifecycle docs still say `chrome.runtime.connectNative()` keeps an MV3 service worker alive while the native port stays connected, and recommend reconnecting on `onDisconnect` when the host exits.
- Chrome's current offscreen API docs still say an extension can hold one offscreen document per profile and that the offscreen context only exposes the `runtime` extension API.
- Chrome's March 2025 Chrome security note on remote-debugging changes says `--remote-debugging-port` / `--remote-debugging-pipe` now require a non-standard `--user-data-dir` from Chrome 136 onward, which reinforces GlassTTY's isolated-profile launcher direction.

## Additional product implications

14. GlassTTY should keep treating per-profile isolation as a first-class operational boundary, not just a testing convenience, because current Chrome debugging/security guidance increasingly assumes a dedicated non-default user-data directory.
15. Archive luxury matters more when offscreen/native/service-worker debugging already spans several contexts; carrying redundant validation binaries forward wastes the operator's attention budget without improving proof quality.


## Additional Chrome docs findings that changed rev0071

- Chrome's native-messaging docs now distinguish Google Chrome for Testing from classic Google Chrome on macOS and Linux, with dedicated `NativeMessagingHosts` paths documented for Chrome for Testing and an explicit note that versions before Chrome 146 still used the Google Chrome locations. That turned GlassTTY's earlier browser-aware recommendation into a stronger product requirement: the install/audit tools should resolve targets automatically and explain mismatches instead of trusting operators to remember the version split.
- The same docs still emphasize that `runtime.connectNative()` keeps the host alive for the life of the port, while `runtime.sendNativeMessage()` starts a fresh host per message and ignores all but the first response. That reinforces GlassTTY's long-lived bridge model and makes install-path correctness even more important: a wrong manifest target silently destroys the entire steady-state transport.
