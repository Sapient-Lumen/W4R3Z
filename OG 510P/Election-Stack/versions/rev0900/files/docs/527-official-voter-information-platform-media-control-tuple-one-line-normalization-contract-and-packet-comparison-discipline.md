# 527 — Official voter-information platform media control tuple, one-line normalization contract, and packet-comparison discipline

**Track:** Shared

This document gives the recent platform-media companion layer one final compact output shape.

It exists so maintainers do not keep solving the same mixed-wrapper incident in four separate prose fragments:
- which media doc controlled (`523`),
- which normalized route state won (`524`),
- which wrapper mutation mattered (`525`), and
- which recovery target should have won (`526`).

The archive now has those decisions.
What it still needs is one **small comparable note contract** so packets can say the same thing the same way.

It composes with:
- `docs/206-digest-cards-and-low-bandwidth-publication.md`
- `docs/216-incident-triage-and-evidence-quickmap.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/524-official-voter-information-platform-media-route-state-lexicon-badge-normalization-and-capture-order-discipline.md`
- `docs/525-official-voter-information-platform-media-mutation-classes-first-contact-evidence-pack-and-snapshot-minimization-discipline.md`
- `docs/526-official-voter-information-platform-media-re-anchor-ladder-canonical-recovery-targets-and-wrapper-exit-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`

## Why this exists (bounded)

Current platform help still shows that one official media event can legitimately present several adjacent objects and state cues across time.
YouTube says a public Premiere watch page exists before the event begins and can be shared before start.
Vimeo says recurring-event viewers can watch past streams from the event page, while a specific archive can also be shared as its own video.
Microsoft says town-hall attendees can rewind during the event, return with **Watch Live**, and later receive an organizer-published recording link if one is published.
(xref: `youtube_premiere_new_video_help_page`; xref: `vimeo_watch_past_streams_recurring_event_help_page`; xref: `vimeo_share_my_video_help_page`; xref: `microsoft_attend_town_hall_help_page`)

That is exactly the environment where packet prose drifts even when reviewers basically agree.
One note says “countdown shell hid the answer.”
Another says “watch page before start.”
Another says “replay shell after the event.”
Another says “the real fix was Watch Live.”
All may be true, but cross-packet comparison becomes needlessly fuzzy.

This document adds one bounded rule:
**for mixed-wrapper platform-media incidents, emit one canonical control tuple before any longer prose.**

Recent revisions also added a large block of doc-only same-object companions (`540–581`).
Those companions are intentionally compact, but packets still risk slipping back into prose drift whenever maintainers need to carry one or two of those bounded state/alias/readiness facts beside the main tuple.
So `527` now also standardizes one optional **companion header line** that can travel with the tuple without pretending those subordinate facts are new heads, new routes, or new primary surfaces.
That header line now has a hard archive-wide **three-tag budget** so the packet header stays compact even when many co-true same-object facts exist, and one optional scoped spillway keeps any necessary overflow canonical without turning it into a second header.

## This is not the same thing as `523`, `524`, `525`, or `526`

`523` decides the controlling numbered doc.

`524` decides the normalized route state and capture order.

`525` decides the smallest evidence pack and the decisive wrapper mutation.

`526` decides the winning re-anchor / recovery target.

`527` does not replace any of them.
It says that once those decisions exist, the archive SHOULD compress them into one comparable line so:
- later reviewers can diff packets quickly,
- digest cards can stay small,
- mixed incidents stop expanding into four paragraphs of near-duplicate explanation, and
- future additions can tighten the tuple before minting another surface.

## The control tuple

For compact packets, the first normalized media note SHOULD fit this shape:

`primary=<doc>; route=<first-contact object>; state=<normalized state>; delta=<mutation class>; cue=<single decisive visible cue>; anchor=<winning recovery target>; why=<one-sentence authority reason>`

This is the archive's preferred one-line summary for incidents controlled by `369` or the `493–522` platform-media family and normalized through `523–526`.

When the same packet also needs one or more bounded same-object companion facts, reviewers MAY add one second line in this shape:

`companions=<doc:canonical_state_token[, doc:canonical_state_token...]>`

Use that optional line only for doc-only chain-layer companions whose main job is to preserve a subordinate same-object alias, state, pane, track, queue, or derivative-readiness fact without changing the controlling head.
Typical examples include `540–581`.

If the header budget is already spent but more bounded same-object facts still matter, reviewers MAY add one scoped third line in this shape:

`companions_overflow=<doc:canonical_state_token[, doc:canonical_state_token...]>`

