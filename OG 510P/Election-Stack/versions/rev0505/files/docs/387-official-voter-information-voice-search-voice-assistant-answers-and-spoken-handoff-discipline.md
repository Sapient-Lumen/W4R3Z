# 387 — Official voter-information voice search, voice-assistant answers, and spoken-handoff discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **voice search and voice-assistant answer surfaces that may speak, summarize, or route official voter information before a voter reaches a full official page**: voice search results, smart-speaker/local-info answers, screenless assistant responses, read-aloud answer modes, and similar spoken first-contact layers.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `364`, which governs **official** voter-help hotlines and script packets,
- `382`, which governs ordinary search-result presentation before a spoken answer,
- `385`, which governs platform place cards / office listings that may feed local-info answers,
- `386`, which governs broader off-platform AI-answer surfaces,
- or `379`, which governs stale-link and expired-page recovery once the voter lands on an older URL.

It adds one narrow rule:
**if voters may encounter voice or screenless answer surfaces before they reach the official page, the jurisdiction should keep the spoken handoff short, clearly official, current-state-aware, and recovery-rich so the voice layer does not quietly become a hidden authority above the current official source.**

## Why this is a distinct surface

Current official and primary technical guidance is enough to justify a bounded control here.

EAC's current AI guidance warns that AI-generated election information can look plausible while still being inaccurate, especially for dates, hours, and locations. EAC's current voter and election-official guidance still says practical registration and voting information is decentralized and that the best practical source is the local election official or current state/local election site. Vote.gov's current trust posture likewise emphasizes official `.gov` and HTTPS routing. (xref: `eac_ai_and_election_administration_page`; xref: `eac_voter_faqs_page`; xref: `eac_best_practices_faqs_election_officials_page`; xref: `vote_gov_home_page`; xref: `vote_gov_about_us_page`)

On the platform side, Apple's current Business Connect guidance says organizations can manage information so customers can find them in Maps, Apple Wallet, Siri, and more, and it says the Place Card appears across Maps, Siri, Calendar, Messages, and more. Apple's current location-attributes guidance also says hours on the Place Card should match the hours on the official website whenever possible. Google's current help says users can search Google with their voice, and Google Assistant's current help explicitly treats local info, business hours, and navigation as voice-answer tasks. Microsoft's current support says Copilot now supports dictation, read-aloud, and voice chat, while Microsoft's current web-search guidance says Copilot can ground responses in real-time web content through Bing. (xref: `apple_business_connect_user_guide_page`; xref: `apple_business_connect_configure_location_attributes_page`; xref: `google_voice_search_help_page`; xref: `google_assistant_local_info_help_page`; xref: `microsoft_365_copilot_voice_features_page`; xref: `microsoft_365_copilot_public_web_access_page`)

That is enough to treat spoken answer layers as a real voter-information surface rather than just a variant of generic search or a subset of hotlines.
The office does not control every vendor voice answer.
But the voter may still trust the spoken answer first, especially when driving, multitasking, or using a screenless device.
So the underlying official source needs to make the handoff safe.

## Spoken answers compress context harder than visual answers

A spoken answer often carries fewer cues than a full page or even a visual search card.
The voter may hear only one sentence, one office name, one hour window, or one route suggestion.
That means scope, date, jurisdiction, and recovery cues can disappear more easily in voice mode than in an ordinary click-through experience.

So the bounded control here is not “optimize every assistant.”
It is:
- keep official office and office-directory data current,
- keep cited/linked official pages easy to recognize quickly,
- keep current-state cues easy to hear or see immediately after handoff,
- and keep the fallback office/help lane obvious when the spoken answer is partial, ambiguous, or stale.

## Spoken handoff is the key bounded control

For this surface, the practical question is not whether a voice assistant sounds confident.
The practical question is:
**when a voter hears a spoken answer, does the handoff carry them into a clearly official, clearly scoped, current-enough destination with an obvious next step if the spoken answer was incomplete?**

That usually means a spoken-answer-safe destination should make at least some combination of these legible immediately:
- responsible office or jurisdiction identity,
- election/date scope when material,
- whether the destination is a directory, office card, FAQ/help answer, notice, or status explainer,
- whether the answer depends on address, district, facility, or record-specific facts,
- and the next official help route when self-service is not enough.

## Current-state cues matter more when the answer is heard instead of scanned

