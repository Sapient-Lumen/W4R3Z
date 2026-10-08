# 584 — Official voter-information platform media provenance signals, Content Credentials, and non-substitutive authenticity discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information media routes that carry provenance or authenticity signals about the same recording, clip, image, or audio object**:
Content Credentials / C2PA disclosures,
“How this content was made” panels,
“captured with a camera” labels,
provenance pins or badges,
creator- or platform-exposed origin/history sidebars,
and similar origin/edit-history cues attached to the same public media route.

It does not try to turn provenance into a new election evidence system.
It adds one narrow control:
**when official voter-information media carries provenance signals about origin, editing history, or AI involvement, those signals should help viewers orient without quietly becoming the office’s whole proof of current authority, legal effect, or still-current instructions.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/499-official-voter-information-platform-ai-video-summaries-ask-this-video-and-answer-module-authority-boundary-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `docs/521-official-voter-information-platform-information-panels-context-boxes-disclosure-labels-and-policy-wrapper-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/566-official-voter-information-platform-media-ai-answer-source-basis-states-transcript-vs-web-provenance-and-head-default-retention-discipline.md`
- `docs/583-official-voter-information-platform-media-stacked-authenticity-cues-identity-context-provenance-ordering-and-non-collapse-firewall.md`
- `docs/585-official-voter-information-platform-media-authenticity-cue-transport-cross-route-divergence-and-absence-non-inference-firewall.md`
- `docs/586-official-voter-information-platform-media-authenticity-cue-tension-aspect-separation-and-non-cancellation-firewall.md`
- `docs/587-official-voter-information-platform-media-authenticity-cue-lifecycle-timing-drift-and-non-retroactive-inference-firewall.md`
- `docs/588-official-voter-information-platform-media-authenticity-cue-attachment-points-scope-boundaries-and-non-inheritance-firewall.md`
- `docs/589-official-voter-information-platform-media-authenticity-cue-inspection-gates-expanded-details-and-non-ambient-visibility-firewall.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `artifacts/checklists/official-voter-information-platform-media-provenance-signal-checklist.md`
- `artifacts/templates/official-voter-information-platform-media-provenance-signal-payload.json`

## Why this exists (bounded)

This archive already distinguishes the media object itself (`369`), source-identity wrappers (`520`), context/policy wrappers (`521`), and player-native AI answer layers (`499`, `566`).
A smaller but distinct seam still remains:
**the same official media may also carry provenance signals about how it was captured, edited, signed, or disclosed, and viewers can overread those signals as if they settle whether the media is still the controlling official answer.**

Current primary-source guidance is specific enough to justify a compact control here.
The current C2PA 2.3 specification says the standard addresses certifying the source and history of media content and now includes live video streaming support, which matters for election briefings and livestream replays.
The C2PA FAQ says Content Credentials are tamper-evident, cryptographically signed provenance structures that can express how content was created and changed over time.
YouTube’s current “How this content was made” help says the platform carries forward disclosures from secure Content Credentials (C2PA) 2.1 or higher and may show labels on the player or in the description.
Its current “Captured with a camera” help says the disclosure depends on compatible tooling, that missing disclosure does **not** mean audio or visuals were altered, that ordinary storage/editing can break the provenance chain, and that some attacks such as “air-gapping” remain a known limitation.
Microsoft Research’s current media-authenticity overview says the usefulness and trustworthiness of provenance signals depend on ecosystem adoption, implementation choices, and governance, not only on the existence of the signal itself.
(xref: `c2pa_content_credentials_spec_2_3_html`; xref: `c2pa_faq_page`; xref: `youtube_how_this_content_was_made_disclosures_help_page`; xref: `youtube_captured_with_a_camera_disclosure_help_page`; xref: `microsoft_research_media_authenticity_methods_in_practice_blog_page`)

So the bounded question is not “are provenance signals good or bad?”
They can be useful.
The bounded question is smaller:
**once a voter sees a provenance icon, disclosure, or verification handoff on the same official media route, does that signal start acting like the whole proof that the media is official, current, unsuperseded, and legally sufficient to act on?**

## This is not the same thing as source identity, policy wrappers, metadata wrappers, or digest-first authenticity

`520` asks whether bylines, handles, badges, profile cards, and similar source-identity cues start acting like the whole proof that a media route is official.

`521` asks whether context panels, ratings, sensitivity cues, disclosure labels, or other policy/context wrappers start acting like the office’s whole explanation of authority or legal effect.

`514` asks whether titles, descriptions, thumbnails, posters, or other mutable metadata wrappers start acting like the controlling scope/currentness summary.

`194` asks how the office makes authenticity cheap to check through digest-first public notices and mirrored evidence, even when forged screenshots and synthetic media spread faster than explanation.

`584` asks a different question:
**once the same official media route carries a provenance signal about origin or edit history, does that supportive signal get overread as if it replaces the written/help lane, the office-channel directory, the current notice chain, or the digest-first authenticity posture?**

If the distinct problem is that **provenance is only one part of a larger same-route authenticity bundle because source-identity cues or context/policy wrappers are simultaneously doing visible work too**, use `583`.

If the distinct problem is that **provenance signals stayed supportive but were preserved, suppressed, or stripped differently across native pages, embeds, mirrors, file flows, or ordinary derivatives and reviewers started reading that transport drift like proof that the underlying answer changed**, use `585`.

If the distinct problem is that **a provenance cue visible for one asset or file was later inherited to sibling uploads, channel-level identity, or neighboring derivatives without separating object-level attachment from broader scope**, use `588`.

If the distinct problem is that **provenance cues are being read as if they cancel or override same-route identity or context/policy cues that are speaking to different aspects**, use `586`.

If the distinct problem is that **provenance detail on the same route was only available after expanded-description or other deliberate inspection and later readers started narrating that same-route detail as if it were ambient first-paint proof or route-level absence**, use `589`.

If the distinct problem is that **provenance-adjacent cue states on the same route differed across viewers because supported surface, language/country availability, or other bounded viewer conditions changed what could be seen without changing the route itself**, use `590`.

If the distinct problem is that **provenance visibility on the same route changed over time and later readers started treating one observed disclosure/provenance state as if it permanently or retroactively described the route**, use `587`.

If the distinct problem is that **later notes, screenshots, or packets fused provenance observations from different routes, times, viewer conditions, or interaction states into one apparent single-state posture**, use `591`.

A route may pass `194`, `203`, `369`, `520`, and `521` and still fail `584` if:
- a provenance badge is treated as proof that the media is still the current controlling instruction even though the written/help lane changed later;
- a “captured with a camera” or AI-made disclosure is treated as the office’s whole authenticity verdict instead of one bounded platform-carried signal;
- a third-party verification handoff becomes the only visible recovery path, so viewers have to leave the official route to decide what the office stands behind now;
- a clipped, transcoded, reuploaded, or embedded derivative loses the original provenance signal but keeps enough surrounding identity cues that viewers mistake the derivative for the fully preserved source object;
- or the absence of provenance is overread as proof of falsity even though the official route is current and ordinary handling stripped or never added the provenance chain.

## Provenance signals are supportive; they are not the office’s whole authority proof

The public-safe posture is simple:
**provenance can help describe where media came from and how it changed, but it does not by itself prove that the media is the still-current controlling answer, the full office instruction, or the only lawful route the voter should trust.**

At minimum, keep these layers distinct:
1. the current written page, notice, FAQ/help entry, or office contact that still controls action-changing next steps;
2. the official media object itself;
3. the provenance signal attached to that object, if any;
4. the verification or inspection handoff used to view provenance details;
5. whether the provenance cue was ambient on the route or only visible after expanded-description / deliberate inspection (`589`);
6. and any derivative routes — embeds, clips, downloads, screenshots, reposts, saved copies, or reuploads — that may preserve, restate, or lose that provenance differently.

That distinction matters because provenance feels decisive.
A viewer may infer that an icon or disclosure means:
- the office has authenticated the route for every present-tense purpose,
- the media is still the current controlling answer,
- the office reviewed every derivative carrying the same signal,
- or media lacking the signal must be altered or false.

This control exists to stop those collapses.

## Presence can help; absence is not dispositive

A provenance signal can be genuinely useful.
But public review should stay honest about what it does **not** settle.

YouTube’s current help is explicit that “captured with a camera” depends on compatible tools and opt-in use, that missing disclosure does not prove the content was altered, and that ordinary edits or unsupported handling can break the chain.
That makes absence a bounded fact, not an automatic falsity verdict.
(xref: `youtube_captured_with_a_camera_disclosure_help_page`)

For election media, that means:
- do not treat missing provenance as proof the office route is fake;
- do not treat present provenance as proof the instruction is still current;
- and do not let provenance presence/absence outrank the office’s written/help recovery lane when the question is what the voter should do now.

## Derivatives, transcodes, storage moves, and reposts can change the signal story

The same public media can appear in many containers:
- native watch pages,
- embedded players,
- downloaded files,
- clipped excerpts,
- screenshots or screen recordings,
- saved offline copies,
- mirrors,
- and platform-specific reuploads.

Some of those routes may preserve provenance signals; others may strip them, restate them differently, or expose only a summarized disclosure rather than the underlying details.
That means a review note for `584` should distinguish:
- the original office-published object,
- the visible provenance state on the route reviewed,
- and whether derivatives materially changed what a viewer could inspect or infer.

This is especially important for official election media because clips, reposts, and screenshots can keep circulating long after the office’s current written guidance changes.
A derivative that once carried an authenticity or provenance cue is still not automatically the present-tense controlling answer.

## Verification handoff should remain bounded

External provenance-inspection tools may help viewers inspect details.
That can be useful.
But the office should not make “go use a third-party verification site” the only recovery path to figure out what the office stands behind.

The safer posture is:
- provenance-inspection handoffs may exist,
- the office may name them honestly,
- but the current official page/help lane still needs to remain recoverable without assuming the viewer can upload media elsewhere, interpret a third-party panel, or resolve ecosystem trust questions on the fly.

## Currentness, legal effect, and actionability still come from the office lane

A provenance signal about origin or edit history does not by itself settle:
- whether the video is still the current guidance,
- whether a deadline or location changed,
- whether the recording has been superseded,
- whether the route is still the office’s preferred public path,
- or whether a viewer should act on the media without checking the current written/help lane.

That is why `584` pairs naturally with `369` and `305`.
The same media may be authentic in origin-history terms and still be stale, superseded, clipped out of context, or unsafe as the only action-changing instruction.

## Claims this control should support

1. **Provenance-subordination claim:** visible provenance signals remain supportive and do not replace the current written/help lane.
2. **Presence/absence honesty claim:** missing provenance is not overread as proof of falsity, and present provenance is not overread as proof of still-current authority.
3. **Derivative-honesty claim:** the archive distinguishes the source object from embeds, clips, screenshots, downloads, and reuploads that may preserve provenance differently.
4. **Verification-handoff claim:** third-party provenance inspection may assist review without becoming the office’s only recovery path.
5. **Currentness non-substitution claim:** origin/edit-history signals do not substitute for supersession, deadline, jurisdiction, or legal-effect review.

## Minimum review artifacts

For this surface, preserve bounded evidence of:
- the official media route reviewed;
- the visible provenance signal or absence state there;
- any verification/inspection handoff exposed to viewers;
- whether the current written/help lane remained recoverable from that route;
- whether derivatives materially changed the visible provenance story;
- and when the review was last verified.

Prefer compact route captures and short notes over large media uploads, user telemetry, or long third-party verification transcripts.

## What good looks like

A public-safe route in this lane usually has these properties:
- provenance signals help viewers orient without pretending to settle every authenticity or currentness question;
- the office names provenance honestly as supportive rather than sufficient;
- the current written/help lane remains visible and recoverable;
- derivatives that lose or restate provenance are reviewed as such;
- and the archive preserves only the small note needed to explain how provenance interacted with authority, currentness, and recovery.

## Related artifacts

- Template payload: `artifacts/templates/official-voter-information-platform-media-provenance-signal-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-media-provenance-signal-checklist.md`

## Source pointers

- C2PA 2.3 specification index (xref: `c2pa_content_credentials_spec_2_3_html`)
- C2PA FAQ (xref: `c2pa_faq_page`)
- YouTube Help: “How this content was made” disclosures (xref: `youtube_how_this_content_was_made_disclosures_help_page`)
- YouTube Help: “Captured with a camera” disclosure (xref: `youtube_captured_with_a_camera_disclosure_help_page`)
- Microsoft Research: media authenticity methods in practice (xref: `microsoft_research_media_authenticity_methods_in_practice_blog_page`)
