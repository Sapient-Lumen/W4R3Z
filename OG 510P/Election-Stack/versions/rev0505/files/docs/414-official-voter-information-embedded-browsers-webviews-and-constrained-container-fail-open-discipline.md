# 414 — Official voter-information embedded browsers, webviews, and constrained-container fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that voters reach inside an embedded or constrained browser container rather than a full ordinary browser context**:
in-app browsers,
app webviews,
Custom Tabs or similar browser-in-app shells,
Safari view-controller style containers,
and other limited containers where address bars, multiwindow behavior, downloads, deep links, history affordances, or “open in browser” expectations may differ from a full browser.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `378`, which governs document downloads and embedded-viewer boundaries,
- `384`, which governs mobile apps, app-store listings, and install boundaries,
- `403`, which governs broader progressive-enhancement and degraded-client recovery,
- `409`, which governs anonymous public read versus sign-in/session walls,
- `412`, which governs browser/device permission prompts,
- or `413`, which governs intentional outbound handoffs into another destination or context.

It adds one narrow rule:
**if an official voter-information page may realistically be reached inside an embedded or constrained browser container, the office should keep the first-party answer lane readable there and should preserve a visible escape hatch — such as open-in-browser, copy-link, or ordinary help routing — when deep links, downloads, new contexts, browser history expectations, or shared-state assumptions do not behave like a full browser.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, usability, accessibility, and accuracy. Android’s current **Use web content within your Android app** guidance says that while apps can use `WebView`, Android recommends `Custom Tabs` for an out-of-the-box browser experience and seamless transition when a user wants to open a web link in the browser. Android’s current **In-app browsing using Embedded Web** guidance says external links to websites an app does not own can use Custom Tabs to keep users in context while still providing a full browser experience with shared browser state. Android’s current **Build web apps in WebView** guidance says apps may override navigation and window behavior, which means link handling is not guaranteed to behave like a full browser by default. Apple’s current `SFSafariViewController` documentation says it presents a self-contained web interface inside an app. MDN’s current anchor guidance says links that open a new tab/window or point to a download should indicate what will happen, and MDN’s current `window.open()` guidance says blocked new browsing contexts can return `null`. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `android_use_web_content_within_app_page`; xref: `android_in_app_browsing_embedded_web_page`; xref: `android_build_web_apps_in_webview_page`; xref: `apple_sfsafariviewcontroller_page`; xref: `mdn_html_anchor_element_page`; xref: `mdn_window_open_method_page`)

That is enough to justify a compact control here.
A voter can be on the correct official page, with current content and no explicit account wall, yet still lose the task because the page is running inside a container that hides ordinary browser context, breaks expected navigation affordances, or handles links/downloads/deep links differently from the full browser the office assumed.

## This is not the same thing as an outbound handoff

`413` governs what happens when the office intentionally sends a voter from the current page to another destination, handler, or browsing context.

`414` governs a different question:
**what if the voter is already inside a constrained container before any intentional handoff happens?**

A page may have no external-jump bug at all and still fail `414` if its current route silently assumes a visible address bar, ordinary history controls, multiwindow support, download handling, or browser-shared session behavior that the container does not reliably provide.

## Keep the first-party answer readable before asking for a better container

A critical official page should not make “open this in a real browser first” the price of reading the current answer.

The archive’s rule is modest:
- the first-party answer lane should remain readable in the constrained container where feasible,
- the office may recommend the full browser for better reliability,
- but the current page should still expose enough first-party answer/help context that the voter is not dropped into a dead end merely because the page opened inside an app shell.

This keeps the surface bounded.
It is not a demand to fully optimize every vendor container.
It is a demand not to let a constrained container erase the answer lane.

## Preserve a visible escape hatch to the canonical browser route

Android’s current guidance emphasizes the distinction between embedded `WebView` experiences and browser-backed Custom Tabs; Apple likewise distinguishes self-contained in-app web interfaces from the broader browser context. For this archive, that means an official voter-information route should usually preserve at least one visible first-party escape hatch when the full browser is operationally safer:
- an explicit **open in browser** action,
- a copyable canonical URL,
- a visible office/help route,
- or another first-party recovery path that does not depend on guessing how the host app handles links. (xref: `android_use_web_content_within_app_page`; xref: `android_in_app_browsing_embedded_web_page`; xref: `apple_sfsafariviewcontroller_page`)

The office does not need to force every user out of the current container.
It **does** need a clear way out when the constrained container is the reason the next step stops making sense.

## Do not assume address-bar, history, or share affordances exist

A full browser gives users cues and controls that many embedded containers minimize or alter:
- visible source identity,
- copy/share URL affordances,
- ordinary back/forward expectations,
- tab or window management,
- and sometimes downloads or handler launches.

`414` treats those missing or altered cues as part of answer integrity, not as cosmetic chrome differences.
If the office expects a voter to verify the source, copy the link, reopen the route elsewhere, or recover with browser history, that recovery path should not depend on UI that the current container may hide.