That overflow line is **not** a rival header and **not** a second route summary. It is reserved for additional companion docs that did not fit in the header budget; do **not** repeat a companion doc there if that same doc already appears in `companions=`.
It is just a compact, body-scoped place to keep extra canonical companion tags when the packet would otherwise fall back into ad hoc prose.

If a carried companion doc also needs **one extra co-true same-doc fact** beyond its header or overflow winner, reviewers MAY add one final scoped line in this shape:

`companions_detail=<doc:canonical_state_token>`

That detail line is **not** a second header, **not** an overflow escape hatch for new companion docs, and **not** a rival to the controlling head.
Use it only for one additional canonical token total from a companion doc that already appears in `companions=` or `companions_overflow=`.
If several carried companion docs could each support extra same-doc residue, keep only the single most comparison-salient extra token in `companions_detail=` using the same carried-doc selection order that already governs header/overflow pressure; move anything else into one short `528` note or scoped sentence.

Examples:
- `companions=561:transcript_pending`
- `companions=545:auto_translate_selected, 552:auto_dub_selected`
- `companions=557:search_active, 561:settled_after_lag`
- `companions=562:answer_visible`
- `companions=562:answer_visible, 570:surface_visible_to_viewer, 572:minimum_word_or_length_floor_not_met`
- `companions=562:answer_visible, 565:linked_grounding_visible, 567:substantive_answer_returned`
  `companions_overflow=564:translated_output, 566:transcript_only_basis, 568:accuracy_warning_visible`
- `companions=562:answer_visible`
  `companions_detail=562:panel_open`
- `companions=562:answer_visible, 565:linked_grounding_visible, 567:substantive_answer_returned`
  `companions_overflow=564:translated_output, 566:transcript_only_basis, 568:accuracy_warning_visible`
- `companions=562:answer_visible, 567:substantive_answer_returned, 574:scene_object_or_slide_basis_disclosed`
  `companions_detail=562:panel_open`

The `companions=` line is intentionally smaller than the full per-doc note shapes in `540–581`.
Its job is packet-header comparability, not replacing the deeper scoped note when one is actually needed.
The optional `companions_overflow=` line exists only so header-budget overflow across **different companion docs** can stay canonicalized and compact instead of slipping back into freeform prose.
The optional `companions_detail=` line exists only so one extra co-true same-doc fact from an already-carried companion doc can stay canonicalized and compact instead of dissolving back into prose drift.
If more than three bounded same-object companion docs matter, choose which docs stay in `companions=` and which spill into `companions_overflow=` by this comparison-selection order **before** you render either line in ascending doc-number order:
- first any present `540–561` route/replay/derivative companions in doc-number order,
- then any present AI companions in this fixed order: `562`, `570`, `581`, `572`, `575`, `576`, `573`, `563`, `580`, `577`, `579`, `578`, `571`, `565`, `567`, `564`, `566`, `574`, `568`, `569`.
Put the first three selected docs in `companions=`, the next three (if any) in `companions_overflow=`, and move anything beyond that into one short scoped sentence or `528` note.
If one of the carried companion docs still needs one extra same-doc fact after that selection, keep at most one additional canonical token total in `companions_detail=` rather than reopening freeform prose. When more than one carried doc could claim that slot, choose the detail token from the earliest carried doc under the same comparison-selection order that governed header/overflow placement. If that carried companion doc also declares `detail_pick_order=<...>`, choose the first applicable token from that list that is **not already carried for that doc**; otherwise render the single most comparison-salient extra same-doc token explicitly.
That selection order is only a compact comparison/reproduction rule for budget pressure; it is **not** a claim that later-spilling facts were false, unimportant, or uncitable. `582` explains the rationale in maintainer terms, adds four starter carry profiles plus a compression ladder, and packages the rest as the **AI-tail proof-budget firewall core**. When the AI-tail bundle still feels underdetermined after the raw order is applied, use `582`'s `availability-first`, `framing-first`, `answer-proof-first`, or `repair-first` profile before inventing an ad hoc four-doc mix, then use its compression ladder if the bundle is still too large; if the remaining problem is sentence packing rather than bundle choice, invoke the firewall core before repacking more AI docs into the same note line. But if the carried AI companions are already obvious from the current route and the only remaining work is tuple/header normalization, stay in `527` and do **not** add `582` just because the same-object AI tail is present. Use `582`'s **neighbor-side handoff default** here: keep the line in `527` while tuple/header/overflow normalization is still the only unresolved move, then swap to the single governing `582` slice only if the remaining difficulty has actually crossed into `582`-owned bundle choice or sentence-packing territory.

## Canonical companion normalization

