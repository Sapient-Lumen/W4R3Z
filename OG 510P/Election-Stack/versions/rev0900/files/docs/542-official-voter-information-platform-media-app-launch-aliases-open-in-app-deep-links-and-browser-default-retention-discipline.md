# 542 — Official voter-information platform media app-launch aliases, open-in-app deep links, and browser-default-retention discipline

**Track:** Shared

This document adds one bounded rule to the recent platform-media chain layer:
once `528` has stitched several observations into one same-object media chain, `529` has named the current controlling head, `534–539` have already separated public aliases, scoped routes, bearer routes, render shells, and offset links, and `540–541` have already separated carriers from the routes they delivered, **how should the archive record cases where the same media object is opened through an installed-app launch, open-in-app prompt, universal link, or app-preferred deep-link handoff without letting that app path silently replace the citation-safe browser/public default?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/384-official-voter-information-mobile-apps-app-store-listings-and-download-boundary-discipline.md`
- `docs/414-official-voter-information-embedded-browsers-webviews-and-constrained-container-fail-open-discipline.md`
- `docs/471-official-voter-information-copy-share-controls-clipboard-write-truthfulness-and-native-share-handoff-discipline.md`
- `docs/498-official-voter-information-platform-follows-subscriptions-and-live-event-reminder-authority-boundary-discipline.md`
- `docs/511-official-voter-information-platform-share-panels-copy-links-timestamp-links-and-embed-export-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/526-official-voter-information-platform-media-re-anchor-ladder-canonical-recovery-targets-and-wrapper-exit-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/534-official-voter-information-platform-media-co-current-aliases-sibling-routes-and-canonical-head-with-alias-discipline.md`
- `docs/535-official-voter-information-platform-media-audience-scoped-current-aliases-scope-labels-and-public-default-retention-discipline.md`
- `docs/537-official-voter-information-platform-media-capability-bearing-current-aliases-link-secret-routes-and-redaction-default-discipline.md`
- `docs/538-official-voter-information-platform-media-player-host-render-aliases-direct-embed-routes-and-watch-page-default-discipline.md`
- `docs/540-official-voter-information-platform-media-notification-carriers-reminder-pointers-and-route-carrier-separation-discipline.md`
- `docs/541-official-voter-information-platform-media-carrier-target-drift-late-delivery-retargeting-and-stale-pointer-non-supersession-discipline.md`
- `docs/543-official-voter-information-platform-media-remembered-resume-aliases-history-reentry-and-full-object-default-discipline.md`
- `docs/544-official-voter-information-platform-media-in-player-moment-jump-aliases-transcript-chapter-picks-and-route-stability-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that one same-object media answer can travel between browser and installed-app containers without becoming a new object or a trustworthy new default route.
YouTube says that on iOS, clicking a `youtube.com`, `m.youtube.com`, or `youtu.be` link automatically opens the YouTube app through Universal Links and that some links and apps explicitly ask whether the user wants to open in YouTube.
YouTube also says links opened inside the YouTube app can be handled by the YouTube in-app browser.
Vimeo says a viewer can share a video directly from mobile web **without using the Vimeo app**, and its mobile-playback help says Vimeo videos play inline in mobile browsers rather than requiring a native-player handoff.
Microsoft says a Teams join link can prompt the user to continue in the browser or join on the Teams app, and its town-hall help says selecting **Join event** launches the event in Teams while mobile web browsers are not currently supported for town-hall attendance.
(xref: `youtube_universal_links_help_page`; xref: `youtube_in_app_browser_ios_help_page`; xref: `vimeo_share_video_mobile_web_help_page`; xref: `vimeo_inline_playback_mobile_help_page`; xref: `microsoft_join_meeting_without_account_help_page`; xref: `microsoft_attend_town_hall_help_page`)

That means the chain layer needs one compact distinction:
- some routes are still just ordinary public co-current aliases and belong in `534`,
- some routes stay current only for a named audience subset and belong in `535`,
- some routes matter because the holder possesses the full bearer path and belong in `537`,
- some routes are really player-host render shells and belong in `538`,
- some facts are really about the carrier that launched the route and belong in `540` or `541`,
- and some same-object facts are specifically about an **installed-app launch or app-preferred handoff** that changes the container and practical path without automatically changing chain control.

