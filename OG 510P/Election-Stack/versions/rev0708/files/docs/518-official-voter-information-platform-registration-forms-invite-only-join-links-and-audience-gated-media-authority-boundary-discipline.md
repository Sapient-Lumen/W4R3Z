# 518 — Official voter-information platform registration forms, invite-only join links, and audience-gated media authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information media whose practical public surface is a platform-native access gate before the viewer can actually enter the event or watch the recording**:
live-event registration forms,
invite-only join links or emailed attendee access,
approval-gated webinar/town-hall entry,
members-only or audience-level-gated videos/livestreams,
and similar enrollment or audience-selection shells where the official media exists but the first thing the voter meets is not the recording itself — it is a gate describing how, whether, or for whom entry is allowed.

It does not ban registration, invitations, or audience gates.
It adds one narrow control:
**when official voter-information media is intentionally fronted by a registration, invite, approval, or audience gate, that gate should stay visibly subordinate to the current written/help lane instead of quietly acting like the whole official answer about who may watch, how to enter, or whether the office is still speaking publicly at all.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/370-official-voter-information-emails-newsletters-reminders-and-forward-context-discipline.md`
- `docs/498-official-voter-information-platform-follows-subscriptions-and-live-event-reminder-authority-boundary-discipline.md`
- `docs/508-official-voter-information-platform-upcoming-event-pages-premiere-watch-pages-and-pre-live-countdown-authority-boundary-discipline.md`
- `docs/510-official-voter-information-platform-search-results-homepage-recommendations-and-browse-feed-authority-boundary-discipline.md`
- `docs/512-official-voter-information-platform-unavailable-private-age-gated-region-blocked-and-playback-restricted-surface-authority-boundary-discipline.md`
- `docs/517-official-voter-information-platform-simulcast-mirrors-multi-route-live-events-and-redirect-chain-authority-boundary-discipline.md`
- `artifacts/checklists/official-voter-information-platform-registration-gate-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-registration-gate-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), reminder relationships (`498`), public pre-start event shells (`508`), platform discovery before entry (`510`), outright unavailable/private/restricted shells (`512`), and same-event multi-route live sets (`517`).
A smaller but distinct seam still remains:
**the office may intentionally keep an official media route behind a registration form, invite-only join link, approval step, membership requirement, or similar audience gate, and that gate itself can start sounding like the office’s public answer about availability, eligibility, or next steps.**

Current platform guidance is specific enough to justify a compact control here.
Vimeo’s current registration-form help says a live event or webinar can have registration turned on while it is being configured and even later before the event ends.
Its current registration FAQ says those registration forms are available on web browsers, but viewers in the Vimeo mobile application will not see the form at the start of the video.
Microsoft’s current town-hall scheduling help says organizers can turn on **Only allow invited people to join**, must publish the event for invited attendees to join, and can manage attendee invitations as part of the event configuration.
Its current attendee help says people join a town hall directly from the **Join event** link in their email invite.
YouTube’s current privacy help says live uploads can be made public, private, or unlisted.
Its current channel-membership help says creators can offer members-only live streams and members-only videos, while viewer-facing membership help says anyone can find a members-only video but only members at the right levels can watch it, and that those gated videos may still surface in Home and Subscriptions.
(xref: `vimeo_live_event_registration_form_help_page`; xref: `vimeo_registration_forms_faq_help_page`; xref: `microsoft_schedule_town_hall_help_page`; xref: `microsoft_attend_town_hall_help_page`; xref: `youtube_change_video_privacy_settings_help_page`; xref: `youtube_channel_memberships_perks_help_page`; xref: `youtube_membership_benefits_help_page`)

So the bounded question is not “may an office use registration or invited-attendee controls for an event?”
Of course it may.
The bounded question is smaller:
**once the official media route is fronted by an audience gate, does that gate stay legible as a gate with recovery paths, or does it start acting like the whole official answer about whether the public can watch, whether the event is still the current briefing, and where non-admitted viewers should go instead?**

## This is not the same thing as reminder registration, a pre-live shell, a discovery row, or a hard denial shell

`498` asks whether a **follow/subscription/reminder relationship** starts to feel like a standing official notice lane.

`508` asks whether a **public pre-start event shell** starts to feel like the current official answer before the event begins.

`510` asks whether **platform-ranked discovery surfaces** become the practical first-contact router before the voter even opens the gated route.

`512` asks whether a route resolves to a **platform-native unavailable/private/restricted shell** that sounds like the office’s final answer about availability.

`517` asks whether **several official live routes for the same event are intentionally in play at once**, so mirrors, embeds, or redirects start acting interchangeable.

`518` asks a different question:
**does an official media route require enrollment, invitation, approval, membership, or another audience gate, and if so, does that pre-access shell stay visibly subordinate to the current written/help lane and clear about what non-admitted viewers should do next?**

A route can pass `498`, `508`, `510`, `512`, and `517` and still fail `518` if:
- a Vimeo registration form is the first public artifact a voter sees, but the office never states whether the same information also exists in an ordinary written/help lane;
- a Teams town hall is invite-only, yet the office speaks about it as though the public can simply “watch the briefing” without clarifying that attendance depends on the invite/email path;
- a members-only or otherwise audience-gated YouTube recording still appears in Home, Subscriptions, or other discovery surfaces, but the office never explains what a non-member should trust instead;
- browser users see a registration flow while app users do not, and the office never reviews the divergence;
- or delivery of an invite email or approval step quietly becomes the practical single point of failure for reaching the official event.