To keep packet headers and scoped overflow lines diffable, a `companions=` line or `companions_overflow=` line SHOULD be normalized before it is published or compared:
- choose which docs occupy the header and overflow by the comparison-selection order above whenever the three-tag budget is actually tight,
- sort the tags **within each rendered line** by doc number ascending (`545` before `561`),
- keep at most **one tag per companion doc** in each line and never repeat the same companion doc across both lines of one packet, and
- treat rendered order as **formatting only**, not as evidence of precedence or chronology.

Companion tags are also **positive and packet-local**.
If a later packet omits a previously seen companion tag from either line, that omission means only that the later packet did not carry that scoped fact there.
It does **not** by itself prove the fact became false, cleared, or permanently irrelevant.
If clearance itself matters, say so explicitly in the packet body or in one short `528` transition note instead of asking readers to infer negation from line silence.

If a later packet carries the **same companion doc** with a **different canonical token** (for example `561:transcript_pending` later becoming `561:settled_after_lag`), read that as an explicit packet-local observed-state replacement for that doc inside the later packet.
That replacement proves a different bounded fact was affirmatively recorded there.
It does **not** by itself rewrite older packets, negate every earlier scoped fact, or promote a new head.
If the replacement matters for continuity, currentness, or citation posture, say so explicitly in one short `528` transition note or packet-body sentence rather than asking readers to infer full semantics from header shape alone.

If two bounded facts from the same companion doc matter, first check whether that companion doc declares a small `header_pick_order=<...>` preference list for packet headers and, when available, a matching `detail_pick_order=<...>` preference list for the single detail slot.
If it does, keep the **first applicable canonical token from that doc-declared header order** in the header and carry one other co-true fact from that *same doc* in `companions_detail=` when that single detail slot is both needed and available, preferably by taking the first applicable non-carried token from the doc-declared detail order; otherwise preserve it in one short scoped sentence or `528` note. Do **not** duplicate that doc in `companions_overflow=`. For example, if the same AI pane is open and already shows an answer card, `562` should normally contribute only `answer_visible` to the header while the co-true `panel_open` fact can live in `companions_detail=562:panel_open`. If that same visible answer also exposes linked grounding, `565` may separately contribute `linked_grounding_visible` without competing with `562` over pane-state vocabulary. If the same observed answer is also visibly conditioned by earlier prompts in the same thread, `563` may separately contribute `follow_up_context_carried` without competing with `562` over pane-state vocabulary. If the same answer is also rendered bilingually, `564` may separately contribute `mixed_or_bilingual_output` without competing with either pane-state or thread-state vocabulary. If the same answer is also documented as transcript-only or platform-and-web in basis, `566` may separately contribute `transcript_only_basis` or `platform_and_web_basis` without competing with pane, thread, language, or grounding vocabulary. If the same visible interaction also needs one compact answer-versus-no-answer disposition token, `567` may separately contribute `substantive_answer_returned`, `scope_limited_no_answer`, or `prerequisite_missing_no_answer` without competing with pane, thread, language, grounding, or provenance vocabulary. Keep prompt-origin and follow-up-conditioning facts in `563`; keep answer-language-mode facts in `564`; keep grounding/reference-state facts in `565`; keep answer-source-basis/provenance facts in `566`; keep answer-outcome/disposition facts in `567`; do not restate any of them as pseudo-fields inside a `562` note once pane state is already preserved.
If it does not, keep the one that most changes reproduction, comparison, or citation scope in the header and carry one other same-doc fact in `companions_detail=` only when that single detail slot is both needed and available, otherwise in the packet body or one short `528` note rather than duplicating that doc in `companions_overflow=`.
That header choice is only a normalization rule for compact packet comparison.
It does **not** mean omitted co-true same-doc facts were false, cleared, or unimportant; it only means they were preserved outside the one-line header in `companions_detail=` or one short scoped note / `528` note rather than duplicated into `companions_overflow=`.

Header tokens should also be **doc-native and canonical**.
For each `doc:...` tag, use that companion document's own principal bounded-state token rather than an ad hoc synonym, paraphrase, or prose gloss.
In practice this usually means reusing the note contract's main enum-like field value directly (for example `545:auto_translate_selected`, `557:search_active`, `559:behind_live`, or `561:transcript_pending`).
If the companion doc's note contract shows a short plain-language value with spaces, normalize it to compact lower-snake-case in the header rather than inventing a new alias.

That rule matters because packet headers are intentionally smaller than the full note contracts.
Without one canonical token source, different maintainers can preserve the same bounded fact with different tag words and create fake diffs even when packet meaning did not change.

## Field meanings