Without that distinction, reviewers tend to make one of four mistakes:
- they treat an app-open path as if it were the new current head,
- they flatten an installed-app launch into `534` even though the practical difference is the app/container jump rather than a second browser/public route,
- they let the app path outrank the citation-safe browser/public default even when the same answer is still recoverable on the web,
- or they restate app-launch behavior as generic carrier weirdness even though the real missing fact is the **target container and launch class after the carrier or link was opened**.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object app-launch aliases + browser-default retention**.

## This is not the same thing as `384`, `414`, `471`, `534`, `538`, `540`, or `541`

`384` governs whether an election office should publish or retire a mobile app at all, how its app-store identity/disclosures work, and how official website/help recovery remains visible before install.

`414` governs constrained browsers, webviews, and in-app browser containers around ordinary official pages.

`471` governs office-exposed copy/share controls and native-share handoff truthfulness.

`534` governs still-current **public sibling routes** for the same answer.

`538` governs still-current **player-host or embed-render shells** for the same answer.

`540` governs the nearby but different case where a reminder, notification, inbox entry, or delivery email is merely the **carrier** and should not be mistaken for the route.

`541` governs the nearby but different case where the delivered carrier target no longer controls when opened.

`543` governs the nearby but different case where the same object comes back through history, Continue Watching, recents, or remembered progress and the real question is memory-shaped re-entry rather than app-launch classification.

`544` governs the nearby but different case where the same object stays current but playback jumps to a selected moment through transcript/chapter/table-of-contents controls and the real question is player-internal navigation rather than app-launch classification.

`542` is different.
It says that sometimes one same-object chain should keep:
- one browser/public current head or fallback anchor,
- plus one or more **installed-app launch aliases** or open-in-app deep-link classes,
- while recording that those app paths matter for reproduction or delivery claims **without** letting the app path silently replace the archive's present-tense default.

If the real ambiguity is “should we have published an app or how does the app-store listing behave,” use `384`.
If the real ambiguity is “the browser container itself hid source identity or recovery,” use `414`.
If the real ambiguity is “the reminder/email/notification is being mistaken for the route,” use `540` or `541`.
Use `542` only when the carrier/route split is already understood but the archive still needs to classify the **installed-app launch or app-preferred target** for the same media object.

## Default rule: record the app-launch alias, keep the browser/public default unless another doc says otherwise

Inside one `528` same-object chain, reviewers MAY keep a compact **app-launch alias note** when all of the following hold:

1. **The underlying object is still the same.**
   The browser path and app-launch path still resolve to the same office-controlled event, recording, or published media answer.
2. **The practical difference is the launch/container class.**
   The decisive fact is that the route opened through an installed app, open-in-app prompt, universal link, or app-preferred deep link rather than staying on the ordinary browser/public page.
3. **Treating the app path as just another public alias would mislead.**
   A reader could mistake the installed-app route for the citation-safe ordinary-public default when the real difference is app/container behavior.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `526` and `529` can still name the browser/public default, or `533` can honestly say no ordinary-public media head exists and point to the best fallback anchor instead.
5. **The app-launch fact still matters.**
   The archive would lose useful truth if it omitted how the same answer launched in-app, required an app on a device class, or exposed a browser-vs-app choice that changed reproduction.

When those conditions hold, keep the head/default under `529–530`, keep any scope or bearer rule under `535` or `537`, and add one `542` app-launch note.
Do **not** silently promote the installed-app launch into the chain's current head.

## Minimal app-launch-alias grammar

When a same-object chain has a browser/public default plus a relevant app-open path, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<ordinary public current tuple|none>; app_aliases=<route family>; app_class=<universal_link|open_in_app_prompt|installed_app_deep_link|app_required_mobile|in_app_browser_jump|other bounded class>; route_scope=<ordinary_public_app|scoped_app|capability_app>; cite_default=<head|fallback anchor>; cite_app_when=<app-specific reproduction, launch-prompt, or device-class claim>; promote_app=<no>; basis=<why the app path mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **what launched where** without making every app-preferred handoff sound like a fresh head or a safer citation target than the browser/public route.

## When to use an app-launch alias note

Typical uses include:

1. **Browser link that auto-opens the installed app**
   A public watch or share link opens the same object through an installed app, but the app path should not replace the browser/public default in the chain.
