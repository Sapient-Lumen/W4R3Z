# 498 — Official voter-information platform follows, subscriptions, and live-event reminder authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **platform-native relationship and reminder surfaces attached to already-open official voter-information media or official platform channels**:
channel subscriptions,
follow states,
notification-bell settings,
“notify me” or reminder registrations for premieres or scheduled livestreams,
platform inbox/bell histories for those follows or reminders,
and similar media-platform features that let the voter treat a platform-managed subscription state as the office’s durable notice lane.

It does not ban follows or reminders.
It adds one narrow control:
**when a platform lets the voter follow an official media account, subscribe to its channel, or register for a scheduled-event reminder, that platform-managed state should stay visibly subordinate to the current official page/help lane instead of quietly becoming a shadow standing subscription for still-current official voter instructions.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/366-official-voter-information-broadcast-alerts-social-posts-and-linkback-discipline.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/370-official-voter-information-emails-newsletters-reminders-and-forward-context-discipline.md`
- `docs/389-official-voter-information-calendar-subscriptions-ics-downloads-and-reminder-handoff-discipline.md`
- `docs/412-official-voter-information-browser-permission-prompts-geolocation-notifications-and-device-capability-fail-open-discipline.md`
- `docs/475-official-voter-information-web-push-notifications-subscription-lifecycle-and-stale-notification-withdrawal-discipline.md`
- `docs/496-official-voter-information-platform-autoplay-end-screens-cards-and-play-next-authority-boundary-discipline.md`
- `docs/497-official-voter-information-platform-watch-later-saved-playlists-offline-downloads-and-smart-download-authority-boundary-discipline.md`
- `artifacts/checklists/official-voter-information-platform-follow-reminder-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-follow-reminder-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), general short-form broadcast alerts (`366`), email reminders (`370`), calendar objects (`389`), browser permissions (`412`), browser-origin web push (`475`), play-next pivots (`496`), and saved-media shelves (`497`).
That still leaves a small but distinct layer:
**platform-native follow, subscribe, and reminder surfaces that can make a channel relationship or one-click event reminder feel like the office’s standing current-notice lane even though the office does not control delivery, ranking, inbox visibility, or reminder persistence in the same way it controls its own page/help route.**

Current platform guidance is specific enough to justify this as a bounded control.
YouTube’s current notification help says subscribing to a channel automatically gives the viewer personalized notifications, that the viewer can switch between All, Personalized, and None, that All can generate mobile, web, or inbox notifications for long-form uploads and live streams, and that re-subscribing resets notification settings.
YouTube’s current subscription help says subscribers automatically get highlight notifications and see new videos in the Subscriptions tab, while recommendations for other channels can appear alongside that feed.
YouTube’s current Premiere help says viewers can set a reminder and then receive one notification about 30 minutes before the Premiere and another when it starts.
Vimeo’s current follow help says viewers can follow people, groups, categories, and channels and later adjust those viewing preferences, while Vimeo’s on-site notifications help says people can receive on-site notifications when someone they follow uploads a new video.
TikTok’s current LIVE Events help says viewers can register for a LIVE Event, receive notifications, and optionally add the event to the device calendar; event times are shown in the viewer’s local time.
Vimeo OTT’s current live-event help says creators can notify followers when a broadcast begins, that those email notifications can take up to 30 minutes to arrive, and that branded app users do not receive push notifications.
(xref: `youtube_manage_notifications_computer_help_page`; xref: `youtube_subscribe_channels_android_help_page`; xref: `youtube_premiere_new_video_help_page`; xref: `vimeo_follow_unfollow_people_groups_categories_channels_help_page`; xref: `vimeo_about_on_site_notifications_help_page`; xref: `tiktok_live_events_help_page`; xref: `vimeo_ott_live_event_notify_followers_help_page`)

So the bounded question is not “should voters ever follow an official channel?”
Of course some will.
The bounded question is smaller:
**once the voter follows, subscribes, or registers for a platform reminder, does that platform-managed relationship start to look like a durable, complete, still-current official notice lane even when delivery is partial, ranked, delayed, reset, mixed with recommendations, or silently absent on some device/app combinations?**

## This is not the same thing as web push, calendar reminders, saved-media shelves, or the recording lane

`369` asks whether the **official recording/channel lane itself** carries enough date, scope, correction, and linkback discipline.

`389` asks whether a **calendar object** or `.ics` reminder survives detached from the page.

`475` asks whether **browser-origin web push** stays truthful about permission state, subscription lifecycle, delayed delivery, and reopen landings.

`497` asks whether **Watch Later, playlists, or offline libraries** make old media feel current simply because they were saved.

`500` asks whether **comments, live chat, Q&A, polls, or reactions beside the media** start to feel like the office’s current help desk or correction lane.

`508` asks whether a **public upcoming-event shell before start** begins to feel like the current official answer page even before the recording or livestream is underway.

