# 586 — Official voter-information platform media authenticity-cue tension, aspect separation, and non-cancellation firewall

**Track:** Shared / Public surfaces

This document defines a bounded control for **the same official voter-information media route when supportive authenticity-adjacent cues point at different aspects of trust and later readers start treating one cue like it cancels, overrides, or neutralizes another**:
source-identity cues such as bylines, handles, badges, uploader cards, and profile names,
platform context/policy wrappers such as election panels, publisher-context boxes, disclosure labels, ratings, sensitivity cues, and protection banners,
and provenance/origin-history signals such as Content Credentials / C2PA disclosures, “How this content was made,” “captured with a camera,” or similar metadata-backed indicators.

It does not create a new authenticity score.
It adds one narrow rule:
**when those supportive cues coexist on the same official media route but answer different questions, the archive should preserve that aspect split without quietly treating one cue as cancellation, cure, or override of the others.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `docs/521-official-voter-information-platform-information-panels-context-boxes-disclosure-labels-and-policy-wrapper-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/583-official-voter-information-platform-media-stacked-authenticity-cues-identity-context-provenance-ordering-and-non-collapse-firewall.md`
- `docs/584-official-voter-information-platform-media-provenance-signals-content-credentials-and-non-substitutive-authenticity-discipline.md`
- `docs/585-official-voter-information-platform-media-authenticity-cue-transport-cross-route-divergence-and-absence-non-inference-firewall.md`
- `docs/588-official-voter-information-platform-media-authenticity-cue-attachment-points-scope-boundaries-and-non-inheritance-firewall.md`
- `docs/587-official-voter-information-platform-media-authenticity-cue-lifecycle-timing-drift-and-non-retroactive-inference-firewall.md`
- `docs/589-official-voter-information-platform-media-authenticity-cue-inspection-gates-expanded-details-and-non-ambient-visibility-firewall.md`
- `docs/590-official-voter-information-platform-media-authenticity-cue-viewer-state-variance-eligibility-conditions-and-non-universality-firewall.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`

## Why this exists (bounded)

The archive already distinguishes:
`520` for source identity,
`521` for context/policy wrappers,
`583` for same-route stacking,
`584` for provenance signals,
and `585` for cross-route cue transport.
A smaller but still important seam remains:
**the same route can show cues that look directionally inconsistent if reviewers forget that they speak to different aspects — for example, channel identity, platform-supplied context, and origin history — and then one cue gets cited as if it cancelled the others.**

Current primary-source guidance is specific enough to justify a compact bridge.
YouTube’s current verified-channel help says verification distinguishes the official channel of a creator, brand, company, or public figure and is not an endorsement from YouTube.
Its current publisher-context and election-information help says some panels are informational, can depend on third-party sources or vetted partners, and can vary by route, election, country, or context.
Its current “How this content was made” and “captured with a camera” help says those disclosures describe how content was made or whether compatible capture/provenance tooling was used, and that missing disclosure does not itself prove alteration.
The current C2PA material says Content Credentials are provenance/history structures and do not themselves make truth-value judgments about the content.
(xref: `youtube_verified_channels_help_page`; xref: `youtube_publisher_context_information_panel_help_page`; xref: `youtube_election_information_panels_help_page`; xref: `youtube_how_this_content_was_made_disclosures_help_page`; xref: `youtube_captured_with_a_camera_disclosure_help_page`; xref: `c2pa_content_credentials_spec_2_3_html`; xref: `c2pa_faq_page`)

So the bounded question is not whether these cues are useful.
They often are.
The bounded question is smaller:
**once the same official media route simultaneously carries cues about source identity, platform context, and provenance/origin history, does the archive start reading them like they all answer the same question — and then use one cue to wipe away another?**

## This is not the same thing as `520`, `521`, `583`, `584`, or `585`

`520` asks whether identity cues start acting like the whole proof that a route is official or current.

`521` asks whether context/policy wrappers start acting like the whole explanation of authority, currentness, or legal effect.

`583` asks whether several supportive cue families stacked on the same route started acting like compound proof.

`584` asks whether provenance/origin-history signals started acting like the whole proof of authenticity or current authority.

`585` asks whether supportive cues were preserved or stripped differently across routes and wrappers.

`586` asks a different question:
**when same-route supportive cues point at different aspects and later readers start treating one as cancellation, contradiction, cure, or override of another, how should the archive preserve that tension without collapsing the route into a single positive-or-negative authenticity score?**

If one cue family clearly governs, use that family doc.
If the harder problem is mere same-route co-presence, use `583`.
If the harder problem is cross-route divergence, use `585`.
If the harder problem is cue attachment-point scope rather than aspect tension, use `588`.
If the harder problem is same-route cue timing rather than same-route non-cancellation, use `587`.
If the harder problem is same-route discoverability rather than same-route non-cancellation, use `589`.
If the harder problem is same-route viewer conditionality rather than same-route non-cancellation, use `590`.
If the harder problem is not same-route tension itself but a later packet or summary fused route/time/viewer/interaction observations into one faux simultaneous posture, use `591`.
Use `586` only when the decisive fact is that **same-route cue tension changed what later readers thought the route proved because they were treating aspect-specific cues as if they cancelled one another.**

## Default rule: keep current control with the head; keep cue aspects separate; do not allow supportive cues to cancel each other

By default, later notes SHOULD still cite the current controlling head under `530`, or the fallback anchor if the chain is headless.
A cue-tension note exists only to explain one bounded interpretation problem around that head.

