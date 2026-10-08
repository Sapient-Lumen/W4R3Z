# 572 — Official voter-information platform media AI-answer input sufficiency states, transcript floors, and content-fit discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- player-native AI answer modules as public-answer boundaries (`499`),
- derivative-readiness / transcript-prerequisite lag (`561`),
- AI pane state (`562`),
- AI question-thread state (`563`),
- AI answer source-basis (`566`),
- AI answer outcome (`567`),
- AI-answer eligibility / rollout gating (`570`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, the AI-answer boundary is already understood, and the surface may even be visible to the captured viewer, but the platform also says the answer layer works only when the transcript or video clears a minimum word-count, duration, or content-fit profile — and that input-sufficiency rule starts to look like a new route, a new head, or proof that the media object itself changed?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/499-official-voter-information-platform-ai-video-summaries-ask-this-video-and-answer-module-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/527-official-voter-information-platform-media-control-tuple-one-line-normalization-contract-and-packet-comparison-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/561-official-voter-information-platform-media-derivative-readiness-states-processing-lag-and-head-default-retention-discipline.md`
- `docs/562-official-voter-information-platform-media-ai-answer-pane-states-summary-focus-and-head-default-retention-discipline.md`
- `docs/563-official-voter-information-platform-media-ai-question-thread-states-follow-up-carryover-and-prompt-history-minimization-discipline.md`
- `docs/566-official-voter-information-platform-media-ai-answer-source-basis-states-transcript-vs-web-provenance-and-head-default-retention-discipline.md`
- `docs/567-official-voter-information-platform-media-ai-answer-outcome-states-no-answer-fallthrough-and-head-default-retention-discipline.md`
- `docs/570-official-voter-information-platform-media-ai-answer-eligibility-states-rollout-gating-and-captured-absence-scope-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that the same media object can remain current while the **AI layer's practical usefulness still depends on minimum transcript or content-fit thresholds** rather than on a new route.
Microsoft's current Clipchamp support says Copilot requires more than 100 words in the video transcript and will not function if the transcript is too short.
Microsoft's current Clipchamp FAQ repeats that Copilot requires at least 100 words in the transcript and also says the tool reads only the first transcript generated for the video.
Vimeo's current AI requirements help says videos that work best with Vimeo AI are at least 2 minutes long, contain at least 100 spoken words in English or another supported language, and have no accompanying music.
(xref: `microsoft_clipchamp_copilot_video_player_support_page`; xref: `microsoft_clipchamp_copilot_video_player_faq_page`; xref: `vimeo_ai_video_requirements_help_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one player-native AI-answer boundary already governed by `499`,
- one viewer who can see the AI surface,
- one transcript that exists but is too short for the tool to answer,
- one video whose speech/music profile is published as a poor fit for the AI layer,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they flatten transcript-too-short or poor-fit facts into `561` even when prerequisites are already settled and the remaining issue is a published sufficiency floor,
- they flatten input-floor failures into `567` even when the answer outcome is downstream of a documented minimum-content rule rather than a free-standing no-answer result,
- they flatten minimum-content rules into `570` even when the viewer was eligible and the real issue is the same surface's content sufficiency rather than rollout or entitlement,
- they flatten transcript/content-fit requirements into `566` even when the issue is not which source the answer drew on but whether the source cleared the platform's own minimum threshold,
- or they leave the sufficiency fact out entirely and later cannot explain why one honest capture showed a visible AI surface but no usable answer behavior on a short or music-heavy video.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object AI-answer input sufficiency state + head/default retention**.

## This is not the same thing as `499`, `561`, `566`, `567`, or `570`

`499` governs player-native AI answer modules as public-answer boundaries around already-open official media.

`561` governs derivative-readiness lag when transcripts, captions, chapters, replay derivatives, or other same-object prerequisites are still settling.

`566` governs what the platform says the answer is based on, such as transcript-only, platform-and-web, or another disclosed provenance posture.

`567` governs what happened **after** the visible AI interaction ran: substantive answer, limited no-answer, prerequisite-missing no-answer, or retry/error state.

`570` governs who could access or see the AI layer in the first place: viewer scope, age/supervision, owner activation, plan/licensing, rollout limits, or client-environment requirements.

`572` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **AI-answer input-sufficiency note** such as transcript-too-short, speech/music profile unsuitable, floor met/sufficient, or published floor not disclosed,
- while recording that the AI layer's practical behavior depended on a published minimum-content rule or fit profile **without** creating a new published route, a new head, or proof that the media object itself changed.

If the decisive issue is whether the AI answer layer itself became a public-answer boundary, use `499`.
If the decisive issue is that transcripts or other prerequisites were still generating or settling, use `561`.
If the decisive issue is what basis the answer drew from, use `566`.
If the decisive issue is what visible answer or no-answer outcome was returned, use `567`.
If the decisive issue is who could access or see the surface at all, use `570`.
Use `572` only when the surface is already understood but the archive still needs to classify the **same-object AI-answer input sufficiency / content-fit state** inside an already-governed media chain.

## Default rule: preserve floor/fit truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **AI-answer input sufficiency state note** when all of the following hold:

1. **The underlying object is still the same.**
   The playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is whether the content clears the AI layer's own published floor or fit profile.**
   The decisive fact is that the same media object had a transcript/video that either met or failed a minimum word-count, duration, or speech-profile requirement disclosed by the platform.
3. **Treating the state as route-global or object-global would mislead.**
   A reader could mistake one transcript-too-short or music-heavy capture for proof that the object or AI boundary itself changed.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The floor/fit fact still matters.**
   The archive would lose useful truth if it omitted why the same visible AI layer behaved differently on a short, low-speech, or otherwise poor-fit input.

When those conditions hold, keep the head/default under `529–530`, keep any public-answer-boundary fact under `499`, keep any derivative-readiness fact under `561`, keep any answer-basis fact under `566`, keep any answer-outcome fact under `567`, keep any viewer-gating fact under `570`, and add one `572` input-sufficiency note.
Do **not** silently promote transcript/content-fit rules into the chain's current head.

## Minimal AI-answer input-sufficiency grammar

When a same-object chain has a current head or fallback anchor plus a meaningful AI-answer input-sufficiency state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; sufficiency_state=<minimum_word_or_length_floor_not_met|spoken_content_profile_unsuitable|input_floor_met_or_sufficient|published_floor_not_disclosed|unknown>; sufficiency_basis=<minimum_word_count_rule|minimum_duration_rule|speech_heavy_content_profile_rule|music_or_non_speech_profile_rule|published_best_fit_requirements|capture_only|no_published_floor|unknown>; cite_default=<head|fallback anchor>; cite_sufficiency_when=<claim about the AI layer's published minimum floor/fit rule or why that rule did not become the safer citation lane>; retain_prompt_text=<no>; basis=<why the sufficiency state mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **whether the same AI layer had enough transcript/content to operate as published** without making that rule sound like a new route or a reviewed office explanation.

`header_pick_order=<minimum_word_or_length_floor_not_met|spoken_content_profile_unsuitable|input_floor_met_or_sufficient|published_floor_not_disclosed|unknown>`

`detail_pick_order=<spoken_content_profile_unsuitable|input_floor_met_or_sufficient|published_floor_not_disclosed|minimum_word_or_length_floor_not_met|unknown>`

For packet headers, that winner order means the carried `572` token should prefer the most reconstructively salient floor/fit fact when several published sufficiency signals co-exist. If one extra same-doc `572` residue fact still matters after the header winner is chosen, use the first applicable token from `detail_pick_order=<...>` that is not already carried for `572`.

## When to use an AI-answer input-sufficiency note

Typical uses include:

1. **Transcript exists, but published minimum length is not met**
   The same head still controls, the surface may even be visible, but the transcript is too short for the answer layer to function as published.
2. **Speech/music profile is a poor fit**
   The same head still controls, but the platform says the video works best only for speech-heavy, low-music content and the captured object does not match that profile.
3. **Published floor was affirmatively met and that matters for comparison**
   The same head stayed current, and later readers need to preserve that the transcript/content did clear the published floor so disagreement is not explained by simple insufficiency.
4. **No floor is published, and that absence matters**
   The same head stayed current, but the archive needs to say the platform did not disclose a minimum-content floor in the reviewed support material rather than inventing one from inference.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `572` AI-answer input-sufficiency note SHOULD be cited only when the later claim is specifically about:
- whether the platform documented a minimum word-count, duration, or content-fit rule for the same AI layer,
- whether the transcript or video cleared that published floor,
- whether a poor-fit speech/music profile shaped why the AI layer was weak or unavailable,
- or why that minimum-content rule did **not** outrank the head-first citation rule.

That means `572` preserves one honest floor/fit exception to head-first citation without letting transcript-length or best-fit guidance quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `572` when:
- the decisive issue is off-platform AI retrieval or synthesis before the player opens — use `386`,
- the decisive issue is the AI answer module as a public-answer boundary in the first place — use `499`,
- the decisive issue is merely that transcript generation or another prerequisite was still settling — use `561`,
- the decisive issue is prompt/thread conditioning or prompt-origin inside the answer flow — use `563`,
- the decisive issue is answer-source provenance rather than minimum-content sufficiency — use `566`,
- the decisive issue is a visible answer/no-answer disposition after the interaction ran — use `567`,
- the decisive issue is viewer/account/rollout gating rather than content sufficiency — use `570`,
- or the archive is trying to preserve full transcript bodies when one compact floor/fit token and short basis note are enough.

If deleting the sufficiency fact would erase **why the same visible AI layer was weak, absent in practice, or non-comparable on a short or poor-fit input**, `572` is probably the right companion.
If deleting that fact would erase the AI boundary, a visible pane state, or the actual answer/no-answer result, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_intro_clip_apr_2026; head=published Clipchamp player packet; sufficiency_state=minimum_word_or_length_floor_not_met; sufficiency_basis=minimum_word_count_rule; cite_default=head; cite_sufficiency_when=proving that the same visible Copilot surface could not function because the transcript stayed below the published floor rather than because the object or route changed; retain_prompt_text=no; basis=the same recording stayed current while Microsoft disclosed a transcript-length minimum for player Q&A`
- `chain=town_hall_music_bumper_replay_apr_2026; head=public Vimeo watch-page packet; sufficiency_state=spoken_content_profile_unsuitable; sufficiency_basis=music_or_non_speech_profile_rule; cite_default=head; cite_sufficiency_when=proving that Vimeo's own requirements page treated the replay as a poor fit for AI features without turning that fit guidance into the new current route; retain_prompt_text=no; basis=the same replay stayed current while the platform's published best-fit profile excluded music-heavy or low-speech content`
- `chain=board_work_session_replay_apr_2026; head=public Vimeo watch-page packet; sufficiency_state=input_floor_met_or_sufficient; sufficiency_basis=published_best_fit_requirements; cite_default=head; cite_sufficiency_when=proving that the transcript and speech profile cleared the published floor so later disagreement had to be explained somewhere other than simple insufficiency; retain_prompt_text=no; basis=the same replay stayed current and the platform's own requirements page said speech-heavy meeting-style videos were a good fit`

## Tie-breaker when reviewers ask “if the platform says the transcript is too short or the video is a poor fit, why isn't that the head?”

Ask three questions:
- does the observed state prove **whether the AI layer's input cleared a published floor or fit profile** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to transcript-length or best-fit guidance instead of the controlling head,
- and can the needed reconstruction stay truthful without preserving full transcript bodies or long prompts?

If yes, keep current control under `529–530`, preserve any AI-answer-surface boundary fact under `499`, preserve any derivative-readiness fact under `561`, preserve any answer-basis fact under `566`, preserve any answer-outcome fact under `567`, preserve any eligibility/gating fact under `570`, and record the input-sufficiency state under `572`.
Do **not** let minimum-content guidance absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because one same-object AI surface discloses minimum transcript length, duration, or best-fit rules.
Tighten `572` first.
Only add another numbered surface when the ambiguity is really about a new public-answer boundary, a new office-controlled route, or a new authority object rather than about **AI-answer input sufficiency inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that floor/fit cases still drift between `499`, `561`, `566`, `567`, and `570` after this compact note contract exists.