| Field | Meaning | Usually comes from |
|---|---|---|
| `primary` | the controlling numbered boundary doc | `523` |
| `route` | the actual first-contact object the reviewer opened | `524` / `525` |
| `state` | the archive-controlled normalized route state | `524` |
| `delta` | the decisive wrapper mutation class | `525` |
| `cue` | one visible cue that proves the state or mutation | `524` / `525` |
| `anchor` | the highest-precedence office-controlled recovery target | `526` |
| `why` | one sentence explaining why `anchor` outranks the nearby loser | `526` |
| `companions` | optional compact header list of subordinate same-object companion classes that most affect reproduction, comparison, or citation scope | `540–581` when relevant |
| `companions_overflow` | optional compact body-scoped list of additional subordinate same-object companion classes from *different companion docs* that mattered but did not fit in the three-tag header budget | `540–581` when relevant |
| `companions_detail` | optional compact body-scoped single extra canonical token from one already-carried companion doc when one same-doc residue fact still needs preservation after header/overflow selection | `540–581` when relevant |

## Compression rules

1. **One route, not every route.**
   Name the first-contact object, not the whole route family.
2. **One state token.**
   Use the `524` normalized state vocabulary, not literal badge soup.
3. **One decisive mutation.**
   If many wrappers were visible, record the one that actually changed authority, currentness, legibility, or recovery.
4. **One cue, not a screenshot inventory.**
   Pick the strongest visible cue that later reviewers can reason from.
5. **One anchor.**
   Name the winning recovery target, not every possible exit.
6. **One why-sentence.**
   The reason should explain precedence, not retell the full incident.
7. **Companions stay subordinate.**
   Use the optional `companions=` line only when a bounded same-object companion fact materially affects reproduction, comparison, or citation scope.
8. **Canonicalize companion order and uniqueness.**
   Sort `doc:bounded_class` tags by doc number ascending and keep at most one tag per companion doc in each companion line. Treat each line as a normalized set, not a mini-timeline.
9. **Use doc-declared header/detail winners when available.**
   If a companion doc declares `header_pick_order=<...>`, choose the first applicable token from that list for the header. If that same carried doc also needs one extra co-true fact and declares `detail_pick_order=<...>`, choose the first applicable token from that list that is not already carried for that doc in `companions_detail=`; otherwise carry the single most comparison-salient extra same-doc fact there explicitly. Move anything beyond that into one short `528` note or scoped sentence, not into `companions_overflow=`.
10. **Enforce the companion-header budget.**
   Keep at most three `doc:bounded_class` tags in `companions=`. If more bounded facts matter, keep the three that most change reproduction, comparison, or citation scope in the header.
11. **Use overflow only as scoped spillway.**
   If more than three companion facts from *different companion docs* still matter after header selection, you MAY add `companions_overflow=` with up to three additional canonical tags. When both lines are used, let the comparison-selection order above decide which docs stay in the header and which spill into overflow; do not choose the top three ad hoc from packet to packet. Treat the overflow line as a compact body-scoped spillway for additional companion docs, not a second header or a rival head.
12. **Use detail only for same-doc residue.**
   If a carried companion doc still needs one extra co-true canonical token after header/overflow selection, you MAY add that one extra token in `companions_detail=`. Keep `companions_detail=` to exactly one tag at most, use it only for a doc that already appears in `companions=` or `companions_overflow=`, and when more than one carried doc could claim that slot choose the earliest carried doc under the same comparison-selection order that governed header/overflow placement. If that doc declares `detail_pick_order=<...>`, use the first applicable token from that list that is not already carried for that doc.
13. **Do not smuggle supersession through companions.**
   A `companions=` line, `companions_overflow=` line, or `companions_detail=` line never changes the head, the first-contact object, or the winning recovery target by itself.
14. **Do not overread same-doc token replacement.**
   A later `561:settled_after_lag` replacing `561:transcript_pending`, or any comparable same-doc canonical-token swap, is explicit scoped observation for that later packet — not automatic durable negation, not chain closeout, and not a new controlling head unless `528–529` say a controlling field moved.

If a packet genuinely needs more than one tuple, emit a second line only when the incident crossed a real state boundary or a second first-contact object.
Do **not** multiply tuples just because several chrome elements were visible at once.
Do **not** fork a new tuple merely because one subordinate companion tag appeared or cleared.

## Examples