2. **Join or watch flow that offers browser-vs-app choice**
   The same event can be reached through Teams for web or Teams app, and the archive needs to preserve that launch fork without reclassifying the object itself.
3. **Mobile device class where the app is required even though a broader head exists elsewhere**
   A device-specific app requirement matters for reproduction, but the app requirement does not itself become the archive's general citation default.
4. **Link opened from inside the platform app into an in-app browser or app-owned container**
   The archive needs the bounded app/container fact, but the controlling same-object route is still governed elsewhere.

## Citation rule

By default, later notes SHOULD still cite the **browser/public head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `542` app-launch alias SHOULD be cited only when the later claim is specifically about:
- whether the same object auto-opened in an installed app,
- whether the user saw an open-in-app prompt or browser-vs-app launch choice,
- whether a device class required the app for that same object,
- or why the archive refused to let the app path outrank the browser/public default.

That means `542` preserves one honest app-container exception to head-first citation without letting app-preferred launch behavior quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `542` when:
- the decisive issue is whether the app exists, is official, or should be installed at all — use `384`,
- the decisive issue is that a browser/webview container hid source identity or broke recovery — use `414`,
- the decisive issue is simply that the same answer has another ordinary public route — use `534`,
- the decisive issue is that the route is current only for a defined audience subset — use `535`,
- the decisive issue is that the route mainly works because the holder already has the bearer path — use `537`,
- the decisive issue is that the same object is being rendered through a player-host or embed shell — use `538`,
- the decisive issue is still just that a reminder, notification, inbox entry, or delivery email carried the route — use `540`,
- the decisive issue is that the delivered target no longer controls when opened — use `541`,
- the decisive issue is that the same object came back through history, Continue Watching, recents, or remembered progress rather than through an app-launch fork — use `543`,
- the decisive issue is that the same object stayed current but the viewer jumped within it through transcript/chapter/table-of-contents controls rather than through an app/container fork — use `544`,
- or the archive is trying to preserve full app analytics, per-device launch telemetry, or app-install histories as a new evidence surface.

If deleting the app-launch fact would erase **how the same object launched or which container a user landed in** but not the underlying chain-control truth, `542` is probably the right companion.
If deleting the app-launch fact would erase the whole routing or access story, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_results_stream_mar_2026; head=public YouTube watch-page packet; app_aliases=youtube.com universal-link handoff into installed YouTube app; app_class=universal_link; route_scope=ordinary_public_app; cite_default=head; cite_app_when=proving that iOS opened the same watch object in the YouTube app; promote_app=no; basis=the same public answer launched in-app, but the browser watch page remained the archive's citation-safe default`
- `chain=city_budget_town_hall_mar_2026; head=535 attendee town-hall route or published attendee recording route as separately bucketed; app_aliases=Join event launch into Teams app on mobile; app_class=app_required_mobile; route_scope=scoped_app; cite_default=head; cite_app_when=proving that mobile attendance required the Teams app even though desktop web or later recording routes existed; promote_app=no; basis=the app requirement mattered for reproduction but did not replace route-control logic`
- `chain=regional_candidate_forum_replay; head=public YouTube watch-page packet; app_aliases=explicit "Open in YouTube" prompt from a shared link; app_class=open_in_app_prompt; route_scope=ordinary_public_app; cite_default=head; cite_app_when=proving that the shared route offered an app-open choice before playback; promote_app=no; basis=the prompt changed container choice, not the controlling same-object answer`

## Tie-breaker when reviewers ask “if people actually opened it in the app, why isn't that the head?”

Ask three questions:
- does the app path prove **where the same object launched** rather than **what the archive says controlled for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to the installed-app route,
- and is the missing fact really the browser-vs-app launch/container difference rather than a new scope, bearer, render, or head-selection rule?

If yes, keep current control under `529–530`, preserve any real scope or bearer rule under `535` or `537`, and record the app/container truth under `542`.
Do **not** let the installed-app launch absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same object launched through an installed app, open-in-app prompt, universal link, or other app-preferred handoff.
Tighten `542` first.
Only add another numbered surface when the ambiguity is really about a new gate object, a new carrier class, or a new browser/container boundary rather than about **app-launch classification inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that app-launch paths still drift between `384`, `414`, `534`, `538`, `540`, and `541` after this compact note contract exists.
