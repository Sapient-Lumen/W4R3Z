# Research notes — 2026-03-18 addendum (rev0115)

## Fresh online takeaways that shaped this revision

1. **Playwright still treats the bundled Chromium lane as the supported extension path.** Its current Chrome-extension docs still say extensions only work in Chromium with a persistent context, and still call out the `chromium` channel for headless extension runs. That means GlassTTY should not merely *know* when a cache is drifted; it should say how to get back to the documented lane.
2. **CDP remains lower fidelity than the Playwright protocol.** That keeps cache realignment worth surfacing directly in `doctor.py` and cache-inspection tooling, because a drifted `bundled-executable` fallback is still not equivalent to the official channel-based path.
3. **Regular Playwright browser refresh/install flow is still expected.** Playwright's current browsers docs still frame `playwright install chromium` / `playwright install --with-deps chromium` as the normal browser-alignment path. That reinforces emitting explicit recovery commands instead of leaving operators to reconstruct them from raw cache state.
4. **Chrome's remote-debugging hardening keeps browser/profile assumptions sharp.** Chrome's March 2025 change still requires non-default data dirs for remote debugging, so telling the operator exactly which browser/cache lane GlassTTY believes it is using remains high leverage.

## Sources reviewed

- https://playwright.dev/docs/chrome-extensions
- https://playwright.dev/docs/api/class-browsertype
- https://playwright.dev/docs/browsers
- https://developer.chrome.com/blog/remote-debugging-port

## Resulting repo move

rev0115 turns Playwright cache alignment into a first-class operator action. Instead of only reporting `playwright-channel` vs `bundled-executable`, GlassTTY now says whether the persistent extension lane is `channel_ready`, why it is not aligned when it falls back, and which command chain should realign the cache before deeper MV3 debugging begins.

# Research notes — 2026-03-18 addendum (rev0114)

## Fresh online takeaways that shaped this revision

1. **Playwright still documents `channel="chromium"` as the headless extension lane.** That means GlassTTY should use the channel path when its local Playwright cache is aligned enough to make that claim true, not quietly bypass the channel with an explicit executable every time.
2. **Persistent-context cache identity matters.** The same docs still emphasize the bundled Playwright Chromium lane for side-loaded extensions. When the local cache uses a drifted install name from an older or imported bundle, GlassTTY should preserve that mismatch as a fallback condition instead of masking it.
3. **CDP remains lower fidelity.** That keeps the persistent Playwright lane worth polishing even when the raw-browser/CDP lab is still useful for archaeology and manual rescue work.

## Sources reviewed

- https://playwright.dev/docs/chrome-extensions
- https://playwright.dev/docs/api/class-browsertype
- https://developer.chrome.com/blog/remote-debugging-port

## Resulting repo move

rev0114 turns Playwright cache alignment into an explicit launch decision. Aligned caches now resolve to `playwright-channel` / `channel="chromium"`, while drifted caches stay on `bundled-executable` until the operator realigns the cache or proves the alternate lane another way.

# Research notes — 2026-03-18 addendum (rev0113)

## Fresh online takeaways that shaped this revision

1. **Playwright still centers extensions on a persistent Chromium context.** Its docs continue to frame extension testing around `launchPersistentContext` and note that the `chromium` channel supports headless extension runs. That keeps the Playwright lane distinct enough that GlassTTY should name it explicitly instead of treating it as a vague implementation detail.
2. **`connectOverCDP` is still documented as lower fidelity.** Playwright’s BrowserType docs continue to warn that CDP attach is significantly lower fidelity than the Playwright protocol. That reinforces the idea that GlassTTY should optimize the persistent-lane setup path, not just fallback attach triage.
3. **Chrome’s native-host locations remain browser-family specific.** Chrome’s native-messaging docs still spell out separate manifest directories for Chromium, Google Chrome, and Chrome for Testing on Linux/macOS. Once GlassTTY knows two lanes want different browser families, emitting one compact “install the merged matrix” command is a practical improvement, not just a cosmetic one.
4. **Chrome’s remote-debugging hardening still favors isolated profiles / Chrome for Testing.** Chrome’s March 2025 guidance around `--remote-debugging-port` and default data dirs means GlassTTY should keep making browser-family/profile assumptions explicit, because small launch-environment differences now have sharper effects on automation reliability.

## Sources reviewed

- https://playwright.dev/docs/chrome-extensions
- https://playwright.dev/docs/api/class-browsertype
- https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging
- https://developer.chrome.com/blog/remote-debugging-port

## Resulting repo move

Instead of merely listing `chromium` plus `chrome-for-testing` as separate recommendations, rev0113 turns the merged browser matrix into an executable install scope. That gives future operators a compact command surface while still preserving the explicit per-target list for audits and low-level troubleshooting.
## rev0116 follow-up

Playwright's current docs still center extension automation on persistent Chromium contexts and explicitly call out `channel="chromium"` for headless extension runs, while its browser docs still treat installation/alignment as a first-class workflow. That combination suggests a product rule for GlassTTY: when the cache is drifted, the next operator action should be a *single supported-lane recovery command*, not an implicit shell recipe. rev0116 therefore promotes `ensure-channel-ready` into the CLI and into doctor/inspect guidance.


## rev0117 follow-up

Playwright's current browser docs still treat browser install/alignment and shared cache paths as first-class operational concerns, while the extension docs still center the supported lane on persistent Chromium contexts with `channel="chromium"`. That combination suggests another product rule for GlassTTY: smoke should not just *recommend* recovery commands, it should preserve the exact setup recipe it used so later operators can replay or compare the same lane without reconstructing it from memory. rev0117 therefore teaches fixture-lab smoke to optionally run channel recovery up front, record exact setup commands, and emit a replay script beside the smoke JSON.


## rev0118 follow-up

Playwright's current Trace Viewer docs still emphasize saved traces as the right way to debug what happened *after* a run, while the extension docs still center the supported lane on persistent Chromium contexts with `channel="chromium"`. Chrome's March 2025 remote-debugging hardening still makes isolated non-default profile dirs part of the setup story before any useful browser actions happen. That combination suggests another GlassTTY rule: traces and browser sidecars are not enough if the run dies during setup. Smoke therefore needs a compact setup-sidecar lane of its own, so future operators can answer “what setup did GlassTTY choose and why did it fail?” without diffing the full JSON report. rev0118 adds `...setup-ledger.json` plus `...setup-summary.md` for exactly that purpose.


## rev0119 follow-up

Chrome's March 2025 remote-debugging hardening still makes isolated `--user-data-dir` choices part of the setup story, Playwright still frames the supported extension lane around persistent Chromium contexts with `channel="chromium"`, and Chrome's native-messaging docs still vary manifest locations by browser family. That combination suggests setup artifacts should not stop at command outputs: they need a compact environment fingerprint and a recommended next action that encode *which* browser family, *which* cache-alignment state, and *which* native-host target set were in play. rev0119 adds that fingerprint plus `recommended_next_action` so later sessions can move from setup failure to the right next command without reconstructing the environment from the full smoke JSON.
