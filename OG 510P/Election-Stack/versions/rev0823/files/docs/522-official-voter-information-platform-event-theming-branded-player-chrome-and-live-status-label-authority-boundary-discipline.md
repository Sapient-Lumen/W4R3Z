# 522 — Official voter-information platform event theming, branded player chrome, and live-status-label authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information media routes whose surrounding event shell or player chrome is organizer-configurable enough to change how the route looks and feels without changing the underlying recording or event itself**:
countdown themes,
trailers on watch pages,
banner images,
logos,
theme colors,
customized player layouts,
backgrounds,
name-tag colors,
before-event schedule overlays,
“latest video” substitutions,
hidden or suppressed live-status labels,
and similar organizer-controlled presentation wrappers around one official media route.

It does **not** ban ordinary theming or event customization.
It adds one narrow rule:
**when an office or platform can materially restyle an official media event shell, that presentation layer should stay visibly subordinate to the current written/help lane and should not quietly blur whether the public is looking at a pre-live shell, a true live route, or a replay/other shell.**

It composes with:
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/508-official-voter-information-platform-upcoming-event-pages-premiere-watch-pages-and-pre-live-countdown-authority-boundary-discipline.md`
- `docs/509-official-voter-information-platform-post-live-archive-replay-and-ended-event-surface-authority-boundary-discipline.md`
- `docs/514-official-voter-information-platform-titles-descriptions-thumbnails-posters-and-metadata-wrapper-authority-boundary-discipline.md`
- `docs/516-official-voter-information-platform-live-edge-behind-live-state-latency-and-watch-live-recovery-authority-boundary-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `docs/521-official-voter-information-platform-information-panels-context-boxes-disclosure-labels-and-policy-wrapper-authority-boundary-discipline.md`
- `docs/524-official-voter-information-platform-media-route-state-lexicon-badge-normalization-and-capture-order-discipline.md`
- `artifacts/checklists/official-voter-information-platform-event-chrome-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-event-chrome-surface-payload.json`

## Why this exists (bounded)

The archive already covers the pre-start event shell itself (`508`), the post-live replay shell (`509`), mutable titles/thumbnails and similar metadata wrappers (`514`), live-vs-behind-live state (`516`), source-identity wrappers (`520`), and platform-added policy/context wrappers (`521`).
A smaller but distinct seam still remains:
**the office can restyle, decorate, or visually tune the same official media route enough that the shell starts sounding more current, more official, or more settled than the underlying route state actually justifies.**

Current platform guidance is specific enough to justify a compact control here.
YouTube’s current Premiere help says a public watch page exists before the Premiere starts, that a trailer can play there, and that organizers can choose a different countdown theme; after the Premiere ends, the countdown theme is not included in the resulting regular upload.
Vimeo’s current live-event player customization help says organizers can customize the appearance and features available on the live event player, can change those settings at any time without re-embedding the player, and can choose before-event states such as showing schedule overlays, “this event hasn’t started yet” messages, or the latest archived video instead of a thumbnail/schedule.
Its current help also says organizers can hide the **Live** label from a live event player.
Microsoft’s current town-hall theming help says organizers can add banner images and logos and change theme colors that affect event buttons, icons, and email links, while its current attendee-screen help says organizers can customize event-screen layouts, background, and name-tag colors during the event.
(xref: `youtube_customize_premiere_help_page`; xref: `vimeo_customize_live_event_player_help_page`; xref: `vimeo_hide_live_label_help_page`; xref: `microsoft_customize_town_hall_help_page`; xref: `microsoft_manage_what_attendees_see_teams_help_page`)

So the bounded question is not “may official live-event shells be branded or visually customized?”
Of course they may.
The bounded question is smaller:
**once a platform lets an office restyle the shell around official election media, does that shell start sounding like the controlling proof of currentness, live-ness, or authority even though the visual treatment is only wrapper state?**

If the boundary is already `522` but the archive needs to normalize hidden or ambiguous state cues into one compact route-state note, use `524`.

## This is not the same thing as pre-start shells, replay shells, metadata wrappers, live-edge state, identity wrappers, or policy wrappers

`508` asks whether **the pre-start event shell itself** starts acting like the current official answer page before the event begins.

`509` asks whether **the surviving replay or ended-event shell** starts acting like the current answer or default return path after the event ends.

`514` asks whether **titles, descriptions, thumbnails, posters, or playlist-local labels** become the controlling summary or currentness claim.

`516` asks whether **the viewer is materially behind the true live edge** even while the event is still live.

`520` asks whether **bylines, handles, badges, uploader names, or profile cards** start sounding like the whole proof that the route is official and current.

`521` asks whether **platform-added context panels, disclosure labels, ratings, sensitivity cues, or protection banners** start sounding like the office’s whole explanation of authority or legal effect.

`522` asks a different question:
**once the office or organizer can restyle the same official event shell with banners, logos, colors, layout modes, before-event substitutions, trailers, or hidden live badges, does that presentation layer start to outrun the route’s actual state and the current written/help lane?**