- `primary=508; route=public Premiere watch page; state=pre_start_public_shell; delta=presentation_wrapper; cue=countdown plus trailer on public watch page; anchor=county event-status page then official watch page; why=the event shell was public before start, but the written status lane still controlled action-changing guidance`
- `primary=516; route=town hall attendee window; state=live_behind_edge; delta=route_state; cue=rewound progress bar plus Watch Live while chat stayed live; anchor=official town-hall route via Watch Live; why=the viewer needed the true live edge rather than a delayed slice`
- `primary=509; route=recurring-event page showing prior stream; state=ended_replay_or_archive; delta=route_state; cue=event player exposed past streams after the live moment ended; anchor=published recording link from the organizer; why=a specific replay object had already been designated`
- `primary=511; route=embedded player on partner page; state=ended_replay_or_archive; delta=portability_wrapper; cue=host-page embed plus canonical source link; anchor=office media hub; why=the embed transported the recording but did not outrank the office-controlled source route`
- `primary=499; route=public watch page; state=ended_replay_or_archive; delta=answer_wrapper; cue=Ask-this-video panel under player; anchor=county written FAQ; why=the generated answer layer stayed subordinate to the office's maintained written route`
  `companions=545:auto_translate_selected, 561:transcript_pending`

A pane-state note and a thread-state note can travel together when they answer different questions.
Good:
`companions=562:answer_visible, 563:follow_up_context_carried`
That means the same object still controls, one generated answer card is visible, and that answer is visibly conditioned by earlier turns — without forcing the archive to preserve the whole conversation log.
Good:
`companions=562:suggested_question_selected, 570:surface_visible_to_viewer, 572:minimum_word_or_length_floor_not_met`
`companions_overflow=563:fresh_turn_only, 564:translated_output, 565:linked_grounding_visible`
`companions_detail=572:spoken_content_profile_unsuitable`
That means a suggested-question chip was the visible pane state, the same packet also needed to preserve that the AI layer was visible to this viewer yet still failed the platform's published minimum-content rule, and the thread remained fresh; translated output and linked grounding spilled compactly because the archive's AI spill order now treats visibility/gating, input-sufficiency, transcript-language alignment, terminology fidelity, and governing-transcript notes as more comparison-salient than later provenance/caution notes when the same packet would otherwise overclaim comparability. The detail line then preserves one extra co-true fit fact from an already-carried sufficiency doc without duplicating that doc across header and overflow. If informational-only warning visibility from `568`, transcript-only basis (`566`), or answer-returned state (`567`) also matters, keep whichever one is more comparison-salient in one short scoped sentence or `528` note once both companion lines are already full and the single detail slot is already in use.

## Relationship to digest cards and capture notes

When a packet also includes a longer capture note, the tuple SHOULD come first and the prose SHOULD elaborate only what the tuple cannot say compactly.
If a bounded same-object companion fact matters, place the optional `companions=` line immediately after the tuple rather than scattering those tags through later prose. Keep that line within the three-tag budget. If more companion facts from additional companion docs still matter, you MAY add one canonicalized `companions_overflow=` line immediately after it; keep that overflow line compact too, and move anything beyond it into one short scoped sentence or `528` note instead of adding more pseudo-header lines. If one already-carried companion doc still needs one extra co-true same-doc fact, you MAY add one canonicalized `companions_detail=` line immediately after the overflow/header lines; keep that detail line to one tag total, prefer the doc's own `detail_pick_order=<...>` winner when one is declared, and move anything beyond it into one short scoped sentence or `528` note. Co-true secondary facts from a doc that is already present in `companions=` or `companions_overflow=` belong in `companions_detail=` when that single slot is enough, not in duplicated header/overflow tags.
That keeps `206` digest cards and `223` capture notes aligned instead of letting one drift into a different interpretation.
`528` then governs whether a later tuple belongs in the same evolving object chain, a forked packet within that chain, or a genuinely new incident.
`529` then says which tuple in that chain should be treated as the current controlling head instead of merely a historical leg.
`530` then says what later notes should cite by default once that head/historical-leg split already exists.

A useful maintainer shortcut is:
- choose the controlling doc with `523`,
- normalize the state with `524`,
- choose the decisive mutation and compact evidence pack with `525`,
- choose the recovery target with `526`,
- then emit the tuple here before writing anything longer.

## Promotion rule

Future media additions should usually **not** be promoted just because packet prose keeps drifting in how it summarizes the same kind of mixed-wrapper incident.
If the real problem is summary-shape drift, tighten `527` first.
If the tuple is already stable but reviewers keep splitting or merging later observations inconsistently, tighten `528` instead.
If the chain is already stable but packets still drift in which one sounds current, tighten `529` instead.
Only add another numbered surface when the underlying first-contact object or authority boundary is genuinely different.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that the tuple cannot stabilize cross-packet comparison on its own.