`518` asks whether **the voter must register, get invited, be approved, or satisfy another audience gate before actually entering the media route**.

`498` asks a different question:
**does a platform-managed follow, subscription, or reminder state begin to function like a standing official notice lane for future media events?**

If the harder problem is **later resurfacing because the platform remembered prior viewing through history, continue-watching, recents, or resume-state**, use `506`.
If the harder problem is **the public pre-start event shell itself rather than the relationship or reminder state that led the voter there**, use `508`.
**once the voter creates or inherits a platform-native follow / subscribe / reminder relationship, does that relationship begin to feel like the office’s standing authoritative notice service even though the platform decides how much to show, when to show it, and what to place beside it?**

A route may pass `369`, `389`, `475`, and `497` and still fail `498` if:
- the voter believes “Subscribed + All notifications” means every important operational change will reach them,
- a premiere or live-event reminder fires on time but the actual controlling written route changed before the stream starts,
- a follow state is reset, filtered, or absent on one device and the office still talks as though notification delivery is guaranteed,
- a subscriptions feed or notification inbox mixes official uploads with unrelated recommended content that now looks like one coherent notice lane,
- or the office treats “follow us for updates” as though it were equivalent to a durable official help subscription it actually controls.

## Follow state is a provenance signal, not a completeness guarantee

The public-safe posture is simple:
**a follow, subscription, or reminder registration proves only that the platform recorded some relationship or scheduled some alert; it does not prove complete delivery, currentness, or enough context to act safely without the current official page/help lane.**

At minimum, keep these layers distinct:
1. the current official page/help lane that still controls the answer,
2. the official channel or media account the office maintains,
3. the viewer’s platform-managed follow/subscription/reminder state,
4. and the platform’s own ranking, inbox, feed, or notification surfaces that decide what the viewer actually sees.

That distinction matters because follow/reminder surfaces feel durable.
A voter often experiences “I’m subscribed to the county’s channel” or “I set a reminder for that election livestream” as stronger evidence than “I once saw the page.”
If the archive lets those layers collapse into one story, later observers cannot tell whether the voter relied on:
- the current official page,
- a platform follow state,
- a one-off reminder notification,
- a subscriptions feed ranked beside recommendations,
- or an inbox/bell history that no longer reflected the current situation.

## Personalized, ranked, or partial notification delivery is not the same thing as official completeness

Current platform guidance makes this explicit.
YouTube says channel subscriptions default to personalized notifications, that the definition of personalized differs by user, and that YouTube uses watch history, popularity, and notification-opening behavior to decide when to send some notifications.
It also says subscriptions can be seen in a subscriptions feed alongside recommendations.
Vimeo OTT says follower email notifications can take up to 30 minutes and that some branded-app users do not receive push notifications.
(xref: `youtube_manage_notifications_computer_help_page`; xref: `youtube_subscribe_channels_android_help_page`; xref: `vimeo_ott_live_event_notify_followers_help_page`)

For `498`, that means:
- the office should not imply that a platform follow state guarantees complete delivery,
- the office should not imply that absence of a notification means absence of a change,
- and a ranked feed or notification inbox should stay subordinate to the current official written answer lane.

## Reminder registration is useful, but the reminder is not the controlling edition

Scheduled-event reminders are attractive because they feel precise.
But the reminder can still outrun the controlling page.
YouTube says a Premiere reminder yields one notice about 30 minutes before the event and another when it starts.
TikTok says LIVE Event times are shown in the viewer’s local time and viewers can also add the event to the device calendar.
(xref: `youtube_premiere_new_video_help_page`; xref: `tiktok_live_events_help_page`)

That means `498` should treat reminder registration as a **pointer to re-enter the current official route**, not as proof that the scheduled media event itself remains the best or only place to learn the rule.
If locations, deadlines, accessibility guidance, or correction notices changed after the reminder was set, the voter still needs a clear path back to the current written lane before acting.

## Follow and reminder surfaces can inherit adjacency and recommendation drift

A subscriptions feed or notification inbox is not a sterile official archive.
It can mix:
- official uploads,
- older channel items,
- recommendations,
- related channels,
- or platform-side discovery surfaces.

YouTube’s subscription help says a subscriber sees new videos in the Subscriptions tab and also receives recommended channels on the screen.
Vimeo’s follow help similarly frames follows inside a broader feed/viewing-preferences surface rather than as a sealed official notice queue.
(xref: `youtube_subscribe_channels_android_help_page`; xref: `vimeo_follow_unfollow_people_groups_categories_channels_help_page`)

So `498` should keep at least these states separate:
- **subscribed/following official channel only**
- **subscribed with default or personalized notifications**
- **subscribed with all notifications**
- **single-event reminder registered**
- **event reminder also exported to device calendar**
- **follow/feed mixed with recommendations or unrelated channels**
- **notification capability absent, delayed, or reset**

## Relationship reset and capability variance matter