A route can pass `508`, `509`, `514`, `516`, `520`, and `521` and still fail `522` if:
- a heavily branded pre-live shell feels like the settled current instruction page merely because it looks polished and official;
- the shell shows a latest archive or trailer before the event starts and the office never clarifies that the public is still looking at a pre-live wrapper rather than the controlling answer lane;
- a live-status badge is hidden or visually minimized and viewers stop being able to tell whether they are seeing a live event, a waiting room, or a replay-like shell;
- organizer-controlled colors, logos, or screen layouts make a same-event route look newly updated even though only decoration changed;
- or during a still-live event, the attendee-facing layout becomes the practical authority cue while the current written/help lane and true route state are harder to recover.

## Event chrome is wrapper state, not proof of current authority

The public-safe posture is simple:
**banners, logos, countdown themes, layout modes, trailers, and similar organizer-controlled event chrome are wrapper state around one official media route; they are not automatic proof that the route is current, official, live, or complete enough to replace the written/help lane.**

At minimum, keep these layers distinct:
1. the current written page, FAQ/help entry, official notice, or office contact that still controls action-changing next steps;
2. the underlying official event/media route itself;
3. the organizer-controlled shell styling or player customization shown around that route;
4. any state cue about whether the route is pre-live, live, behind-live, ended, or replay-oriented;
5. and any separate recovery path the office provides when the shell’s visual treatment could mislead about route state.

That distinction matters because design polish carries authority.
A voter, journalist, or partner may infer that a more branded or better staged shell means:
- this must be the current official answer,
- this must now be live,
- this must have been newly reviewed,
- or this must supersede the plainer written lane.

But the vendor guidance points the other way.
The platforms describe these as configurable presentation features, some of which can change without changing the embed, route, or underlying recording.
For `522`, the bounded rule is simply to stop the archive from treating that shell styling as though it were a self-proving currentness signal.

## Live/pre-live/replay state should stay legible even when the shell is customized

`522` is especially load-bearing where shell customization can blur route state.
YouTube says the public watch page exists before the Premiere starts and that after the Premiere ends the countdown theme does not remain in the uploaded video.
Vimeo says organizers can choose before-event states such as schedule overlays or showing the latest archive, and separately says they can hide the live label.
Microsoft says event theming and attendee-screen customization can change the presentation viewers receive without rewriting the underlying official policy/help lane.
(xref: `youtube_customize_premiere_help_page`; xref: `vimeo_customize_live_event_player_help_page`; xref: `vimeo_hide_live_label_help_page`; xref: `microsoft_customize_town_hall_help_page`; xref: `microsoft_manage_what_attendees_see_teams_help_page`)

So `522` should bias toward explicit review whenever customized shell treatment could make one state look like another:
- pre-live shell versus actual live program,
- live program versus replay-like or archive-like shell,
- same underlying event with only decorative changes versus a substantively newer official answer,
- or attendee-facing production layout versus the written/help lane that still controls operational questions.

## Minimum review artifact

For the exact route reviewed, capture compact evidence of:
- which shell elements were customized there;
- what state the route was actually in when reviewed (pre-live, live, behind-live, ended, replay, mixed, or unclear);
- whether the shell visually exposed or obscured that state;
- whether the current written/help lane remained easy to recover;
- and whether the same route looked materially different across native, embedded, or attendee-facing views.

Avoid exporting private production controls, backstage layouts, or internal operator artifacts unless they themselves became part of the public route under review.

## Minimum claims / review questions

1. **Shell-state claim:** the reviewed public route recorded which organizer-controlled chrome or layout treatment was present there.
2. **State-legibility claim:** viewers could still tell whether the route was pre-live, live, replay, or mixed without inferring from polish alone.
3. **No-authority-lift claim:** customized event chrome did not silently become the office’s whole proof of currentness, authority, or superseding status.
4. **Recovery claim:** the current written/help lane remained recoverable even when the media shell was heavily themed or visually persuasive.

Review prompts:
- Which route was reviewed: native event page, embed, attendee view, or another public shell?
- Which shell elements changed the presentation there?
- Could a viewer tell whether the route was pre-live, live, behind-live, or replay/ended?
- Did any banner, logo, trailer, latest-video substitution, or hidden live badge make the route feel newer or more dispositive than it really was?
- If the shell looked persuasive on its own, was the current written/help lane still easy to find?

## Related artifacts

- Template payload: `artifacts/templates/official-voter-information-platform-event-chrome-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-event-chrome-surface-checklist.md`

## Sources

- YouTube Help: Premiere a new video (xref: `youtube_customize_premiere_help_page`)
- Vimeo Help Center: How to customize my live event's player (xref: `vimeo_customize_live_event_player_help_page`)
- Vimeo Help Center: Hide the 'Live' label from my live event player (xref: `vimeo_hide_live_label_help_page`)
- Microsoft Support: Customize a town hall in Microsoft Teams (xref: `microsoft_customize_town_hall_help_page`)
- Microsoft Support: Manage what attendees see in Microsoft Teams (xref: `microsoft_manage_what_attendees_see_teams_help_page`)