EAC's current AI guidance is explicit that plausible output can still be wrong on operationally critical facts like dates, hours, and locations. Apple's current place-card guidance and Google's current local-info voice guidance show that business hours, local discovery, and navigation are exactly the kind of facts users will often request through voice. (xref: `eac_ai_and_election_administration_page`; xref: `apple_business_connect_configure_location_attributes_page`; xref: `google_assistant_local_info_help_page`)

That means official pages and office-directory anchors likely to feed spoken answers should not rely only on timeless prose when the fact is operationally volatile.
For action-changing topics, they should prefer visible or audible cues such as:
- current election or cycle labeling,
- current office status or temporary-closure state,
- explicit special-hours or holiday adjustments,
- direct routing to current lookup/help pages,
- and immediate office/help recovery when the answer depends on local facts.

The goal is not to timestamp everything.
The goal is to reduce the chance that a screenless or spoken answer strips away the very context the voter needed in order to act safely.

## Voice answers are routing layers, not rule sources

A voice answer MAY help a voter reach the right official source faster.
It MUST NOT become the controlling authority for jurisdiction-specific election rules.

The controlling artifact remains the current official page, signed notice, office directory entry, or direct office confirmation that the jurisdiction itself stands behind.
So the voice layer should do only enough to:
- expose or lead to the current official source,
- preserve office/jurisdiction identity,
- avoid turning one spoken sentence into the whole practical answer,
- and recover quickly when the answer depends on location, hours, deadlines, or individualized facts.

This is close to the no-authority-lift principle in `363` and `386`, but applied to a voice-first surface that may be shorter, less inspectable, and easier to over-trust.

## Screenless recovery and “show me the official source”

A safe spoken-answer pattern is not just read-aloud.
It is **spoken answer plus recovery**.

For high-risk topics, a voter should be able to move quickly from the spoken answer into one of these:
- the current official office/help page,
- the current location/directory page,
- the current notice/alert page,
- or the office phone/help route when self-service is unsafe.

If the answer depends on address, district, polling-place assignment, temporary closure, language path, or a rights-sensitive fact, the spoken answer should be treated as a routing cue rather than as a final legal statement.

## Local-info and office-card coherence matter disproportionately here

Apple's current guidance says its Place Card appears across Siri and related Apple surfaces, and Google's current guidance says voice users commonly ask for business hours and navigation. That means voice answers often inherit from office cards, local-search records, and current office/help anchors rather than from a perfectly scoped voter FAQ page. (xref: `apple_business_connect_configure_location_attributes_page`; xref: `google_assistant_local_info_help_page`)

So maintainers should review `305`, `376`, `382`, and `385` together when they care about spoken-answer integrity.
If office hours, website actions, location names, temporary closures, or directions state drift at the place-card layer, the spoken layer may faithfully repeat the wrong thing.

## Accessibility and language boundaries still apply

Microsoft's current voice-feature guidance explicitly frames voice interaction and read-aloud as accessibility-supporting features, while also warning users to review generated or transcribed content for accuracy. Apple's current guidance allows language-specific content on place-card fields when kept consistent, and Google's current Assistant help says some queries do not work on all devices and in all languages. (xref: `microsoft_365_copilot_voice_features_page`; xref: `apple_business_connect_configure_location_attributes_page`; xref: `google_assistant_local_info_help_page`)

So the bounded rule here is:
- do not assume spoken access solves the accessibility problem by itself,
- do not assume every language path or device exposes the same answer shape,
- and do keep the fallback human-help route visible when spoken delivery is incomplete, unavailable, or language-limited.

## Minimal voice-answer state taxonomy

A small taxonomy is enough:

1. **spoken_current_answer_with_clear_official_handoff**
2. **spoken_answer_needing_screen_followup_or_lookup**
3. **spoken_local_info_answer_backed_by_current_office_card**
4. **ambiguous_or_partial_voice_answer_recovered_by_official_help_lane**
5. **stale_voice_answer_recovered_by_current_notice_or_office_confirmation**

That is usually more useful than pretending every assistant ecosystem needs its own theory.

## Bounded trace minimum

The archive does **not** need raw third-party audio logs, wake-word telemetry, vendor dashboard dumps, or individualized recordings of voters asking questions.
But for accountability and later reconstruction, it is still useful to preserve a bounded **voice-answer handoff policy trace** for action-changing official pages and office records.

