# 648 — Official voter-information platform media authenticity-cue packet cast target AirPlay mirroring second screen and non-governing wrapper-remote-playback-state firewall

**Track:** Shared / Public surfaces

This document covers a narrow packet-wrapper problem:
**later packets can preserve cast-target chips, AirPlay destination posture, screen-mirroring state, wireless-display projection state, remote-playback-session indicators, or similar visible wrapper remote-playback-state layers around same-route detached derivatives, and later readers can start mistaking that second-screen posture for source-native viewing environment, official second-screen publication, office-preferred display context, or the packet's governing member.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/503-official-voter-information-platform-remote-playback-casting-and-second-screen-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/550-official-voter-information-platform-media-remote-playback-target-states-cast-controller-splits-and-sender-default-retention-discipline.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/593-official-voter-information-platform-media-authenticity-cue-player-state-occlusion-reduced-context-suppression-and-non-absence-inference-firewall.md`
- `docs/600-official-voter-information-platform-media-authenticity-cue-detached-derivative-family-quickmap-mixed-packets-and-anti-fragmentation-firewall.md`
- `docs/646-official-voter-information-platform-media-authenticity-cue-packet-fullscreen-theater-mode-miniplayer-picture-in-picture-popout-and-non-governing-wrapper-player-state-firewall.md`

## What this is for

Use `648` when a later packet preserves or reenacts a **visible wrapper remote-playback-state layer** around same-route detached derivatives:
- a cast target selected,
- an AirPlay destination selected,
- screen mirroring or wireless-display projection active,
- a TV / projector / room-display destination badge,
- a remote-playback-session indicator,
- sender-controls-target posture visible in the later packet,
- or similar later packet second-screen foregrounding.

Those remote-playback surfaces are real packet facts and should be preserved honestly.
But they are still **later wrapper-added second-screen posture**, not automatic proof of:
- source-native viewing environment,
- official second-screen publication or canonical display context,
- office-preferred display routing,
- or the packet's governing member.

Current primary-source guidance is already enough to justify one bounded remote-playback-state bridge.
Google's Chromecast help says YouTube videos can be cast from the YouTube app and YouTube.com and that devices on the same Wi-Fi network can cast.
Vimeo Help says videos can be cast via AirPlay or Chromecast from its mobile apps and that Chromecast is also supported in embedded players in web browsers.
Apple's AirPlay guidance says video can be streamed to a TV or Mac, distinguishes direct streaming from screen mirroring, and says iPhone or iPad can automatically AirPlay to frequently used devices.
Microsoft Support says Windows can cast to a wireless display and Microsoft Teams Rooms can receive cast content from desktop or mobile devices.
That is enough for one bounded firewall here.
(xref: `google_chromecast_youtube_cast_help_page`; xref: `vimeo_cast_videos_airplay_chromecast_help_page`; xref: `apple_support_airplay_stream_video_or_mirror_iphone_ipad_page`; xref: `w3c_remote_playback_api_candidate_recommendation`; xref: `microsoft_windows_screen_mirroring_wireless_display_page`)

`648` exists so maintainers can say:
**this packet preserved a later cast-target / AirPlay / mirroring / second-screen posture around same-route detached derivatives, and that posture mattered for how later readers interpreted the packet, but the remote-playback layer itself does not silently prove source-native viewing environment, official second-screen publication, office-preferred display context, or the governing member.**

## Why this is distinct

`503` asks whether remote playback, casting, or second-screen transfer became the **authority-boundary** problem on the public surface in the first place.

`550` asks whether the same current media object preserved **remote target / controller-split state** — cast target, AirPlay destination, mirrored display, projector session, or similar — while the same object still controlled.

`593` asks whether reduced-context playback caused surrounding authenticity-adjacent cues to fall out of view, creating an occlusion / non-absence-inference problem.

`646` asks whether a later packet preserved **player-container posture** such as fullscreen, theater mode, miniplayer, picture-in-picture, or popout.

`648` asks a different question:
**did a later packet add or preserve a visible remote-playback layer — cast target, AirPlay destination, screen mirroring, wireless-display projection, remote-playback-session indicator, or similar second-screen posture — and did later readers start overreading that layer as if it proved source-native viewing environment, official second-screen publication, office-preferred display context, or the packet's governing member?**

If the real problem is remote playback as a voter-facing authority boundary, use `503`.
If the real problem is same-object cast-target / controller-split state while the current head still controls, use `550`.
If the real problem is cue hiddenness caused by reduced-context viewing, use `593`.
If the real problem is player-container posture rather than second-screen posture, use `646`.
Use `648` only when the missing distinction is **wrapper remote-playback-state posture itself** around a later detached derivative packet.

## Decision test

Use `648` when all three conditions hold:

1. later evidence preserves or reenacts a **visible remote-playback layer** around same-route detached derivatives — for example a cast target selected, an AirPlay destination selected, screen mirroring active, wireless-display projection active, a room-display destination badge, or similar second-screen posture;
2. that layer is **later wrapper-added remote-playback state**, not proof that the underlying source route itself officially published a second-screen edition, officially preferred one display context, or officially made the packet governing; and
3. later readers are drifting toward treating that layer as if it proved **source-native viewing environment, official second-screen publication, office-preferred display context, or the governing member**.

If any condition fails, keep the packet under the narrower doc that already owns the real problem.
If the surviving packet is still mainly a remote-playback authority-boundary problem, same-object remote-target problem, cue-occlusion problem, or player-state problem with some visible second-screen posture around it, keep authority-boundary in `503`, keep same-object remote-target state in `550`, keep cue-occlusion in `593`, keep player-container posture in `646`, and add one bounded `648` remote-playback-state note only if the visible second-screen layer itself changed the reading.

## Keep remote playback, same-object controller splits, player state, and cue occlusion separate