## Audience-gated media is still subordinate to the current written/help lane

The public-safe posture is simple:
**an audience gate is not itself the controlling public answer.**
It is an access condition over one official media route.

At minimum, keep these layers distinct:
1. the current written page, notice, FAQ/help entry, or named office contact that still controls action-changing next steps;
2. the event or recording route that is being gated;
3. the gate type itself (registration, invite-only, approval, members-only, private/unlisted, or mixed route posture);
4. the concrete entry artifact the viewer receives or uses, such as a registration form, join email, invite link, or membership prompt;
5. and the fallback path for people who do not qualify, do not receive the invite, or cannot complete the gate on the device they are using.

That distinction matters because “registration required” or “invited attendees only” can sound like the whole authoritative answer.
But the office usually still owes the public a recoverable written/help lane explaining:
- whether the event is public, limited, or staff/internal only;
- whether the voter needs the event at all to act safely;
- where the current written instructions live if the gate cannot be completed;
- and whom to contact if access fails or the audience-selection rule is unclear.

## Gated discovery is especially risky because people may find what they still cannot enter

YouTube’s current viewer-facing membership help is especially useful here because it makes the split explicit: anyone can find a members-only video, but only members at the right levels can watch it, and those videos may still surface in Home and Subscriptions.
Vimeo’s current registration FAQ is useful for a different reason: the gate may display in a browser but not in the mobile app.
(xref: `youtube_membership_benefits_help_page`; xref: `vimeo_registration_forms_faq_help_page`)

For `518`, offices should review whether:
- the public can discover the event or recording without being able to enter it;
- app/browser differences change what the gate even looks like;
- invitation or approval email delivery is being mistaken for the office’s ordinary public-help lane;
- and the written/help route still explains what to do when the gate is not satisfied.

## Invite-only and approval-gated events need explicit recovery language

Microsoft’s current town-hall documentation makes the join path concrete: attendees use a join link in an email invite, and invited-only town halls must be published before attendees can join.
That is operationally useful, but it also means a missing invite, stale invite, misaddressed invite, or misread audience rule can become the viewer’s whole story about the event.
(xref: `microsoft_schedule_town_hall_help_page`; xref: `microsoft_attend_town_hall_help_page`)

For `518`, the office should not let “I did not receive or could not use the invite” silently collapse into “there is no official answer for me.”
Review whether:
- the office states whether the event is public, limited, or internal;
- a nonqualified or failed-entry viewer can still recover the current written/help lane;
- the gate clearly says whether the viewer is missing permission, missing invitation, missing membership, or simply on the wrong route/device;
- and help/contact recovery is visible enough that the gate does not sound like a dead end.

## Membership-only or limited-audience media should not become the public instruction lane by accident

YouTube’s current help makes clear that audience-gated video can still be quite visible around the platform.
Creators can offer members-only live streams or videos, and viewer-facing help says those videos may still surface in Home and Subscriptions even though only eligible members can watch them.
(xref: `youtube_channel_memberships_perks_help_page`; xref: `youtube_membership_benefits_help_page`)

For election use, that means a limited-audience recording should not quietly become the office’s only public way of communicating action-changing instructions.
If the office intentionally limits access to one media route, it should still preserve a recoverable public written/help lane for people outside that audience gate whenever the underlying instruction affects them.

## Minimal public proof posture

Publish a **small registration/gate digest**, not attendee rosters or payment records.

Useful public facts are things like:
- which official media route was gated;
- what the gate type was (registration, invite-only, approval, members-only, private/unlisted, or mixed);
- whether discovery without entry was possible;
- whether browser/app or route-specific differences were reviewed;
- whether non-admitted viewers could recover the current written/help lane;
- and when that gate posture was reviewed.

Do **not** publish by default:
- attendee email addresses,
- approval rosters,
- membership/payment status,
- individualized registration answers,
- or detailed vendor-admin traces when a compact public reconstruction is enough.

## Verification questions for third parties

A verifier, journalist, observer, community partner, or court should be able to answer:
- Was the official media route public, registered, invited-only, approval-gated, members-only, or otherwise audience-limited?
- Could ordinary viewers discover the route even if they could not enter it?
- Was it clear what non-admitted viewers should do instead?
- Did app/browser, inbox, approval, or membership differences materially change access?
- Could an ordinary voter recover the current written/help lane without needing the gated route to be the whole answer?

## Artifacts and companion references

- Template payload: `artifacts/templates/official-voter-information-platform-registration-gate-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-registration-gate-surface-checklist.md`
- Neighbor docs: `369`, `370`, `498`, `508`, `510`, `512`, `517`

## Sources

- Vimeo Help Center: How to configure the registration form for your live event or webinar. (xref: `vimeo_live_event_registration_form_help_page`)
- Vimeo Help Center: FAQ: Registration forms. (xref: `vimeo_registration_forms_faq_help_page`)
- Microsoft Support: Schedule a town hall in Microsoft Teams. (xref: `microsoft_schedule_town_hall_help_page`)
- Microsoft Support: Attend a town hall in Microsoft Teams. (xref: `microsoft_attend_town_hall_help_page`)
- YouTube Help: Change video privacy settings. (xref: `youtube_change_video_privacy_settings_help_page`)
- YouTube Help: Create or manage your YouTube channel’s memberships levels & perks. (xref: `youtube_channel_memberships_perks_help_page`)
- YouTube Help: Use & manage your channel membership benefits on YouTube. (xref: `youtube_membership_benefits_help_page`)
