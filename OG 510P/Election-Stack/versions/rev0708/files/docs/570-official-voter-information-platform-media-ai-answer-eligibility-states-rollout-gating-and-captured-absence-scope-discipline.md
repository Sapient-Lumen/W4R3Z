# 570 — Official voter-information platform media AI-answer eligibility states, rollout gating, and captured-absence-scope discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- player-native AI answer modules as public-answer boundaries (`499`),
- derivative-readiness / transcript-prerequisite lag (`561`),
- AI pane state (`562`),
- AI question-thread state (`563`),
- AI answer outcome (`567`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, the AI-answer boundary is already understood, but the visible AI surface is present for some viewers and absent for others because of signed-in scope, age/supervision, region/language limits, owner activation, plan/licensing, selective rollout, or client-environment requirements — and that captured availability difference starts to look like a new current route, a platform-wide fact about the video, or proof that the object itself changed?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/499-official-voter-information-platform-ai-video-summaries-ask-this-video-and-answer-module-authority-boundary-discipline.md`
- `docs/512-official-voter-information-platform-unavailable-private-age-gated-region-blocked-and-playback-restricted-surface-authority-boundary-discipline.md`
- `docs/518-official-voter-information-platform-registration-forms-invite-only-join-links-and-audience-gated-media-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/527-official-voter-information-platform-media-control-tuple-one-line-normalization-contract-and-packet-comparison-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/561-official-voter-information-platform-media-derivative-readiness-states-processing-lag-and-head-default-retention-discipline.md`
- `docs/562-official-voter-information-platform-media-ai-answer-pane-states-summary-focus-and-head-default-retention-discipline.md`
- `docs/563-official-voter-information-platform-media-ai-question-thread-states-follow-up-carryover-and-prompt-history-minimization-discipline.md`
- `docs/567-official-voter-information-platform-media-ai-answer-outcome-states-no-answer-fallthrough-and-head-default-retention-discipline.md`
- `docs/568-official-voter-information-platform-media-ai-answer-qualification-states-disclaimer-visibility-and-head-default-retention-discipline.md`
- `docs/569-official-voter-information-platform-media-ai-answer-feedback-states-helpfulness-votes-and-report-lane-non-authority-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that the same media object can remain current while the **AI layer's visibility is viewer-scoped, entitlement-scoped, rollout-scoped, or client-scoped** rather than object-global.
YouTube's current conversational-AI help says the tool is available only to signed-in users who meet the minimum age requirement, in available languages and countries, on select videos, and not for supervised kid accounts or the YouTube Kids app.
Vimeo's current Ask AI help says account owners on select Enterprise plans can activate Ask AI on AI-eligible videos, that all viewers can use it only where it is activated, and that viewers should look for the Vimeo AI button to know whether questions are supported on that video.
Microsoft's current Clipchamp support says Copilot in the player requires a Microsoft 365 Copilot license plus the Microsoft 365 Copilot for SharePoint service plan, and that third-party cookies must be enabled for the feature to work in the player page.
(xref: `youtube_conversational_ai_tool_help_page`; xref: `vimeo_ai_ask_questions_about_videos_help_page`; xref: `microsoft_clipchamp_copilot_video_player_support_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one player-native AI-answer boundary already governed by `499`,
- one captured viewer for whom the AI surface is visible,
- another captured viewer or environment for whom the same surface is absent,
- one product page that says the feature is only available in select regions, languages, or videos,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they treat one capture without an AI button as proof that the object or platform has no AI-answer layer at all,
- they treat one visible AI pane as proof that every viewer can access the same surface,
- they flatten owner activation, plan/licensing, or account-scope gating into `499` even when the authority boundary is already understood,
- they flatten viewer/client gating into `561` even when the decisive issue is not derivative readiness but who could access the surface in the first place,
- or they leave the gating fact out entirely and later cannot explain why two honest captures of the same object disagree about whether the AI layer was present.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object AI-answer eligibility/exposure state + head/default retention**.

## This is not the same thing as `499`, `512`, `518`, `561`, or `567`

`499` governs player-native AI answer modules as public-answer boundaries around already-open official media.

`512` governs restriction shells around the media object itself, such as unavailable, private, age-gated, region-blocked, or playback-restricted surfaces.

`518` governs registration forms, invite-only joins, and audience-gated access to the media object itself.

`561` governs derivative-readiness lag when transcripts, captions, chapters, replay derivatives, or other same-object prerequisites are still settling.

`567` governs what happened **after** the visible AI interaction ran: substantive answer, limited no-answer, prerequisite-missing no-answer, or retry/error state.

`570` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **AI-answer eligibility/exposure note** such as visible-to-viewer, viewer-ineligible, entitlement/owner-setting gated, rollout-limited, or environment-blocked,
- while recording that the AI surface's presence or absence was scoped to the captured viewer/environment **without** creating a new published route, a new head, or proof that the media object itself changed.

If the decisive issue is whether the AI answer layer itself became a public-answer boundary, use `499`.
If the decisive issue is that the media object is itself private, blocked, or invite-gated, use `512` or `518`.
If the decisive issue is that transcripts/captions or other prerequisites are still settling, use `561`.
If the decisive issue is that the visible AI pane returned a no-answer or error after opening, use `567`.
Use `570` only when the surface is already understood but the archive still needs to classify the **same-object AI-answer eligibility/exposure state** inside an already-governed media chain.

## Default rule: preserve exposure truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **AI-answer eligibility/exposure state note** when all of the following hold:

1. **The underlying object is still the same.**
   The playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is who could access the AI layer.**
   The decisive fact is that the same media object showed or hid the AI surface because of account scope, age/supervision, region/language availability, owner activation, plan/licensing, selective rollout, or client-environment requirements.
3. **Treating the state as object-global would mislead.**
   A reader could mistake one capture's visible or absent AI module for a universal fact about the media object or a new current route.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The exposure/gating fact still matters.**
   The archive would lose useful truth if it omitted why the same object showed the AI layer for one viewer/environment but not another.

When those conditions hold, keep the head/default under `529–530`, keep any public-answer-boundary fact under `499`, keep any derivative-readiness fact under `561`, keep any answer-outcome fact under `567`, and add one `570` eligibility/exposure note.
Do **not** silently promote viewer-scoped availability into the chain's current head.

## Minimal AI-answer eligibility grammar

When a same-object chain has a current head or fallback anchor plus a meaningful AI-answer eligibility/exposure state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; eligibility_state=<viewer_account_or_age_ineligible|region_or_language_scope_limited|entitlement_or_owner_setting_gated|environment_or_client_requirement_blocked|rollout_or_video_selection_limited|surface_visible_to_viewer|eligibility_state_unclear|unknown>; eligibility_basis=<signed_in_age_or_supervision_rule|region_language_availability_rule|owner_toggle_or_plan_rule|license_or_service_plan_rule|cookies_browser_surface_requirement|select_video_or_ai_eligible_scope|visible_ai_button_or_module|capture_absence_only|unknown>; cite_default=<head|fallback anchor>; cite_eligibility_when=<claim about why the AI layer was or was not visible in that capture>; retain_session_payload=<no>; basis=<why the exposure/gating fact mattered without becoming a new authority object>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **how the same object's AI layer was scoped to a viewer, environment, entitlement, or rollout condition** without making one capture's visibility or absence sound like a new official route.

`header_pick_order=<viewer_account_or_age_ineligible|region_or_language_scope_limited|entitlement_or_owner_setting_gated|environment_or_client_requirement_blocked|rollout_or_video_selection_limited|surface_visible_to_viewer|eligibility_state_unclear|unknown>`

`detail_pick_order=<surface_visible_to_viewer|rollout_or_video_selection_limited|viewer_account_or_age_ineligible|region_or_language_scope_limited|entitlement_or_owner_setting_gated|environment_or_client_requirement_blocked|eligibility_state_unclear|unknown>`

For packet headers, that winner order means the carried `570` token should prefer the most reconstructively specific gating fact when several truthful exposure states can be named at once. If one extra same-doc `570` residue fact still matters after the header winner is chosen, use the first applicable token from `detail_pick_order=<...>` that is not already carried for `570`. If the same packet both visibly shows the AI module and also relies on a select-video rollout or other bounded-availability rule, the header should usually keep the gating token and the detail slot may keep `surface_visible_to_viewer` when that single extra residue fact matters.

## When to use an AI-answer eligibility/exposure note

Typical uses include:

1. **Viewer-specific account or age/supervision gating**
   The same head still controls, but the archive needs to preserve that the AI surface was unavailable because the viewer was signed out, below the minimum age threshold, or on a supervised/kids account class.
2. **Region/language or select-video scope limits**
   The same object stayed current, but the AI feature is only offered in certain countries, languages, or select videos, so one visible or absent capture should not be overread as universal.
3. **Entitlement, owner-setting, or plan gating**
   The same object stayed current, but the visible AI layer depended on owner activation, plan tier, service license, or another entitlement state.
4. **Environment/client requirements**
   The same object stayed current, but the AI surface was blocked by client-environment requirements such as cookies, browser/surface support, or another visible runtime precondition.
5. **Captured absence with bounded caution**
   The same object stayed current, the AI button was absent in the capture, and the archive needs to preserve that absence honestly while also marking that the precise gating reason stayed unclear.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `570` AI-answer eligibility/exposure note SHOULD be cited only when the later claim is specifically about:
- why one visible AI layer was or was not available in that capture,
- whether a viewer/account/region/entitlement/environment limit explained the absence,
- whether a visible module was still rollout-limited or selective rather than universal,
- or why that exposure/gating posture did **not** outrank the head-first citation rule.

That means `570` preserves one honest eligibility/exposure exception to head-first citation without letting one viewer-scoped state quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `570` when:
- the decisive issue is off-platform AI retrieval or synthesis before the player opens — use `386`,
- the decisive issue is browser/page AI summarization over an already-open page rather than a player-native video-answer layer — use `486`,
- the decisive issue is the AI answer module as a public-answer boundary in the first place — use `499`,
- the decisive issue is that the media object itself is unavailable, private, age-gated, region-blocked, or playback-restricted — use `512`,
- the decisive issue is that the media object itself is registration-gated, invite-only, or audience-restricted — use `518`,
- the decisive issue is derivative-readiness lag such as transcripts/captions or other same-object prerequisites still settling — use `561`,
- the decisive issue is merely that the AI pane was open, summary-focused, or answer-visible once available — use `562`,
- the decisive issue is prompt/thread conditioning rather than surface availability — use `563`,
- the decisive issue is answer/no-answer outcome after the AI interaction ran — use `567`,
- the decisive issue is caution/disclaimer visibility rather than availability/gating — use `568`,
- the decisive issue is feedback/report posture rather than availability/gating — use `569`,
- or the archive is trying to preserve full session logs, account payloads, or entitlement internals when one compact state token and short basis note are enough.

If deleting the eligibility/exposure fact would erase **why the visible AI layer was or was not present for that capture**, `570` is probably the right companion.
If deleting that fact would erase the whole AI boundary, a derivative-readiness problem, or a visible no-answer state, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; eligibility_state=viewer_account_or_age_ineligible; eligibility_basis=signed_in_age_or_supervision_rule; cite_default=head; cite_eligibility_when=proving that the conversational-AI surface was absent because the viewer capture came from a signed-out or supervised account class rather than because the underlying video changed; retain_session_payload=no; basis=the same current video still controlled while the AI layer stayed viewer-scoped`
- `chain=regional_town_hall_replay_mar_2026; head=public Vimeo watch-page packet; eligibility_state=entitlement_or_owner_setting_gated; eligibility_basis=owner_toggle_or_plan_rule; cite_default=head; cite_eligibility_when=proving that Ask AI was absent because the owner had not enabled it on an eligible enterprise-scoped video rather than because the replay route had lost authority; retain_session_payload=no; basis=the same replay stayed current while Ask AI depended on a bounded owner/plan setting`
- `chain=city_clerk_recording_apr_2026; head=published Microsoft 365 recording packet; eligibility_state=environment_or_client_requirement_blocked; eligibility_basis=cookies_browser_surface_requirement; cite_default=head; cite_eligibility_when=proving that Copilot was hidden because the player environment failed a runtime requirement instead of because the recording itself changed; retain_session_payload=no; basis=the same recording stayed current while the AI layer was blocked by client-environment state`

## Tie-breaker when reviewers ask “if the AI surface is missing here, why isn't that the head?”

Ask three questions:
- does the observed state prove **who could access the AI layer in that capture** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to viewer-scoped availability instead of the controlling head,
- and can the needed reconstruction stay truthful without preserving session payloads or full account details?

If yes, keep current control under `529–530`, preserve any AI-answer-surface boundary fact under `499`, preserve any derivative-readiness fact under `561`, preserve any answer-outcome fact under `567`, and record the eligibility/exposure state under `570`.
Do **not** let viewer-scoped AI availability absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same AI surface is visible for one viewer and absent for another.
Tighten `570` first.
Only add another numbered surface when the ambiguity is really about a new public-answer boundary, a new office-controlled route, or a new authority object rather than about **AI-answer eligibility/exposure state inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that eligibility/exposure cases still drift between `499`, `512`, `518`, `561`, and `567` after this compact note contract exists.