Platform-managed relationship state is not permanent.
YouTube says re-subscribing resets channel notification settings.
Vimeo says unfollowing does not itself generate a notification.
Vimeo OTT says some branded apps do not send push notifications to users.
TikTok says adding a LIVE Event to the device calendar may require calendar access.
(xref: `youtube_manage_notifications_computer_help_page`; xref: `vimeo_follow_unfollow_people_groups_categories_channels_help_page`; xref: `vimeo_ott_live_event_notify_followers_help_page`; xref: `tiktok_live_events_help_page`)

So the office should not promise:
- “follow us and you will definitely receive every important change,”
- “once subscribed, your notification state will stay fixed,”
- or “registering for the event means the reminder lane is equivalent to the office’s own current-help lane.”

## High-risk voter questions should bias toward rechecking the live written route

Some topics are especially unsafe to resolve from a follow/reminder surface alone:
- polling-place and drop-box locations or hours,
- registration-status, ballot-status, or cure guidance,
- ID rules near deadlines,
- emergency closures or weather contingencies,
- and any route where the safe next step is really `305` office/help recovery.

For those topics, `498` does not require the platform follow/reminder lane to be perfect.
It requires the archive to make sure the relationship surface points clearly back to the current written route before the voter acts.

## Minimal state taxonomy

Keep at least these states separate:
- **followed / subscribed with default or personalized delivery**
- **followed / subscribed with all-available notifications**
- **followed but notifications effectively absent or unsupported**
- **single-event reminder registered**
- **single-event reminder plus calendar export**
- **relationship/feed mixed with recommendations or unrelated channels**
- **relationship reset, unsubscribed, or reminder canceled**

The point is not to preserve each voter’s private notification history.
The point is to keep the public explanation honest about which relationship/reminder surfaces existed and which ones the office actually reviewed.

## Bounded follow/reminder trace minimum

A small public digest should make it possible to reconstruct:
- which official channels or scheduled media events were reviewed for follow/subscribe/reminder behavior,
- whether delivery was personalized, all-available, single-event, or otherwise capability-limited,
- whether the surface could mix recommendations or unrelated followed content beside the official item,
- whether reminders or event times could leave the platform into a calendar,
- where the current written recovery lane lived,
- and when the route was last verified.

It should **not** require subscriber rosters, per-viewer notification histories, watch histories, or inbox exports.

## Minimal claim-set

1. **Relationship-boundary claim:** follows, subscriptions, and reminder registrations stay subordinate to the current official page/help lane.
2. **Delivery-humility claim:** the office does not treat platform-managed notification delivery as complete, uniform, or guaranteed.
3. **Reminder-boundary claim:** event reminders point voters back to the current route rather than acting as the controlling edition themselves.
4. **Adjacency claim:** subscription feeds, notification inboxes, and followed-channel views do not inherit one clean official authority just because one official channel is present.
5. **Recovery claim:** the voter can recover the current page, FAQ/help entry, or named office contact before acting on time-sensitive guidance discovered from a follow/reminder surface.

## Canonical digest artifacts

Publish **small digests of follow/reminder posture**, not subscriber exports.

- **Follow/Reminder Surface Digest (FRSD):** digest of routes reviewed for follows, subscriptions, and scheduled-event reminders.
- **Follow/Reminder Delivery Note (FRDN):** optional note identifying personalized/default/all delivery posture and any unsupported or delayed-notification constraints.
- **Follow/Reminder Recovery Boundary Note (FRRBN):** optional note identifying how follow/reminder routes point back to the current written help lane.

## What belongs in the public follow/reminder payload

Keep the payload **small, route-aware, and explicit about relationship state, delivery limits, and recovery**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `follow_reminder_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_follow_reminder_contexts[]`
- `follow_reminder_provenance_note`
- `delivery_limitations_note`
- `feed_and_inbox_adjacency_note`
- `calendar_export_boundary_note`
- `current_help_recovery_note`
- `latest_notice_uri`
- `last_verified_at`
- `supersedes[]`
- `superseded_by[]`

## References

- YouTube Help — Manage YouTube notifications (computer). (xref: `youtube_manage_notifications_computer_help_page`)
- YouTube Help — Subscribe to YouTube channels (Android). (xref: `youtube_subscribe_channels_android_help_page`)
- YouTube Help — Premiere a new video. (xref: `youtube_premiere_new_video_help_page`)
- Vimeo Help Center — How to follow and unfollow people, groups, categories, and channels. (xref: `vimeo_follow_unfollow_people_groups_categories_channels_help_page`)
- Vimeo Help Center — About on-site notifications. (xref: `vimeo_about_on_site_notifications_help_page`)
- TikTok Support — TikTok LIVE Events. (xref: `tiktok_live_events_help_page`)
- Vimeo Help Center — How to set up a live event on Vimeo OTT. (xref: `vimeo_ott_live_event_notify_followers_help_page`)