At minimum, keep these layers separate:
1. **current office control** — the current written/help lane and current media head (`194`, `529`, `530`);
2. **surviving detached derivative** — which `595–599` member, if any, the packet actually preserved;
3. **family routing** — whether the packet needed `600` because no single detached derivative dominated;
4. **authority-boundary / same-object remote-playback class** — whether casting / second-screen transfer already became the route problem or remained a same-object sender-target state (`503`, `550`);
5. **cue occlusion** — whether surrounding authenticity-adjacent cues fell out of view because playback moved onto a reduced-context screen (`593`);
6. **wrapper-added player state** — fullscreen / miniplayer / popout posture rather than second-screen transfer (`646`);
7. **carrier wrapper** — slide deck, PDF memo, browser shell, doc shell, saved page, ticket, or email thread (`437`, `490`, `600`);
8. **assembly state** — whether later materials also fused several observations into one stronger-looking posture (`591`).

That separation matters because later packets can otherwise make two different mistakes:
- treating a visible cast target, AirPlay destination, or mirrored-display badge as if it proved the source itself was natively a TV edition, projector edition, room-display edition, or officially preferred display context; or
- letting a later second-screen wrapper become evidence that the packet itself is governance-bearing rather than just a later display layer around one preserved derivative.

`648` exists so the archive can keep that later visible remote-playback layer **truthful but non-governing**.

## Minimal wrapper-remote-playback-state note grammar

When wrapper remote playback matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; governing_member=<595|596|597|598|599|600|none>; wrapper_remote_playback_kind=<chromecast_cast|airplay_stream|screen_mirroring|wireless_display_projection|remote_playback_api_session|mixed|unknown>; controller_split=<sender_controls_target|shared_queue|mirrored_sender|target_self_fetches|unknown>; target_visibility=<remote_screen_only|sender_plus_remote|duplicate_display|second_screen_only|unknown>; state_scope=<viewer_selected|platform_suggested|platform_automatic|device_default|session_persistent|unknown>; source_native_viewing_environment_proved=<forbid>; official_second_screen_publication_proved=<forbid>; official_display_context_preference_proved=<forbid>; governing_member_from_remote_playback_state=<forbid>; carrier_wrapper=<browser_shell|doc_shell|pdf_shell|review_shell|slide_deck|saved_page|ticket|email_thread|none>; cite_default=<head|fallback anchor>; use_648_when=<remote_playback_state_changed_reading>; promote_wrapper_remote_playback_state=<no>; basis=<why the later second-screen layer needed one bounded note>`

This is a note contract, not a new schema.
It exists so packets and summaries can say “this later packet also carried a visible cast-target / AirPlay / mirroring / second-screen posture” without minting a new detached-derivative member or silently rewriting source environment, official display preference, or packet governance.

## Typical uses

1. **Cast-target overread**
   A later packet shows the preserved derivative on a TV cast target and later readers start retelling the source as if the office itself published a TV-native edition rather than a later cast state.
2. **Automatic AirPlay overread**
   A later packet foregrounds a suggested or automatic AirPlay destination and later readers start treating that familiar second-screen target as if it proved the office preferred or officially adopted that display context.
3. **Mirrored-display overread**
   A later packet preserves mirrored-display or wireless-projection posture and later readers start treating the projected screen as if it were the controlling route rather than a later display layer around one detached derivative.
4. **Second-screen plus detached derivative bundle**
   A later packet carries a still image, shared URL, copied metadata, or transcript excerpt from the same route and also preserves a visible cast-target / AirPlay / second-screen cue; keep the detached derivative governing and use `648` only for the later remote-playback-state drift.

## When not to use this

Do **not** use `648` when:
- the decisive issue is still remote playback / casting as a voter-facing authority boundary (`503`),
- the decisive issue is still same-object remote-target or controller-split state (`550`),
- the decisive issue is still cue hiddenness / reduced-context non-absence inference (`593`),
- the decisive issue is still wrapper player-state posture (`646`),
- the decisive issue is still a mixed detached-derivative packet with no dominant member (`600`),
- or the decisive issue is still cross-state composite assembly (`591`).

If deleting the visible second-screen layer leaves an ordinary remote-playback-boundary, same-object remote-target, cue-occlusion, or player-state problem, use the narrower doc and omit `648`.
If deleting it would erase **why a later second-screen layer changed the way the packet was being read or retold**, `648` is probably right.

## Promotion rule

Future media additions should usually **not** be promoted just because a later packet carried cast-target selection, AirPlay destination posture, screen mirroring, wireless-display projection, remote-playback-session state, or similar second-screen posture around same-route detached derivatives.
Tighten `503`, `550`, `593`, `600`, `646`, or `648` first.
Only add another numbered doc when repeated wrapper-remote-playback-state mistakes still cannot be expressed as:
- one governing `595–599` member,
- or a mixed-packet routing note under `600`,
- plus one bounded wrapper-remote-playback-state note under `648`.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless wrapper-remote-playback-state drift still persists after this compact bridge exists.

## Sources

- Google Help — How to cast from the YouTube app and YouTube.com. (xref: `google_chromecast_youtube_cast_help_page`)
- Vimeo Help Center — How to cast videos via AirPlay or Chromecast. (xref: `vimeo_cast_videos_airplay_chromecast_help_page`)
- Apple Support — Use AirPlay to stream video or mirror the screen of your iPhone or iPad. (xref: `apple_support_airplay_stream_video_or_mirror_iphone_ipad_page`)
- W3C — Remote Playback API Candidate Recommendation. (xref: `w3c_remote_playback_api_candidate_recommendation`)
- Microsoft Support — Screen mirroring and projecting to your PC or wireless display. (xref: `microsoft_windows_screen_mirroring_wireless_display_page`)
