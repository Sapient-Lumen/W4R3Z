## 2026-03-09 — rev0059 related-frame audit note

- Chrome's content-script docs still make frame reach explicit: `all_frames` defaults to top frame only, and related `about:` / `data:` / `blob:` / `filesystem:` frames are called out as a separate case for `match_origin_as_fallback`, with `match_about_blank` only covering a narrower subset.
- The Chrome instant-navigation guidance still reinforces that document/frame truth is explicit rather than page-global, which fits GlassTTY's receiver inventory model and argues for better gap/audit surfaces before any broader manifest change.
- Product consequence for rev0059: add browser-side coverage audits that tell future operators when a missing receiver is a primeable supported subframe versus one of Chrome's related-frame URL cases, instead of widening manifest scope blind.

# Research notes — 2026-03-09 — receiver truth after conservative priming

## Sources revisited online

- Chrome Extensions manifest/content-script docs for `all_frames`, `match_about_blank`, and `match_origin_as_fallback`
- Chrome `chrome.scripting` docs for explicit runtime targeting by `allFrames`, `frameIds`, and `documentIds`
- Chrome `chrome.webNavigation` / extension-instant-navigation docs for `documentId`, `documentLifecycle`, `frameType`, and the warning that `frameId == 0` is no longer the full story for outermost frames
- Playwright frames / `FrameLocator` docs as a reminder that iframe work stays frame-scoped in serious browser automation systems
- recent academic work on Chrome-extension performance as a reminder that broad extension surfaces should still be justified, not widened casually

## What mattered most

1. Chrome still treats frame reach as explicit policy. Manifest `all_frames` remains opt-in, and related-frame coverage such as `about:`, `data:`, and `blob:` still depends on separate content-script policy like `match_origin_as_fallback` instead of happening automatically.
2. Chrome's runtime injection model still lets GlassTTY choose a narrower lane: `chrome.scripting.executeScript()` can target specific `documentIds` or `frameIds`, which means GlassTTY can improve receiver discovery without immediately widening the manifest.
3. Chrome's frame/document model still makes `documentId` the safer precise target when available, because document identity changes on navigation while frame identity can persist across navigations.
4. Chrome's instant-navigation guidance explicitly says `frameId == 0` is no longer a reliable test for the outermost frame in all cases; `frameType` and `documentLifecycle` are the safer signals when they are available.
5. Playwright still treats iframe work as frame-rooted (`frameLocator(...)`) rather than page-global, which reinforces GlassTTY's receiver-inventory / receiver-selection model instead of arguing for a magic one-page abstraction.
6. Recent measurement work on Chrome extensions suggests extension surface area can have real performance cost, which is another reason to prefer targeted runtime priming and tighter receiver truth before widening manifest scope.

## Design consequence for rev0054

The highest-leverage change was not a blanket `all_frames` flip. It was a conservative receiver-priming lane:

- inspect Chrome frame inventory with `webNavigation.getAllFrames()`
- identify supported subframes that do not yet have an observed receiver
- inject the existing content script into those exact subframes via `documentId` first, `frameId` second
- keep explicit receiver inventory / override / ancestry metadata as the audit trail

That improves real discovery pressure while keeping the security/surface-area decision about broader manifest policy open for a later live-browser proof.

## Design consequence for rev0055

The next highest-leverage change after receiver priming was not broader manifest policy. It was **navigation- and lifecycle-honest receiver truth**:

- treat a same-frame new `documentId` as a replacement of the old receiver document, not as a sibling entry to keep forever
- prefer active or lifecycle-unknown receivers over known inactive (`prerender`, `cached`, `pending_deletion`) receivers when choosing where GlassTTY should send the next request
- preserve `documentLifecycle` in navigation trace entries so future live proofs can show why GlassTTY preferred one receiver over another

That keeps GlassTTY's browser↔CLI receiver model closer to what Chrome says is still alive in the tab, without yet widening manifest coverage or pretending the live-browser end-to-end proof already exists.


## Design consequence for rev0056

The next highest-leverage gap was no longer inside the extension. It was in the **shell-side operator surface**:

- Chrome's instant-navigation guidance says `frameId == 0` is not a safe universal outermost-frame test anymore; prerendered outermost frames can be non-zero while still being outermost
- GlassTTY's extension-side receiver logic had already learned that lesson, but `glassttyd resolve-receiver` and CLI labels were still using older `frameId == 0` instincts in a few places
- the right fix was to make daemon/CLI outermost detection mirror the richer browser-side logic, then expose lifecycle-aware resolver filters so shell automation can ask for the **active outermost** receiver directly