## Shared-state and sign-in assumptions must stay bounded

Android’s current embedded-web guidance highlights that browser-backed Custom Tabs can share browser cookie state, while pure app-controlled webviews may behave differently. (xref: `android_in_app_browsing_embedded_web_page`; xref: `android_use_web_content_within_app_page`)

That means an official page should not quietly assume that because a route works in the full browser with a remembered session, it will behave identically inside every constrained container.
This composes with `409`, but it is narrower:
- `409` asks whether public read was wrongly turned into an account wall,
- `414` asks whether the container assumptions themselves turned a nominally available route into a confusing or broken path.

## Deep links, downloads, and new contexts need recovery inside constrained containers

Some of the highest-friction failures happen at container boundaries:
- a download route that does nothing useful inside the container,
- a directions or calendar handoff that opens unpredictably,
- a new-tab workflow that the container blocks or reshapes,
- or an app/universal-link route that changes behavior depending on where the link was activated.

`378`, `389`, and `413` still govern those substantive handoffs.
`414` adds the container-specific rule that the current official page should preserve a bounded fallback when those steps are attempted from an embedded environment.
A voter should not have to reverse-engineer the host app merely to keep moving.

## Minimal container taxonomy

A small taxonomy is enough:

1. **Browser-backed embedded container** — constrained UI but still a real browser-backed context.
2. **App-controlled webview** — the host application controls navigation and window behavior more directly.
3. **Container with weak browser chrome** — source identity, URL copying, history, or multiwindow affordances are reduced or hidden.
4. **Container-sensitive handoff route** — downloads, deep links, handler launches, or new contexts may behave differently here than in the full browser.
5. **Constrained-container recovery available** — the official page exposes open-in-browser, copy-link, canonical source identity, or ordinary help fallback.

## Preserve bounded reconstruction, not container telemetry exhaust

What matters here is bounded reconstruction of the office’s container posture:
- which critical routes are reviewed in constrained containers,
- which container classes are known to matter,
- whether the current answer remains readable,
- whether a visible open-in-browser or copy-link recovery exists,
- whether downloads/deep links/new contexts fail open,
- and when the route was last verified.

Do **not** preserve device fingerprints, app package identifiers, per-user embedded-browser analytics, browsing histories, or other container telemetry exhaust when bounded public-answer reconstruction is sufficient.

## Suggested payload fields

The payload for this surface can stay small.
Suggested fields include:

- `surface_id`
- `jurisdiction_id`
- `embedded_browser_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `constrained_container_classes[]`
- `critical_answer_routes[]`
- `public_read_in_constrained_container_note`
- `open_in_browser_or_copy_link_note`
- `visible_canonical_source_identity_note`
- `back_navigation_and_return_path_note`
- `download_deeplink_multiwindow_recovery_note`
- `shared_state_and_sign_in_assumption_note`
- `container_specific_failure_note`
- `container_state_classes[]`
- `container_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct the constrained-container posture:
- route labels,
- relevant container classes,
- current-answer readability state,
- open-in-browser/copy-link recovery state,
- source-identity visibility state,
- handoff/download/new-context recovery state,
- and review time.

Do **not** preserve device fingerprints, app identifiers, browsing histories, referrer exhaust, or per-user embedded-browser analytics when bounded policy reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Which critical official routes were reviewed in constrained or embedded browser containers?
- Could a voter still read the current official answer before switching containers?
- Did the page expose a visible open-in-browser, copy-link, or official help route when the constrained container became a problem?
- Could the voter still identify the canonical official source even if address-bar chrome was weak or absent?
- Did downloads, deep links, or new contexts fail open to a first-party recovery lane?
- Did shared-session or remembered-browser assumptions quietly break the route inside the embedded container?

## How this fits the family map

This is **not** a generic mobile-web tuning guide.
It is a bounded first-contact integrity control.
Use it when the official page is correct in principle, but the voter reaches it inside a constrained browsing shell that changes navigation, source visibility, session assumptions, download/deep-link behavior, or recovery affordances enough to endanger the answer lane.

The substantive voter question still lives in the ordinary surface families.
`414` only governs whether the current official page remains readable and recoverable when it is opened inside a constrained browser container.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-embedded-browser-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-embedded-browser-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Android Developers: Use web content within your Android app (xref: `android_use_web_content_within_app_page`)
- Android Developers: In-app browsing using Embedded Web (xref: `android_in_app_browsing_embedded_web_page`)
- Android Developers: Build web apps in WebView (xref: `android_build_web_apps_in_webview_page`)
- Apple Developer: `SFSafariViewController` (xref: `apple_sfsafariviewcontroller_page`)
- MDN: `<a>` element (xref: `mdn_html_anchor_element_page`)
- MDN: `window.open()` (xref: `mdn_window_open_method_page`)