At minimum, a jurisdiction should be able to reconstruct:
- which official pages or office records were intended as spoken-answer anchors for volatile topics,
- which office/help route was supposed to be the fallback,
- which current-state cues were expected to remain visible after handoff,
- and when the office last verified the voice-answer-ready destination set.

That gives the archive enough to evaluate whether the spoken layer was safely bounded without turning the archive into a telemetry sink.

## Proof obligations

If a jurisdiction claims to operate this surface responsibly, it should be able to prove at least:

1. **Authority-boundary claim:** the spoken layer is treated as a routing/summary layer, not the controlling rule source.
2. **Official-anchor claim:** high-risk spoken answers land on current official pages or office/help routes.
3. **Current-state claim:** volatile facts like hours, closures, locations, and deadline windows remain current enough to recover from spoken compression.
4. **Fallback claim:** address-specific, district-specific, record-specific, or rights-sensitive questions visibly route to lookup/help/human assistance.
5. **Trace-minimization claim:** bounded reconstruction is possible without storing individualized third-party audio or voice-usage telemetry.

## Canonical digest artifacts

Publish **digests of handoff policy and destination class state**, not vendor dashboards.

- **Voice Answer Handoff Surface Digest (VAHSD):** digest of the bounded public payload for spoken-answer readiness.
- **Spoken Destination Class Digest (SDCD):** digest of the policy describing which destination classes are maintained for safe spoken handoff and recovery.
- **Voice Recovery State Digest (VRSD):** optional digest proving what current-state / fallback cues a spoken-answer destination class was supposed to expose at time `T`.

## What belongs in the public payload

Keep the payload **small, current-state-aware, and authority-boundary explicit**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `voice_surface_label`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `authority_boundary_note`
- `spoken_handoff_policy_note`
- `screenless_recovery_policy_note`
- `current_state_cue_policy_note`
- `office_card_dependency_note`
- `accessibility_language_policy_note`
- `voice_answer_state_classes[]`
- `voice_answer_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `rights_escalation_uri`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw third-party audio recordings,
- individualized wake-word or voice-query telemetry,
- private vendor dashboards,
- or synthetic confidence scores that are not needed to reconstruct the bounded public handoff policy.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official pages, office records, or help routes were intended to be safe spoken-answer anchors at time `T`?
- Did those destinations make office identity, current-state, and next-step recovery legible immediately after handoff?
- Could a voter safely recover when the spoken answer depended on address, district, facility status, or temporary hours?
- Was there a visible or audible route from the spoken answer to the current official domain or office/help phone path?
- Did the jurisdiction preserve a bounded handoff-policy trace without collecting unnecessary voice telemetry?

## How this fits the family map

Voice search and voice-assistant answers are **not** a new canonical voter-question family bucket.
They are a first-contact delivery layer that may speak or summarize existing voter-information surfaces before the voter sees a full page.

So the underlying question remains:
- where to vote,
- which office is authoritative,
- whether the office is open right now,
- which deadline or location page controls,
- or where the voter should escalate when ordinary self-service fails.

This document only says that, if voters may meet a spoken or screenless surface first, the official destination set should stay authority-bounded, current-state-aware, office-legible, and recovery-rich instead of letting the spoken layer quietly become the trusted answer.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-voice-answer-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-voice-answer-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Artificial Intelligence (AI) and Election Administration (xref: `eac_ai_and_election_administration_page`)
- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Best Practices: FAQs for Election Officials (xref: `eac_best_practices_faqs_election_officials_page`)
- Vote.gov: Home / trust marker (xref: `vote_gov_home_page`)
- Vote.gov: About Vote.gov (xref: `vote_gov_about_us_page`)
- Apple: Apple Business Connect User Guide (xref: `apple_business_connect_user_guide_page`)
- Apple: Configure location attributes in Apple Business Connect (xref: `apple_business_connect_configure_location_attributes_page`)
- Google Search Help: Use Google Voice Search (xref: `google_voice_search_help_page`)
- Google Assistant Help: What you can ask Google Assistant (xref: `google_assistant_local_info_help_page`)
- Microsoft Support: Get started with voice features in Microsoft 365 Copilot (xref: `microsoft_365_copilot_voice_features_page`)
- Microsoft Learn: Data, privacy, and security for web search in Microsoft 365 Copilot and Microsoft 365 Copilot Chat (xref: `microsoft_365_copilot_public_web_access_page`)