Use this triage order:
1. if the decisive claim is really about source identity, use `520`;
2. if the decisive claim is really about a context/policy wrapper, use `521`;
3. if the decisive claim is really about provenance/origin-history signaling, use `584`;
4. if the decisive claim is that several supportive cues merely stacked and cumulatively over-signaled trust, use `583`;
5. if the decisive claim is that a route or wrapper change altered which cues were visible, use `585`;
6. if the decisive claim is that reviewers were inheriting a cue to the wrong object or wrapper scope, use `588`;
7. use `586` only when the decisive claim is that **reviewers were reading same-route aspect-specific cues as if one cancelled or overruled another**.
8. if the decisive claim is that a same-route cue required deliberate inspection and later notes flattened that into ambient visibility or absence, use `589`.
9. if the decisive claim is that different viewers on the same route saw different cue states because of bounded viewer conditions, use `590`.

This means `586` is not a new preferred citation lane.
It is a compact bridge for the cases where same-route supportive cues felt inconsistent only because they were answering different questions.

## Keep aspect splits explicit

At minimum, keep these aspects separate:
1. **channel/source identity** — who the platform says owns or publishes the route (`520`);
2. **platform context/policy state** — what the platform or partner-supplied wrapper says about topic, funding, sensitivity, disclosure, or protection (`521`);
3. **origin/history posture** — what provenance tooling says about how the asset was captured, edited, or carried (`584`);
4. **current office control** — whether the office’s written/help lane and the current media head still control (`194`, `369`, `529`, `530`).

That separation matters because the public may wrongly perform a kind of informal arithmetic:
- “verified uploader” can be overread as if it cancelled provenance caution,
- provenance/camera cues can be overread as if they cancelled identity or currentness questions,
- and context/policy wrappers can be overread as if they disowned or endorsed the route as a whole.

`586` exists to stop that arithmetic from turning into archive logic.

## Minimal cue-tension note grammar

When same-route cue tension itself matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; cue_tension_state=<identity_vs_context|identity_vs_provenance|context_vs_provenance|identity_context_provenance_tension|mixed_or_unclear|unknown>; aspect_owner=<520|521|584|mixed>; cancellation_rule=<none>; cite_default=<head|fallback anchor>; cite_tension_when=<claim about same-route non-cancellation or aspect separation>; promote_tension=<no>; basis=<why the same-route cue tension mattered without becoming a new proof object>`

This is a note contract, not a new schema.
It exists so packet notes can say “these cues were read against each other, but they were speaking to different aspects” without minting a new head, a new evidence kind, or a positive/negative authenticity score.

## Typical uses

1. **Identity vs provenance**
   The same head still controls, but a familiar verified uploader and a provenance/disclosure cue were read as if one settled or negated the other.
2. **Identity vs context**
   The same head still controls, but a familiar official-looking byline/badge and a platform context/policy wrapper were read as if one overrode the other.
3. **Context vs provenance**
   The same head still controls, but a policy/disclosure wrapper and provenance signal were read as if they answered the same question when they did not.
4. **Three-way tension**
   The same head still controls, but identity, context, and provenance cues all appeared and later readers started doing informal cancellation across the whole stack.

## When not to use this

Do **not** use `586` when:
- only one of `520`, `521`, or `584` actually matters;
- the real issue is simply that several supportive cues appeared together — use `583`;
- the real issue is that supportive cues traveled unevenly across routes — use `585`;
- the decisive issue is still the media object’s date, scope, currentness, or correction status — use `369`/`529`/`530`;
- the decisive issue is that a same-route cue only appeared after expand/click/tap/hover/details interaction and later notes flattened that discoverability fact into ambient visibility or absence — use `589`;
- or the only reason to cite `586` is that reviewers found the route emotionally confusing without any bounded same-route cue-cancellation claim.

If deleting the same-route aspect-split fact would erase **why one supportive cue was wrongly treated as wiping out another**, `586` is probably right.
If deleting that fact would still leave a plain single-family claim or a simple stacked-cues claim, use the narrower doc and omit `586`.

## Examples

- `head=county_board_watch_packet; cue_tension_state=identity_vs_provenance; aspect_owner=mixed; cancellation_rule=none; cite_default=head; cite_tension_when=proving that a verified official-channel wrapper was later read as if it cancelled an origin-history disclosure about altered or synthetic content; promote_tension=no; basis=identity and provenance answered different questions on the same route`
- `head=state_results_replay_packet; cue_tension_state=identity_vs_context; aspect_owner=mixed; cancellation_rule=none; cite_default=head; cite_tension_when=proving that a familiar official uploader byline was later cited as if it overrode the watch-page context/disclosure wrapper; promote_tension=no; basis=channel identity did not erase the wrapper’s own aspect`
- `head=town_hall_embed_packet; cue_tension_state=context_vs_provenance; aspect_owner=mixed; cancellation_rule=none; cite_default=head; cite_tension_when=proving that a platform disclosure wrapper and a provenance cue were later read as if they were one merged truth judgment; promote_tension=no; basis=policy/disclosure and origin history remained distinct aspects`

## Tie-breaker when reviewers ask “which cue wins?”

Ask four questions:
- did the underlying office-controlled media object or written/help head actually change,
- which cue is speaking to source identity,
- which cue is speaking to context/policy posture,
- and which cue is speaking to origin/history provenance?

If the answer is that the route is stable and the cues merely speak to different aspects, **none of the supportive cues “wins” by cancelling the others**.
Keep current control anchored elsewhere and use `586` only to preserve that aspect split.

## Promotion rule

Future media additions should usually **not** be promoted just because same-route supportive cues felt awkward or mutually confusing.
Tighten `520`, `521`, `583`, `584`, `585`, or `586` first.
Only add another numbered surface when the archive proves that one narrower cue family or one narrower route class still causes repeated misrouting after this non-cancellation bridge exists.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless same-route cue-tension notes still drift after this compact bridge exists.