That tightens GlassTTY's browser↔CLI story without widening manifest scope or pretending a live prerender/active browser proof already exists in this container.


## Design consequence for rev0057

The next highest-leverage gap after rev0056 was no longer frame identity. It was **resolver transparency**:

- Chrome's instant-navigation model already requires GlassTTY to think in terms of `documentId`, lifecycle, and outermost-frame truth rather than a single simplistic top-frame test
- Chrome's runtime/frame APIs still target specific documents or frames explicitly, and Playwright still treats iframe work as frame-scoped, which means receiver choice is a real operational decision rather than cosmetic UI sugar
- once GlassTTY had that receiver metadata, letting `resolve-receiver` trust incidental row order became the least-defensible part of the operator surface

That led rev0057 to make receiver resolution deterministic and auditable: matching receivers are now ranked by lifecycle preference, outermost-ness, readiness, shallowness, and recency, and `--explain` exposes that policy directly so live proof bundles can show *why* a receiver won instead of only which key was returned.


## Design consequence for rev0058

The next highest-leverage gap after rev0057 was not receiver ranking itself. It was **where that ranking evidence lived**:

- Chrome's frame/document model still makes receiver choice a real browser-state question, not a cosmetic shell concern
- Chrome and Playwright both keep frame targeting explicit, which means future live proof bundles are stronger when browser-side artifacts already preserve receiver-choice reasoning
- once rev0057 made ranking explainable in the daemon, keeping that explanation CLI-only would have left `bridge.probe` and live fixtures weaker than they needed to be

That led rev0058 to move the audit lane into shared receiver helpers and thread it through `bridge.probe.receiverAudit` plus live `fixture.capture` metadata. The product gain is small but high-leverage: future live browser captures can now preserve both the winning receiver and the reasoning that chose it.


## 2026-03-09 — rev0060 policy-hint note

- Chrome's content-script docs still make three different levers explicit rather than interchangeable: `all_frames` broadens declarative reach to matching child frames, `match_about_blank` covers matching `about:blank` descendants, and `match_origin_as_fallback` extends declarative matching to `about:` / `data:` / `blob:` / `filesystem:` frames created by a matching origin.
- Chrome also still requires a `*` path when `match_origin_as_fallback` is enabled, and gives that lever priority over `match_about_blank`; that means future GlassTTY manifest experiments need to be deliberate and evidence-backed, not casual toggles.
- Product consequence for rev0060: keep the manifest conservative, but teach `bridge.probe` and `fixture.capture` to preserve the current content-script posture plus evidence-backed policy hints so future live gap bundles can say which Chrome lever is being suggested before anyone widens default scope.


## 2026-03-09 — rev0061 experiment-matrix note

- Chrome's current content-script docs still describe `all_frames`, `match_about_blank`, and `match_origin_as_fallback` as separate levers rather than one broad 'iframe mode'; `match_origin_as_fallback` also still requires a `*` path and takes priority over `match_about_blank`.
- That means a receiver-gap artifact should preserve more than a flat hint list. The useful question is not just 'which lever might help?' but 'what would remain broken after each plausible experiment?'
- Product consequence for rev0061: keep GlassTTY conservative by default, but save an explicit experiment matrix in `bridge.probe` and fixture metadata so future live sessions can compare the current runtime-priming baseline against narrow (`match_about_blank`) and broader (`match_origin_as_fallback`) manifest variants before changing defaults.

## 2026-03-09 — rev0062 dynamic experiment note

- Chrome's current docs keep saying the same thing in slightly different places: frame reach is a set of separate levers, not a single iframe switch. Static declarations can use `all_frames`, `match_about_blank`, and `match_origin_as_fallback`, while the `chrome.scripting` API can register dynamic content scripts and unregister them later.
- Product consequence for rev0062: GlassTTY should stop making manifest experiments purely theoretical. A non-persistent dynamic registration lane lets future live sessions test a coverage hypothesis, reload the page, capture `bridge.probe`, and then clear the experiment without forking or repackaging the archive.
- Important caveat: dynamic registration still is not retroactive proof for already-loaded documents, so probe guidance and handoff docs should keep telling future operators to reload or renavigate before comparing before/after coverage.
